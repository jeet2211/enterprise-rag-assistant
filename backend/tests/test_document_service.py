from pathlib import Path

from app.models.db import Document
from app.services.document_service import DocumentService


def test_document_service_crud(session_factory, tmp_path):
    service = DocumentService(session_factory)
    document_id = "doc-123"
    file_path = tmp_path / "uploads" / "doc-123-report.pdf"
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text("pdf")

    created = service.create_document(
        document_id=document_id,
        filename="report.pdf",
        file_path=str(file_path),
        file_size=1234,
    )

    assert created.id == document_id
    assert created.status == "processing"
    assert created.file_size == 1234

    updated = service.update_document(document_id, status="ready", page_count=8, error_msg=None)
    assert updated is not None
    assert updated.status == "ready"
    assert updated.page_count == 8
    assert service.get_document(document_id).filename == "report.pdf"

    listed = service.list_documents()
    assert [doc.id for doc in listed] == [document_id]

    deleted = service.delete_document(document_id)
    assert deleted is not None
    assert service.get_document(document_id) is None


def test_remove_file_only_deletes_existing_paths(tmp_path):
    target = tmp_path / "file.txt"
    target.write_text("hello")

    DocumentService.remove_file(str(target))

    assert not target.exists()

    missing = tmp_path / "missing.txt"
    DocumentService.remove_file(str(missing))


def test_document_service_returns_none_for_missing_document(session_factory):
    service = DocumentService(session_factory)

    assert service.get_document("missing") is None
    assert service.update_document("missing", status="ready") is None
    assert service.delete_document("missing") is None
