from typing import List, Union
from src.duckie_objects.docs.doc_obj import DuckieDoc
from src.duckie_objects.threads.thread_obj import DuckieThread
from src.duckie_objects.ticketing.ticketing_obj import DuckieTicket
from src.ingestion import ContentIngestor
from src.ingestion.loader import ContentLoaderFactory
from src.ingestion.preprocessor import ThreadPreprocessor, DocPreprocessor, TicketPreprocessor
from src.ingestion.embedder import EmbeddingGenerator


def ingest_batch(batch, ingestor: ContentIngestor):
    for item in batch:
        ingestor.ingest(item)

def main():

    content_ingestor = ContentIngestor(
        preprocessors={
            "thread": ThreadPreprocessor(),
            "doc": DocPreprocessor(),
            "ticket": TicketPreprocessor()
        },
        embedding_generator=EmbeddingGenerator(),
        collection_name="test_collection"
    )

    def load_content_from_json(file_path: str, content_type: str) -> List[Union[DuckieThread, DuckieDoc, DuckieTicket]]:
        loader = ContentLoaderFactory.get_loader(content_type)
        return loader.load(file_path)

    content = load_content_from_json('data/raw/forums/technical_support_thread_messages.json', "thread")
    content = content[0:1]
    print(f"Starting parallel ingestion of {len(content)} documents...")
    ingest_batch(content, content_ingestor)
    print("Content ingestion complete.")

if __name__ == "__main__":
    main()

