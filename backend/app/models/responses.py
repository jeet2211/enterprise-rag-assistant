from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class UploadResponse(BaseModel):
    document_id: str
    filename: str
    status: str
    message: str


class Citation(BaseModel):
    document_name: str
    page_number: int
    chunk_preview: str


class ChatResponse(BaseModel):
    answer: str
    citations: list[Citation]
    session_id: str
    sources_used: int


class DocumentListItem(BaseModel):
    id: str
    filename: str
    page_count: int
    status: str
    uploaded_at: datetime
    file_size_bytes: int


class DocumentDetail(BaseModel):
    id: str
    filename: str
    page_count: int
    status: str
    error_msg: Optional[str]
    uploaded_at: datetime
    updated_at: datetime
    file_size_bytes: int


class DeleteResponse(BaseModel):
    document_id: str
    status: str
    message: str


class HealthResponse(BaseModel):
    status: str
    chromadb: str
    gemini: str
    uptime_seconds: float
