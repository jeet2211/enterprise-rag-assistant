from app.rag.retriever import Retriever


class FakeCollection:
    def __init__(self):
        self.upsert_calls = []
        self.query_calls = []
        self.delete_calls = []
        self.count_calls = 0

    def upsert(self, **kwargs):
        self.upsert_calls.append(kwargs)

    def query(self, **kwargs):
        self.query_calls.append(kwargs)
        return {
            "documents": [["Alpha", "Beta"]],
            "metadatas": [[{"page_number": 1}, {"page_number": 2}]],
            "distances": [[0.12, 0.34]],
        }

    def delete(self, **kwargs):
        self.delete_calls.append(kwargs)

    def count(self):
        self.count_calls += 1
        return 2


class FakeClient:
    def __init__(self, path: str):
        self.path = path
        self.collection = FakeCollection()

    def get_or_create_collection(self, name: str, metadata: dict[str, object]):
        self.name = name
        self.metadata = metadata
        return self.collection


class FakeEmbeddingService:
    def embed_texts(self, texts):
        return [[float(index + 1)] for index, _ in enumerate(texts)]

    def embed_query(self, text: str):
        return [0.5]


def test_retriever_add_search_delete_and_healthcheck(monkeypatch, tmp_path):
    fake_client = FakeClient(str(tmp_path))
    monkeypatch.setattr("app.rag.retriever.chromadb.PersistentClient", lambda path: fake_client)

    retriever = Retriever(str(tmp_path), FakeEmbeddingService())
    retriever.add_chunks(
        document_id="doc-1",
        filename="report.pdf",
        chunks=[
            {"text": "Alpha chunk", "page_number": 1, "chunk_index": 0},
            {"text": "Beta chunk", "page_number": 2, "chunk_index": 1},
        ],
    )

    assert fake_client.collection.upsert_calls
    upsert = fake_client.collection.upsert_calls[0]
    assert upsert["ids"] == ["doc-1:1:0", "doc-1:2:1"]
    assert upsert["documents"] == ["Alpha chunk", "Beta chunk"]

    matches = retriever.search("Find alpha", top_k=2, document_ids=["doc-1"])
    assert len(matches) == 2
    assert fake_client.collection.query_calls[0]["where"] == {"doc_id": {"$in": ["doc-1"]}}

    retriever.delete_document("doc-1")
    assert fake_client.collection.delete_calls[0] == {"where": {"doc_id": "doc-1"}}

    assert retriever.healthcheck() is True
    assert fake_client.collection.count_calls == 1


def test_retriever_handles_empty_chunks_and_blank_queries(monkeypatch, tmp_path):
    fake_client = FakeClient(str(tmp_path))
    monkeypatch.setattr("app.rag.retriever.chromadb.PersistentClient", lambda path: fake_client)

    retriever = Retriever(str(tmp_path), FakeEmbeddingService())
    retriever.add_chunks(document_id="doc-2", filename="empty.pdf", chunks=[])

    assert fake_client.collection.upsert_calls == []
    assert retriever.search("   ") == []
