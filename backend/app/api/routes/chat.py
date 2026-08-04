import json

from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse

from app.api.deps import get_chat_service
from app.config.settings import get_settings
from app.models.requests import ChatRequest
from app.models.responses import ChatResponse
from app.core.rate_limit import limiter
from app.auth.deps import get_current_user
from app.models.user import User

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
@limiter.limit(get_settings().rate_limit_chat)
def chat(
    request: Request,
    payload: ChatRequest,
    chat_service=Depends(get_chat_service),
    current_user: User = Depends(get_current_user),
):
    result = chat_service.answer(
        question=payload.question,
        session_id=payload.session_id,
        top_k=payload.top_k,
        document_ids=payload.document_ids,
        user_id=current_user.id,
    )
    return ChatResponse(
        answer=result["answer"],
        citations=result["citations"],
        session_id=payload.session_id,
        sources_used=len(result["citations"]),
        confidence=result["confidence"],
        evidence_status=result["evidence_status"],
        answer_style=result["answer_style"],
        trace_id=result["trace_id"],
        follow_up_questions=result["follow_up_questions"],
        latency_ms=result["latency_ms"],
    )


def _sse(event: str, data: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(data)}\n\n"


@router.post("/stream")
@limiter.limit(get_settings().rate_limit_chat)
def chat_stream(
    request: Request,
    payload: ChatRequest,
    chat_service=Depends(get_chat_service),
    current_user: User = Depends(get_current_user),
):
    def events():
        try:
            for item in chat_service.answer_stream(
                question=payload.question,
                session_id=payload.session_id,
                top_k=payload.top_k,
                document_ids=payload.document_ids,
                user_id=current_user.id,
            ):
                yield _sse(item["event"], item["data"])
        except Exception as exc:
            yield _sse("error", {"detail": str(exc)})

    return StreamingResponse(events(), media_type="text/event-stream")


@router.get("/sessions")
def list_sessions(
    chat_service=Depends(get_chat_service),
    current_user: User = Depends(get_current_user),
):
    """List all chat sessions for the authenticated user."""
    return chat_service.list_sessions(user_id=current_user.id)


@router.get("/sessions/{session_id}/messages")
def get_session_messages(
    session_id: str,
    chat_service=Depends(get_chat_service),
    current_user: User = Depends(get_current_user),
):
    """Fetch messages for a specific session, securing it to the logged-in user."""
    return chat_service.get_session_messages(session_id=session_id, user_id=current_user.id)


@router.delete("/sessions/{session_id}")
def delete_session(
    session_id: str,
    chat_service=Depends(get_chat_service),
    current_user: User = Depends(get_current_user),
):
    """Delete a chat session and its message history."""
    success = chat_service.delete_session(session_id=session_id, user_id=current_user.id)
    if not success:
        return {"status": "error", "message": "Session not found or unauthorized"}
    return {"status": "success", "message": "Session deleted"}

