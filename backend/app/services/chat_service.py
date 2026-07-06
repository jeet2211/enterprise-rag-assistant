from __future__ import annotations

import json
import logging
import re
import time
import uuid
from collections import defaultdict, deque
from datetime import datetime

from app.models.responses import Citation
from app.rag.prompt import build_followup_prompt, build_prompt, build_verifier_prompt

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


def _route_question(question: str) -> str:
    lower = question.lower()
    if re.search(r"\b[A-Z][A-Z0-9_]{2,}\b", question) or any(token in lower for token in ("optimal", "threshold", "tune", "tuning", "parameter", "config")):
        return "parameter"
    if any(token in lower for token in ("compare", "difference", "versus", "tradeoff", "why", "how", "factor", "influence", "strategy")):
        return "explanation"
    return "general"


def _extract_key_terms(question: str) -> list[str]:
    terms = re.findall(r"\b[A-Z][A-Z0-9_]{2,}\b", question)
    # Only preserve explicitly technical tokens; generic words are too noisy
    # for refusal gating and should not force a not_found verdict.
    terms.extend(re.findall(r"\b[a-z]*_[a-z0-9_]+\b", question.lower()))
    stop = {
        "what",
        "how",
        "when",
        "where",
        "which",
        "could",
        "would",
        "should",
        "choice",
        "factors",
        "about",
        "there",
        "their",
        "these",
        "those",
        "using",
        "choose",
        "chosen",
        "impact",
        "retrieval",
        "question",
        "answer",
        "document",
        "documents",
        "system",
        "model",
        "does",
        "do",
        "did",
    }
    seen: set[str] = set()
    cleaned: list[str] = []
    for term in terms:
        key = term.lower()
        if key not in stop and key not in seen:
            seen.add(key)
            cleaned.append(term)
    return cleaned[:8]


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

    @staticmethod
    def _format_context(matches: list[dict[str, object]]) -> str:
        context_parts = []
        for match in matches:
            metadata = match["metadata"] or {}
            document_name = str(metadata.get("document_name", "Unknown document"))
            page_number = int(metadata.get("page_number", 0))
            section_title = str(metadata.get("section_title", "")).strip()
            section_prefix = f"Section: {section_title} | " if section_title else ""
            context_parts.append(f"[{document_name} p.{page_number}] {section_prefix}{match['text']}")
        return "\n\n".join(context_parts)

    def _verify_answer(self, *, question: str, answer: str, context: str) -> dict[str, str | bool]:
        key_terms = _extract_key_terms(question)
        if key_terms:
            context_lower = context.lower()
            missing_terms = [term for term in key_terms if term.lower() not in context_lower]
            # If the question asks about specific symbols/parameters, require
            # those exact symbols to be present. Otherwise let the LLM judge.
            if missing_terms and len(key_terms) <= 4:
                return {"evidence_status": "not_found", "allow_answer": False, "reason": f"Missing key terms in context: {', '.join(missing_terms[:4])}"}
        llm = self._load_llm()
        if llm is None:
            return {"evidence_status": "partial", "allow_answer": True, "reason": "Verifier unavailable; using retrieval confidence only."}
        try:
            response = llm.invoke(build_verifier_prompt(question, answer, context))
            raw = response.content if hasattr(response, "content") else str(response)
            data = json.loads(raw)
            evidence_status = str(data.get("evidence_status", "partial"))
            allow_answer = bool(data.get("allow_answer", evidence_status != "not_found"))
            reason = str(data.get("reason", "")).strip()
            if evidence_status not in {"exact", "partial", "not_found"}:
                evidence_status = "partial"
            return {"evidence_status": evidence_status, "allow_answer": allow_answer, "reason": reason}
        except Exception:
            return {"evidence_status": "partial", "allow_answer": True, "reason": "Verifier could not parse model output."}

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
        evidence_status = "partial"
        answer_style = "supported"
        follow_up_questions: list[str] = []

        requested_top_k = top_k or self.settings.top_k
        route = _route_question(question)
        if route == "parameter":
            candidate_multiplier = max(self.settings.retrieval_candidate_multiplier, 6)
            mmr_lambda = min(self.settings.retrieval_mmr_lambda, 0.55)
        elif route == "explanation":
            candidate_multiplier = self.settings.retrieval_candidate_multiplier
            mmr_lambda = self.settings.retrieval_mmr_lambda
        else:
            candidate_multiplier = self.settings.retrieval_candidate_multiplier
            mmr_lambda = self.settings.retrieval_mmr_lambda

        matches = self.retriever.search(
            question,
            top_k=requested_top_k,
            document_ids=document_ids or None,
            candidate_multiplier=candidate_multiplier,
            mmr_lambda=mmr_lambda,
            max_chunks_per_page=self.settings.retrieval_max_chunks_per_page,
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
            citations.append(
                Citation(
                    document_name=document_name,
                    page_number=page_number,
                    chunk_preview=chunk_preview,
                    token_count=token_count,
                    doc_id=doc_id,
                    distance=float(match["distance"]),
                    section_title=str(metadata.get("section_title", "")),
                )
            )

        # If confidence is not_found, skip LLM call entirely
        if confidence == "not_found":
            answer_text = "I could not find this information in the uploaded documents."
            evidence_status = "not_found"
            answer_style = "refused"
        else:
            history = self.memory_store.render(session_id)
            full_context = self._format_context(matches)
            prompt = build_prompt(history=history, context=full_context, question=question)
            llm = self._load_llm()

            if llm is None:
                answer_text = self._fallback_answer(question, citations)
                follow_up_questions = []
                evidence_status = "partial"
                answer_style = "supported"
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
                    evidence_status = "partial"
                    answer_style = "supported"
                else:
                    follow_up_questions = self._generate_followups(full_context, llm)
                    verifier = self._verify_answer(question=question, answer=answer_text, context=full_context)
                    evidence_status = str(verifier["evidence_status"])
                    if not bool(verifier["allow_answer"]):
                        answer_text = "I could not find this information in the uploaded documents."
                        follow_up_questions = []
                        evidence_status = "not_found"
                        answer_style = "refused"
                    else:
                        answer_style = "supported"

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
            "evidence_status": evidence_status,
            "answer_style": answer_style,
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
