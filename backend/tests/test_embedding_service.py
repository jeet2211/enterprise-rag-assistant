import numpy as np

from app.services.embedding_service import EmbeddingService


class FakeModel:
    def encode(self, texts, normalize_embeddings=True, convert_to_numpy=True):
        assert normalize_embeddings is True
        assert convert_to_numpy is True
        return np.array([[1.0, 2.0], [3.0, 4.0]])


def test_embedding_service_uses_loaded_model(monkeypatch):
    service = EmbeddingService()
    monkeypatch.setattr(service, "_load", lambda: FakeModel())

    embeddings = service.embed_texts(["alpha", "beta"])

    assert embeddings == [[1.0, 2.0], [3.0, 4.0]]
    assert service.embed_query("alpha") == [1.0, 2.0]


def test_embedding_service_ready_reflects_model_state():
    service = EmbeddingService()

    assert service.ready is False
    service._model = FakeModel()
    assert service.ready is True


def test_embedding_service_lazily_loads_model(monkeypatch):
    class ImportedModel:
        def __init__(self, model_name):
            self.model_name = model_name

    monkeypatch.setattr("app.services.embedding_service.SentenceTransformer", ImportedModel)

    service = EmbeddingService()
    model = service._load()

    assert isinstance(model, ImportedModel)
    assert model.model_name == "sentence-transformers/all-MiniLM-L6-v2"
    assert service.ready is True
