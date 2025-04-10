import pytest
from fastapi.testclient import TestClient
from main import app
from db import documents

client = TestClient(app)

@pytest.fixture(autouse=True)
def run_around_tests():
    documents.clear()
    yield
    documents.clear()

def test_add_document():
    response = client.post("/add/", json={"id": "1", "content": "Test content"})
    assert response.status_code == 200
    assert response.json() == {"message": "Document added successfully"}

    assert "1" in documents

def test_add_duplicate_document():
    client.post("/add/", json={"id": "1", "content": "Test content"})
    response = client.post("/add/", json={"id": "1", "content": "Another content"})
    assert response.status_code == 400
    assert response.json() == {"detail": "Document ID already exists."}

def test_delete_document():
    client.post("/add/", json={"id": "1", "content": "Test content"})
    response = client.delete("/delete/1")
    assert response.status_code == 200
    assert response.json() == {"message": "Document deleted successfully"}

    assert "1" not in documents

def test_delete_nonexistent_document():
    response = client.delete("/delete/1")
    assert response.status_code == 404
    assert response.json() == {"detail": "Document not found"}

def test_update_document():
    client.post("/add/", json={"id": "1", "content": "Test content"})
    response = client.put("/update/", json={"id": "1", "content": "Updated content"})
    assert response.status_code == 200
    assert response.json() == {"message": "Document updated successfully"}

    assert "1" in documents
    assert documents["1"] == "Updated content"

def test_update_nonexistent_document():
    response = client.put("/update/", json={"id": "1", "content": "Updated content"})
    assert response.status_code == 404
    assert response.json() == {"detail": "Document not found"}

def test_query_document():
    client.post("/add/", json={"id": "1", "content": "Test content"})
    response = client.get("/query/?query=Test content")
    assert response.status_code == 200

    # Проверка, что возвращается результат
    results = response.json().get("results", [])
    assert len(results) > 0
