from abc import ABC, abstractmethod
from typing import Dict, Any, List 
from src.weaviate_db import WeaviateDB
from contextlib import contextmanager
import sys 


class DatabaseInserter(ABC):
    @abstractmethod
    def insert(self, data: Dict[str, Any], embedding: List[float]):
        pass

class WeaviateInserter(DatabaseInserter):
    def __init__(self, collection_name: str):
        self.collection_name = collection_name

    @contextmanager
    def _get_vdb(self):
        with WeaviateDB(self.collection_name) as vdb:
            yield vdb

    def insert(self, data: Dict[str, Any], embedding: List[float]):
        weaviate_object = self._to_weaviate_object(data, embedding)
        with self._get_vdb() as vdb:
            vdb.insert_many([weaviate_object])


    def insert_many(self, data_list: List[Dict[str, Any]], embeddings: List[List[float]]):
        weaviate_objects = [
            self._to_weaviate_object(data, embedding)
            for data, embedding in zip(data_list, embeddings)
        ]
        with self._get_vdb() as vdb:
            vdb.insert_many(weaviate_objects)


    def _to_weaviate_object(self, data: Dict[str, Any], embedding: List[float]) -> Dict[str, Any]:
        weaviateDict =  {
            "metadata": {
                "timestamp": data.get("timestamp"),
                "ingest_type": data.get("type"),
                **{k: v for k, v in data.items() if k not in ["id", "object_id", "timestamp", "type", "raw"]},
                "raw": data.get("raw", str(data))
            },
            "vec": embedding,
            "id": data.get("object_id") or data.get("id")
        }

        weaviate_object = None 
        with self._get_vdb() as vdb:
            weaviate_object = vdb._to_data(weaviateDict)
        
        return weaviate_object


    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.vdb.__exit__(exc_type, exc_value, traceback)