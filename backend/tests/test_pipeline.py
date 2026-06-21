from __future__ import annotations
from typing import Optional

from app.config.settings import Settings
from app.rag.pipeline import RAGPipeline


class FakePDFService:
    def __init__(self, pages):
        self.pages = pages
        self.calls = []

    def extract_pages(self, file_path: str):
        self.calls.append(file_path)
        return self.pages


class FakeEmbeddingService:
    def embed_texts(self, texts):
        return [[float(index)] for index, _ in enumerate(texts)]


class FakeRetriever:
    def __init__(self):
        self.added = []
        self.deleted = []

    def add_chunks(self, *, document_id: str, filename: str, chunks: list[dict[str, object]]) -> None:
        self.added.append({"document_id": document_id, "filename": filename, "chunks": chunks})

    def delete_document(self, document_id: str) -> None:
        self.deleted.append(document_id)


class FakeDocumentService:
    def __init__(self):
        self.created = []
        self.updated = []

    def update_document(self, document_id: str, *, status: Optional[str] = None, page_count: Optional[int] = None, error_msg: Optional[str] = None):
        self.updated.append(
            {
                "document_id": document_id,
                "status": status,
                "page_count": page_count,
                "error_msg": error_msg,
            }
        )


def test_pipeline_process_document_success(tmp_path):
    pdf_service = FakePDFService(
        [
            type("Page", (), {"page_number": 1, "text": "First page text"})(),
            type("Page", (), {"page_number": 2, "text": "Second page text"})(),
        ]
    )
    retriever = FakeRetriever()
    document_service = FakeDocumentService()
    settings = Settings(chunk_size=220, chunk_overlap=40)
    pipeline = RAGPipeline(pdf_service, FakeEmbeddingService(), retriever, document_service, settings)

    pipeline.process_document("doc-1", str(tmp_path / "input.pdf"), "report.pdf")

    assert pdf_service.calls == [str(tmp_path / "input.pdf")]
    assert retriever.added[0]["document_id"] == "doc-1"
    assert retriever.added[0]["filename"] == "report.pdf"
    assert retriever.added[0]["chunks"][0]["text"] == "First page text"
    assert document_service.updated[-1]["status"] == "ready"
    assert document_service.updated[-1]["page_count"] == 2
    assert document_service.updated[-1]["error_msg"] is None


def test_pipeline_process_document_marks_failure():
    class ExplodingPDFService:
        def extract_pages(self, file_path: str):
            raise RuntimeError("broken pdf")

    retriever = FakeRetriever()
    document_service = FakeDocumentService()
    settings = Settings()
    pipeline = RAGPipeline(ExplodingPDFService(), FakeEmbeddingService(), retriever, document_service, settings)

    try:
        pipeline.process_document("doc-2", "/tmp/input.pdf", "report.pdf")
    except RuntimeError as exc:
        assert str(exc) == "broken pdf"
    else:
        raise AssertionError("Expected pipeline to re-raise the PDF error")

    assert document_service.updated[-1]["status"] == "failed"
    assert "broken pdf" in document_service.updated[-1]["error_msg"]


def test_pipeline_delete_document_removes_vector_entries_and_file(tmp_path):
    retriever = FakeRetriever()
    document_service = FakeDocumentService()
    settings = Settings()
    pipeline = RAGPipeline(FakePDFService([]), FakeEmbeddingService(), retriever, document_service, settings)
    file_path = tmp_path / "document.pdf"
    file_path.write_text("content")

    pipeline.delete_document("doc-3", str(file_path))

    assert retriever.deleted == ["doc-3"]
    assert not file_path.exists()
