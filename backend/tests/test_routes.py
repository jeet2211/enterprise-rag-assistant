import uuid

def test_root_endpoint(client):
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "version" in data

def test_health_endpoint(client):
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "chromadb" in data
    assert "gemini" in data

def test_documents_list_empty(client):
    response = client.get("/api/v1/documents")
    assert response.status_code == 200
    assert response.json() == []

def test_feedback_endpoint(client):
    feedback_payload = {
        "message_id": str(uuid.uuid4()),
        "session_id": str(uuid.uuid4()),
        "rating": "good",
        "reason": "Very accurate answer, thank you!"
    }
    response = client.post("/api/v1/feedback", json=feedback_payload)
    assert response.status_code == 201
    data = response.json()
    assert "feedback_id" in data
    assert data["message"] == "Feedback recorded. Thank you!"
