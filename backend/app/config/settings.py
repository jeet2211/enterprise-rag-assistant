from functools import lru_cache
import json

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "local"
    gemini_api_key: str = ""
    model_name: str = "gemini-2.5-flash"
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    chunk_size: int = 1000
    chunk_overlap: int = 150
    top_k: int = 5
    no_answer_threshold: float = 0.55  # cosine distance above which we refuse to answer
    max_file_mb: int = 50
    session_memory_k: int = 10
    chroma_persist_dir: str = "./backend/chroma_db"
    upload_dir: str = "./backend/uploads"
    db_url: str = Field(default="sqlite:///./backend/app.db", alias="DATABASE_URL")
    log_level: str = "INFO"
    cors_origins_raw: str = Field(default='["http://localhost:5173","http://localhost:4173"]', alias="CORS_ORIGINS")
    rate_limit_chat: str = "20/minute"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore", protected_namespaces=(), populate_by_name=True)

    @property
    def cors_origins(self) -> list[str]:
        raw = self.cors_origins_raw
        if isinstance(raw, list):
            return raw
        try:
            value = json.loads(raw)
            return value if isinstance(value, list) else [str(value)]
        except Exception:
            return [origin.strip() for origin in str(raw).split(",") if origin.strip()]


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
