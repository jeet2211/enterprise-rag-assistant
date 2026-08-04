from __future__ import annotations

from celery import Celery
from celery.schedules import crontab

from app.config.settings import get_settings

settings = get_settings()

celery_app = Celery(
    "enterprise_rag_assistant",
    broker=settings.resolved_celery_broker_url,
    backend=settings.resolved_celery_result_backend,
    include=[
        "app.tasks.document_tasks",
        "app.tasks.eval_tasks",      # RAGAS nightly evaluation task
    ],
)

celery_app.conf.update(
    task_always_eager=settings.celery_task_always_eager,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    worker_prefetch_multiplier=1,
    broker_connection_retry_on_startup=True,
    task_track_started=True,
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    # ---------------------------------------------------------------------------
    # Celery Beat: nightly RAGAS evaluation at 02:00 UTC
    # ---------------------------------------------------------------------------
    beat_schedule={
        "nightly-ragas-eval": {
            "task": "evals.run_nightly",
            "schedule": crontab(hour=2, minute=0),   # every day at 02:00 UTC
            "kwargs": {"days": 1, "limit": 50},
        },
    },
)
