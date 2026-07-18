from __future__ import annotations

from pathlib import Path

from app.rag.chunker import Chunker


# 7-stage document processing status values:
# uploaded → extracting_text → chunking → embedding → indexing → ready / failed

class RAGPipeline:
    def __init__(self, pdf_service, embedding_service, retriever, document_service, settings):
        self.pdf_service = pdf_service
        self.embedding_service = embedding_service
        self.retriever = retriever
        self.document_service = document_service
        self.settings = settings
        self.chunker = Chunker(settings.chunk_size, settings.chunk_overlap)

    def process_document(self, document_id: str, file_path: str, filename: str) -> None:
        try:
            # Stage 1: extracting_text
            self.document_service.update_document(document_id, status="extracting_text", error_msg=None)
            pages = self.pdf_service.extract_pages(file_path)

            # Stage 2: chunking
            self.document_service.update_document(document_id, status="chunking")
            page_texts = [(page.page_number, page.text) for page in pages]
            chunks = self.chunker.chunk_pages(page_texts)

            # Stage 3: embedding
            self.document_service.update_document(document_id, status="embedding")
            chunk_payloads = [
                {
                    "text": chunk.text,
                    "page_number": chunk.page_number,
                    "chunk_index": chunk.chunk_index,
                    "token_count": chunk.token_count,
                }
                for chunk in chunks
            ]

            # Stage 4: indexing (embed + store in ChromaDB)
            self.document_service.update_document(document_id, status="indexing")
            self.retriever.add_chunks(document_id=document_id, filename=filename, chunks=chunk_payloads)

            # Done
            self.document_service.update_document(
                document_id,
                status="ready",
                page_count=len(pages),
                chunk_count=len(chunks),
                error_msg=None,
            )

        except Exception as exc:
            self.document_service.update_document(document_id, status="failed", error_msg=str(exc))
            raise

    def delete_document(self, document_id: str, file_path: str) -> None:
        self.retriever.delete_document(document_id)
        Path(file_path).unlink(missing_ok=True)
