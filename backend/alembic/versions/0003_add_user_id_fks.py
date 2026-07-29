"""Add user_id FK columns

Revision ID: 0003
Revises: 0002
Create Date: 2026-07-29
"""

from __future__ import annotations
from alembic import op
import sqlalchemy as sa

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("documents", sa.Column("user_id", sa.String(36), nullable=True))
    op.create_index("ix_documents_user_id", "documents", ["user_id"])

    op.add_column("chat_sessions", sa.Column("user_id", sa.String(36), nullable=True))
    op.create_index("ix_chat_sessions_user_id", "chat_sessions", ["user_id"])

    op.add_column("chat_messages", sa.Column("user_id", sa.String(36), nullable=True))
    op.create_index("ix_chat_messages_user_id", "chat_messages", ["user_id"])

    op.add_column("feedback", sa.Column("user_id", sa.String(36), nullable=True))
    op.create_index("ix_feedback_user_id", "feedback", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_documents_user_id", "documents")
    op.drop_column("documents", "user_id")
    op.drop_index("ix_chat_sessions_user_id", "chat_sessions")
    op.drop_column("chat_sessions", "user_id")
    op.drop_index("ix_chat_messages_user_id", "chat_messages")
    op.drop_column("chat_messages", "user_id")
    op.drop_index("ix_feedback_user_id", "feedback")
    op.drop_column("feedback", "user_id")
