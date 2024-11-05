from src.weaviate_db import WeaviateDB

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
