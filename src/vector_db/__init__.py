import chromadb
from chromadb.utils import embedding_functions as ef

class VectorDbObject:
    def __init__(self, id: str, data: dict, metadata: dict):
        self.id = id
        self.data = data
        self.metadata = metadata

class VectorDB:
    def __init__(self, collection_name: str):
        self.client = chromadb.Client()
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            embedding_function=ef.DefaultEmbeddingFunction()
        )

    def add_data(self, data: list[VectorDbObject]):
        self.collection.add(
            ids=[obj.id for obj in data],
            documents=[obj.data for obj in data],
            metadatas=[obj.metadata for obj in data]
        )

    def query(self, query: str):
        return self.collection.query(query_texts=query)
    
    def add_documents(self, documents: list[str], metadatas: list[dict] = None, ids: list[str] = None):
        return self.collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
    
    def query_by_text(self, query_text: str, n_results: int = 10, where: dict = None):
        return self.collection.query(
            query_texts=[query_text],
            n_results=n_results,
            where=where
        )
    
    def delete(self, ids: list[str] = None, where: dict = None):
        return self.collection.delete(
            ids=ids,
            where=where
        )
    
    def update(self, ids: list[str], documents: list[str] = None, metadatas: list[dict] = None):
        return self.collection.update(
            ids=ids,
            documents=documents,
            metadatas=metadatas
        )
    
    def get(self, ids: list[str] = None, where: dict = None, limit: int = None):
        return self.collection.get(
            ids=ids,
            where=where,
            limit=limit
        )
    
    def count(self):
        return self.collection.count()
    
    def reset(self):
        self.collection.delete()

if __name__ == "__main__":
    db = VectorDB("test")
    db.add_data([VectorDbObject(id="1", data="Hello, world!", metadata={"source": "test"})])
    print(db.query("Hello, world!"))