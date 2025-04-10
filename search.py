import numpy as np
from db import index, documents

def search(query_embedding: np.ndarray, k: int = 5):
    distances, indices = index.search(query_embedding, k)
    if not documents or not indices:
        return []
    results = [(documents[i], distances[idx]) for idx, i in enumerate(indices[0])]
    return results
