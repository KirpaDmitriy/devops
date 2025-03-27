from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import redis

model = SentenceTransformer('all-MiniLM-L6-v2')

app = FastAPI()

dim = 384
index = faiss.IndexFlatL2(dim)

redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)

class DocumentRequest(BaseModel):
    content: str

class SearchRequest(BaseModel):
    query: str
    top_k: int = 5

@app.post("/add_document/")
async def add_document(doc: DocumentRequest):
    embedding = model.encode(doc.content)
    index.add(np.array([embedding], dtype=np.float32))
    doc_id = index.ntotal - 1
    redis_client.set(f"document:{doc_id}", doc.content)
    return {"message": "Document added successfully", "id": doc_id}

@app.post("/search/")
async def search(search_request: SearchRequest):
    query_embedding = model.encode(search_request.query)
    top_k = search_request.top_k

    if index.ntotal == 0:
        raise HTTPException(status_code=404, detail="No documents in the database")

    distances, indices = index.search(np.array([query_embedding], dtype=np.float32), top_k)
    results = [{"content": redis_client.get(f"document:{i}"), "distance": float(distances[0][k])} for k, i in enumerate(indices[0])]

    return {"results": results}