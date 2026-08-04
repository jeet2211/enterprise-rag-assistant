"""Tests for EvalService and RAGAS eval pipeline."""
from __future__ import annotations

import uuid
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models.db import Base, EvalResult
from app.services.eval_service import EvalService


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

TEST_DB_URL = "sqlite:///:memory:"


@pytest.fixture(name="in_memory_session_factory")
def fixture_in_memory_session_factory():
    engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    factory = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    yield factory
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(name="eval_service")
def fixture_eval_service(in_memory_session_factory):
    return EvalService(in_memory_session_factory)


def _insert_eval_result(session_factory, **kwargs) -> EvalResult:
    row = EvalResult(
        id=str(uuid.uuid4()),
        trace_id=kwargs.get("trace_id", str(uuid.uuid4())),
        session_id=kwargs.get("session_id", str(uuid.uuid4())),
        message_id=kwargs.get("message_id", str(uuid.uuid4())),
        faithfulness=kwargs.get("faithfulness", 0.8),
        answer_relevancy=kwargs.get("answer_relevancy", 0.75),
        context_precision=kwargs.get("context_precision", 0.70),
        overall_score=kwargs.get("overall_score", 0.75),
        question=kwargs.get("question", "Test question?"),
        answer=kwargs.get("answer", "Test answer."),
        evaluated_at=datetime.utcnow(),
    )
    with session_factory() as session:
        session.add(row)
        session.commit()
    return row


# ---------------------------------------------------------------------------
# EvalService tests
# ---------------------------------------------------------------------------


class TestEvalServiceSummary:
    def test_summary_returns_zeroed_when_no_results(self, eval_service):
        result = eval_service.get_summary(days=7)
        assert result["sample_count"] == 0
        assert result["faithfulness"] is None
        assert result["answer_relevancy"] is None
        assert result["overall_score"] is None

    def test_summary_aggregates_correctly(self, eval_service, in_memory_session_factory):
        _insert_eval_result(in_memory_session_factory, faithfulness=0.8, answer_relevancy=0.6, context_precision=0.7, overall_score=0.7)
        _insert_eval_result(in_memory_session_factory, faithfulness=0.9, answer_relevancy=0.8, context_precision=0.9, overall_score=0.867)

        result = eval_service.get_summary(days=7)
        assert result["sample_count"] == 2
        assert result["faithfulness"] == pytest.approx(0.85, abs=0.01)
        assert result["answer_relevancy"] == pytest.approx(0.7, abs=0.01)

    def test_summary_period_days_filters_old_results(self, eval_service, in_memory_session_factory):
        # Result from "10 days ago" — should be excluded when querying last 7 days
        old = EvalResult(
            id=str(uuid.uuid4()),
            faithfulness=0.5,
            overall_score=0.5,
            evaluated_at=datetime(2020, 1, 1),  # very old
        )
        with in_memory_session_factory() as session:
            session.add(old)
            session.commit()

        result = eval_service.get_summary(days=7)
        assert result["sample_count"] == 0  # old result not counted


class TestEvalServiceMessageScores:
    def test_returns_none_for_unknown_message(self, eval_service):
        assert eval_service.get_message_scores("nonexistent-id") is None

    def test_returns_scores_for_known_message(self, eval_service, in_memory_session_factory):
        msg_id = str(uuid.uuid4())
        _insert_eval_result(in_memory_session_factory, message_id=msg_id, faithfulness=0.9, overall_score=0.85)

        result = eval_service.get_message_scores(msg_id)
        assert result is not None
        assert result["message_id"] == msg_id
        assert result["faithfulness"] == pytest.approx(0.9)
        assert result["overall_score"] == pytest.approx(0.85)


# ---------------------------------------------------------------------------
# ragas_eval helpers (mocked)
# ---------------------------------------------------------------------------


class TestSaveResultsToDB:
    def test_saves_results_to_db(self, in_memory_session_factory):
        from evals.ragas_eval import save_results_to_db

        results = [
            {
                "question": "What is X?",
                "answer": "X is Y.",
                "faithfulness": 0.9,
                "answer_relevancy": 0.85,
                "context_precision": 0.8,
                "overall_score": 0.85,
                "trace_id": str(uuid.uuid4()),
                "session_id": str(uuid.uuid4()),
                "message_id": str(uuid.uuid4()),
            }
        ]
        save_results_to_db(results, in_memory_session_factory)

        with in_memory_session_factory() as session:
            rows = session.query(EvalResult).all()
        assert len(rows) == 1
        assert rows[0].faithfulness == pytest.approx(0.9)

    def test_save_empty_results_is_no_op(self, in_memory_session_factory):
        from evals.ragas_eval import save_results_to_db

        save_results_to_db([], in_memory_session_factory)
        with in_memory_session_factory() as session:
            count = session.query(EvalResult).count()
        assert count == 0
