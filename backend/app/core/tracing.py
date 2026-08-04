"""
Langfuse LLM observability tracing for the RAG application.

Provides a thin wrapper around the Langfuse Python SDK that:
  - Initialises a LangfuseClient from env vars
  - Falls back to a silent no-op if LANGFUSE_SECRET_KEY is not set (so local
    dev without Langfuse continues to work without any code changes)
  - Exposes helpers used inside ChatService and the feedback route

Environment variables:
    LANGFUSE_SECRET_KEY  — generated from http://localhost:3000 (Settings → API Keys)
    LANGFUSE_PUBLIC_KEY  — same page
    LANGFUSE_HOST        — default: http://langfuse-server:3000

Usage:
    tracer = get_tracer()
    trace = tracer.start_trace(name="chat", session_id=..., user_id=...)
    retrieval_span = trace.span(name="retrieval")
    # ... do retrieval ...
    retrieval_span.end(output={"sources": len(matches)})
    trace.end(output={"confidence": confidence})
    tracer.score(trace_id=trace.id, name="user_feedback", value=1.0)
"""
from __future__ import annotations

import logging
import os
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# No-op fallback (used when Langfuse is not configured)
# ---------------------------------------------------------------------------


class _NoOpSpan:
    """Span stub that does nothing."""
    id: str = "noop"

    def end(self, **kwargs: Any) -> None:  # noqa: D401
        pass


class _NoOpTrace:
    """Trace stub that does nothing."""
    id: str = "noop"

    def span(self, **kwargs: Any) -> _NoOpSpan:
        return _NoOpSpan()

    def end(self, **kwargs: Any) -> None:
        pass

    def score(self, **kwargs: Any) -> None:
        pass


class _NoOpTracer:
    """Tracer stub used when LANGFUSE_SECRET_KEY is absent."""

    def start_trace(self, **kwargs: Any) -> _NoOpTrace:
        return _NoOpTrace()

    def score(self, **kwargs: Any) -> None:
        pass

    def flush(self) -> None:
        pass


# ---------------------------------------------------------------------------
# Live Langfuse tracer
# ---------------------------------------------------------------------------

def _safe_call(client: Any, method_names: tuple[str, ...], **kwargs: Any) -> None:
    """Call the first available Langfuse SDK method, ignoring observability failures."""
    for method_name in method_names:
        method = getattr(client, method_name, None)
        if not callable(method):
            continue
        try:
            method(**kwargs)
        except TypeError:
            # Some Langfuse client methods accept a smaller kwarg set.
            method()
        return


@dataclass
class _LangfuseSpanAdapter:
    """Small compatibility layer for different Langfuse span SDK versions."""

    _span: Any
    id: str = field(init=False)

    def __post_init__(self) -> None:
        self.id = str(getattr(self._span, "id", "noop"))

    def end(self, **kwargs: Any) -> None:
        try:
            _safe_call(self._span, ("end", "update"), **kwargs)
        except Exception as exc:
            logger.warning("Langfuse span close failed: %s", exc)


@dataclass
class _LangfuseTraceAdapter:
    """Trace adapter that exposes the app's expected `.span()` / `.end()` API."""

    _trace: Any
    _client: Any
    id: str = field(init=False)

    def __post_init__(self) -> None:
        self.id = str(getattr(self._trace, "id", "noop"))

    def span(self, **kwargs: Any) -> _LangfuseSpanAdapter | _NoOpSpan:
        span = getattr(self._trace, "span", None)
        if not callable(span):
            return _NoOpSpan()
        try:
            return _LangfuseSpanAdapter(span(**kwargs))
        except Exception as exc:
            logger.warning("Langfuse span start failed: %s", exc)
            return _NoOpSpan()

    def end(self, **kwargs: Any) -> None:
        try:
            _safe_call(self._trace, ("end", "update"), **kwargs)
            flush = getattr(self._client, "flush", None)
            if callable(flush):
                flush()
        except Exception as exc:
            logger.warning("Langfuse trace close failed: %s", exc)


class _LangfuseTracer:
    """Real Langfuse tracer backed by the langfuse Python SDK."""

    def __init__(self, client: Any) -> None:  # client: langfuse.Langfuse
        self._client = client

    def start_trace(
        self,
        *,
        name: str,
        session_id: str | None = None,
        user_id: str | None = None,
        input: dict | None = None,
        metadata: dict | None = None,
    ) -> _LangfuseTraceAdapter | _NoOpTrace:
        try:
            trace = self._client.trace(
                name=name,
                session_id=session_id,
                user_id=user_id,
                input=input,
                metadata=metadata,
            )
            return _LangfuseTraceAdapter(trace, self._client)
        except Exception as exc:
            logger.warning("Langfuse trace start failed: %s", exc)
            return _NoOpTrace()

    def score(
        self,
        *,
        trace_id: str,
        name: str,
        value: float,
        comment: str | None = None,
    ) -> None:
        try:
            self._client.score(
                trace_id=trace_id,
                name=name,
                value=value,
                comment=comment,
            )
        except Exception as exc:
            logger.warning("Langfuse score failed: %s", exc)

    def flush(self) -> None:
        try:
            self._client.flush()
        except Exception as exc:
            logger.warning("Langfuse flush failed: %s", exc)


# ---------------------------------------------------------------------------
# Singleton factory
# ---------------------------------------------------------------------------

_tracer: _LangfuseTracer | _NoOpTracer | None = None


def get_tracer() -> _LangfuseTracer | _NoOpTracer:
    """Return the singleton tracer instance (initialised on first call)."""
    global _tracer  # noqa: PLW0603
    if _tracer is not None:
        return _tracer

    secret_key = os.getenv("LANGFUSE_SECRET_KEY", "")
    public_key = os.getenv("LANGFUSE_PUBLIC_KEY", "")
    host = os.getenv("LANGFUSE_HOST", "http://langfuse-server:3000")

    placeholder_values = {
        "sk-lf-...your-secret-key...",
        "pk-lf-...your-public-key...",
    }
    if not secret_key or not public_key or secret_key in placeholder_values or public_key in placeholder_values:
        logger.info(
            "LANGFUSE_SECRET_KEY / LANGFUSE_PUBLIC_KEY not set — "
            "LLM observability disabled (no-op tracer active)"
        )
        _tracer = _NoOpTracer()
        return _tracer

    try:
        from langfuse import Langfuse  # type: ignore[import-untyped]

        client = Langfuse(
            secret_key=secret_key,
            public_key=public_key,
            host=host,
        )
        _tracer = _LangfuseTracer(client)
        logger.info("Langfuse tracer initialised — host=%s", host)
    except Exception as exc:
        logger.warning("Failed to initialise Langfuse tracer (%s); using no-op.", exc)
        _tracer = _NoOpTracer()

    return _tracer
