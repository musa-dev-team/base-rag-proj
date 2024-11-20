import logging
from typing import List, Union
from src.duckie_objects.docs.doc_obj import DuckieDoc
from src.duckie_objects.threads.thread_obj import DuckieThread
from src.duckie_objects.ticketing.ticketing_obj import DuckieTicket
from src.ingestion.loader import ContentLoaderFactory
from src.schema_extraction import schema_extraction_from_text


def main():
    def load_content_from_json(file_path: str, content_type: str) -> List[Union[DuckieThread, DuckieDoc, DuckieTicket]]:
        loader = ContentLoaderFactory.get_loader(content_type)
        return loader.load(file_path)

    logging.getLogger().setLevel(logging.ERROR)

    content = load_content_from_json('data/raw/forums/technical_support_thread_messages.json', "thread")
    content = content[0]
    
    schema = schema_extraction_from_text(model='gpt-4o-mini',input_text=content.format_thread())
    print(schema)

if __name__ == "__main__":
    main()