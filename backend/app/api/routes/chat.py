from fastapi import APIRouter, Depends, Request

from app.api.deps import get_chat_service
from app.config.settings import get_settings
from app.models.requests import ChatRequest
from app.models.responses import ChatResponse
from app.core.rate_limit import limiter

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
@limiter.limit(get_settings().rate_limit_chat)
def chat(request: Request, payload: ChatRequest, chat_service=Depends(get_chat_service)):
    result = chat_service.answer(
        question=payload.question,
        session_id=payload.session_id,
        top_k=payload.top_k,
        document_ids=payload.document_ids,
    )
    return ChatResponse(
        answer=result["answer"],
        citations=result["citations"],
        session_id=payload.session_id,
        sources_used=len(result["citations"]),
        confidence=result["confidence"],
        trace_id=result["trace_id"],
        follow_up_questions=result["follow_up_questions"],
        latency_ms=result["latency_ms"],
    )
