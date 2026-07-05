from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    question: str = Field(min_length=1, max_length=4000)
    session_id: str = Field(min_length=8)
    top_k: int | None = Field(default=None, ge=1, le=20)
    document_ids: list[str] | None = Field(default=None, description="Filter retrieval to specific document IDs")


class FeedbackRequest(BaseModel):
    message_id: str = Field(min_length=1)
    session_id: str = Field(min_length=8)
    rating: str = Field(pattern="^(good|bad)$")
    reason: str | None = Field(default=None, max_length=64)
