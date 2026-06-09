from __future__ import annotations

import uuid
from pathlib import Path

import aiofiles
from fastapi import APIRouter, BackgroundTasks, File, HTTPException, Request, UploadFile, status

from app.api.deps import get_pipeline
from app.models.responses import UploadResponse
from app.utils.validators import validate_pdf_upload

router = APIRouter(prefix="/upload", tags=["upload"])


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
    )
    background_tasks.add_task(_background_process, document_id, str(destination), original_name, request.app.state)
    return UploadResponse(
        document_id=document_id,
        filename=original_name,
        status="processing",
        message="Upload accepted. Processing has started in the background.",
    )

