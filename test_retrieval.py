from src.retrieval import RetrieverFactory
from src.retrieval.evaluator import RetrieverEvaluator
from src.retrieval.metrics import RetrievalMetrics


def main():
    retriever = RetrieverFactory.get_retriever("weaviate", collection_name="test_collection")
    metrics = RetrievalMetrics()
    evaluator = RetrieverEvaluator(retriever, metrics,  "data/synthetic_qa/docs/handbook_qa.json")
    
    k = 10
    results = evaluator.evaluate(k=k)
    
    for k, v in results.items():
        print(f"{k}: {v:.4f}")
if __name__ == "__main__":
    main()