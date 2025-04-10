from fastapi import FastAPI, HTTPException
from models import Document
from db import add_document, delete_document, update_document
from utils import get_embedding
from search import search

app = FastAPI()

@app.post("/add/")
async def add_document_endpoint(document: Document):
    embedding = get_embedding(document.content)
    try:
        add_document(document.id, embedding, document.content)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"message": "Document added successfully"}

@app.delete("/delete/{doc_id}")
async def delete_document_endpoint(doc_id: str):
    try:
        delete_document(doc_id)
        return {"message": "Document deleted successfully"}
    except KeyError:
        raise HTTPException(status_code=404, detail="Document not found")

@app.put("/update/")
async def update_document_endpoint(document: Document):
    embedding = get_embedding(document.content)
    try:
        update_document(document.id, embedding, document.content)
        return {"message": "Document updated successfully"}
    except KeyError:
        raise HTTPException(status_code=404, detail="Document not found")

@app.get("/query/")
async def query_document(query: str):
    embedding = get_embedding(query)
    results = search(embedding)

    return {"results": results}
