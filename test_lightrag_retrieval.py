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
import logging
import tracemalloc

from src.retrieval import RetrieverFactory
from src.retrieval.evaluator import RetrieverEvaluator
from src.retrieval.metrics import RetrievalMetrics


def main():
    WORKING_DIR = "./ragIndex"
    file_path = 'data/synthetic_qa/docs/handbook_qa.json'
    retriever = RetrieverFactory.get_retriever("lightrag", working_dir=WORKING_DIR)
    metrics = RetrievalMetrics()
    evaluator = RetrieverEvaluator(retriever, metrics,  file_path)
    
    k = 10
    results = evaluator.evaluate(k=k)
    
    for k, v in results.items():
        print(f"{k}: {v:.4f}")
if __name__ == "__main__":
    main()