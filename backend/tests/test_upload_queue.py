from __future__ import annotations


PDF_BYTES = b"%PDF-1.4\n1 0 obj\n<<>>\nendobj\ntrailer\n<<>>\n%%EOF\n"


def test_upload_enqueues_document_processing_task(client, monkeypatch):
    queued: list[tuple[str, str, str]] = []

    def fake_delay(document_id: str, file_path: str, filename: str):
        queued.append((document_id, file_path, filename))

    monkeypatch.setattr("app.api.routes.upload.process_document_task.delay", fake_delay)

    response = client.post(
        "/api/v1/upload",
        files={"file": ("sample.pdf", PDF_BYTES, "application/pdf")},
    )

    assert response.status_code == 202
    data = response.json()
    assert data["status"] == "uploaded"
    assert data["deduplicated"] is False
    assert len(queued) == 1
    assert queued[0][0] == data["document_id"]
    assert queued[0][2] == "sample.pdf"


def test_duplicate_processing_upload_is_not_queued_twice(client, monkeypatch):
    queued: list[tuple[str, str, str]] = []

    def fake_delay(document_id: str, file_path: str, filename: str):
        queued.append((document_id, file_path, filename))

    monkeypatch.setattr("app.api.routes.upload.process_document_task.delay", fake_delay)

    first = client.post(
        "/api/v1/upload",
        files={"file": ("sample.pdf", PDF_BYTES, "application/pdf")},
    )
    second = client.post(
        "/api/v1/upload",
        files={"file": ("sample.pdf", PDF_BYTES, "application/pdf")},
    )

    assert first.status_code == 202
    assert second.status_code == 202
    assert second.json()["deduplicated"] is True
    assert second.json()["status"] == "uploaded"
    assert len(queued) == 1
