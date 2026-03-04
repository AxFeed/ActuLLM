import os
import chromadb
import ollama
from dotenv import load_dotenv

load_dotenv()

N_RESULTS = 6

client = ollama.Client(host=os.environ.get("OLLAMA_URL"))


def embed(texts: list[str]) -> list[list[float]]:
    vectors = []
    for text in texts:
        resp = client.embeddings(model=os.getenv("EMBEDDING_MODEL"), prompt=text)
        vectors.append(resp["embedding"])
    return vectors


def _get_collection():
    chroma = chromadb.PersistentClient(path=os.environ.get("CHROMA_PATH", "./chroma_db"))
    return chroma.get_or_create_collection(
        name=os.environ.get("COLLECTION_NAME"),
        metadata={"hnsw:space": "cosine"},
    )


def create_collection():
    """Explicitly create the collection if it doesn't exist."""
    collection = _get_collection()
    print(f"[database] Collection ready. {collection.count()} documents.")
    return collection


def reset_collection():
    """Delete and recreate the collection."""
    chroma = chromadb.PersistentClient(path=os.environ.get("CHROMA_PATH", "./chroma_db"))
    try:
        chroma.delete_collection(os.environ.get("COLLECTION_NAME"))
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