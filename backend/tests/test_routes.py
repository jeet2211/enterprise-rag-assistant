from __future__ import annotations

from pathlib import Path
from datetime import datetime

from app.models.db import Document
from app.api.routes.documents import _serialize_document


def test_health_route_reports_status(client, test_app):
    response = client.get("/api/v1/health")

    payload = response.json()
    assert response.status_code == 200
    assert payload["status"] == "healthy"
    assert payload["chromadb"] == "healthy"
    assert payload["gemini"] == "degraded"
    assert payload["uptime_seconds"] == 42.0
    assert test_app.state.retriever.healthcheck_calls == 1


def test_health_route_reports_degraded_when_retriever_fails(client, test_app):
    test_app.state.retriever.fail_health = True

    response = client.get("/api/v1/health")

    payload = response.json()
    assert response.status_code == 200
    assert payload["status"] == "degraded"
    assert payload["chromadb"] == "degraded"


def test_upload_document_creates_row_and_runs_background_task(client, test_app, tmp_path):
    response = client.post(
        "/api/v1/upload",
        files={"file": ("report.pdf", b"%PDF-1.4 fake content", "application/pdf")},
    )

    payload = response.json()
    assert response.status_code == 202
    assert payload["status"] == "processing"

    stored = test_app.state.document_service.get_document(payload["document_id"])
    assert stored is not None
    assert stored.status == "ready"
    assert stored.page_count == 3
    assert test_app.state.pipeline.process_calls
    assert Path(stored.file_path).exists()


def test_documents_routes_list_detail_and_delete(client, test_app):
    created = test_app.state.document_service.create_document(
        document_id="doc-1",
        filename="report.pdf",
        file_path=str(Path(test_app.state.settings.upload_dir) / "doc-1_report.pdf"),
        file_size=2048,
    )
    test_app.state.document_service.update_document("doc-1", status="ready", page_count=9, error_msg=None)
    Path(created.file_path).parent.mkdir(parents=True, exist_ok=True)
    Path(created.file_path).write_text("content")

    list_response = client.get("/api/v1/documents")
    assert list_response.status_code == 200
    assert list_response.json()[0]["id"] == "doc-1"

    detail_response = client.get("/api/v1/documents/doc-1")
    assert detail_response.status_code == 200
    assert detail_response.json()["page_count"] == 9

    delete_response = client.delete("/api/v1/documents/doc-1")
    assert delete_response.status_code == 200
    assert delete_response.json()["status"] == "deleted"
    assert test_app.state.pipeline.delete_calls == [("doc-1", created.file_path)]
    assert test_app.state.document_service.get_document("doc-1") is None
    assert not Path(created.file_path).exists()


def test_documents_route_404s(client):
    assert client.get("/api/v1/documents/missing").status_code == 404
    assert client.delete("/api/v1/documents/missing").status_code == 404


def test_serialize_document_helper():
    document = type(
        "Doc",
        (),
        {
            "id": "doc-9",
            "filename": "helper.pdf",
            "page_count": None,
            "status": "ready",
            "uploaded_at": datetime(2024, 1, 1, 0, 0, 0),
            "file_size": None,
        },
    )()

    serialized = _serialize_document(document)

    assert serialized.id == "doc-9"
    assert serialized.page_count == 0
    assert serialized.file_size_bytes == 0


def test_chat_route_formats_response(client, test_app):
    response = client.post(
        "/api/v1/chat",
        json={"question": "What is in the document?", "session_id": "session-123", "top_k": 2},
    )

    payload = response.json()
    assert response.status_code == 200
    assert payload["answer"] == "Answer for What is in the document?"
    assert payload["sources_used"] == 2
    assert payload["citations"][0]["document_name"] == "policy.pdf"
    assert test_app.state.chat_service.calls[0]["session_id"] == "session-123"


def test_root_route(client):
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "enterprise-rag-assistant"}
