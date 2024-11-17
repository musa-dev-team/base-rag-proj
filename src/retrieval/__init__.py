from contextlib import contextmanager
from src.weaviate_db import WeaviateDB
from abc import ABC, abstractmethod
from typing import List, Dict, Any

class BaseRetriever(ABC):
    @abstractmethod
    def retrieve(self, query: str) -> List[Dict[str, Any]]:
        pass

class RetrieverFactory:
    @staticmethod
    def get_retriever(retriever_type: str, **kwargs) -> BaseRetriever:
        if retriever_type.lower() == "weaviate":
            return WeaviateRetriever(**kwargs)
        else:
            raise ValueError(f"Unsupported retriever type: {retriever_type}")
        
class WeaviateRetriever(BaseRetriever):
    def __init__(self, collection_name: str, alpha: float = 0.5, limit: int = 5, threshold: float = 0.5):
        self.alpha = alpha
        self.limit = limit
        self.threshold = threshold
        self.collection_name = collection_name

    @contextmanager
    def _get_vdb(self):
        with WeaviateDB(self.collection_name) as vdb:
            yield vdb

    def retrieve(self, query: str) -> List[Dict[str, Any]]:
        embeddings = self._hybrid_search(query)
        return self._process_embeddings(embeddings)

    def _hybrid_search(self, query: str) -> List[Dict[str, Any]]:
        with self._get_vdb() as vdb:
            return vdb.hybrid_search(
                query=query,
                limit=self.limit,
                alpha=self.alpha,
                metadata=True,
                threshold=self.threshold,
                filters=None
            )

    def _process_embeddings(self, embeddings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return [
            {
                "content": embedding.get("content", ""),
                "source": embedding.get("url", ""),
                "score": embedding.get("score", 0)
            }
            for embedding in embeddings
        ]



class Retriever:
    def __init__(
        self,
    ):
        self.db_class = WeaviateDB

    def run(self, query: str, alpha: str = 0.5, limit=5, threshold=0.5) -> list:
        collection_name = ""
        embeddings = self.hybrid_search(query, collection_name, alpha, limit, threshold)
        matches = self.get_matches_from_embeddings(embeddings)
        return matches
    
    def hybrid_search(self, query: str, collection_name: str, alpha: str = 0.5, limit=5, threshold=0.5) -> list:
        filters = None

        with self.vector_db(
            collection_name=collection_name,
        ) as vdb:
            embeddings = vdb.hybrid_search(
                query=query,
                limit=limit,
                alpha=alpha,
                metadata=True,
                threshold=threshold,
                filters=filters,
            )
        
        return embeddings
    
    def get_matches_from_embeddings(self, embeddings: list) -> list:
        return embeddings
