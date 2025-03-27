from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from fastapi.responses import HTMLResponse
from typing import List
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="templates")

model = SentenceTransformer('all-MiniLM-L6-v2')

app = FastAPI()

dim = 384
index = faiss.IndexFlatL2(dim)

documents = []

class DocumentRequest(BaseModel):
    content: str

class SearchRequest(BaseModel):
    query: str
    top_k: int = 5

@app.post("/add_document/")
async def add_document(doc: DocumentRequest):
    embedding = model.encode(doc.content)
    index.add(np.array([embedding], dtype=np.float32))
    documents.append(doc.content)
    return {"message": "Document added successfully", "id": len(documents) - 1}

@app.post("/search/")
async def search(search_request: SearchRequest):
    query_embedding = model.encode(search_request.query)
    top_k = search_request.top_k

    if index.ntotal == 0:
        raise HTTPException(status_code=404, detail="No documents in the database")

    distances, indices = index.search(np.array([query_embedding], dtype=np.float32), top_k)
    results = [{"content": documents[i], "distance": float(distances[0][k])} for k, i in enumerate(indices[0])]

    return {"results": results}

@app.get("/page", response_class=HTMLResponse)
async def page(request: Request, id: str):
    return templates.TemplateResponse(request=request, name="index.html")