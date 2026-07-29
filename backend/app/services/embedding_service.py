from __future__ import annotations

import threading
from functools import lru_cache

import numpy as np
from sentence_transformers import SentenceTransformer


class EmbeddingService:
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):  # noqa: D107
        self.model_name = model_name
        self._model: SentenceTransformer | None = None
        self._lock = threading.Lock()

    def _load(self) -> SentenceTransformer:
        if self._model is None:
            with self._lock:
                if self._model is None:
                    self._model = SentenceTransformer(self.model_name)
        return self._model

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        model = self._load()
        embeddings = model.encode(texts, normalize_embeddings=True, convert_to_numpy=True)
        return np.asarray(embeddings, dtype=np.float32).tolist()

    def embed_query(self, text: str) -> list[float]:
        return self.embed_texts([text])[0]

    @property
    def ready(self) -> bool:
        return self._model is not None
