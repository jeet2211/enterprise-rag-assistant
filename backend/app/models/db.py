from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String, Text, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker
from sqlalchemy.pool import StaticPool


class Base(DeclarativeBase):
    pass


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[str | None] = mapped_column(String(36), nullable=True, index=True)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str] = mapped_column(Text, nullable=False)
    file_hash: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    page_count: Mapped[int] = mapped_column(Integer, default=0)
    chunk_count: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(32), default="uploaded")
    error_msg: Mapped[str | None] = mapped_column(Text, nullable=True)
    file_size: Mapped[int] = mapped_column(Integer, default=0)
    uploaded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[str | None] = mapped_column(String(36), nullable=True, index=True)
    document_ids: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON list of doc IDs
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[str | None] = mapped_column(String(36), nullable=True, index=True)
    session_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    role: Mapped[str] = mapped_column(String(16), nullable=False)  # 'user' | 'assistant'
    content: Mapped[str] = mapped_column(Text, nullable=False)
    citations: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON list of citation dicts
    confidence: Mapped[str | None] = mapped_column(String(16), nullable=True)  # high/medium/low/not_found
    trace_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    latency_ms: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Feedback(Base):
    __tablename__ = "feedback"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[str | None] = mapped_column(String(36), nullable=True, index=True)
    message_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    session_id: Mapped[str] = mapped_column(String(36), nullable=False)
    rating: Mapped[str] = mapped_column(String(8), nullable=False)  # 'good' | 'bad'
    reason: Mapped[str | None] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class EvalResult(Base):
    """Stores RAGAS evaluation scores for assistant responses (populated by nightly batch job)."""

    __tablename__ = "eval_results"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    trace_id: Mapped[str | None] = mapped_column(String(36), nullable=True, index=True)
    session_id: Mapped[str | None] = mapped_column(String(36), nullable=True, index=True)
    message_id: Mapped[str | None] = mapped_column(String(36), nullable=True, index=True)
    # RAGAS metric scores (0.0 – 1.0 scale)
    faithfulness: Mapped[float | None] = mapped_column(Float, nullable=True)
    answer_relevancy: Mapped[float | None] = mapped_column(Float, nullable=True)
    context_precision: Mapped[float | None] = mapped_column(Float, nullable=True)
    overall_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    # Input snapshot for reproducibility
    question: Mapped[str | None] = mapped_column(Text, nullable=True)
    answer: Mapped[str | None] = mapped_column(Text, nullable=True)
    evaluated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


def build_engine(db_url: str):
    """Build a SQLAlchemy engine with appropriate settings for PostgreSQL or SQLite."""
    if db_url.startswith("sqlite"):
        connect_args = {"check_same_thread": False}
        kwargs: dict = {"connect_args": connect_args}
        if db_url in {"sqlite:///:memory:", "sqlite://"}:
            kwargs["poolclass"] = StaticPool
        return create_engine(db_url, **kwargs)

    # PostgreSQL — use a proper connection pool
    return create_engine(
        db_url,
        pool_size=5,
        max_overflow=10,
        pool_pre_ping=True,   # verify connections before reuse
        pool_recycle=3600,    # recycle connections every hour
    )


def build_session_factory(engine):
    return sessionmaker(bind=engine, autoflush=False, autocommit=False)
