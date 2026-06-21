from __future__ import annotations

import io

import pytest
from fastapi import HTTPException

from app.utils.validators import validate_pdf_upload


class FakeUploadFile:
    def __init__(self, filename: str, content_type: str, content: bytes):
        self.filename = filename
        self.content_type = content_type
        self._buffer = io.BytesIO(content)
        self.closed = False

    async def read(self, size: int = -1):
        return self._buffer.read(size)

    async def seek(self, offset: int):
        self._buffer.seek(offset)

    async def close(self):
        self.closed = True


@pytest.mark.anyio
async def test_validate_pdf_upload_accepts_pdf():
    file = FakeUploadFile("report.pdf", "application/pdf", b"%PDF-1.4 content")

    await validate_pdf_upload(file, max_bytes=1024)

    assert file._buffer.tell() == 0


@pytest.mark.anyio
async def test_validate_pdf_upload_rejects_non_pdf():
    file = FakeUploadFile("notes.txt", "text/plain", b"hello")

    with pytest.raises(HTTPException) as exc:
        await validate_pdf_upload(file, max_bytes=1024)

    assert exc.value.status_code == 400


@pytest.mark.anyio
async def test_validate_pdf_upload_rejects_empty_file():
    file = FakeUploadFile("report.pdf", "application/pdf", b"")

    with pytest.raises(HTTPException) as exc:
        await validate_pdf_upload(file, max_bytes=1024)

    assert exc.value.status_code == 400


@pytest.mark.anyio
async def test_validate_pdf_upload_rejects_large_file():
    file = FakeUploadFile("report.pdf", "application/pdf", b"x" * 32)

    with pytest.raises(HTTPException) as exc:
        await validate_pdf_upload(file, max_bytes=16)

    assert exc.value.status_code == 413
