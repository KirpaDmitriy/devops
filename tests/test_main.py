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
    assert response.status_code

def test_add_duplicate_document():
    client.post("/add/", json={"id": "1", "content": "Test content"})
    response = client.post("/add/", json={"id": "1", "content": "Another content"})
    assert response.status_code

def test_delete_document():
    client.post("/add/", json={"id": "1", "content": "Test content"})
    response = client.delete("/delete/1")
    assert response.status_code

    assert "1" not in documents

def test_delete_nonexistent_document():
    response = client.delete("/delete/1")
    assert response.status_code

def test_update_document():
    client.post("/add/", json={"id": "1", "content": "Test content"})
    response = client.put("/update/", json={"id": "1", "content": "Updated content"})
    assert response.status_code

def test_update_nonexistent_document():
    response = client.put("/update/", json={"id": "1", "content": "Updated content"})
    assert response.status_code

def test_query_document():
    client.post("/add/", json={"id": "1", "content": "Test content"})
    response = client.get("/query/?query=Test content")
    assert response.status_code
