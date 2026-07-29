from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import httpx
from mcp.server.fastmcp import FastMCP


API_BASE_URL = os.getenv("MCP_RAG_API_BASE_URL", "http://localhost:8000/api/v1").rstrip("/")
REQUEST_TIMEOUT_SECONDS = float(os.getenv("MCP_RAG_TIMEOUT_SECONDS", "60"))

mcp = FastMCP(
    "enterprise-rag-assistant",
    instructions=(
        "Use these tools to query, inspect, upload, and manage documents in the Enterprise RAG Assistant. "
        "The FastAPI backend must be running before these tools are called."
    ),
)


def _api_request(method: str, path: str, **kwargs: Any) -> Any:
    url = f"{API_BASE_URL}{path}"
    try:
        with httpx.Client(timeout=REQUEST_TIMEOUT_SECONDS) as client:
            response = client.request(method, url, **kwargs)
            response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        detail = exc.response.text
        raise RuntimeError(f"RAG API returned {exc.response.status_code} for {method} {path}: {detail}") from exc
    except httpx.HTTPError as exc:
        raise RuntimeError(f"Could not reach RAG API at {API_BASE_URL}: {exc}") from exc

    if response.content:
        return response.json()
    return {"status": "ok"}


@mcp.tool()
def check_rag_health() -> dict[str, Any]:
    """Check whether the Enterprise RAG backend, vector store, and Gemini configuration are healthy."""
    return _api_request("GET", "/health")


@mcp.tool()
def check_worker_health() -> dict[str, Any]:
    """Check whether Redis and the Celery document-processing worker are healthy."""
    return _api_request("GET", "/health/worker")


@mcp.tool()
def list_documents(status: str | None = None) -> list[dict[str, Any]]:
    """List uploaded documents, optionally filtering by status."""
    documents = _api_request("GET", "/documents")
    if status is None:
        return documents
    return [document for document in documents if document.get("status") == status]


@mcp.tool()
def get_document(document_id: str) -> dict[str, Any]:
    """Get detailed metadata for one uploaded document."""
    return _api_request("GET", f"/documents/{document_id}")


@mcp.tool()
def get_document_status(document_id: str) -> dict[str, Any]:
    """Get the current processing status for one uploaded document."""
    return _api_request("GET", f"/documents/{document_id}/status")


@mcp.tool()
def ask_rag(
    question: str,
    session_id: str = "mcp-session",
    top_k: int | None = None,
    document_ids: list[str] | None = None,
) -> dict[str, Any]:
    """Ask a grounded question over uploaded documents and return the answer with citations."""
    payload: dict[str, Any] = {"question": question, "session_id": session_id}
    if top_k is not None:
        payload["top_k"] = top_k
    if document_ids is not None:
        payload["document_ids"] = document_ids
    return _api_request("POST", "/chat", json=payload)


@mcp.tool()
def upload_pdf(file_path: str) -> dict[str, Any]:
    """Upload a local PDF file to the RAG assistant for background processing."""
    path = Path(file_path).expanduser().resolve()
    if not path.exists():
        raise ValueError(f"PDF file does not exist: {path}")
    if not path.is_file():
        raise ValueError(f"PDF path is not a file: {path}")
    if path.suffix.lower() != ".pdf":
        raise ValueError(f"Only PDF uploads are supported: {path}")

    with path.open("rb") as pdf:
        files = {"file": (path.name, pdf, "application/pdf")}
        return _api_request("POST", "/upload", files=files)


@mcp.tool()
def delete_document(document_id: str) -> dict[str, Any]:
    """Delete an uploaded document and remove its indexed chunks."""
    return _api_request("DELETE", f"/documents/{document_id}")


def main() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
