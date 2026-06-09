from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    question: str = Field(min_length=1, max_length=4000)
    session_id: str = Field(min_length=8)
    top_k: int | None = Field(default=None, ge=1, le=20)

