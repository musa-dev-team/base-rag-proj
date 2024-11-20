from typing import Any, Dict, List, Union

import concurrent.futures
import yaml
from src.duckie_objects.docs.doc_obj import DuckieDoc
from src.duckie_objects.threads.thread_obj import DuckieThread
from src.duckie_objects.ticketing.ticketing_obj import DuckieTicket
from src.ingestion import ContentIngestor
from src.ingestion.inserter import WeaviateInserter
from src.ingestion.loader import ContentLoaderFactory
from src.ingestion.preprocessor import ThreadPreprocessor, DocPreprocessor, TicketPreprocessor
from src.ingestion.embedder import EmbeddingGenerator
from tqdm import tqdm

def load_config(config_path: str) -> Dict[str, Any]:
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def ingest_file(file_path: str, content_type: str, content_ingestor: ContentIngestor) -> int:
    
    def load_content_from_json(file_path: str, content_type: str) -> List[Union[DuckieThread, DuckieDoc, DuckieTicket]]:
        loader = ContentLoaderFactory.get_loader(content_type)
        return loader.load(file_path)
    
    content = load_content_from_json(file_path, content_type)
    content_ingestor.ingest_many(content)
    return len(content)

def main():
    config_path = 'config_ingestion.yaml'
    config = load_config(config_path)

    content_ingestor = ContentIngestor(
        preprocessors={
            "thread": ThreadPreprocessor(),
            "doc": DocPreprocessor(),
            "ticket": TicketPreprocessor()
        },
        embedding_generator=EmbeddingGenerator(),
        db_inserter=WeaviateInserter,
        collection_name=config.get('collection_name', 'test_collection'),
        batch_size=config.get('batch_size', 100)
    )
    
    total_documents = 0
    print(f"Starting parallel ingestion of documents...")
    with concurrent.futures.ThreadPoolExecutor(max_workers=config.get('max_workers', 4)) as executor:
        futures = []
        for config_type, fileDict in config.items():
            if isinstance(fileDict, dict):  # Skip non-list items like batch_size
                for content_type, file_list in fileDict.items():
                    for file_path in file_list:
                        futures.append(executor.submit(ingest_file, file_path, content_type, content_ingestor))
            
        for future in tqdm(concurrent.futures.as_completed(futures), 
                           total=len(futures), 
                           desc="Ingesting files"):
            try:
                num_documents = future.result()
                total_documents += num_documents
            except Exception as e:
                print(f"Error ingesting file: {str(e)}")
    print(f"Total documents ingested: {total_documents}")
    print("Content ingestion complete.")

if __name__ == "__main__":
    main()

