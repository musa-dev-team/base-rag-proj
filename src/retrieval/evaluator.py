import sys
from src.retrieval import BaseRetriever
from typing import Any, List, Dict
import json
import numpy as np
from tqdm import tqdm
from src.retrieval.metrics import RetrievalMetrics 


class RetrieverEvaluator:
    def __init__(self, retriever: BaseRetriever, metrics: RetrievalMetrics, qa_data_path: str):
        self.retriever = retriever
        self.qa_data = self._load_qa_data(qa_data_path)
        self.metrics = metrics

    @staticmethod
    def _load_qa_data(file_path: str) -> List[Dict[str, str]]:
        with open(file_path, 'r') as f:
            return json.load(f)

    def evaluate(self, k:int = 10) -> Dict[str, float]:
        retrieval_lists = []
        for qa_item in tqdm(self.qa_data):
            query = qa_item['question']
            expected_source = qa_item['source']
            try:
                results = self.retriever.retrieve(query)
                relevant_docs = self._get_relevant_docs(results, expected_source)
                retrieval_lists.append(relevant_docs)
            except:
                pass
        retrieval_metrics = self.metrics.calculate_metrics(retrieval_lists)
            
        return {
            **{k: v for k, v in retrieval_metrics.items()}
        }
    
    def _get_relevant_docs(self, results: List[Dict[str, Any]], expected_source: str) -> List[bool]:
        rel = []
        for result in results:
            try:
                assert expected_source != result['source']
                rel.append(False)
            except:
                rel.append(True)
                break
        return rel