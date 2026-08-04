"""
EvalService — thin wrapper used by API routes and Celery tasks.

The actual evaluation logic lives in evals/ragas_eval.py.
This service just provides a clean interface for the API layer to:
  - query eval results from the DB
  - trigger a batch eval run
"""
from __future__ import annotations

import logging
from datetime import datetime, timedelta

from sqlalchemy import func

from app.models.db import EvalResult

logger = logging.getLogger(__name__)


class EvalService:
    def __init__(self, session_factory) -> None:
        self.session_factory = session_factory

    def get_summary(self, days: int = 7) -> dict:
        """
        Return aggregate RAGAS scores for the last `days` days.
        If no results exist yet, returns zeroed aggregates.
        """
        cutoff = datetime.utcnow() - timedelta(days=days)
        with self.session_factory() as session:
            row = (
                session.query(
                    func.avg(EvalResult.faithfulness).label("faithfulness"),
                    func.avg(EvalResult.answer_relevancy).label("answer_relevancy"),
                    func.avg(EvalResult.context_precision).label("context_precision"),
                    func.avg(EvalResult.overall_score).label("overall_score"),
                    func.count(EvalResult.id).label("sample_count"),
                )
                .filter(EvalResult.evaluated_at >= cutoff)
                .one()
            )

        def _round(v) -> float | None:
            return round(float(v), 4) if v is not None else None

        return {
            "period_days": days,
            "sample_count": row.sample_count or 0,
            "faithfulness": _round(row.faithfulness),
            "answer_relevancy": _round(row.answer_relevancy),
            "context_precision": _round(row.context_precision),
            "overall_score": _round(row.overall_score),
        }

    def get_message_scores(self, message_id: str) -> dict | None:
        """Return RAGAS scores for a specific message_id, or None if not yet evaluated."""
        with self.session_factory() as session:
            row = (
                session.query(EvalResult)
                .filter(EvalResult.message_id == message_id)
                .order_by(EvalResult.evaluated_at.desc())
                .first()
            )
        if row is None:
            return None
        return {
            "message_id": message_id,
            "faithfulness": row.faithfulness,
            "answer_relevancy": row.answer_relevancy,
            "context_precision": row.context_precision,
            "overall_score": row.overall_score,
            "evaluated_at": row.evaluated_at.isoformat() if row.evaluated_at else None,
        }

    def get_recent_results(self, limit: int = 100, days: int = 7) -> list[dict]:
        """Return the most recent individual eval results."""
        cutoff = datetime.utcnow() - timedelta(days=days)
        with self.session_factory() as session:
            rows = (
                session.query(EvalResult)
                .filter(EvalResult.evaluated_at >= cutoff)
                .order_by(EvalResult.evaluated_at.desc())
                .limit(limit)
                .all()
            )
        return [
            {
                "id": r.id,
                "trace_id": r.trace_id,
                "session_id": r.session_id,
                "message_id": r.message_id,
                "faithfulness": r.faithfulness,
                "answer_relevancy": r.answer_relevancy,
                "context_precision": r.context_precision,
                "overall_score": r.overall_score,
                "question": r.question,
                "evaluated_at": r.evaluated_at.isoformat() if r.evaluated_at else None,
            }
            for r in rows
        ]
