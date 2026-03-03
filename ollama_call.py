# ollama_call.py
import ollama
import os
from dotenv import load_dotenv
from pathlib import Path

def embed(texts: list[str]) -> list[list[float]]:
    vectors = []
    for text in texts:
        resp = client.embeddings(model=os.getenv("EMBEDDING_MODEL"), prompt=text)
        vectors.append(resp["embedding"])
    return vectors
#-------------------------------------------------------------------------
#for testing purposes only  and it hehes e
#load_dotenv()

# DEBUG - add these lines
#print("OLLAMA_URL:", os.getenv("OLLAMA_URL"))
#print("EMBEDDING_MODEL:", os.getenv("EMBEDDING_MODEL"))

#"client = ollama.Client(host=os.getenv("OLLAMA_URL"))
#---------------------------------------------------------------------------