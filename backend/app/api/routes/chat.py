from __future__ import annotations

import functools
from fastapi import APIRouter, Depends, Request

from app.api.deps import get_chat_service
from app.config.settings import get_settings
from app.models.requests import ChatRequest
from app.models.responses import ChatResponse
from app.core.rate_limit import limiter

router = APIRouter(prefix="/chat", tags=["chat"])


def limit_chat(limit_value):
    def decorator(func):
        wrapped = limiter.limit(limit_value)(func)
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            return wrapped(*args, **kwargs)
        return sync_wrapper
    return decorator


@router.post("", response_model=ChatResponse)
@limit_chat(get_settings().rate_limit_chat)
def chat(request: Request, payload: ChatRequest, chat_service=Depends(get_chat_service)):
    answer, citations = chat_service.answer(
        question=payload.question,
        session_id=payload.session_id,
        top_k=payload.top_k,
    )
    return ChatResponse(
        answer=answer,
        citations=citations,
        session_id=payload.session_id,
        sources_used=len(citations),
    )
