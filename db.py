import faiss
import numpy as np
from utils import get_embedding

dimension = 384
index = faiss.IndexFlatL2(dimension)

documents = {}

documents = {}
current_idx = 0

def add_document(doc_id, embedding: np.ndarray, content: str):
    if doc_id in documents:
        raise ValueError("Document ID already exists.")
    global current_idx
    index.add(np.array([embedding]))
    documents[current_idx] = content
    current_idx += 1

def delete_document(doc_id: str):
    if doc_id not in documents:
        raise KeyError("Document not found.")

    content = documents[doc_id]
    embedding = get_embedding(content)

    del documents[doc_id]

    all_embeddings = [get_embedding(documents[doc]) for doc in documents]
    new_index = faiss.IndexFlatL2(dimension)
    if all_embeddings:
        new_index.add(np.vstack(all_embeddings))

    global index
    index = new_index

def update_document(doc_id: str, embedding: np.ndarray, content: str):
    delete_document(doc_id)
    add_document(doc_id, embedding, content)
