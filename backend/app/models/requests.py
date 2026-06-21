from pydantic import BaseModel, Field
from typing import Optional


class ChatRequest(BaseModel):
    question: str = Field(min_length=1, max_length=4000)
    session_id: str = Field(min_length=8)
    top_k: Optional[int] = Field(default=None, ge=1, le=20)
