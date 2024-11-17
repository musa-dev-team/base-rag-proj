from typing import Dict, List, Union
from src.duckie_objects.threads.thread_obj import DuckieThread
from src.duckie_objects.docs.doc_obj import DuckieDoc
from src.ingestion.inserter import WeaviateInserter
from src.ingestion.preprocessor import DataPreprocessor
from src.ingestion.embedder import EmbeddingGenerator
from src.duckie_objects.ticketing.ticketing_obj import DuckieTicket
import sys 


class ExampleThreadIngestor:
    def __init__(self, thread_obj: DuckieThread):
        self.thread_obj = thread_obj

    def ingest(self):
        self.pre_process()
        self.generate_embeddings()
        self.insert_data()

    def pre_process(self):
        pass

    def generate_embeddings(self):
        pass

    def insert_data(self):
        pass


class ContentIngestor:
    def __init__(self, 
                 preprocessors: Dict[str, DataPreprocessor],
                 embedding_generator: EmbeddingGenerator,
                 collection_name: str):
        self.preprocessors = preprocessors
        self.embedding_generator = embedding_generator
        self.inserter = WeaviateInserter(collection_name)

    def ingest(self, content: Union[DuckieThread, DuckieDoc, DuckieTicket]):
        content_type = content.__class__.__name__.lower().replace("duckie", "")
        preprocessor = self.preprocessors[content_type]
        preprocessed_data = preprocessor.preprocess(content)
        embedding = self.embedding_generator.generate(preprocessed_data["content"])
        self.inserter.insert(preprocessed_data, embedding)

    def ingest_many(self, contents: List[Union[DuckieThread, DuckieDoc, DuckieTicket]]):
        preprocessed_data_list = []
        embeddings = []
        
        for content in contents:
            content_type = content.__class__.__name__.lower().replace("duckie", "")
            preprocessor = self.preprocessors[content_type]
            preprocessed_data = preprocessor.preprocess(content)
            embedding = self.embedding_generator.generate(preprocessed_data["content"])
            
            preprocessed_data_list.append(preprocessed_data)
            embeddings.append(embedding)
        
        self.inserter.insert_many(preprocessed_data_list, embeddings)