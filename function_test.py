from src.ingestion.embedder import EmbeddingGenerator


def test_embedding_size(text):
    embedder = EmbeddingGenerator()
    embs = embedder.generate(text)
    return len(embs)


ln = test_embedding_size("Hello World")
print(ln)