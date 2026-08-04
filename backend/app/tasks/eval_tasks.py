"""
Celery task for nightly RAGAS evaluation.

Triggered automatically by the Celery beat schedule at 02:00 UTC every night.
Can also be triggered manually via:
    POST /api/v1/evals/run
"""
from __future__ import annotations

import logging

from app.config.settings import get_settings
from app.tasks.celery_app import celery_app
from app.utils.logger import configure_logging

logger = logging.getLogger(__name__)


@celery_app.task(
    bind=True,
    name="evals.run_nightly",
    max_retries=1,
    default_retry_delay=300,
    soft_time_limit=1800,   # 30 min max
    time_limit=2100,
)
def run_nightly_eval_task(self, days: int = 1, limit: int = 50) -> dict:
    """
    Nightly RAGAS evaluation task.

    Fetches the last `days` days of assistant messages (up to `limit`),
    evaluates them with RAGAS (faithfulness, answer_relevancy, context_precision),
    saves results to eval_results table, and pushes scores to Langfuse.
    """
    configure_logging(get_settings().log_level)
    logger.info('{\"event\":\"eval_task_started\",\"days\":%d,\"limit\":%d}', days, limit)

    try:
        from app.config.settings import get_settings as _settings
        from app.services.factory import build_app_services
        from evals.ragas_eval import (
            evaluate_samples,
            fetch_recent_samples,
            push_scores_to_langfuse,
            save_results_to_db,
        )

        settings = _settings()
        services = build_app_services(settings, include_chat=False)

        samples = fetch_recent_samples(services.session_factory, limit=limit, days=days)
        logger.info('{\"event\":\"eval_samples_fetched\",\"count\":%d}', len(samples))

        if not samples:
            logger.info('{\"event\":\"eval_task_skipped\",\"reason\":\"no_samples\"}')
            return {"status": "skipped", "reason": "no_samples"}

        results = evaluate_samples(samples)
        save_results_to_db(results, services.session_factory)
        push_scores_to_langfuse(results)

        avg_overall = (
            round(sum(r["overall_score"] for r in results) / len(results), 4)
            if results
            else None
        )
        logger.info(
            '{\"event\":\"eval_task_completed\",\"evaluated\":%d,\"avg_overall\":%s}',
            len(results),
            avg_overall,
        )
        return {"status": "completed", "evaluated": len(results), "avg_overall": avg_overall}

    except Exception as exc:
        logger.error('{\"event\":\"eval_task_error\",\"error\":\"%s\"}', str(exc), exc_info=True)
        raise self.retry(exc=exc) from exc
