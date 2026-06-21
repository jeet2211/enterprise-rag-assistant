from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.routes.chat import router as chat_router
from app.api.routes.documents import router as documents_router
from app.api.routes.health import router as health_router
from app.api.routes.upload import router as upload_router
from app.config.settings import Settings
from app.models.db import Base, build_engine, build_session_factory
from app.services.document_service import DocumentService


class FakeRetriever:
    def __init__(self, search_results: Optional[list[dict[str, object]]] = None, fail_health: bool = False):
        self.search_results = search_results or []
        self.fail_health = fail_health
        self.search_calls: list[tuple[str, int, Optional[list[str]]]] = []
        self.deleted_document_ids: list[str] = []
        self.healthcheck_calls = 0

    def add_chunks(self, *, document_id: str, filename: str, chunks: list[dict[str, object]]) -> None:
        self.search_results = self.search_results

    def search(self, query: str, top_k: int = 5, document_ids: Optional[list[str]] = None) -> list[dict[str, object]]:
        self.search_calls.append((query, top_k, document_ids))
        return self.search_results

    def delete_document(self, document_id: str) -> None:
        self.deleted_document_ids.append(document_id)

    def healthcheck(self) -> bool:
        self.healthcheck_calls += 1
        if self.fail_health:
            raise RuntimeError("retriever unavailable")
        return True


class FakePipeline:
    def __init__(self, document_service: DocumentService):
        self.document_service = document_service
        self.process_calls: list[tuple[str, str, str]] = []
        self.delete_calls: list[tuple[str, str]] = []

    def process_document(self, document_id: str, file_path: str, filename: str) -> None:
        self.process_calls.append((document_id, file_path, filename))
        self.document_service.update_document(document_id, status="ready", page_count=3, error_msg=None)

    def delete_document(self, document_id: str, file_path: str) -> None:
        self.delete_calls.append((document_id, file_path))
        Path(file_path).unlink(missing_ok=True)


class FakeChatService:
    def __init__(self):
        self.calls: list[dict[str, object]] = []

    def answer(self, *, question: str, session_id: str, top_k: Optional[int] = None):
        from app.models.responses import Citation

        self.calls.append({"question": question, "session_id": session_id, "top_k": top_k})
        return (
            f"Answer for {question}",
            [
                Citation(document_name="policy.pdf", page_number=2, chunk_preview="Relevant excerpt"),
                Citation(document_name="guide.pdf", page_number=7, chunk_preview="Supporting excerpt"),
            ],
            [
                "Show the exact passage that supports the answer.",
                "Summarize the key ideas from policy.pdf page 2.",
                "Compare policy.pdf page 2 with guide.pdf page 7.",
            ],
        )


@pytest.fixture()
def settings(tmp_path: Path) -> Settings:
    return Settings(
        gemini_api_key="",
        db_url=f"sqlite:///{tmp_path / 'test.db'}",
        upload_dir=str(tmp_path / "uploads"),
        chroma_persist_dir=str(tmp_path / "chroma"),
        log_level="DEBUG",
    )


@pytest.fixture()
def session_factory(settings: Settings):
    engine = build_engine(settings.db_url)
    Base.metadata.create_all(bind=engine)
    return build_session_factory(engine)


@pytest.fixture()
def document_service(session_factory):
    return DocumentService(session_factory)


@pytest.fixture()
def retriever():
    return FakeRetriever(
        search_results=[
            {
                "text": "Relevant policy details",
                "metadata": {
                    "document_name": "policy.pdf",
                    "page_number": 2,
                    "chunk_preview": "Relevant policy details",
                },
                "distance": 0.11,
            }
        ]
    )


@pytest.fixture()
def pipeline(document_service: DocumentService):
    return FakePipeline(document_service)


@pytest.fixture()
def chat_service():
    return FakeChatService()


@pytest.fixture()
def test_app(settings: Settings, document_service, retriever, pipeline, chat_service):
    app = FastAPI()
    app.include_router(health_router, prefix="/api/v1")
    app.include_router(upload_router, prefix="/api/v1")
    app.include_router(chat_router, prefix="/api/v1")
    app.include_router(documents_router, prefix="/api/v1")

    @app.get("/")
    def root():
        return {"status": "ok", "service": "enterprise-rag-assistant"}

    app.state.settings = settings
    app.state.document_service = document_service
    app.state.retriever = retriever
    app.state.pipeline = pipeline
    app.state.chat_service = chat_service
    app.state.embedding_service = object()
    app.state.start_time = datetime(2024, 1, 1, 12, 0, 0)
    app.state.now = lambda: datetime(2024, 1, 1, 12, 0, 42)
    return app


@pytest.fixture()
def client(test_app):
    with TestClient(test_app) as test_client:
        yield test_client
