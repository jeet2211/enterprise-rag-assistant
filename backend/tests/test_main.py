from __future__ import annotations

from fastapi.testclient import TestClient

from app import main as main_module


def test_main_app_starts_and_serves_root(tmp_path):
    main_module.settings.upload_dir = str(tmp_path / "uploads")
    main_module.settings.chroma_persist_dir = str(tmp_path / "chroma")
    main_module.settings.db_url = f"sqlite:///{tmp_path / 'app.db'}"
    main_module.settings.gemini_api_key = ""

    with TestClient(main_module.app) as client:
        root_response = client.get("/")
        health_response = client.get("/api/v1/health")

    assert root_response.status_code == 200
    assert root_response.json() == {"status": "ok", "service": "enterprise-rag-assistant"}
    assert health_response.status_code == 200
    assert health_response.json()["status"] in {"healthy", "degraded"}
