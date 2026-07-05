from __future__ import annotations

import json
import logging
import time
import uuid
from collections import defaultdict, deque
from datetime import datetime

from app.models.responses import Citation
from app.rag.prompt import build_followup_prompt, build_prompt

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# In-memory session memory (sliding window for LLM context)
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Confidence scoring
# ---------------------------------------------------------------------------

def _compute_confidence(distances: list[float], no_answer_threshold: float) -> str:
    if not distances:
        return "not_found"
    best = min(distances)
    if best > no_answer_threshold:
        return "not_found"
    if best < 0.20:
        return "high"
    if best < 0.38:
        return "medium"
    return "low"


# ---------------------------------------------------------------------------
# Chat service
# ---------------------------------------------------------------------------

class ChatService:
    def __init__(self, retriever, settings, memory_store: SessionMemoryStore, session_factory=None):
        self.retriever = retriever
        self.settings = settings
        self.memory_store = memory_store
        self.session_factory = session_factory  # may be None if DB persistence is not needed
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

    def answer(
        self,
        *,
        question: str,
        session_id: str,
        top_k: int | None = None,
        document_ids: list[str] | None = None,
    ) -> dict:
        """
        Returns a dict with keys:
          answer, citations, confidence, trace_id, follow_up_questions, latency_ms
        """
        trace_id = str(uuid.uuid4())
        t_start = time.perf_counter()

        matches = self.retriever.search(
            question,
            top_k=top_k or self.settings.top_k,
            document_ids=document_ids or None,
        )

        distances = [float(m["distance"]) for m in matches]
        confidence = _compute_confidence(distances, self.settings.no_answer_threshold)

        context_parts = []
        citations: list[Citation] = []

        for match in matches:
            metadata = match["metadata"] or {}
            document_name = str(metadata.get("document_name", "Unknown document"))
            page_number = int(metadata.get("page_number", 0))
            token_count = int(metadata.get("token_count", 0))
            chunk_preview = str(metadata.get("chunk_preview", match["text"]))[:200]
            doc_id = str(metadata.get("doc_id", ""))
            context_parts.append(f"[{document_name} p.{page_number}] {match['text']}")
            citations.append(
                Citation(
                    document_name=document_name,
                    page_number=page_number,
                    chunk_preview=chunk_preview,
                    token_count=token_count,
                    doc_id=doc_id,
                    distance=float(match["distance"]),
                )
            )

        # If confidence is not_found, skip LLM call entirely
        if confidence == "not_found":
            answer_text = "I could not find this information in the uploaded documents."
            follow_up_questions: list[str] = []
        else:
            history = self.memory_store.render(session_id)
            full_context = "\n\n".join(context_parts)
            prompt = build_prompt(history=history, context=full_context, question=question)
            llm = self._load_llm()

            if llm is None:
                answer_text = self._fallback_answer(question, citations)
                follow_up_questions = []
            else:
                try:
                    response = llm.invoke(prompt)
                    answer_text = response.content if hasattr(response, "content") else str(response)
                except Exception as exc:
                    logger.error(
                        '{"event":"llm_error","trace_id":"%s","error":"%s"}',
                        trace_id,
                        str(exc),
                    )
                    answer_text = "The AI model encountered an error generating a response. Please try again."
                    follow_up_questions = []
                    confidence = "low"
                else:
                    follow_up_questions = self._generate_followups(full_context, llm)

        latency_ms = round((time.perf_counter() - t_start) * 1000, 1)
        self.memory_store.add_turn(session_id, question, answer_text)

        logger.info(
            '{"event":"chat_request","trace_id":"%s","session_id":"%s","confidence":"%s",'
            '"sources":%d,"latency_ms":%s}',
            trace_id, session_id, confidence, len(citations), latency_ms,
        )

        # Persist to DB if session_factory is available
        if self.session_factory is not None:
            self._persist_messages(session_id, question, answer_text, citations, confidence, trace_id, latency_ms, document_ids)

        return {
            "answer": answer_text,
            "citations": citations,
            "confidence": confidence,
            "trace_id": trace_id,
            "follow_up_questions": follow_up_questions,
            "latency_ms": latency_ms,
        }

    def _generate_followups(self, context: str, llm) -> list[str]:
        """Ask the LLM to generate 3 follow-up questions from the retrieved context."""
        try:
            followup_prompt = build_followup_prompt(context)
            response = llm.invoke(followup_prompt)
            raw = response.content if hasattr(response, "content") else str(response)
            # Parse numbered list: "1. question\n2. question\n3. question"
            questions = []
            for line in raw.strip().splitlines():
                line = line.strip()
                if line and line[0].isdigit() and "." in line:
                    q = line.split(".", 1)[-1].strip()
                    if q:
                        questions.append(q)
            return questions[:3]
        except Exception:
            return []

    def _fallback_answer(self, question: str, citations: list[Citation]) -> str:
        if not citations:
            return (
                "I could not find a relevant answer in the uploaded documents. "
                "Upload a PDF or try a different question."
            )
        source_text = ", ".join(f"{c.document_name} p.{c.page_number}" for c in citations[:3])
        return (
            f"I found related content in {source_text}, but Gemini is not configured. "
            "Set GEMINI_API_KEY to get a generated answer."
        )

    def _persist_messages(
        self,
        session_id: str,
        question: str,
        answer: str,
        citations: list[Citation],
        confidence: str,
        trace_id: str,
        latency_ms: float,
        document_ids: list[str] | None,
    ) -> None:
        """Persist user question and assistant answer to the database."""
        try:
            from app.models.db import ChatMessage, ChatSession

            citations_json = json.dumps(
                [
                    {
                        "document_name": c.document_name,
                        "page_number": c.page_number,
                        "chunk_preview": c.chunk_preview,
                    }
                    for c in citations
                ]
            )

            with self.session_factory() as session:
                # Upsert ChatSession
                existing = session.get(ChatSession, session_id)
                if not existing:
                    session.add(
                        ChatSession(
                            id=session_id,
                            document_ids=json.dumps(document_ids or []),
                            created_at=datetime.utcnow(),
                            updated_at=datetime.utcnow(),
                        )
                    )
                else:
                    existing.updated_at = datetime.utcnow()

                # User message
                session.add(
                    ChatMessage(
                        id=str(uuid.uuid4()),
                        session_id=session_id,
                        role="user",
                        content=question,
                        created_at=datetime.utcnow(),
                    )
                )
                # Assistant message
                session.add(
                    ChatMessage(
                        id=str(uuid.uuid4()),
                        session_id=session_id,
                        role="assistant",
                        content=answer,
                        citations=citations_json,
                        confidence=confidence,
                        trace_id=trace_id,
                        latency_ms=latency_ms,
                        created_at=datetime.utcnow(),
                    )
                )
                session.commit()
        except Exception as exc:
            logger.warning('{"event":"chat_persist_error","error":"%s"}', str(exc))
