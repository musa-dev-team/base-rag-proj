from typing import List
from src.llm.embedding_helper import generate_embedding

class EmbeddingGenerator:
    def __init__(self, model_name = 'text-embedding-3-small'):
        self.model_name = model_name

    def generate(self, text: str) -> List[float]:
        return generate_embedding(text, self.model_name)