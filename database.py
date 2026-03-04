import os
import chromadb
from openai import AzureOpenAI
from dotenv import load_dotenv

load_dotenv()

N_RESULTS = 6

azure_client = AzureOpenAI(
    azure_endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT"),
    api_key=os.environ.get("AZURE_OPENAI_API_KEY"),
    api_version=os.environ.get("AZURE_OPENAI_API_VERSION", "2024-02-01"),
)

def embed(texts: list[str]) -> list[list[float]]:
    response = azure_client.embeddings.create(
        model=os.environ.get("AZURE_EMBEDDING_DEPLOYMENT"),
        input=texts,
    )
    return [item.embedding for item in response.data]

def _get_collection():
    chroma = chromadb.PersistentClient(path=os.environ.get("CHROMA_PATH", "./chroma_db"))
    return chroma.get_or_create_collection(
        name=os.environ.get("COLLECTION_NAME", "actullm"),
        metadata={"hnsw:space": "cosine"},
    )

def create_collection():
    collection = _get_collection()
    print(f"[database] Collection ready. {collection.count()} documents.")
    return collection

def reset_collection():
    chroma = chromadb.PersistentClient(path=os.environ.get("CHROMA_PATH", "./chroma_db"))
    try:
        chroma.delete_collection(os.environ.get("COLLECTION_NAME", "actullm"))
        print("[database] Collection deleted.")
    except Exception:
        pass
    create_collection()

def upsert_articles(articles: list[dict]):
    collection = _get_collection()
    batch_size = int(os.environ.get("BATCH_SIZE", 50))
    added = 0
    for i in range(0, len(articles), batch_size):
        batch = articles[i : i + batch_size]
        texts = [a["text"] for a in batch]
        vectors = embed(texts)
        collection.upsert(
            ids=[a["id"] for a in batch],
            embeddings=vectors,
            documents=texts,
            metadatas=[a["metadata"] for a in batch],
        )
        added += len(batch)
    print(f"[database] {added} articles upserted. Total: {collection.count()}")
    return added

def search(query: str, n_results: int = N_RESULTS) -> list[dict]:
    collection = _get_collection()
    if collection.count() == 0:
        return []
    query_vector = embed([query])[0]
    results = collection.query(
        query_embeddings=[query_vector],
        n_results=min(n_results, collection.count()),
        include=["documents", "metadatas", "distances"],
    )
    articles = []
    for i, doc in enumerate(results["documents"][0]):
        articles.append({
            "text": doc,
            "metadata": results["metadatas"][0][i],
            "distance": results["distances"][0][i],
        })
    articles.sort(key=lambda a: a["metadata"].get("published_at", ""))
    return articles

def count() -> int:
    return _get_collection().count()