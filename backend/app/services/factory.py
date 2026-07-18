from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from sqlalchemy import text

from app.config.settings import Settings
from app.models.db import Base, build_engine, build_session_factory
from app.rag.pipeline import RAGPipeline
from app.rag.retriever import Retriever
from app.services.chat_service import ChatService, SessionMemoryStore
from app.services.document_service import DocumentService
from app.services.embedding_service import EmbeddingService
from app.services.pdf_service import PDFService


@dataclass(slots=True)
class AppServices:
    engine: object
    session_factory: object
    embedding_service: EmbeddingService
    retriever: Retriever
    document_service: DocumentService
    pdf_service: PDFService
    memory_store: SessionMemoryStore
    chat_service: ChatService | None
    pipeline: RAGPipeline


def migrate_sqlite_schema(engine) -> None:
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


def build_app_services(settings: Settings, *, include_chat: bool = True) -> AppServices:
    Path(settings.upload_dir).mkdir(parents=True, exist_ok=True)
    Path(settings.chroma_persist_dir).mkdir(parents=True, exist_ok=True)

    engine = build_engine(settings.db_url)
    Base.metadata.create_all(bind=engine)
    migrate_sqlite_schema(engine)
    session_factory = build_session_factory(engine)

    embedding_service = EmbeddingService(settings.embedding_model)
    retriever = Retriever(settings.chroma_persist_dir, embedding_service)
    document_service = DocumentService(session_factory)
    pdf_service = PDFService()
    memory_store = SessionMemoryStore(settings.session_memory_k)
    chat_service = (
        ChatService(retriever, settings, memory_store, session_factory=session_factory)
        if include_chat
        else None
    )
    pipeline = RAGPipeline(pdf_service, embedding_service, retriever, document_service, settings)

    return AppServices(
        engine=engine,
        session_factory=session_factory,
        embedding_service=embedding_service,
        retriever=retriever,
        document_service=document_service,
        pdf_service=pdf_service,
        memory_store=memory_store,
        chat_service=chat_service,
        pipeline=pipeline,
    )
