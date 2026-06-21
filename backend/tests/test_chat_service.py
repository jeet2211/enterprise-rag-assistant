from app.config.settings import Settings
from app.models.responses import Citation
from app.services.chat_service import ChatService, SessionMemoryStore
import sys
import types


class FakeRetriever:
    def __init__(self, results=None):
        self.results = results or []
        self.calls = []

    def search(self, query: str, top_k: int = 5, document_ids=None):
        self.calls.append((query, top_k, document_ids))
        return self.results


class FakeLLM:
    def __init__(self):
        self.prompts = []

    def invoke(self, prompt: str):
        self.prompts.append(prompt)

        class Response:
            content = "Generated answer from Gemini"

        return Response()


def test_chat_service_falls_back_without_llm():
    retriever = FakeRetriever(
        results=[
            {
                "text": "Policy excerpt",
                "metadata": {
                    "document_name": "policy.pdf",
                    "page_number": 5,
                    "chunk_preview": "Policy excerpt",
                },
            }
        ]
    )
    settings = Settings(gemini_api_key="")
    memory = SessionMemoryStore(window_size=2)
    service = ChatService(retriever, settings, memory)

    answer, citations = service.answer(question="What does it say?", session_id="session-123", top_k=3)

    assert "Gemini is not configured" in answer
    assert citations == [Citation(document_name="policy.pdf", page_number=5, chunk_preview="Policy excerpt")]
    history = memory.render("session-123")
    assert "USER: What does it say?" in history
    assert "ASSISTANT:" in history


def test_chat_service_uses_llm_when_available():
    retriever = FakeRetriever(
        results=[
            {
                "text": "Guidance excerpt",
                "metadata": {
                    "document_name": "guide.pdf",
                    "page_number": 2,
                    "chunk_preview": "Guidance excerpt",
                },
            }
        ]
    )
    settings = Settings(gemini_api_key="test-key")
    memory = SessionMemoryStore(window_size=2)
    service = ChatService(retriever, settings, memory)
    fake_llm = FakeLLM()
    service._llm = fake_llm

    answer, citations = service.answer(question="Summarize it", session_id="session-456", top_k=1)

    assert answer == "Generated answer from Gemini"
    assert citations[0].document_name == "guide.pdf"
    assert fake_llm.prompts
    assert "Summarize it" in fake_llm.prompts[0]


def test_chat_service_loads_llm_from_dependency(monkeypatch):
    retriever = FakeRetriever(results=[])
    settings = Settings(gemini_api_key="test-key")
    memory = SessionMemoryStore(window_size=2)
    service = ChatService(retriever, settings, memory)

    class ImportedLLM:
        def __init__(self, **kwargs):
            self.kwargs = kwargs
            self.prompts = []

        def invoke(self, prompt: str):
            self.prompts.append(prompt)

            class Response:
                content = "Imported LLM answer"

            return Response()

    monkeypatch.setitem(sys.modules, "langchain_google_genai", types.SimpleNamespace(ChatGoogleGenerativeAI=ImportedLLM))

    answer, citations = service.answer(question="Use the dependency", session_id="session-789", top_k=1)

    assert answer == "Imported LLM answer"
    assert citations == []
    assert isinstance(service._llm, ImportedLLM)


def test_chat_service_falls_back_when_no_citations():
    retriever = FakeRetriever(results=[])
    settings = Settings(gemini_api_key="")
    memory = SessionMemoryStore(window_size=2)
    service = ChatService(retriever, settings, memory)

    answer, citations = service.answer(question="Unknown question", session_id="session-999", top_k=1)

    assert "could not find a relevant answer" in answer.lower()
    assert citations == []


def test_session_memory_store_limits_turns():
    store = SessionMemoryStore(window_size=1)

    store.add_turn("session", "Q1", "A1")
    store.add_turn("session", "Q2", "A2")

    history = store.render("session")
    assert "Q1" not in history
    assert "Q2" in history

    store.reset("session")
    assert store.render("session") == ""


def test_chat_service_deduplicates_citations():
    retriever = FakeRetriever(
        results=[
            {
                "text": "Chunk 1 text",
                "metadata": {
                    "document_name": "policy.pdf",
                    "page_number": 5,
                    "chunk_preview": "Preview 1",
                },
            },
            {
                "text": "Chunk 2 text",
                "metadata": {
                    "document_name": "policy.pdf",
                    "page_number": 5,
                    "chunk_preview": "Preview 2",
                },
            },
            {
                "text": "Chunk 3 text",
                "metadata": {
                    "document_name": "policy.pdf",
                    "page_number": 6,
                    "chunk_preview": "Preview 3",
                },
            },
        ]
    )
    settings = Settings(gemini_api_key="")
    memory = SessionMemoryStore(window_size=2)
    service = ChatService(retriever, settings, memory)

    answer, citations = service.answer(question="Test question", session_id="session-dup", top_k=3)

    assert len(citations) == 2
    assert citations[0].document_name == "policy.pdf"
    assert citations[0].page_number == 5
    assert citations[0].chunk_preview == "Preview 1\n\n[...]\n\nPreview 2"
    assert citations[1].document_name == "policy.pdf"
    assert citations[1].page_number == 6
    assert citations[1].chunk_preview == "Preview 3"
