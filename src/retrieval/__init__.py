from contextlib import contextmanager
import re
from lightrag.base import QueryParam
from lightrag.lightrag import LightRAG
from src.graphrag import GraphRAGDB
from src.ingestion.embedder import EmbeddingGenerator
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
        elif retriever_type.lower() == "graphrag":
            return GraphRAGRetriever(**kwargs)
        elif retriever_type.lower() == "lightrag":
            return LightRAGRetriever(**kwargs)
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

class LightRAGRetriever(BaseRetriever):
    def __init__(self, working_dir: str, top_k: int = 60):
        self.rag = LightRAG(working_dir=working_dir)
        self.top_k = top_k

    def retrieve(self, query: str) -> List[Dict[str, Any]]:
        response = self.rag.query(
            query,
            param=QueryParam(
                only_need_context=True,
                mode="hybrid",
                top_k=self.top_k
            )
        )
        
        urls = self.extract_urls(response)
        
        return [
            { 
                "content": response,
                "source": url
            }
            for url in urls
        ]

    @staticmethod
    def extract_urls(text: str) -> set:
        url_pattern = r'URL:https?://(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&//=]*)'
        urls = re.findall(url_pattern, text)
        urls = [url[4:] for url in urls]
        return set(urls)

class GraphRAGRetriever(BaseRetriever):
    def __init__(self, collection_name: str, embedding_generator:EmbeddingGenerator, limit: int = 50, threshold: float = 0.5):
        self.collection_name = collection_name
        self.embedding_generator = embedding_generator
        self.limit = limit
        self.threshold = threshold
        self.db = GraphRAGDB(collection_name)

    @contextmanager
    def _get_db(self):
        try:
            yield self.db
        finally:
            self.db._save()

    def retrieve(self, query: str) -> List[Dict[str, Any]]:
        query_embedding = self.embedding_generator.generate(query)
        results = self._search(query, query_embedding)
        return self._process_results(results)

    def _search(self, query: str, query_embedding: List[float]) -> List[Dict[str, Any]]:
        with self._get_db() as db:
            return db.hybrid_search(
                query=query,
                embedding=query_embedding,
                limit=self.limit,
                metadata=True,
                threshold=self.threshold
            )

    def _process_results(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return [
            {
                "content": result.get("content", ""),
                "source": result.get("url", ""),
                "score": result.get("score", 0)
            }
            for result in results
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
