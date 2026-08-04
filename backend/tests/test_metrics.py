"""Tests for custom Prometheus RAG metrics."""
from __future__ import annotations

from types import SimpleNamespace

import pytest
from prometheus_client import REGISTRY

from app.core.metrics import RAGMetrics


def _get_metric_value(metric_name: str, labels: dict | None = None) -> float:
    """Helper to read a Prometheus metric value from the default registry."""
    # Use collect() approach for robustness across prometheus_client versions
    base_metric_name = metric_name.removesuffix("_total")
    for metric in REGISTRY.collect():
        if metric.name == metric_name or metric.name == base_metric_name:
            for sample in metric.samples:
                if labels is None:
                    return sample.value
                if all(sample.labels.get(k) == v for k, v in labels.items()):
                    return sample.value
    return 0.0


class TestRAGMetricsRecordChat:
    """Verify that record_chat correctly updates Prometheus counters and histograms."""

    def test_record_chat_high_confidence_increments_counter(self):
        """record_chat should increment rag_requests_total with correct labels."""
        before = _get_metric_value("rag_requests_total", {"confidence": "high", "evidence_status": "exact", "answer_style": "supported"})
        RAGMetrics.record_chat(
            confidence="high",
            evidence_status="exact",
            answer_style="supported",
            latency_ms=200.0,
            retrieval_ms=50.0,
            llm_ms=140.0,
        )
        after = _get_metric_value("rag_requests_total", {"confidence": "high", "evidence_status": "exact", "answer_style": "supported"})
        assert after == before + 1

    def test_record_chat_refused_increments_not_found(self):
        """Refused answers should increment the rag_not_found_total counter."""
        before = _get_metric_value("rag_not_found_total")
        RAGMetrics.record_chat(
            confidence="not_found",
            evidence_status="not_found",
            answer_style="refused",
            latency_ms=50.0,
        )
        after = _get_metric_value("rag_not_found_total")
        assert after == before + 1

    def test_record_chat_supported_does_not_increment_not_found(self):
        """Supported answers should NOT increment the not_found counter."""
        before = _get_metric_value("rag_not_found_total")
        RAGMetrics.record_chat(
            confidence="medium",
            evidence_status="partial",
            answer_style="supported",
            latency_ms=300.0,
            retrieval_ms=80.0,
            llm_ms=210.0,
        )
        after = _get_metric_value("rag_not_found_total")
        assert after == before  # unchanged


class TestRAGMetricsFeedback:
    def test_record_feedback_good(self):
        before = _get_metric_value("rag_feedback_total", {"rating": "good"})
        RAGMetrics.record_feedback("good")
        after = _get_metric_value("rag_feedback_total", {"rating": "good"})
        assert after == before + 1

    def test_record_feedback_bad(self):
        before = _get_metric_value("rag_feedback_total", {"rating": "bad"})
        RAGMetrics.record_feedback("bad")
        after = _get_metric_value("rag_feedback_total", {"rating": "bad"})
        assert after == before + 1


class TestRAGMetricsDocumentProcessing:
    def test_record_document_processed_ready(self):
        before = _get_metric_value("rag_document_processing_total", {"status": "ready"})
        RAGMetrics.record_document_processed("ready")
        after = _get_metric_value("rag_document_processing_total", {"status": "ready"})
        assert after == before + 1

    def test_record_document_processed_failed(self):
        before = _get_metric_value("rag_document_processing_total", {"status": "failed"})
        RAGMetrics.record_document_processed("failed")
        after = _get_metric_value("rag_document_processing_total", {"status": "failed"})
        assert after == before + 1
