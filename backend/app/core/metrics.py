"""
Custom Prometheus metrics for the RAG application.

These complement the generic HTTP metrics from prometheus-fastapi-instrumentator
with domain-specific RAG quality and performance signals.

Usage:
    from app.core.metrics import RAGMetrics
    RAGMetrics.record_chat(confidence="high", evidence_status="exact",
                           answer_style="supported", latency_ms=340.5,
                           retrieval_ms=80.0, llm_ms=250.0)
"""
from __future__ import annotations

from prometheus_client import Counter, Gauge, Histogram

# ---------------------------------------------------------------------------
# Counters
# ---------------------------------------------------------------------------

_rag_requests = Counter(
    "rag_requests_total",
    "Total RAG chat requests, labeled by confidence, evidence status, and answer style",
    ["confidence", "evidence_status", "answer_style"],
)

_rag_not_found = Counter(
    "rag_not_found_total",
    "Total answers refused because no relevant context was found",
)

_feedback = Counter(
    "rag_feedback_total",
    "User feedback submitted (thumbs up/down)",
    ["rating"],  # 'good' | 'bad'
)

_document_processing = Counter(
    "rag_document_processing_total",
    "Document processing completions",
    ["status"],  # 'ready' | 'failed'
)

# ---------------------------------------------------------------------------
# Histograms (latency in seconds — Prometheus convention)
# ---------------------------------------------------------------------------

_LATENCY_BUCKETS = (0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0, 20.0, 30.0)

_latency_e2e = Histogram(
    "rag_request_duration_seconds",
    "End-to-end chat request latency",
    buckets=_LATENCY_BUCKETS,
)

_latency_retrieval = Histogram(
    "rag_retrieval_duration_seconds",
    "ChromaDB vector retrieval latency",
    buckets=(0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5),
)

_latency_llm = Histogram(
    "rag_llm_duration_seconds",
    "LLM (Gemini) generation latency",
    buckets=_LATENCY_BUCKETS,
)

_latency_verifier = Histogram(
    "rag_verifier_duration_seconds",
    "LLM verifier call latency",
    buckets=_LATENCY_BUCKETS,
)

# ---------------------------------------------------------------------------
# Gauges
# ---------------------------------------------------------------------------

_chroma_chunks = Gauge(
    "rag_chroma_chunk_count",
    "Total number of document chunks indexed in ChromaDB",
)

_active_sessions = Gauge(
    "rag_active_sessions_total",
    "Number of chat sessions currently held in the in-memory session store",
)


# ---------------------------------------------------------------------------
# Public interface
# ---------------------------------------------------------------------------

class RAGMetrics:
    """Thin wrapper around raw prometheus_client objects for ergonomic use."""

    @staticmethod
    def record_chat(
        *,
        confidence: str,
        evidence_status: str,
        answer_style: str,
        latency_ms: float,
        retrieval_ms: float | None = None,
        llm_ms: float | None = None,
        verifier_ms: float | None = None,
    ) -> None:
        """Record all per-request metrics after a chat answer is produced."""
        _rag_requests.labels(
            confidence=confidence,
            evidence_status=evidence_status,
            answer_style=answer_style,
        ).inc()

        if answer_style == "refused":
            _rag_not_found.inc()

        _latency_e2e.observe(latency_ms / 1000)

        if retrieval_ms is not None:
            _latency_retrieval.observe(retrieval_ms / 1000)
        if llm_ms is not None:
            _latency_llm.observe(llm_ms / 1000)
        if verifier_ms is not None:
            _latency_verifier.observe(verifier_ms / 1000)

    @staticmethod
    def record_feedback(rating: str) -> None:
        """Increment feedback counter. rating should be 'good' or 'bad'."""
        _feedback.labels(rating=rating).inc()

    @staticmethod
    def record_document_processed(status: str) -> None:
        """Record a document processing completion. status: 'ready' or 'failed'."""
        _document_processing.labels(status=status).inc()

    @staticmethod
    def set_chroma_chunk_count(count: int) -> None:
        _chroma_chunks.set(count)

    @staticmethod
    def set_active_sessions(count: int) -> None:
        _active_sessions.set(count)
