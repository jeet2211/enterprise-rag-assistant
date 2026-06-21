from __future__ import annotations
from typing import Optional

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
        ids = [f"{document_id}:{chunk['page_number']}:{chunk['chunk_index']}" for chunk in chunks]
        texts = [str(chunk["text"]) for chunk in chunks]
        embeddings = self.embedding_service.embed_texts(texts)
        metadatas = [
            {
                "doc_id": document_id,
                "document_name": filename,
                "page_number": int(chunk["page_number"]),
                "chunk_index": int(chunk["chunk_index"]),
                "chunk_preview": str(chunk["text"])[:200],
            }
            for chunk in chunks
        ]
        self.collection.upsert(ids=ids, documents=texts, embeddings=embeddings, metadatas=metadatas)

    def search(self, query: str, top_k: int = 5, document_ids: Optional[list[str]] = None) -> list[dict[str, object]]:
        if not query.strip():
            return []
        where = {"doc_id": {"$in": document_ids}} if document_ids else None
        result = self.collection.query(
            query_embeddings=[self.embedding_service.embed_query(query)],
            n_results=top_k,
            where=where,
            include=["documents", "metadatas", "distances"],
        )
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
        self.collection.delete(where={"doc_id": document_id})

    def healthcheck(self) -> bool:
        self.collection.count()
        return True
