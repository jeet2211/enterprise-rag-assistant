from __future__ import annotations

import logging
from pathlib import Path

from app.config.settings import get_settings
from app.services.factory import build_app_services
from app.tasks.celery_app import celery_app
from app.utils.logger import configure_logging

logger = logging.getLogger(__name__)


def _is_non_retryable(exc: Exception) -> bool:
    if isinstance(exc, FileNotFoundError):
        return True
    if isinstance(exc, ValueError):
        return True
    return False


@celery_app.task(bind=True, name="documents.process", max_retries=3, default_retry_delay=30)
def process_document_task(self, document_id: str, file_path: str, filename: str) -> dict[str, str]:
    settings = get_settings()
    configure_logging(settings.log_level)
    services = build_app_services(settings, include_chat=False)
    document_service = services.document_service

    document = document_service.get_document(document_id)
    if document is None:
        logger.info('{"event":"document_task_skipped","document_id":"%s","reason":"missing_document"}', document_id)
        return {"status": "skipped", "reason": "missing_document"}

    if document.status == "ready":
        logger.info('{"event":"document_task_skipped","document_id":"%s","reason":"already_ready"}', document_id)
        return {"status": "skipped", "reason": "already_ready"}

    if not Path(file_path).exists():
        document_service.update_document(document_id, status="failed", error_msg="Uploaded file is missing.")
        logger.warning('{"event":"document_task_failed","document_id":"%s","reason":"missing_file"}', document_id)
        return {"status": "failed", "reason": "missing_file"}

    try:
        services.pipeline.process_document(document_id, file_path, filename)
    except Exception as exc:
        if _is_non_retryable(exc):
            logger.warning(
                '{"event":"document_task_failed","document_id":"%s","retryable":false,"error":"%s"}',
                document_id,
                str(exc),
            )
            return {"status": "failed", "reason": str(exc)}

        logger.warning(
            '{"event":"document_task_retry","document_id":"%s","retries":%d,"error":"%s"}',
            document_id,
            self.request.retries,
            str(exc),
        )
        raise self.retry(exc=exc) from exc

    logger.info('{"event":"document_task_completed","document_id":"%s"}', document_id)
    return {"status": "ready", "document_id": document_id}
