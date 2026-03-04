import chromadb

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