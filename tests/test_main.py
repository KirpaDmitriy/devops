import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_add_document():
    response = client.post("/add_document/", json={"id": "https://itmo.ru", "content": "Hello, this is a test document!"})
    assert response.status_code == 201
    data = response.json()
    assert data["message"] == "Document added successfully"
    assert "id" in data

def test_search():
    client.post("/add_document/", json={"id": "https://neitmo.ru", "content": "FastAPI or Django... That is the question!"})
  
    response = client.get("/search/", params={"query": "test document", "top_k": 1})
    assert response.status_code == 200
    data = response.json()
    
    assert "results" in data
    assert len(data["results"]) > 0
    assert "content" in data["results"][0]
    assert data["results"][0]["content"] == "Hello, this is a test document!"
