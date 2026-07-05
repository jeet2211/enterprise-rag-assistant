from __future__ import annotations

from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi import _rate_limit_exceeded_handler
from sqlalchemy import text

from app.core.rate_limit import limiter
from app.api.routes.chat import router as chat_router
from app.api.routes.documents import router as documents_router
from app.api.routes.feedback import router as feedback_router
from app.api.routes.health import router as health_router
from app.api.routes.upload import router as upload_router
from app.config.settings import get_settings
from app.models.db import Base, build_engine, build_session_factory
from app.rag.pipeline import RAGPipeline
from app.rag.retriever import Retriever
from app.services.chat_service import ChatService, SessionMemoryStore
from app.services.document_service import DocumentService
from app.services.embedding_service import EmbeddingService
from app.services.pdf_service import PDFService
from app.utils.logger import configure_logging


settings = get_settings()
configure_logging(settings.log_level)


def _migrate_sqlite_schema(engine) -> None:
    """Backfill columns for older SQLite volumes created before the current model."""
    if engine.url.get_backend_name() != "sqlite":
        return

    with engine.connect() as conn:
        rows = conn.execute(text("PRAGMA table_info(documents)")).fetchall()
        existing_columns = {row[1] for row in rows}

    migrations = []
    if "file_hash" not in existing_columns:
        migrations.append("ALTER TABLE documents ADD COLUMN file_hash VARCHAR(64)")
    if "chunk_count" not in existing_columns:
        migrations.append("ALTER TABLE documents ADD COLUMN chunk_count INTEGER NOT NULL DEFAULT 0")

    if not migrations:
        return

    with engine.begin() as conn:
        for statement in migrations:
            conn.execute(text(statement))

    with engine.begin() as conn:
        conn.execute(text("CREATE INDEX IF NOT EXISTS ix_documents_file_hash ON documents (file_hash)"))


@asynccontextmanager
async def lifespan(app: FastAPI):
    Path(settings.upload_dir).mkdir(parents=True, exist_ok=True)
    Path(settings.chroma_persist_dir).mkdir(parents=True, exist_ok=True)

    engine = build_engine(settings.db_url)
    Base.metadata.create_all(bind=engine)
    _migrate_sqlite_schema(engine)
    session_factory = build_session_factory(engine)

    embedding_service = EmbeddingService(settings.embedding_model)
    retriever = Retriever(settings.chroma_persist_dir, embedding_service)
    document_service = DocumentService(session_factory)
    pdf_service = PDFService()
    memory_store = SessionMemoryStore(settings.session_memory_k)
    chat_service = ChatService(retriever, settings, memory_store, session_factory=session_factory)
    pipeline = RAGPipeline(pdf_service, embedding_service, retriever, document_service, settings)

    app.state.settings = settings
    app.state.engine = engine
    app.state.session_factory = session_factory
    app.state.embedding_service = embedding_service
    app.state.retriever = retriever
    app.state.document_service = document_service
    app.state.pdf_service = pdf_service
    app.state.memory_store = memory_store
    app.state.chat_service = chat_service
    app.state.pipeline = pipeline
    app.state.start_time = datetime.utcnow()
    app.state.now = datetime.utcnow

    yield


app = FastAPI(title="Enterprise RAG Assistant", version="2.0.0", lifespan=lifespan)
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router, prefix="/api/v1")
app.include_router(upload_router, prefix="/api/v1")
app.include_router(chat_router, prefix="/api/v1")
app.include_router(documents_router, prefix="/api/v1")
app.include_router(feedback_router, prefix="/api/v1")


@app.get("/")
def root():
    return {"status": "ok", "service": "enterprise-rag-assistant", "version": "2.0.0"}
