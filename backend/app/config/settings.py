from functools import lru_cache
import json

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "local"
    gemini_api_key: str = ""
    model_name: str = "gemini-2.5-flash"
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    chunk_size: int = 1000  # token-based chunk window
    chunk_overlap: int = 150  # token overlap between adjacent chunks
    top_k: int = 5
    retrieval_candidate_multiplier: int = 4
    retrieval_mmr_lambda: float = 0.75
    retrieval_max_chunks_per_page: int = 2
    no_answer_threshold: float = 0.55  # cosine distance above which we refuse to answer
    chat_context_top_k: int = 5
    chat_context_chunk_chars: int = 1200
    chat_sync_followups: bool = False
    chat_llm_verifier_min_confidence: str = "low"
    warm_embedding_model_on_startup: bool = True
    max_file_mb: int = 50
    session_memory_k: int = 10
    chroma_persist_dir: str = "./backend/chroma_db"
    upload_dir: str = "./backend/uploads"
    db_url: str = Field(default="sqlite:///./backend/app.db", alias="DATABASE_URL")
    redis_url: str = Field(default="redis://redis:6379/0", alias="REDIS_URL")
    celery_broker_url: str | None = Field(default=None, alias="CELERY_BROKER_URL")
    celery_result_backend: str | None = Field(default=None, alias="CELERY_RESULT_BACKEND")
    celery_task_always_eager: bool = Field(default=False, alias="CELERY_TASK_ALWAYS_EAGER")
    log_level: str = "INFO"
    cors_origins_raw: str = Field(default='["http://localhost:5173","http://localhost:4173"]', alias="CORS_ORIGINS")
    rate_limit_chat: str = "20/minute"

    # Auth
    secret_key: str = Field(default="change-me-in-production-use-openssl-rand-hex-32", alias="SECRET_KEY")
    access_token_expire_minutes: int = Field(default=15, alias="ACCESS_TOKEN_EXPIRE_MINUTES")
    refresh_token_expire_days: int = Field(default=7, alias="REFRESH_TOKEN_EXPIRE_DAYS")

    # Public URLs
    public_app_url: str = Field(default="http://localhost:5173", alias="PUBLIC_APP_URL")
    api_base_url: str = Field(default="http://localhost:8000/api/v1", alias="API_BASE_URL")

    # Rate limits
    rate_limit_login: str = Field(default="5/minute", alias="RATE_LIMIT_LOGIN")
    rate_limit_signup: str = Field(default="3/minute", alias="RATE_LIMIT_SIGNUP")

    model_config = SettingsConfigDict(env_file=".env", extra="ignore", protected_namespaces=(), populate_by_name=True)

    @model_validator(mode="after")
    def validate_production_settings(self) -> "Settings":
        if self.app_env.lower() != "production":
            return self

        if not self.gemini_api_key or self.gemini_api_key == "your_gemini_api_key_here":
            raise ValueError("GEMINI_API_KEY must be set in production")
        if self.secret_key == "change-me-in-production-use-openssl-rand-hex-32":
            raise ValueError("SECRET_KEY must be changed in production")
        if "localhost" in self.public_app_url or "localhost" in self.api_base_url:
            raise ValueError("PUBLIC_APP_URL and API_BASE_URL must use production URLs")
        return self

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

    @property
    def resolved_celery_broker_url(self) -> str:
        return self.celery_broker_url or self.redis_url

    @property
    def resolved_celery_result_backend(self) -> str:
        return self.celery_result_backend or self.redis_url


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
