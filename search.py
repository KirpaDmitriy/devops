import numpy as np
from db import index, documents

def search(query_embedding: np.ndarray, k: int = 5):
    distances, indices = index.search(query_embedding, k)
    if not documents or not indices.any():
        return []
    print(f'Documentici {documents}')
    print(f'distances {documents, indices}')
    results = [(documents[i], distances[0, idx]) for idx, i in enumerate(indices[0]) if i in documents]
    return results
