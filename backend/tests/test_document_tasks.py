from __future__ import annotations

from types import SimpleNamespace

from app.tasks import document_tasks


class FakeDocumentService:
    def __init__(self, status: str | None):
        self.document = SimpleNamespace(status=status) if status else None
        self.updates: list[dict[str, str]] = []

    def get_document(self, document_id: str):
        return self.document

    def update_document(self, document_id: str, **kwargs):
        self.updates.append(kwargs)
        if self.document is not None and "status" in kwargs:
            self.document.status = kwargs["status"]
        return self.document


class FakePipeline:
    def __init__(self):
        self.calls: list[tuple[str, str, str]] = []

    def process_document(self, document_id: str, file_path: str, filename: str) -> None:
        self.calls.append((document_id, file_path, filename))


def test_document_task_skips_missing_document(monkeypatch, tmp_path):
    document_service = FakeDocumentService(status=None)
    pipeline = FakePipeline()
    monkeypatch.setattr(
        document_tasks,
        "build_app_services",
        lambda settings, include_chat=False: SimpleNamespace(document_service=document_service, pipeline=pipeline),
    )

    result = document_tasks.process_document_task.run("missing", str(tmp_path / "missing.pdf"), "missing.pdf")

    assert result == {"status": "skipped", "reason": "missing_document"}
    assert pipeline.calls == []


def test_document_task_skips_ready_document(monkeypatch, tmp_path):
    document_service = FakeDocumentService(status="ready")
    pipeline = FakePipeline()
    monkeypatch.setattr(
        document_tasks,
        "build_app_services",
        lambda settings, include_chat=False: SimpleNamespace(document_service=document_service, pipeline=pipeline),
    )

    result = document_tasks.process_document_task.run("doc-id", str(tmp_path / "already.pdf"), "already.pdf")

    assert result == {"status": "skipped", "reason": "already_ready"}
    assert pipeline.calls == []


def test_document_task_processes_existing_document(monkeypatch, tmp_path):
    document_service = FakeDocumentService(status="uploaded")
    pipeline = FakePipeline()
    file_path = tmp_path / "sample.pdf"
    file_path.write_bytes(b"%PDF-1.4\n%%EOF\n")
    monkeypatch.setattr(
        document_tasks,
        "build_app_services",
        lambda settings, include_chat=False: SimpleNamespace(document_service=document_service, pipeline=pipeline),
    )

    result = document_tasks.process_document_task.run("doc-id", str(file_path), "sample.pdf")

    assert result == {"status": "ready", "document_id": "doc-id"}
    assert pipeline.calls == [("doc-id", str(file_path), "sample.pdf")]


def test_document_task_marks_missing_file_failed(monkeypatch, tmp_path):
    document_service = FakeDocumentService(status="uploaded")
    pipeline = FakePipeline()
    monkeypatch.setattr(
        document_tasks,
        "build_app_services",
        lambda settings, include_chat=False: SimpleNamespace(document_service=document_service, pipeline=pipeline),
    )

    result = document_tasks.process_document_task.run("doc-id", str(tmp_path / "missing.pdf"), "missing.pdf")

    assert result == {"status": "failed", "reason": "missing_file"}
    assert document_service.updates == [{"status": "failed", "error_msg": "Uploaded file is missing."}]
    assert pipeline.calls == []
