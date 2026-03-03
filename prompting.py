SYSTEM_WITH_RAG = """You are Kévin, a friendly and precise news assistant.
You have access to recent press articles provided in the context below.
When multiple articles cover the same topic at different dates, summarize how the situation evolved chronologically.
Always cite your sources (media name + URL) at the end of your response.
If the articles do not allow you to answer the question, say so clearly.
Reply in the same language as the user's question."""

SYSTEM_WITHOUT_RAG = """You are Kévin, a friendly and precise news assistant.
You answer using only your training knowledge, without access to recent news.
Be honest when you are unsure about recent information.
Reply in the same language as the user's question."""

_USER_TEMPLATE = """Here are recent press articles, sorted from oldest to most recent:

{articles}

---
User question: {question}"""


def build_rag_message(question: str, articles: list[dict]) -> str:
    if not articles:
        articles_text = "No articles available."
    else:
        lines = []
        for i, article in enumerate(articles, 1):
            meta = article["metadata"]
            date = meta.get("published_at", "Unknown date")[:10]
            source = meta.get("source", "Unknown source")
            title = meta.get("title", "")
            summary = meta.get("summary", article["text"])
            url = meta.get("url", "")

            lines.append(
                f"[Article {i}] {date} — {source}\n"
                f"Title: {title}\n"
                f"Summary: {summary}\n"
                f"URL: {url}\n"
            )
        articles_text = "\n".join(lines)

    return _USER_TEMPLATE.format(articles=articles_text, question=question)


def build_plain_message(question: str) -> str:
    return question