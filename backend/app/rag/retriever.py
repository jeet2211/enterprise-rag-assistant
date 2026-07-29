from __future__ import annotations

from collections import defaultdict
import re
from datetime import datetime, timezone
from collections.abc import Sequence
from typing import Any, cast

import chromadb
from chromadb.api.types import Include


class Retriever:
    def __init__(self, persist_dir: str, embedding_service, collection_name: str = "documents"):
        self.persist_dir = persist_dir
        self.embedding_service = embedding_service
        self.client = chromadb.PersistentClient(path=persist_dir)
        self.collection = self.client.get_or_create_collection(name=collection_name, metadata={"hnsw:space": "cosine"})

    @staticmethod
    def _dot(left: Sequence[float], right: Sequence[float]) -> float:
        return sum(float(a) * float(b) for a, b in zip(left, right))

    @staticmethod
    def _query_terms(query: str) -> list[str]:
        exact_terms = re.findall(r"\b[A-Z][A-Z0-9_]{2,}\b", query)
        words = re.findall(r"\b[a-z0-9_]{4,}\b", query.lower())
        seen: set[str] = set()
        terms: list[str] = []
        for term in exact_terms + words:
            key = term.lower()
            if key not in seen:
                seen.add(key)
                terms.append(term)
        return terms[:10]

    def _mmr_rerank(
        self,
        *,
        query_embedding: Sequence[float],
        query: str,
        candidates: list[dict[str, object]],
        limit: int,
        lambda_mult: float,
        max_chunks_per_page: int,
    ) -> list[dict[str, object]]:
        if limit <= 0 or not candidates:
            return []

        lambda_mult = max(0.0, min(1.0, float(lambda_mult)))
        max_chunks_per_page = max(1, int(max_chunks_per_page))

        candidate_embs: list[Sequence[float] | None] = []
        query_sims: list[float] = []
        query_terms = self._query_terms(query)
        for candidate in candidates:
            embedding = candidate.get("embedding")
            text = str(candidate.get("text", "")).lower()
            if isinstance(embedding, list):
                candidate_embs.append(embedding)
                lexical_bonus = 0.0
                if query_terms:
                    matches = sum(1 for term in query_terms if term.lower() in text)
                    lexical_bonus = min(0.35, matches * 0.12)
                query_sims.append(min(1.0, self._dot(query_embedding, embedding) + lexical_bonus))
            else:
                candidate_embs.append(None)
                distance = float(candidate.get("distance", 1.0))
                lexical_bonus = 0.0
                if query_terms:
                    matches = sum(1 for term in query_terms if term.lower() in text)
                    lexical_bonus = min(0.35, matches * 0.12)
                query_sims.append(min(1.0, (1.0 - distance) + lexical_bonus))

        selected: list[dict[str, object]] = []
        selected_indices: list[int] = []
        per_page_counts: dict[tuple[str, int], int] = defaultdict(int)

        while len(selected) < limit:
            best_index: int | None = None
            best_score: float | None = None

            for index, candidate in enumerate(candidates):
                if index in selected_indices:
                    continue

                metadata = candidate.get("metadata") or {}
                doc_id = str(metadata.get("doc_id", ""))
                page_number = int(metadata.get("page_number", 0))
                page_key = (doc_id, page_number)
                if per_page_counts[page_key] >= max_chunks_per_page:
                    continue

                redundancy = 0.0
                candidate_embedding = candidate_embs[index]
                if candidate_embedding is not None and selected_indices:
                    selected_embeddings = [
                        candidate_embs[selected_index]
                        for selected_index in selected_indices
                        if candidate_embs[selected_index] is not None
                    ]
                    if selected_embeddings:
                        redundancy = max(
                            self._dot(candidate_embedding, selected_embedding)
                            for selected_embedding in selected_embeddings
                        )  # type: ignore[arg-type]

                score = lambda_mult * query_sims[index] - (1.0 - lambda_mult) * redundancy
                if best_score is None or score > best_score:
                    best_index = index
                    best_score = score

            if best_index is None:
                break

            selected_indices.append(best_index)
            selected_candidate = candidates[best_index]
            selected.append(selected_candidate)

            metadata = selected_candidate.get("metadata") or {}
            doc_id = str(metadata.get("doc_id", ""))
            page_number = int(metadata.get("page_number", 0))
            per_page_counts[(doc_id, page_number)] += 1

        return selected

    def add_chunks(self, *, document_id: str, filename: str, chunks: list[dict[str, object]]) -> None:
        if not chunks:
            return
        now_iso = datetime.now(timezone.utc).isoformat()
        ids = [f"{document_id}:{chunk['page_number']}:{chunk['chunk_index']}" for chunk in chunks]
        texts = [str(chunk["text"]) for chunk in chunks]
        embeddings = self.embedding_service.embed_texts(texts)
        metadatas = [
            {
                "doc_id": document_id,
                "document_name": filename,
                "page_number": int(chunk["page_number"]),
                "chunk_index": int(chunk["chunk_index"]),
                "token_count": int(chunk.get("token_count", 0)),
                "chunk_preview": str(chunk["text"])[:200],
                "section_title": str(chunk.get("section_title", "")),
                "created_at": now_iso,
            }
            for chunk in chunks
        ]
        self.collection.upsert(ids=ids, documents=texts, embeddings=embeddings, metadatas=metadatas)

    def search(
        self,
        query: str,
        top_k: int = 5,
        document_ids: list[str] | None = None,
        candidate_multiplier: int = 4,
        mmr_lambda: float = 0.75,
        max_chunks_per_page: int = 2,
    ) -> list[dict[str, object]]:
        if not query.strip():
            return []

        requested_top_k = max(1, int(top_k))
        candidate_multiplier = max(1, int(candidate_multiplier))
        candidate_top_k = min(max(requested_top_k * candidate_multiplier, requested_top_k), 50)

        # Build where clause for metadata filtering
        where: dict | None = None
        if document_ids:
            if len(document_ids) == 1:
                where = {"doc_id": {"$eq": document_ids[0]}}
            else:
                where = {"doc_id": {"$in": document_ids}}

        try:
            query_embedding = self.embedding_service.embed_query(query)
            include: Any = ["documents", "metadatas", "distances", "embeddings"]
            result = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=candidate_top_k,
                where=where,
                include=include,
            )
        except Exception:
            # Collection may be empty or filter matched nothing — return empty
            return []

        documents = cast(list[list[str]], result.get("documents") or [[]])[0]
        metadatas = cast(list[list[dict[str, object]]], result.get("metadatas") or [[]])[0]
        distances = cast(list[list[float]], result.get("distances") or [[]])[0]
        embeddings = cast(list[list[Sequence[float]]], result.get("embeddings") or [[]])[0]
        matches: list[dict[str, object]] = []
        for text, metadata, distance, embedding in zip(documents, metadatas, distances, embeddings):
            matches.append(
                {
                    "text": text,
                    "metadata": metadata,
                    "distance": distance,
                    "embedding": embedding,
                }
            )
        return self._mmr_rerank(
            query_embedding=query_embedding,
            query=query,
            candidates=matches,
            limit=requested_top_k,
            lambda_mult=mmr_lambda,
            max_chunks_per_page=max_chunks_per_page,
        )

    def delete_document(self, document_id: str) -> None:
        try:
            self.collection.delete(where={"doc_id": document_id})
        except Exception:
            pass  # If no chunks exist, silently skip

    def count(self) -> int:
        return self.collection.count()

    def healthcheck(self) -> bool:
        self.collection.count()
        return True
