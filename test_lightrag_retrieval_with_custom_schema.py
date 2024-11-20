import os
import sys
from typing import Any, Dict, List, Union
import yaml
from lightrag import LightRAG, QueryParam
from lightrag.llm import gpt_4o_mini_complete, gpt_4o_complete
from src.duckie_objects.docs.doc_obj import DuckieDoc
from src.duckie_objects.threads.thread_obj import DuckieThread
from src.duckie_objects.ticketing.ticketing_obj import DuckieTicket
from src.ingestion.loader import ContentLoaderFactory
from lightrag.prompt import PROMPTS
from tqdm import tqdm 
import concurrent.futures
import time
import logging

from src.schema_extraction import schema_extraction_from_text

def load_config(config_path: str) -> Dict[str, Any]:
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

WORKING_DIR = "./ragIndex"
file_path = 'data/raw/docs/handbook.json'

config_path = 'config_graph.yaml'
config = load_config(config_path)

content_type = 'doc'

if not os.path.exists(WORKING_DIR):
    os.mkdir(WORKING_DIR)



def load_content_from_json(file_path: str, content_type: str) -> List[Union[DuckieThread, DuckieDoc, DuckieTicket]]:
        loader = ContentLoaderFactory.get_loader(content_type)
        return loader.load(file_path)

content = load_content_from_json('data/raw/docs/handbook.json', content_type)


rag = LightRAG(
    working_dir=WORKING_DIR,
    llm_model_func=gpt_4o_mini_complete  # Use gpt_4o_mini_complete LLM model
    # llm_model_func=gpt_4o_complete  # Optionally, use a stronger model
)

def insert(rag: LightRAG, content: Union[DuckieDoc, DuckieThread, DuckieTicket]):
    schema = schema_extraction_from_text(model='gpt-4o-mini',input_text=content.format_doc())
    PROMPTS["DEFAULT_ENTITY_TYPES"] = schema.labels
    rag.insert(content.format_doc())


logging.getLogger().setLevel(logging.ERROR)


def insert_wrapper(args):
    sample, rag = args
    insert(rag, sample)

def parallel_insert(content, rag, max_workers=None):
    total_samples = len(content)
    start_time = time.time()
    completed = 0

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        with tqdm(total=total_samples, desc="Processing", unit="sample") as pbar:
            futures = [executor.submit(insert_wrapper, (sample, rag)) for sample in content]

            # Process completed futures
            for future in concurrent.futures.as_completed(futures):
                future.result()  # This will raise any exceptions that occurred during execution
                completed += 1
                pbar.update(1)

                # Estimate time remaining
                elapsed_time = time.time() - start_time
                avg_time_per_sample = elapsed_time / completed
                estimated_time_remaining = avg_time_per_sample * (total_samples - completed)

                pbar.set_postfix({"Est. Time Remaining": f"{estimated_time_remaining:.2f}s"})

    total_time = time.time() - start_time
    print(f"\nTotal execution time: {total_time:.2f} seconds")

parallel_insert(content, rag, max_workers=4)




