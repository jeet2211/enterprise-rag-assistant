from __future__ import annotations

from types import SimpleNamespace

import pytest

from app.services.chat_service import ChatService, SessionMemoryStore, _should_run_verifier


class DummySettings(SimpleNamespace):
    pass


class DummyRetriever:
    def __init__(self, matches=None):
        self.matches = matches or []

    def search(self, *args, **kwargs):
        return self.matches


class FakeLLM:
    def __init__(self, answer: str = "answer", stream_chunks=None):
        self.answer = answer
        self.stream_chunks = stream_chunks or [answer]

    def invoke(self, prompt):
        return SimpleNamespace(content=self.answer)

    def stream(self, prompt):
        for chunk in self.stream_chunks:
            yield SimpleNamespace(content=chunk)


@pytest.mark.parametrize(
    ("confidence", "min_confidence", "expected"),
    [
        ("not_found", "low", True),
        ("low", "low", True),
        ("medium", "low", False),
        ("high", "low", False),
        ("medium", "medium", True),
        ("high", "medium", False),
        ("high", "high", True),
    ],
)
def test_should_run_verifier_respects_confidence_threshold(confidence, min_confidence, expected):
    assert _should_run_verifier(confidence, min_confidence) is expected


def test_answer_skips_followup_generation_when_disabled(monkeypatch):
    settings = DummySettings(
        gemini_api_key="test",
        model_name="gemini-test",
        top_k=3,
        chat_context_top_k=3,
        chat_context_chunk_chars=400,
        retrieval_candidate_multiplier=4,
        retrieval_mmr_lambda=0.75,
        retrieval_max_chunks_per_page=2,
        no_answer_threshold=0.55,
        chat_sync_followups=False,
        chat_llm_verifier_min_confidence="low",
    )
    retriever = DummyRetriever(
        [
            {
                "text": "The answer is in the document.",
                "distance": 0.1,
                "metadata": {"document_name": "doc", "page_number": 1, "section_title": "Intro"},
            }
        ]
    )
    service = ChatService(retriever, settings, SessionMemoryStore())
    fake_llm = FakeLLM(answer="A direct answer")
    monkeypatch.setattr(service, "_load_llm", lambda: fake_llm)

    result = service.answer(question="What is the answer?", session_id="sess-1")

    assert result["follow_up_questions"] == []
    assert result["answer"] == "A direct answer"


def test_format_context_trims_long_matches_to_prevent_large_prompts():
    settings = DummySettings(
        gemini_api_key="test",
        model_name="gemini-test",
        top_k=3,
        chat_context_top_k=3,
        chat_context_chunk_chars=40,
        retrieval_candidate_multiplier=4,
        retrieval_mmr_lambda=0.75,
        retrieval_max_chunks_per_page=2,
        no_answer_threshold=0.55,
        chat_sync_followups=False,
        chat_llm_verifier_min_confidence="high",
    )
    retriever = DummyRetriever([])
    service = ChatService(retriever, settings, SessionMemoryStore())

    matches = [{"text": "x" * 80, "distance": 0.1, "metadata": {"document_name": "doc", "page_number": 1}}]

    context = service._format_context(matches)

    assert len(context) < 120
    assert context.endswith("...")


def test_answer_stream_emits_tokens_and_final_event(monkeypatch):
    settings = DummySettings(
        gemini_api_key="test",
        model_name="gemini-test",
        top_k=3,
        chat_context_top_k=3,
        chat_context_chunk_chars=400,
        retrieval_candidate_multiplier=4,
        retrieval_mmr_lambda=0.75,
        retrieval_max_chunks_per_page=2,
        no_answer_threshold=0.55,
        chat_sync_followups=False,
        chat_llm_verifier_min_confidence="high",
    )
    retriever = DummyRetriever(
        [
            {
                "text": "Streaming context.",
                "distance": 0.1,
                "metadata": {"document_name": "doc", "page_number": 2, "section_title": "Body"},
            }
        ]
    )
    service = ChatService(retriever, settings, SessionMemoryStore())
    fake_llm = FakeLLM(answer="", stream_chunks=["Hello", " world"])
    monkeypatch.setattr(service, "_load_llm", lambda: fake_llm)

    events = list(service.answer_stream(question="Stream me", session_id="sess-2"))

    token_events = [event for event in events if event["event"] == "token"]
    final_event = [event for event in events if event["event"] == "final"][0]

    assert [event["data"]["text"] for event in token_events] == ["Hello", " world"]
    assert final_event["data"]["answer"] == "Hello world"
    assert final_event["data"]["session_id"] == "sess-2"
