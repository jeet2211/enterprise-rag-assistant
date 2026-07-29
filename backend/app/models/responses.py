from datetime import datetime

from pydantic import BaseModel


class UploadResponse(BaseModel):
    document_id: str
    filename: str
    status: str
    message: str
    deduplicated: bool = False


class Citation(BaseModel):
    document_name: str
    page_number: int
    chunk_preview: str
    token_count: int = 0
    doc_id: str = ""
    distance: float = 0.0
    section_title: str = ""


class ChatResponse(BaseModel):
    answer: str
    citations: list[Citation]
    session_id: str
    sources_used: int
    confidence: str = "medium"  # high | medium | low | not_found
    evidence_status: str = "partial"  # exact | partial | not_found
    answer_style: str = "supported"  # supported | refused
    trace_id: str = ""
    follow_up_questions: list[str] = []
    latency_ms: float = 0.0


class DocumentListItem(BaseModel):
    id: str
    filename: str
    page_count: int
    chunk_count: int = 0
    status: str
    uploaded_at: datetime
    file_size_bytes: int


class DocumentDetail(BaseModel):
    id: str
    filename: str
    page_count: int
    chunk_count: int = 0
    file_hash: str | None
    status: str
    error_msg: str | None
    uploaded_at: datetime
    updated_at: datetime
    file_size_bytes: int


class DocumentStatusResponse(BaseModel):
    id: str
    status: str
    error_msg: str | None = None


class DeleteResponse(BaseModel):
    document_id: str
    status: str
    message: str


class FeedbackResponse(BaseModel):
    feedback_id: str
    message: str


class HealthResponse(BaseModel):
    status: str
    chromadb: str
    gemini: str
    uptime_seconds: float
    total_documents: int = 0
    ready_documents: int = 0
    failed_documents: int = 0
    processing_documents: int = 0
    total_chunks: int = 0


class WorkerHealthResponse(BaseModel):
    status: str
    redis: str
    celery: str
    worker_count: int = 0
