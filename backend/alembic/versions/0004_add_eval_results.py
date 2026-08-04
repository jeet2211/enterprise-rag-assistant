"""Add eval_results table

Revision ID: 0004
Revises: 0003
Create Date: 2026-08-01
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0004"
down_revision = "0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "eval_results",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("trace_id", sa.String(36), nullable=True),
        sa.Column("session_id", sa.String(36), nullable=True),
        sa.Column("message_id", sa.String(36), nullable=True),
        sa.Column("faithfulness", sa.Float(), nullable=True),
        sa.Column("answer_relevancy", sa.Float(), nullable=True),
        sa.Column("context_precision", sa.Float(), nullable=True),
        sa.Column("overall_score", sa.Float(), nullable=True),
        sa.Column("question", sa.Text(), nullable=True),
        sa.Column("answer", sa.Text(), nullable=True),
        sa.Column("evaluated_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_eval_results_trace_id", "eval_results", ["trace_id"])
    op.create_index("ix_eval_results_session_id", "eval_results", ["session_id"])
    op.create_index("ix_eval_results_message_id", "eval_results", ["message_id"])
    op.create_index("ix_eval_results_evaluated_at", "eval_results", ["evaluated_at"])


def downgrade() -> None:
    op.drop_index("ix_eval_results_evaluated_at", "eval_results")
    op.drop_index("ix_eval_results_message_id", "eval_results")
    op.drop_index("ix_eval_results_session_id", "eval_results")
    op.drop_index("ix_eval_results_trace_id", "eval_results")
    op.drop_table("eval_results")
