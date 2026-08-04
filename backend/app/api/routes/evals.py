"""
Evals API routes — expose RAGAS evaluation results and manual trigger.

Endpoints:
    GET  /api/v1/evals/summary         → aggregate RAGAS scores (last N days)
    GET  /api/v1/evals/{message_id}    → per-message RAGAS scores
    GET  /api/v1/evals/recent          → list of recent individual results
    POST /api/v1/evals/run             → trigger nightly eval task immediately
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status

from app.auth.deps import get_current_user, require_admin
from app.models.user import User
from app.tasks.eval_tasks import run_nightly_eval_task

router = APIRouter(prefix="/evals", tags=["evaluations"])


@router.get("/summary")
def get_eval_summary(
    days: int = Query(default=7, ge=1, le=90, description="Look-back window in days"),
    request: Request = None,
    current_user: User = Depends(get_current_user),
) -> dict:
    """Return aggregate RAGAS scores across the specified look-back window."""
    eval_service = getattr(request.app.state, "eval_service", None)
    if eval_service is None:
        raise HTTPException(status_code=503, detail="Evaluation service not available")
    return eval_service.get_summary(days=days)


@router.get("/recent")
def get_recent_evals(
    limit: int = Query(default=50, ge=1, le=200),
    days: int = Query(default=7, ge=1, le=90),
    request: Request = None,
    current_user: User = Depends(require_admin),
) -> dict:
    """Return the most recent per-message RAGAS evaluation results."""
    eval_service = getattr(request.app.state, "eval_service", None)
    if eval_service is None:
        raise HTTPException(status_code=503, detail="Evaluation service not available")
    results = eval_service.get_recent_results(limit=limit, days=days)
    return {"count": len(results), "results": results}


@router.get("/{message_id}")
def get_message_eval(
    message_id: str,
    request: Request = None,
    current_user: User = Depends(require_admin),
) -> dict:
    """Return RAGAS scores for a specific assistant message."""
    eval_service = getattr(request.app.state, "eval_service", None)
    if eval_service is None:
        raise HTTPException(status_code=503, detail="Evaluation service not available")
    result = eval_service.get_message_scores(message_id)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No evaluation results found for message_id={message_id}",
        )
    return result


@router.post("/run", status_code=status.HTTP_202_ACCEPTED)
def trigger_eval_run(
    days: int = Query(default=1, ge=1, le=30, description="Evaluate messages from the last N days"),
    limit: int = Query(default=50, ge=1, le=200, description="Max messages to evaluate"),
    request: Request = None,
    current_user: User = Depends(require_admin),
) -> dict:
    """
    Trigger the RAGAS nightly evaluation task immediately (runs in background via Celery).
    Useful for manual evaluation runs and testing.
    """
    task = run_nightly_eval_task.apply_async(kwargs={"days": days, "limit": limit})
    return {
        "status": "accepted",
        "task_id": task.id,
        "message": f"RAGAS evaluation started for the last {days} day(s), up to {limit} messages.",
    }
