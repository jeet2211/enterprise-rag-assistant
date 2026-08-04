from __future__ import annotations

import json
import logging
import re
import time
import uuid
from collections import defaultdict, deque
from datetime import datetime

from app.core.metrics import RAGMetrics
from app.core.tracing import get_tracer
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


def _should_run_verifier(confidence: str, min_confidence: str) -> bool:
    order = {"not_found": 0, "low": 1, "medium": 2, "high": 3}
    threshold = order.get(min_confidence, order["low"])
    return order.get(confidence, 0) <= threshold


def _route_question(question: str) -> str:
    lower = question.lower()
    parameter_terms = ("optimal", "threshold", "tune", "tuning", "parameter", "config")
    if re.search(r"\b[A-Z][A-Z0-9_]{2,}\b", question) or any(token in lower for token in parameter_terms):
        return "parameter"
    if any(
        token in lower
        for token in (
            "architecture",
            "best",
            "build",
            "compare",
            "create",
            "design",
            "difference",
            "factor",
            "how",
            "implement",
            "influence",
            "pattern",
            "plan",
            "strategy",
            "tradeoff",
            "versus",
            "why",
        )
    ):
        return "explanation"
    return "general"


def _is_document_summary_question(question: str) -> bool:
    lower = question.lower()
    summary_terms = ("summarize", "summary", "overview", "simple terms", "explain this document")
    document_terms = ("document", "pdf", "book", "file", "it", "this")
    return any(term in lower for term in summary_terms) and any(term in lower for term in document_terms)


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
    def _trim_text(text: str, limit: int) -> str:
        if limit <= 0 or len(text) <= limit:
            return text
        return text[:limit].rsplit(" ", 1)[0].rstrip() + "..."

    def _format_context(self, matches: list[dict[str, object]]) -> str:
        context_parts = []
        for idx, match in enumerate(matches, 1):
            metadata = match["metadata"] or {}
            document_name = str(metadata.get("document_name", "Unknown document"))
            page_number = int(metadata.get("page_number", 0))
            section_title = str(metadata.get("section_title", "")).strip()
            section_prefix = f"Section: {section_title} | " if section_title else ""
            text = self._trim_text(str(match["text"]), self.settings.chat_context_chunk_chars)
            context_parts.append(f"Source [{idx}]: [{document_name} p.{page_number}]\n{section_prefix}{text}")
        return "\n\n".join(context_parts)

    def _build_citations(self, matches: list[dict[str, object]]) -> list[Citation]:
        citations: list[Citation] = []
        for match in matches:
            metadata = match["metadata"] or {}
            citations.append(
                Citation(
                    document_name=str(metadata.get("document_name", "Unknown document")),
                    page_number=int(metadata.get("page_number", 0)),
                    chunk_preview=str(metadata.get("chunk_preview", match["text"]))[:200],
                    token_count=int(metadata.get("token_count", 0)),
                    doc_id=str(metadata.get("doc_id", "")),
                    distance=float(match["distance"]),
                    section_title=str(metadata.get("section_title", "")),
                )
            )
        return citations

    @staticmethod
    def _record_timing(timings: dict[str, float], name: str, start: float) -> None:
        timings[name] = round((time.perf_counter() - start) * 1000, 1)

    def _retrieve(
        self,
        *,
        question: str,
        top_k: int | None,
        document_ids: list[str] | None,
        timings: dict[str, float],
    ) -> tuple[list[dict[str, object]], list[Citation], str]:
        requested_top_k = min(top_k or self.settings.top_k, self.settings.chat_context_top_k)
        route = _route_question(question)
        if route == "parameter":
            candidate_multiplier = max(self.settings.retrieval_candidate_multiplier, 5)
            mmr_lambda = min(self.settings.retrieval_mmr_lambda, 0.55)
        elif route == "explanation":
            candidate_multiplier = max(self.settings.retrieval_candidate_multiplier, 4)
            mmr_lambda = min(self.settings.retrieval_mmr_lambda, 0.65)
        else:
            candidate_multiplier = self.settings.retrieval_candidate_multiplier
            mmr_lambda = self.settings.retrieval_mmr_lambda

        t_stage = time.perf_counter()
        matches = self.retriever.search(
            question,
            top_k=requested_top_k,
            document_ids=document_ids or None,
            candidate_multiplier=candidate_multiplier,
            mmr_lambda=mmr_lambda,
            max_chunks_per_page=self.settings.retrieval_max_chunks_per_page,
        )
        if document_ids and _is_document_summary_question(question):
            representative_matches = self.retriever.get_document_chunks(
                document_ids,
                limit=max(requested_top_k, self.settings.chat_context_top_k),
            )
            if representative_matches:
                matches = representative_matches
        elif document_ids and not matches:
            matches = self.retriever.get_document_chunks(document_ids, limit=requested_top_k)

        # Keep the most relevant chunk first so the answer/verifier prompts
        # preserve the strongest evidence even when later chunks are truncated.
        matches = sorted(matches, key=lambda match: float(match["distance"]))
        self._record_timing(timings, "retrieval_ms", t_stage)

        citations = self._build_citations(matches)
        distances = [float(m["distance"]) for m in matches]
        confidence = _compute_confidence(distances, self.settings.no_answer_threshold)
        return matches, citations, confidence

    def _verify_answer(self, *, question: str, answer: str, context: str) -> dict[str, str | bool]:
        key_terms = _extract_key_terms(question)
        if key_terms:
            context_lower = context.lower()
            missing_terms = [term for term in key_terms if term.lower() not in context_lower]
            # If the question asks about specific symbols/parameters, require
            # those exact symbols to be present. Otherwise let the LLM judge.
            if missing_terms and len(key_terms) <= 4:
                return {
                    "evidence_status": "not_found",
                    "allow_answer": False,
                    "reason": f"Missing key terms in context: {', '.join(missing_terms[:4])}",
                }
        llm = self._load_llm()
        if llm is None:
            return {
                "evidence_status": "partial",
                "allow_answer": True,
                "reason": "Verifier unavailable; using retrieval confidence only.",
            }
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
            return {
                "evidence_status": "partial",
                "allow_answer": True,
                "reason": "Verifier could not parse model output.",
            }

    def answer(
        self,
        *,
        question: str,
        session_id: str,
        top_k: int | None = None,
        document_ids: list[str] | None = None,
        user_id: str | None = None,
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

        # --- Langfuse: open a trace for this request ---
        tracer = get_tracer()
        lf_trace = tracer.start_trace(
            name="chat_answer",
            session_id=session_id,
            user_id=user_id,
            input={"question": question},
            metadata={"document_ids": document_ids},
        )
        if getattr(lf_trace, "id", "noop") != "noop":
            trace_id = str(lf_trace.id)

        timings: dict[str, float] = {}

        # Retrieval span
        lf_retrieval = lf_trace.span(name="retrieval", input={"question": question})
        matches, citations, confidence = self._retrieve(
            question=question,
            top_k=top_k,
            document_ids=document_ids,
            timings=timings,
        )
        lf_retrieval.end(output={"sources": len(citations), "confidence": confidence})

        # If confidence is not_found, skip LLM call entirely
        if confidence == "not_found":
            answer_text = "I could not find this information in the uploaded documents."
            evidence_status = "not_found"
            answer_style = "refused"
        else:
            t_stage = time.perf_counter()
            history = self.memory_store.render(session_id)
            full_context = self._format_context(matches)
            prompt = build_prompt(history=history, context=full_context, question=question)
            self._record_timing(timings, "prompt_ms", t_stage)
            llm = self._load_llm()

            if llm is None:
                answer_text = self._fallback_answer(question, citations)
                follow_up_questions = []
                evidence_status = "partial"
                answer_style = "supported"
            else:
                try:
                    t_stage = time.perf_counter()
                    lf_llm = lf_trace.span(name="llm_generation", input={"question": question})
                    response = llm.invoke(prompt)
                    answer_text = response.content if hasattr(response, "content") else str(response)
                    self._record_timing(timings, "llm_answer_ms", t_stage)
                    lf_llm.end(output={"answer_length": len(answer_text)})
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
                    if self.settings.chat_sync_followups:
                        t_stage = time.perf_counter()
                        follow_up_questions = self._generate_followups(full_context, llm)
                        self._record_timing(timings, "followups_ms", t_stage)
                    if _should_run_verifier(confidence, self.settings.chat_llm_verifier_min_confidence):
                        t_stage = time.perf_counter()
                        lf_verifier = lf_trace.span(name="verifier")
                        verifier = self._verify_answer(question=question, answer=answer_text, context=full_context)
                        self._record_timing(timings, "verifier_ms", t_stage)
                        evidence_status = str(verifier["evidence_status"])
                        lf_verifier.end(output={"evidence_status": evidence_status})
                        if not bool(verifier["allow_answer"]):
                            answer_text = "I could not find this information in the uploaded documents."
                            follow_up_questions = []
                            evidence_status = "not_found"
                            answer_style = "refused"
                        else:
                            answer_style = "supported"
                    else:
                        evidence_status = "exact" if confidence == "high" else "partial"
                        answer_style = "supported"

        latency_ms = round((time.perf_counter() - t_start) * 1000, 1)
        self.memory_store.add_turn(session_id, question, answer_text)

        # --- Langfuse: close trace ---
        lf_trace.end(output={"confidence": confidence, "evidence_status": evidence_status, "latency_ms": latency_ms})

        # --- Prometheus metrics ---
        RAGMetrics.record_chat(
            confidence=confidence,
            evidence_status=evidence_status,
            answer_style=answer_style,
            latency_ms=latency_ms,
            retrieval_ms=timings.get("retrieval_ms"),
            llm_ms=timings.get("llm_answer_ms"),
            verifier_ms=timings.get("verifier_ms"),
        )

        logger.info(
            '{"event":"chat_request","trace_id":"%s","session_id":"%s","confidence":"%s","sources":%d,"latency_ms":%s}',
            trace_id,
            session_id,
            confidence,
            len(citations),
            latency_ms,
        )

        # Persist to DB if session_factory is available
        if self.session_factory is not None:
            t_stage = time.perf_counter()
            self._persist_messages(
                session_id,
                question,
                answer_text,
                citations,
                confidence,
                trace_id,
                latency_ms,
                document_ids,
                user_id,
            )
            self._record_timing(timings, "persist_ms", t_stage)

        logger.info(
            '{"event":"chat_timing","trace_id":"%s","timings":%s}',
            trace_id,
            json.dumps(timings, sort_keys=True),
        )

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

    def answer_stream(
        self,
        *,
        question: str,
        session_id: str,
        top_k: int | None = None,
        document_ids: list[str] | None = None,
        user_id: str | None = None,
    ):
        trace_id = str(uuid.uuid4())
        t_start = time.perf_counter()
        timings: dict[str, float] = {}
        evidence_status = "partial"
        answer_style = "supported"
        answer_parts: list[str] = []

        tracer = get_tracer()
        lf_trace = tracer.start_trace(
            name="chat_answer_stream",
            session_id=session_id,
            user_id=user_id,
            input={"question": question},
            metadata={"document_ids": document_ids},
        )
        if getattr(lf_trace, "id", "noop") != "noop":
            trace_id = str(lf_trace.id)

        lf_retrieval = lf_trace.span(name="retrieval", input={"question": question})
        matches, citations, confidence = self._retrieve(
            question=question,
            top_k=top_k,
            document_ids=document_ids,
            timings=timings,
        )
        lf_retrieval.end(output={"sources": len(citations), "confidence": confidence})

        yield {"event": "trace", "data": {"trace_id": trace_id, "confidence": confidence}}

        if confidence == "not_found":
            answer_text = "I could not find this information in the uploaded documents."
            answer_parts.append(answer_text)
            evidence_status = "not_found"
            answer_style = "refused"
            yield {"event": "token", "data": {"text": answer_text}}
        else:
            t_stage = time.perf_counter()
            history = self.memory_store.render(session_id)
            full_context = self._format_context(matches)
            prompt = build_prompt(history=history, context=full_context, question=question)
            self._record_timing(timings, "prompt_ms", t_stage)
            llm = self._load_llm()

            if llm is None:
                answer_text = self._fallback_answer(question, citations)
                answer_parts.append(answer_text)
                yield {"event": "token", "data": {"text": answer_text}}
            else:
                t_stage = time.perf_counter()
                lf_llm = lf_trace.span(name="llm_generation", input={"question": question})
                try:
                    for chunk in llm.stream(prompt):
                        text = chunk.content if hasattr(chunk, "content") else str(chunk)
                        if not text:
                            continue
                        answer_parts.append(text)
                        yield {"event": "token", "data": {"text": text}}
                except Exception:
                    if not answer_parts:
                        response = llm.invoke(prompt)
                        text = response.content if hasattr(response, "content") else str(response)
                        answer_parts.append(text)
                        yield {"event": "token", "data": {"text": text}}
                    else:
                        raise
                self._record_timing(timings, "llm_answer_ms", t_stage)
                lf_llm.end(output={"answer_length": len("".join(answer_parts))})

                answer_text = "".join(answer_parts)
                if _should_run_verifier(confidence, self.settings.chat_llm_verifier_min_confidence):
                    t_stage = time.perf_counter()
                    lf_verifier = lf_trace.span(name="verifier")
                    verifier = self._verify_answer(question=question, answer=answer_text, context=full_context)
                    self._record_timing(timings, "verifier_ms", t_stage)
                    evidence_status = str(verifier["evidence_status"])
                    lf_verifier.end(output={"evidence_status": evidence_status})
                    if not bool(verifier["allow_answer"]):
                        answer_text = "I could not find this information in the uploaded documents."
                        answer_parts[:] = [answer_text]
                        evidence_status = "not_found"
                        answer_style = "refused"
                        yield {"event": "replace", "data": {"text": answer_text}}
                else:
                    evidence_status = "exact" if confidence == "high" else "partial"

        answer_text = "".join(answer_parts)
        latency_ms = round((time.perf_counter() - t_start) * 1000, 1)
        self.memory_store.add_turn(session_id, question, answer_text)
        lf_trace.end(output={"confidence": confidence, "evidence_status": evidence_status, "latency_ms": latency_ms})
        if self.session_factory is not None:
            t_stage = time.perf_counter()
            self._persist_messages(
                session_id,
                question,
                answer_text,
                citations,
                confidence,
                trace_id,
                latency_ms,
                document_ids,
                user_id,
            )
            self._record_timing(timings, "persist_ms", t_stage)

        logger.info(
            '{"event":"chat_request","trace_id":"%s","session_id":"%s","confidence":"%s","sources":%d,"latency_ms":%s}',
            trace_id,
            session_id,
            confidence,
            len(citations),
            latency_ms,
        )
        logger.info(
            '{"event":"chat_timing","trace_id":"%s","timings":%s}',
            trace_id,
            json.dumps(timings, sort_keys=True),
        )

        # --- Prometheus metrics ---
        RAGMetrics.record_chat(
            confidence=confidence,
            evidence_status=evidence_status,
            answer_style=answer_style,
            latency_ms=latency_ms,
            retrieval_ms=timings.get("retrieval_ms"),
            llm_ms=timings.get("llm_answer_ms"),
            verifier_ms=timings.get("verifier_ms"),
        )

        yield {
            "event": "final",
            "data": {
                "answer": answer_text,
                "citations": [citation.model_dump() for citation in citations],
                "session_id": session_id,
                "sources_used": len(citations),
                "confidence": confidence,
                "evidence_status": evidence_status,
                "answer_style": answer_style,
                "trace_id": trace_id,
                "follow_up_questions": [],
                "latency_ms": latency_ms,
            },
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
        user_id: str | None = None,
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
                            user_id=user_id,
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
                        user_id=user_id,
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
                        user_id=user_id,
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

    def list_sessions(self, user_id: str) -> list[dict]:
        """List all chat sessions for the given user, ordered by last activity."""
        if self.session_factory is None:
            return []
        try:
            from app.models.db import ChatMessage, ChatSession
            with self.session_factory() as session:
                rows = (
                    session.query(ChatSession)
                    .filter(ChatSession.user_id == user_id)
                    .order_by(ChatSession.updated_at.desc())
                    .all()
                )
                
                results = []
                for r in rows:
                    # Fetch first user question in this session to display as title
                    first_msg = (
                        session.query(ChatMessage)
                        .filter(ChatMessage.session_id == r.id, ChatMessage.role == "user")
                        .order_by(ChatMessage.created_at.asc())
                        .first()
                    )
                    title = first_msg.content[:40] + "..." if first_msg and len(first_msg.content) > 40 else (first_msg.content if first_msg else "New Chat")
                    
                    results.append({
                        "id": r.id,
                        "title": title,
                        "document_ids": json.loads(r.document_ids) if r.document_ids else [],
                        "created_at": r.created_at.isoformat() if r.created_at else None,
                        "updated_at": r.updated_at.isoformat() if r.updated_at else None,
                    })
                return results
        except Exception as exc:
            logger.warning('{"event":"list_sessions_error","error":"%s"}', str(exc))
            return []

    def get_session_messages(self, session_id: str, user_id: str) -> list[dict]:
        """Fetch all messages for a session, checking authorization."""
        if self.session_factory is None:
            return []
        try:
            from app.models.db import ChatMessage, ChatSession
            with self.session_factory() as session:
                meta = session.get(ChatSession, session_id)
                if not meta or meta.user_id != user_id:
                    return []
                rows = (
                    session.query(ChatMessage)
                    .filter(ChatMessage.session_id == session_id)
                    .order_by(ChatMessage.created_at.asc())
                    .all()
                )
                return [
                    {
                        "id": r.id,
                        "role": r.role,
                        "content": r.content,
                        "citations": json.loads(r.citations) if r.citations else [],
                        "confidence": r.confidence,
                        "trace_id": r.trace_id,
                        "latency_ms": r.latency_ms,
                        "timestamp": r.created_at.isoformat() if r.created_at else None,
                    }
                    for r in rows
                ]
        except Exception as exc:
            logger.warning('{"event":"get_session_messages_error","error":"%s"}', str(exc))
            return []

    def delete_session(self, session_id: str, user_id: str) -> bool:
        """Delete a chat session and all its messages, checking authorization."""
        if self.session_factory is None:
            return False
        try:
            from app.models.db import ChatMessage, ChatSession
            with self.session_factory() as session:
                meta = session.get(ChatSession, session_id)
                if not meta or meta.user_id != user_id:
                    return False
                session.query(ChatMessage).filter(ChatMessage.session_id == session_id).delete()
                session.delete(meta)
                session.commit()
                return True
        except Exception as exc:
            logger.warning('{"event":"delete_session_error","error":"%s"}', str(exc))
            return False
