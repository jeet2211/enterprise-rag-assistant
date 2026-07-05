from __future__ import annotations

import hashlib
import uuid
from pathlib import Path

import aiofiles
from fastapi import APIRouter, BackgroundTasks, File, HTTPException, Request, UploadFile, status

from app.models.responses import UploadResponse
from app.utils.validators import validate_pdf_upload

router = APIRouter(prefix="/upload", tags=["upload"])


async def _compute_hash(file: UploadFile) -> str:
    """Compute SHA-256 hash of the uploaded file without loading it all into memory."""
    h = hashlib.sha256()
    await file.seek(0)
    while True:
        chunk = await file.read(1024 * 1024)
        if not chunk:
            break
        h.update(chunk)
    await file.seek(0)
    return h.hexdigest()


async def _save_upload(file: UploadFile, destination: Path) -> int:
    total = 0
    async with aiofiles.open(destination, "wb") as out:
        while True:
            chunk = await file.read(1024 * 1024)
            if not chunk:
                break
            total += len(chunk)
            await out.write(chunk)
    await file.close()
    return total


def _background_process(document_id: str, file_path: str, filename: str, request_state):
    request_state.pipeline.process_document(document_id, file_path, filename)


@router.post("", response_model=UploadResponse, status_code=status.HTTP_202_ACCEPTED)
async def upload_document(
    request: Request,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
):
    settings = request.app.state.settings
    await validate_pdf_upload(file, settings.max_file_mb * 1024 * 1024)

    # ── Deduplication: compute SHA-256 hash and check for existing document ──
    file_hash = await _compute_hash(file)
    existing = request.app.state.document_service.get_by_hash(file_hash)
    if existing is not None and existing.status == "ready":
        return UploadResponse(
            document_id=existing.id,
            filename=existing.filename,
            status=existing.status,
            message=(
                f"This file has already been processed as '{existing.filename}'. "
                "No duplicate processing needed."
            ),
            deduplicated=True,
        )

    document_id = str(uuid.uuid4())
    uploads_dir = Path(settings.upload_dir)
    uploads_dir.mkdir(parents=True, exist_ok=True)

    original_name = Path(file.filename or "document.pdf").name
    stored_name = f"{document_id}_{original_name}"
    destination = uploads_dir / stored_name
    size = await _save_upload(file, destination)

    request.app.state.document_service.create_document(
        document_id=document_id,
        filename=original_name,
        file_path=str(destination),
        file_size=size,
        file_hash=file_hash,
    )
    background_tasks.add_task(
        _background_process, document_id, str(destination), original_name, request.app.state
    )
    return UploadResponse(
        document_id=document_id,
        filename=original_name,
        status="uploaded",
        message="Upload accepted. Processing has started in the background.",
    )
