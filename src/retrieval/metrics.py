import numpy as np
from typing import List

class RetrievalMetrics:
    def __init__(self):
        pass
    
    @staticmethod
    def mean_reciprocal_rank(results) -> float:
        """Calculate Mean Reciprocal Rank (MRR)"""
        reciprocal_ranks = []
        for result in results:
            try:
                rank = result.index(True) + 1
                reciprocal_ranks.append(1 / rank)
            except ValueError:
                reciprocal_ranks.append(0)
        return np.mean(reciprocal_ranks)

    @staticmethod
    def precision_at_k(results, k: int) -> float:
        """Calculate Precision@k"""
        precisions = []
        for result in results:
            relevant = sum(result[:k])
            precisions.append(relevant / k)
        return np.mean(precisions)

    @staticmethod
    def success_at_k(results, k: int) -> float:
        """Calculate Success@k"""
        successes = []
        for result in results:
            successes.append(1 if True in result[:k] else 0)
        return np.mean(successes)

    @classmethod
    def calculate_metrics(cls, results: List[List[bool]], k_values: List[int] = [1, 3, 5, 10]) -> dict:
        """Calculate all metrics"""
        metrics = {
            "MRR": cls.mean_reciprocal_rank(results),
        }
        for k in k_values:
            metrics[f"Precision@{k}"] = cls.precision_at_k(results,k)
            metrics[f"Success@{k}"] = cls.success_at_k(results, k)
        return metrics