from typing import Dict, List, Union
from src.duckie_objects.threads.thread_obj import DuckieThread
from src.duckie_objects.docs.doc_obj import DuckieDoc
from src.ingestion.inserter import WeaviateInserter
from src.ingestion.preprocessor import DataPreprocessor
from src.ingestion.embedder import EmbeddingGenerator
from src.duckie_objects.ticketing.ticketing_obj import DuckieTicket
from tqdm import tqdm
import multiprocessing
import concurrent.futures


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
                 collection_name: str,
                 batch_size: int = 10,
                 max_workers: int = 0):
        self.preprocessors = preprocessors
        self.embedding_generator = embedding_generator
        self.inserter = WeaviateInserter(collection_name)
        self.batch_size = batch_size
        self.max_workers = max_workers or multiprocessing.cpu_count() - 1

    def ingest(self, content: Union[DuckieThread, DuckieDoc, DuckieTicket]):
        content_type = content.__class__.__name__.lower().replace("duckie", "")
        preprocessor = self.preprocessors[content_type]
        preprocessed_data = preprocessor.preprocess(content)
        embedding = self.embedding_generator.generate(preprocessed_data["content"])
        self.inserter.insert(preprocessed_data, embedding)

    def preprocess_and_embed(self, content: Union[DuckieThread, DuckieDoc, DuckieTicket]):
        content_type = content.__class__.__name__.lower().replace("duckie", "")
        preprocessor = self.preprocessors[content_type]
        preprocessed_data = preprocessor.preprocess(content)
        embedding = self.embedding_generator.generate(preprocessed_data["content"])
        return preprocessed_data, embedding

    def ingest_batch(self, batch: List[Union[DuckieThread, DuckieDoc, DuckieTicket]]):
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            results = list(executor.map(self.preprocess_and_embed, batch)) 
        preprocessed_data_list, embeddings = zip(*results)
        self.inserter.insert_many(list(preprocessed_data_list), list(embeddings))
        
    def ingest_many(self, contents: List[Union[DuckieThread, DuckieDoc, DuckieTicket]]):
        batches = [contents[i:i + self.batch_size] for i in range(0, len(contents), self.batch_size)]

        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = [executor.submit(self.ingest_batch, batch) for batch in batches]
        
            for _ in tqdm(concurrent.futures.as_completed(futures), total=len(futures), desc="Ingesting batches"):
                    pass