from typing import List, Union
from src.duckie_objects.docs.doc_obj import DuckieDoc
from src.duckie_objects.threads.thread_obj import DuckieThread
from src.duckie_objects.ticketing.ticketing_obj import DuckieTicket
from src.ingestion import ContentIngestor
from src.ingestion.inserter import LightRAGInserter
from src.ingestion.loader import ContentLoaderFactory
from src.ingestion.preprocessor import ThreadPreprocessor, DocPreprocessor, TicketPreprocessor
from src.ingestion.embedder import EmbeddingGenerator



def main():

    content_ingestor = ContentIngestor(
        preprocessors={
            "thread": ThreadPreprocessor(),
            "doc": DocPreprocessor(),
            "ticket": TicketPreprocessor()
        },
        embedding_generator=EmbeddingGenerator(),
        db_inserter = LightRAGInserter,
        collection_name="test_collection",
        batch_size=32
    )

    def load_content_from_json(file_path: str, content_type: str) -> List[Union[DuckieThread, DuckieDoc, DuckieTicket]]:
        loader = ContentLoaderFactory.get_loader(content_type)
        return loader.load(file_path)

    content = load_content_from_json('data/raw/forums/technical_support_thread_messages.json', "thread")
    print(f"Starting parallel ingestion of {len(content)} documents...")
    content_ingestor.ingest_many(content)
    print("Content ingestion complete.")

if __name__ == "__main__":
    main()

