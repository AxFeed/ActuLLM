# ollama_call.py
import os
from pathlib import Path

def embed(texts: list[str]) -> list[list[float]]:
    vectors = []
    for text in texts:
        resp = client.embeddings(model=os.getenv("EMBEDDING_MODEL"), prompt=text)
        vectors.append(resp["embedding"])
    return vectors
