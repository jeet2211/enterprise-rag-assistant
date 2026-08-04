"""Tests for the /api/v1/evals/* API routes."""
from __future__ import annotations

import uuid
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.services.eval_service import EvalService
from app.auth.deps import require_admin
from app.models.user import User


class TestEvalsRoutes:
    """Tests for the /api/v1/evals endpoints."""

    def test_get_summary_returns_valid_shape(self, client: TestClient):
        """GET /api/v1/evals/summary should return a dict with the expected keys."""
        # Inject a mock eval_service into app state
        mock_service = MagicMock(spec=EvalService)
        mock_service.get_summary.return_value = {
            "period_days": 7,
            "sample_count": 10,
            "faithfulness": 0.82,
            "answer_relevancy": 0.79,
            "context_precision": 0.74,
            "overall_score": 0.78,
        }
        client.app.state.eval_service = mock_service
        client.app.dependency_overrides[require_admin] = lambda: User(
            id="admin-user-id",
            email="admin@example.com",
            password_hash="test-password-hash",
            is_active=True,
            role="admin",
        )

        resp = client.get("/api/v1/evals/summary")
        assert resp.status_code == 200
        data = resp.json()
        assert "faithfulness" in data
        assert "answer_relevancy" in data
        assert "overall_score" in data
        assert data["sample_count"] == 10

    def test_get_summary_with_days_param(self, client: TestClient):
        """GET /api/v1/evals/summary?days=30 should forward days to the service."""
        mock_service = MagicMock(spec=EvalService)
        mock_service.get_summary.return_value = {
            "period_days": 30,
            "sample_count": 5,
            "faithfulness": None,
            "answer_relevancy": None,
            "context_precision": None,
            "overall_score": None,
        }
        client.app.state.eval_service = mock_service
        client.app.dependency_overrides[require_admin] = lambda: User(
            id="admin-user-id",
            email="admin@example.com",
            password_hash="test-password-hash",
            is_active=True,
            role="admin",
        )

        resp = client.get("/api/v1/evals/summary?days=30")
        assert resp.status_code == 200
        mock_service.get_summary.assert_called_once_with(days=30)

    def test_get_message_eval_not_found(self, client: TestClient):
        """GET /api/v1/evals/{message_id} should return 404 when not evaluated yet."""
        mock_service = MagicMock(spec=EvalService)
        mock_service.get_message_scores.return_value = None
        client.app.state.eval_service = mock_service
        client.app.dependency_overrides[require_admin] = lambda: User(
            id="admin-user-id",
            email="admin@example.com",
            password_hash="test-password-hash",
            is_active=True,
            role="admin",
        )

        resp = client.get(f"/api/v1/evals/{uuid.uuid4()}")
        assert resp.status_code == 404

    def test_get_message_eval_found(self, client: TestClient):
        """GET /api/v1/evals/{message_id} returns scores when available."""
        msg_id = str(uuid.uuid4())
        mock_service = MagicMock(spec=EvalService)
        mock_service.get_message_scores.return_value = {
            "message_id": msg_id,
            "faithfulness": 0.9,
            "answer_relevancy": 0.85,
            "context_precision": 0.80,
            "overall_score": 0.85,
            "evaluated_at": datetime.utcnow().isoformat(),
        }
        client.app.state.eval_service = mock_service
        client.app.dependency_overrides[require_admin] = lambda: User(
            id="admin-user-id",
            email="admin@example.com",
            password_hash="test-password-hash",
            is_active=True,
            role="admin",
        )

        resp = client.get(f"/api/v1/evals/{msg_id}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["faithfulness"] == pytest.approx(0.9)

    def test_trigger_eval_run_returns_accepted(self, client: TestClient):
        """POST /api/v1/evals/run should return 202 and a task_id."""
        mock_task = MagicMock()
        mock_task.id = "celery-task-abc123"
        client.app.dependency_overrides[require_admin] = lambda: User(
            id="admin-user-id",
            email="admin@example.com",
            password_hash="test-password-hash",
            is_active=True,
            role="admin",
        )

        with patch("app.api.routes.evals.run_nightly_eval_task") as mock_task_fn:
            mock_task_fn.apply_async.return_value = mock_task
            resp = client.post("/api/v1/evals/run?days=1&limit=10")

        assert resp.status_code == 202
        data = resp.json()
        assert data["status"] == "accepted"
        assert "task_id" in data
