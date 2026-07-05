from __future__ import annotations

from datetime import datetime, timezone

import chromadb


class Retriever:
    def __init__(self, persist_dir: str, embedding_service, collection_name: str = "documents"):
        self.persist_dir = persist_dir
        self.embedding_service = embedding_service
        self.client = chromadb.PersistentClient(path=persist_dir)
        self.collection = self.client.get_or_create_collection(name=collection_name, metadata={"hnsw:space": "cosine"})

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
    ) -> list[dict[str, object]]:
        if not query.strip():
            return []

        # Build where clause for metadata filtering
        where: dict | None = None
        if document_ids:
            if len(document_ids) == 1:
                where = {"doc_id": {"$eq": document_ids[0]}}
            else:
                where = {"doc_id": {"$in": document_ids}}

        try:
            result = self.collection.query(
                query_embeddings=[self.embedding_service.embed_query(query)],
                n_results=top_k,
                where=where,
                include=["documents", "metadatas", "distances"],
            )
        except Exception:
            # Collection may be empty or filter matched nothing — return empty
            return []

        documents = result.get("documents", [[]])[0]
        metadatas = result.get("metadatas", [[]])[0]
        distances = result.get("distances", [[]])[0]
        matches: list[dict[str, object]] = []
        for text, metadata, distance in zip(documents, metadatas, distances):
            matches.append(
                {
                    "text": text,
                    "metadata": metadata,
                    "distance": distance,
                }
            )
        return matches

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
