from __future__ import annotations

from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi import _rate_limit_exceeded_handler

from app.core.rate_limit import limiter
from app.api.routes.chat import router as chat_router
from app.api.routes.documents import router as documents_router
from app.api.routes.evals import router as evals_router
from app.api.routes.feedback import router as feedback_router
from app.api.routes.health import router as health_router
from app.api.routes.upload import router as upload_router
from app.api.routes.auth import router as auth_router
from prometheus_fastapi_instrumentator import Instrumentator
from app.config.settings import get_settings
from app.services.factory import build_app_services
from app.utils.logger import configure_logging


settings = get_settings()
configure_logging(settings.log_level)


@asynccontextmanager
async def lifespan(app: FastAPI):
    services = build_app_services(settings)

    app.state.settings = settings
    app.state.engine = services.engine
    app.state.session_factory = services.session_factory
    app.state.embedding_service = services.embedding_service
    app.state.retriever = services.retriever
    app.state.document_service = services.document_service
    app.state.pdf_service = services.pdf_service
    app.state.memory_store = services.memory_store
    app.state.chat_service = services.chat_service
    app.state.pipeline = services.pipeline
    app.state.eval_service = services.eval_service
    app.state.start_time = datetime.utcnow()
    app.state.now = datetime.utcnow

    if settings.warm_embedding_model_on_startup:
        services.embedding_service.embed_query("warmup")
        services.retriever.healthcheck()

    yield


app = FastAPI(title="Enterprise RAG Assistant", version="2.0.0", lifespan=lifespan)
Instrumentator().instrument(app).expose(app, endpoint="/metrics", include_in_schema=False)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    import logging
    import uuid

    trace_id = str(uuid.uuid4())
    logger = logging.getLogger("app.main")
    logger.error(
        '{"event":"unhandled_error","trace_id":"%s","path":"%s","error":"%s"}',
        trace_id,
        request.url.path,
        str(exc),
        exc_info=True,
    )
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error. Please contact support.",
            "trace_id": trace_id,
        },
    )


app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router, prefix="/api/v1")
app.include_router(upload_router, prefix="/api/v1")
app.include_router(chat_router, prefix="/api/v1")
app.include_router(documents_router, prefix="/api/v1")
app.include_router(feedback_router, prefix="/api/v1")
app.include_router(evals_router, prefix="/api/v1")
app.include_router(auth_router, prefix="/api/v1")


@app.get("/")
def root():
    return {"status": "ok", "service": "enterprise-rag-assistant", "version": "2.0.0"}
