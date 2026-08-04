"""
RAGAS-based RAG evaluation pipeline.

This module provides two things:
1. A Celery task (run_nightly_eval_task) triggered by beat every night at 02:00 UTC
   that evaluates a sample of recent chat messages and scores them with RAGAS.
2. A standalone CLI entry-point for manual batch evaluation against golden_dataset.json.

RAGAS metrics used:
  - faithfulness        : Is the answer grounded in the retrieved context?
  - answer_relevancy    : Does the answer address the user's question?
  - context_precision   : Are the retrieved chunks actually relevant to the question?

All scores are in the range [0.0, 1.0] (higher is better).
Results are stored in the `eval_results` DB table and also pushed to Langfuse
as evaluation scores on the corresponding traces.

Usage (CLI):
    python -m evals.ragas_eval --limit 20 --days 7
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import sys
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datasets import Dataset

logger = logging.getLogger(__name__)

# Add project root to path for standalone invocation
_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))


def _build_ragas_dataset(samples: list[dict]) -> Dataset:
    """Convert our sample dicts to a RAGAS-compatible HuggingFace Dataset."""
    from datasets import Dataset  # type: ignore[import-untyped]

    rows = {
        "question": [s["question"] for s in samples],
        "answer": [s["answer"] for s in samples],
        "contexts": [s.get("contexts", []) for s in samples],
        "ground_truth": [s.get("ground_truth", "") for s in samples],
    }
    return Dataset.from_dict(rows)


def _get_ragas_metrics():
    """Lazily import RAGAS metrics to avoid slow startup."""
    from ragas.metrics import answer_relevancy, context_precision, faithfulness  # type: ignore[import-untyped]

    return faithfulness, answer_relevancy, context_precision


def _get_llm_for_ragas():
    """Return a LangChain LLM compatible with RAGAS using Gemini."""
    api_key = os.getenv("GEMINI_API_KEY", "")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY not set — cannot run RAGAS evaluation")

    from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings  # type: ignore

    llm = ChatGoogleGenerativeAI(
        model=os.getenv("MODEL_NAME", "gemini-2.5-flash"),
        google_api_key=api_key,
        temperature=0,
    )
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/embedding-001",
        google_api_key=api_key,
    )
    return llm, embeddings


def evaluate_samples(samples: list[dict]) -> list[dict]:
    """
    Run RAGAS evaluation on a list of sample dicts.

    Each sample must have:
        question    : str
        answer      : str
        contexts    : list[str]   (retrieved chunk texts)
        ground_truth: str         (expected answer — can be empty for live evals)

    Returns a list of result dicts with keys:
        question, answer, faithfulness, answer_relevancy, context_precision, overall_score
    """
    if not samples:
        return []

    try:
        from ragas import evaluate  # type: ignore[import-untyped]

        faithfulness_m, relevancy_m, precision_m = _get_ragas_metrics()
        llm, embeddings = _get_llm_for_ragas()

        dataset = _build_ragas_dataset(samples)
        result = evaluate(
            dataset=dataset,
            metrics=[faithfulness_m, relevancy_m, precision_m],
            llm=llm,
            embeddings=embeddings,
            raise_exceptions=False,
        )
        df = result.to_pandas()

        results = []
        for i, row in df.iterrows():
            faith = float(row.get("faithfulness", 0.0) or 0.0)
            relev = float(row.get("answer_relevancy", 0.0) or 0.0)
            prec = float(row.get("context_precision", 0.0) or 0.0)
            overall = round((faith + relev + prec) / 3, 4)
            results.append(
                {
                    "question": samples[i]["question"],
                    "answer": samples[i]["answer"],
                    "faithfulness": round(faith, 4),
                    "answer_relevancy": round(relev, 4),
                    "context_precision": round(prec, 4),
                    "overall_score": overall,
                    "trace_id": samples[i].get("trace_id"),
                    "session_id": samples[i].get("session_id"),
                    "message_id": samples[i].get("message_id"),
                }
            )
        return results
    except Exception as exc:
        logger.error("RAGAS evaluation failed: %s", exc, exc_info=True)
        return []


def save_results_to_db(results: list[dict], session_factory) -> None:
    """Persist RAGAS scores to the eval_results table."""
    if not results:
        return
    from app.models.db import EvalResult

    with session_factory() as session:
        for r in results:
            session.add(
                EvalResult(
                    id=str(uuid.uuid4()),
                    trace_id=r.get("trace_id"),
                    session_id=r.get("session_id"),
                    message_id=r.get("message_id"),
                    faithfulness=r.get("faithfulness"),
                    answer_relevancy=r.get("answer_relevancy"),
                    context_precision=r.get("context_precision"),
                    overall_score=r.get("overall_score"),
                    question=r.get("question"),
                    answer=r.get("answer"),
                    evaluated_at=datetime.utcnow(),
                )
            )
        session.commit()
    logger.info("Saved %d eval results to DB", len(results))


def push_scores_to_langfuse(results: list[dict]) -> None:
    """Push per-trace evaluation scores to Langfuse."""
    from app.core.tracing import get_tracer

    tracer = get_tracer()
    for r in results:
        trace_id = r.get("trace_id")
        if not trace_id:
            continue
        for metric, value in [
            ("ragas_faithfulness", r.get("faithfulness")),
            ("ragas_answer_relevancy", r.get("answer_relevancy")),
            ("ragas_context_precision", r.get("context_precision")),
            ("ragas_overall", r.get("overall_score")),
        ]:
            if value is not None:
                tracer.score(trace_id=trace_id, name=metric, value=float(value))
    tracer.flush()


def fetch_recent_samples(session_factory, limit: int = 50, days: int = 1) -> list[dict]:
    """
    Fetch recent assistant messages from the DB to evaluate.
    Returns a list of sample dicts ready for evaluate_samples().
    """
    from app.models.db import ChatMessage

    cutoff = datetime.utcnow() - timedelta(days=days)
    samples = []

    with session_factory() as session:
        messages = (
            session.query(ChatMessage)
            .filter(
                ChatMessage.role == "assistant",
                ChatMessage.created_at >= cutoff,
                ChatMessage.content != "I could not find this information in the uploaded documents.",
            )
            .order_by(ChatMessage.created_at.desc())
            .limit(limit)
            .all()
        )

        for msg in messages:
            # Retrieve the preceding user message as the question
            user_msg = (
                session.query(ChatMessage)
                .filter(
                    ChatMessage.session_id == msg.session_id,
                    ChatMessage.role == "user",
                    ChatMessage.created_at < msg.created_at,
                )
                .order_by(ChatMessage.created_at.desc())
                .first()
            )
            if not user_msg:
                continue

            # Parse citations as context strings
            contexts: list[str] = []
            if msg.citations:
                try:
                    for c in json.loads(msg.citations):
                        preview = c.get("chunk_preview") or c.get("chunk_text", "")
                        if preview:
                            contexts.append(preview)
                except Exception:
                    pass

            samples.append(
                {
                    "question": user_msg.content,
                    "answer": msg.content,
                    "contexts": contexts or ["[no context available]"],
                    "ground_truth": "",  # live eval: no ground truth needed
                    "trace_id": msg.trace_id,
                    "session_id": msg.session_id,
                    "message_id": msg.id,
                }
            )

    return samples


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def _run_cli() -> None:
    parser = argparse.ArgumentParser(description="Run RAGAS evaluation on recent RAG responses")
    parser.add_argument("--limit", type=int, default=50, help="Max messages to evaluate")
    parser.add_argument("--days", type=int, default=1, help="Look back N days for messages")
    parser.add_argument("--output", type=str, default="evals/last_eval_report.json", help="Output JSON file")
    args = parser.parse_args()

    from app.config.settings import get_settings
    from app.services.factory import build_app_services

    settings = get_settings()
    services = build_app_services(settings, include_chat=False)

    logger.info("Fetching up to %d samples from the last %d day(s)...", args.limit, args.days)
    samples = fetch_recent_samples(services.session_factory, limit=args.limit, days=args.days)
    logger.info("Evaluating %d samples with RAGAS...", len(samples))

    results = evaluate_samples(samples)
    save_results_to_db(results, services.session_factory)
    push_scores_to_langfuse(results)

    # Write human-readable report
    report = {
        "evaluated_at": datetime.utcnow().isoformat(),
        "sample_count": len(results),
        "aggregate": {
            "faithfulness": round(sum(r["faithfulness"] for r in results) / len(results), 4) if results else None,
            "answer_relevancy": round(sum(r["answer_relevancy"] for r in results) / len(results), 4) if results else None,
            "context_precision": round(sum(r["context_precision"] for r in results) / len(results), 4) if results else None,
            "overall_score": round(sum(r["overall_score"] for r in results) / len(results), 4) if results else None,
        },
        "samples": results,
    }

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2))
    logger.info("Report written to %s", out_path)
    print(json.dumps(report["aggregate"], indent=2))


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    _run_cli()
