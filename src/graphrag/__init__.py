import os
from typing import List, Dict, Any
from lightrag import LightRAG, QueryParam
from faiss import IndexFlatL2
import json

import numpy as np 

class GraphRAGDB:
    def __init__(self, collection_name: str):
        self.collection_name = collection_name
        self.working_dir = f"./faiss/{collection_name}"
        self.index = IndexFlatL2(1536)  
        self.documents = []
        if not os.path.exists(self.working_dir):
            os.makedirs(self.working_dir, exist_ok = True)
        
    def insert(self, data: Dict[str, Any], embedding: List[float]):
        self.documents.append(data)
        self.index.add(np.array([embedding], dtype=np.float32))
        self._save()

    def insert_many(self, data_list: List[Dict[str, Any]], embeddings: List[List[float]]):
        self.documents.extend(data_list)
        self.index.add(np.array(embeddings, dtype=np.float32))
        self._save()

    def hybrid_search(self, query: str, embedding: List[float], limit: int = 50, alpha: float = None, 
                      metadata: bool = False, filters: dict = None, threshold: float = 0.0):
        self._load()
        D, I = self.index.search(np.array([embedding], dtype=np.float32), limit)
        results = []
        for i, (distance, idx) in enumerate(zip(D[0], I[0])):
            if distance < threshold:
                item = self.documents[idx].copy()
                item['score'] = 1 - distance if metadata else 1
                results.append(item)
        return results

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self._save()

    def _save(self):
        import faiss
        faiss.write_index(self.index, f"{self.working_dir}/index.faiss")
        with open(f"{self.working_dir}/documents.json", "w") as f:
            json.dump(self.documents, f)

    def _load(self):
        import faiss
        self.index = faiss.read_index(f"{self.working_dir}/index.faiss")
        with open(f"{self.working_dir}/documents.json", "r") as f:
            self.documents = json.load(f)