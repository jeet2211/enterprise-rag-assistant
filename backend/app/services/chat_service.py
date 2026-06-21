from __future__ import annotations

from collections import defaultdict, deque
from typing import Optional

from app.models.responses import Citation
from app.rag.prompt import build_prompt


class SessionMemoryStore:
    def __init__(self, window_size: int = 10):
        self.window_size = window_size
        self._sessions: dict[str, deque[tuple[str, str]]] = defaultdict(lambda: deque(maxlen=window_size * 2))

    def add_turn(self, session_id: str, question: str, answer: str) -> None:
        self._sessions[session_id].append(("user", question))
        self._sessions[session_id].append(("assistant", answer))

    def render(self, session_id: str) -> str:
        turns = self._sessions.get(session_id, deque())
        return "\n".join(f"{role.upper()}: {content}" for role, content in turns)

    def reset(self, session_id: str) -> None:
        self._sessions.pop(session_id, None)


class ChatService:
    def __init__(self, retriever, settings, memory_store: SessionMemoryStore):
        self.retriever = retriever
        self.settings = settings
        self.memory_store = memory_store
        self._llm = None

    def _load_llm(self):
        if self._llm is not None:
            return self._llm
        if not self.settings.gemini_api_key:
            return None
        from langchain_google_genai import ChatGoogleGenerativeAI

        self._llm = ChatGoogleGenerativeAI(
            model=self.settings.model_name,
            google_api_key=self.settings.gemini_api_key,
            temperature=0.2,
        )
        return self._llm

    def answer(self, *, question: str, session_id: str, top_k: Optional[int] = None):
        matches = self.retriever.search(question, top_k=top_k or self.settings.top_k)
        context_parts = []
        citation_map = {}
        for match in matches:
            metadata = match["metadata"] or {}
            document_name = str(metadata.get("document_name", "Unknown document"))
            page_number = int(metadata.get("page_number", 0))
            chunk_preview = str(metadata.get("chunk_preview", match["text"]))[:200]
            context_parts.append(
                f"[{document_name} p.{page_number}] {match['text']}"
            )
            key = (document_name, page_number)
            if key not in citation_map:
                citation_map[key] = {
                    "document_name": document_name,
                    "page_number": page_number,
                    "previews": [chunk_preview]
                }
            else:
                if chunk_preview not in citation_map[key]["previews"]:
                    citation_map[key]["previews"].append(chunk_preview)

        citations: list[Citation] = []
        for val in citation_map.values():
            merged_preview = "\n\n[...]\n\n".join(val["previews"])
            citations.append(
                Citation(
                    document_name=val["document_name"],
                    page_number=val["page_number"],
                    chunk_preview=merged_preview,
                )
            )

        history = self.memory_store.render(session_id)
        prompt = build_prompt(history=history, context="\n\n".join(context_parts), question=question)
        llm = self._load_llm()

        if llm is None:
            answer = self._fallback_answer(question, citations)
            self.memory_store.add_turn(session_id, question, answer)
            return answer, citations

        response = llm.invoke(prompt)
        answer = response.content if hasattr(response, "content") else str(response)
        self.memory_store.add_turn(session_id, question, answer)
        return answer, citations

    def _fallback_answer(self, question: str, citations: list[Citation]) -> str:
        if not citations:
            return (
                "I could not find a relevant answer in the uploaded documents. "
                "Add a PDF or try a different question."
            )
        source_text = ", ".join(f"{c.document_name} p.{c.page_number}" for c in citations[:3])
        return f"I found related content in {source_text}, but Gemini is not configured. Set GEMINI_API_KEY to get a generated answer."
