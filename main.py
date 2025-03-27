from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')

class Document(BaseModel):
    id: int
    content: str

app = FastAPI()

document_store: Dict[int, Document] = {}
document_vectors: Dict[int, np.ndarray] = {}

vector_dim = model.get_sentence_embedding_dimension()

index = faiss.IndexFlatL2(vector_dim)

def text_to_vector(text: str) -> np.ndarray:
    vector = model.encode(text, convert_to_tensor=False)
    return np.array(vector).astype('float32')

@app.post("/add_document", response_model=Document)
async def add_document(document: Document):
    if document.id in document_store:
        raise HTTPException(status_code=400, detail="Document already exists")
    
    doc_vector = text_to_vector(document.content)
    
    document_store[document.id] = document
    document_vectors[document.id] = doc_vector
    
    index.add(np.array([doc_vector]))
    
    return document

@app.delete("/delete_document/{doc_id}", response_model=Dict[str, Any])
async def delete_document(doc_id: int):
    if doc_id not in document_store:
        raise HTTPException(status_code=404, detail="Document not found")
    
    del document_store[doc_id]
    del document_vectors[doc_id]
    
    reindex_faiss()
    
    return {"message": "Document deleted successfully", "doc_id": doc_id}

@app.put("/update_document/{doc_id}", response_model=Document)
async def update_document(doc_id: int, new_data: Document):
    if doc_id not in document_store:
        raise HTTPException(status_code=404, detail="Document not found")
    
    existing_doc = document_store[doc_id]
    updated_doc = existing_doc.copy(update=new_data.dict(exclude_unset=True))
    updated_vector = text_to_vector(updated_doc.content)
    
    document_store[doc_id] = updated_doc
    document_vectors[doc_id] = updated_vector
    
    reindex_faiss()
    
    return updated_doc

@app.get("/search/", response_model=List[int])
async def search(query: str, k: int = 5):
    query_vector = text_to_vector(query)
    dist, indices = index.search(np.array([query_vector]), k)
    
    result_ids = [list(document_vectors.keys())[i] for i in indices[0] if i < len(document_vectors)]
    
    return result_ids

def reindex_faiss():
    """Переиндексация FAISS после удаления/обновления."""
    index.reset()
    vectors = np.array(list(document_vectors.values()))
    if len(vectors) > 0:
        index.add(vectors)
