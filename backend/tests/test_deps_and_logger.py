from __future__ import annotations

import json
import logging
import sys

from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from app.api.deps import get_chat_service, get_document_service, get_pipeline, get_settings
from app.utils.logger import JsonFormatter, configure_logging


def test_dependency_helpers_return_state_objects():
    app = FastAPI()
    app.state.settings = {"kind": "settings"}
    app.state.document_service = {"kind": "documents"}
    app.state.pipeline = {"kind": "pipeline"}
    app.state.chat_service = {"kind": "chat"}

    @app.get("/deps")
    def read_deps(
        settings=Depends(get_settings),
        document_service=Depends(get_document_service),
        pipeline=Depends(get_pipeline),
        chat_service=Depends(get_chat_service),
    ):
        return {
            "settings_kind": settings["kind"],
            "document_kind": document_service["kind"],
            "pipeline_kind": pipeline["kind"],
            "chat_kind": chat_service["kind"],
        }

    with TestClient(app) as client:
        response = client.get("/deps")

    assert response.json() == {
        "settings_kind": "settings",
        "document_kind": "documents",
        "pipeline_kind": "pipeline",
        "chat_kind": "chat",
    }


def test_json_formatter_serializes_exception():
    formatter = JsonFormatter()
    try:
        raise ValueError("boom")
    except ValueError:
        record = logging.LogRecord("test", logging.ERROR, __file__, 10, "failed", (), None)
        record.exc_info = sys.exc_info()
        rendered = formatter.format(record)

    payload = json.loads(rendered)
    assert payload["level"] == "ERROR"
    assert payload["logger"] == "test"
    assert payload["message"] == "failed"
    assert "exception" in payload


def test_configure_logging_emits_json(capsys):
    configure_logging("INFO")
    logger = logging.getLogger("enterprise.test")

    logger.info("hello world")

    output = capsys.readouterr().out.strip()
    payload = json.loads(output)
    assert payload["level"] == "INFO"
    assert payload["logger"] == "enterprise.test"
    assert payload["message"] == "hello world"
