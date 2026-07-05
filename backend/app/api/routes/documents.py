from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request, status

from app.models.responses import (
    DeleteResponse,
    DocumentDetail,
    DocumentListItem,
    DocumentStatusResponse,
)

router = APIRouter(prefix="/documents", tags=["documents"])


@router.get("", response_model=list[DocumentListItem])
def list_documents(request: Request):
    docs = request.app.state.document_service.list_documents()
    return [
        DocumentListItem(
            id=doc.id,
            filename=doc.filename,
            page_count=doc.page_count or 0,
            chunk_count=doc.chunk_count or 0,
            status=doc.status,
            uploaded_at=doc.uploaded_at,
            file_size_bytes=doc.file_size or 0,
        )
        for doc in docs
    ]


@router.get("/{document_id}/status", response_model=DocumentStatusResponse)
def get_document_status(document_id: str, request: Request):
    """Lightweight polling endpoint — returns only id, status, error_msg."""
    doc = request.app.state.document_service.get_document(document_id)
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    return DocumentStatusResponse(id=doc.id, status=doc.status, error_msg=doc.error_msg)


@router.get("/{document_id}", response_model=DocumentDetail)
def get_document(document_id: str, request: Request):
    doc = request.app.state.document_service.get_document(document_id)
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    return DocumentDetail(
        id=doc.id,
        filename=doc.filename,
        page_count=doc.page_count or 0,
        chunk_count=doc.chunk_count or 0,
        file_hash=doc.file_hash,
        status=doc.status,
        error_msg=doc.error_msg,
        uploaded_at=doc.uploaded_at,
        updated_at=doc.updated_at,
        file_size_bytes=doc.file_size or 0,
    )


@router.delete("/{document_id}", response_model=DeleteResponse)
def delete_document(document_id: str, request: Request):
    service = request.app.state.document_service
    pipeline = request.app.state.pipeline
    doc = service.get_document(document_id)
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    pipeline.delete_document(document_id, doc.file_path)
    service.delete_document(document_id)
    return DeleteResponse(document_id=document_id, status="deleted", message="Document deleted successfully.")
