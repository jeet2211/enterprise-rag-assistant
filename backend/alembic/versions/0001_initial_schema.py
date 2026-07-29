"""Initial schema

Revision ID: 0001
Revises:
Create Date: 2026-07-29
"""

from __future__ import annotations
from alembic import op
import sqlalchemy as sa

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "documents",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("filename", sa.String(255), nullable=False),
        sa.Column("file_path", sa.Text(), nullable=False),
        sa.Column("file_hash", sa.String(64), nullable=True),
        sa.Column("page_count", sa.Integer(), default=0),
        sa.Column("chunk_count", sa.Integer(), default=0),
        sa.Column("status", sa.String(32), default="uploaded"),
        sa.Column("error_msg", sa.Text(), nullable=True),
        sa.Column("file_size", sa.Integer(), default=0),
        sa.Column("uploaded_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_documents_file_hash", "documents", ["file_hash"])

    op.create_table(
        "chat_sessions",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("document_ids", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )

    op.create_table(
        "chat_messages",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("session_id", sa.String(36), nullable=False),
        sa.Column("role", sa.String(16), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("citations", sa.Text(), nullable=True),
        sa.Column("confidence", sa.String(16), nullable=True),
        sa.Column("trace_id", sa.String(36), nullable=True),
        sa.Column("latency_ms", sa.Float(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_chat_messages_session_id", "chat_messages", ["session_id"])

    op.create_table(
        "feedback",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("message_id", sa.String(36), nullable=False),
        sa.Column("session_id", sa.String(36), nullable=False),
        sa.Column("rating", sa.String(8), nullable=False),
        sa.Column("reason", sa.String(64), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_feedback_message_id", "feedback", ["message_id"])


def downgrade() -> None:
    op.drop_table("feedback")
    op.drop_table("chat_messages")
    op.drop_table("chat_sessions")
    op.drop_table("documents")
