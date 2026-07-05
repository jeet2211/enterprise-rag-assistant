from __future__ import annotations

from fastapi import APIRouter, Request

from app.models.responses import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def health(request: Request):
    settings = request.app.state.settings
    retriever = request.app.state.retriever
    document_service = request.app.state.document_service

    chroma_status = "healthy"
    total_chunks = 0
    try:
        retriever.healthcheck()
        total_chunks = retriever.count()
    except Exception:
        chroma_status = "degraded"

    gemini_status = "healthy" if settings.gemini_api_key else "degraded"
    overall = "healthy" if chroma_status == "healthy" and gemini_status in {"healthy", "degraded"} else "degraded"
    uptime = (request.app.state.now() - request.app.state.start_time).total_seconds()

    stats = document_service.get_stats()

    return HealthResponse(
        status=overall,
        chromadb=chroma_status,
        gemini=gemini_status,
        uptime_seconds=uptime,
        total_documents=stats["total"],
        ready_documents=stats["ready"],
        failed_documents=stats["failed"],
        processing_documents=stats["processing"],
        total_chunks=total_chunks,
    )
