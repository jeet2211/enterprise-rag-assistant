from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Request, status

from app.models.db import Feedback
from app.models.requests import FeedbackRequest
from app.models.responses import FeedbackResponse
from app.auth.deps import get_current_user
from app.models.user import User

router = APIRouter(prefix="/feedback", tags=["feedback"])


@router.post("", response_model=FeedbackResponse, status_code=status.HTTP_201_CREATED)
def submit_feedback(payload: FeedbackRequest, request: Request, current_user: User = Depends(get_current_user)):
    """Record user feedback (good/bad) for a specific assistant message."""
    session_factory = request.app.state.session_factory
    feedback_id = str(uuid.uuid4())
    try:
        with session_factory() as session:
            row = Feedback(
                id=feedback_id,
                user_id=current_user.id,
                message_id=payload.message_id,
                session_id=payload.session_id,
                rating=payload.rating,
                reason=payload.reason,
            )
            session.add(row)
            session.commit()
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to record feedback: {exc}",
        ) from exc

    return FeedbackResponse(feedback_id=feedback_id, message="Feedback recorded. Thank you!")
