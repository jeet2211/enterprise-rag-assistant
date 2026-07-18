from __future__ import annotations

from fastapi import APIRouter, Request
from redis import Redis

from app.models.responses import HealthResponse, WorkerHealthResponse
from app.tasks.celery_app import celery_app

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


@router.get("/health/worker", response_model=WorkerHealthResponse)
def worker_health(request: Request):
    settings = request.app.state.settings

    redis_status = "healthy"
    try:
        redis_client = Redis.from_url(settings.redis_url, socket_connect_timeout=1, socket_timeout=1)
        redis_client.ping()
    except Exception:
        redis_status = "degraded"

    worker_count = 0
    celery_status = "degraded"
    try:
        responses = celery_app.control.inspect(timeout=1).ping() or {}
        worker_count = len(responses)
        celery_status = "healthy" if worker_count > 0 else "degraded"
    except Exception:
        celery_status = "degraded"

    overall = "healthy" if redis_status == "healthy" and celery_status == "healthy" else "degraded"
    return WorkerHealthResponse(
        status=overall,
        redis=redis_status,
        celery=celery_status,
        worker_count=worker_count,
    )
