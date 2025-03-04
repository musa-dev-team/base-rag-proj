from src.vector_db import VectorDB


class Retriever:
    def __init__(
        self,
        collection_name: str
    ):
        self.db_class = VectorDB(collection_name)

    def run(self, query: str) -> list:
        return self.db_class.query(query)
