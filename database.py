# database.py
import chromadb
from ollama_call import embed

client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_or_create_collection(name="news")

def add_articles(articles: list[dict]):
    texts = [f"{a['title']}\n\n{a['summary']}" for a in articles]
    print(texts)
    ids = [a["id"] for a in articles]
    metadatas = [
        {
            "title":  a["title"],
            "url":    a["url"],
            "date":   a["date"],
            "source": a["source"],
        }
        for a in articles
    ]

    vectors = embed(texts)
    collection.add(ids=ids, embeddings=vectors, documents=texts, metadatas=metadatas)
    print(f"{len(articles)} articles stored")
    

def search(query: str, top_k: int = 5) -> list[dict]:
    vector = embed([query])[0]
    results = collection.query(
        query_embeddings=[vector],
        n_results=top_k,
        include=["documents", "metadatas"]
    )
    articles = []
    for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
        articles.append({**meta, "text": doc})
    return articles


if __name__ == "__main__":
    fake_articles = [
        {
            "id":      "test-001",
            "title":   "Macron parle de défense européenne",
            "summary": "Le président français a évoqué le budget militaire.",
            "url":     "https://france24.com/article1",
            "date":    "2026-03-01",
            "source":  "France24",
        }
    ]
    add_articles(fake_articles)
    
    results = search("défense Europe")
    for r in results:
        print(r["title"], "|", r["date"])