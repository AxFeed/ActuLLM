import feedparser
import hashlib
import spacy
from datetime import datetime
from bs4 import BeautifulSoup
from config import RSS_FEEDS
from database import create_collection, upsert_articles, reset_collection

nlp_fr = spacy.load("fr_core_news_sm")
nlp_en = spacy.load("en_core_web_sm")

def get_nlp(language: str):
    if language == "en":
        return nlp_en
    return nlp_fr

def parse_date(entry) -> str:
    if hasattr(entry, "published_parsed") and entry.published_parsed:
        return datetime(*entry.published_parsed[:6]).isoformat()
    if hasattr(entry, "updated_parsed") and entry.updated_parsed:
        return datetime(*entry.updated_parsed[:6]).isoformat()
    return datetime.now().isoformat()

def clean_html(text: str) -> str:
    return BeautifulSoup(text, "html.parser").get_text(separator=" ").strip()

def lemmatize(text: str, language: str = "fr") -> str:
    nlp = get_nlp(language)
    doc = nlp(text)
    return " ".join([token.lemma_ for token in doc if not token.is_stop and not token.is_punct])

def make_id(url: str) -> str:
    return hashlib.md5(url.encode()).hexdigest()

def deduplicate(articles: list[dict]) -> list[dict]:
    seen = set()
    unique = []
    for a in articles:
        if a["id"] not in seen:
            seen.add(a["id"])
            unique.append(a)
    return unique

def fetch_articles(feed_config: dict) -> list[dict]:
    print(f"  Fetching: {feed_config['name']} ({feed_config['url']})")
    language = feed_config.get("language", "fr")
    parsed = feedparser.parse(feed_config["url"])
    articles = []
    for entry in parsed.entries:
        title = entry.get("title", "").strip()
        summary = entry.get("summary", "").strip()
        url = entry.get("link", "").strip()
        if not title and not summary:
            continue
        raw_text = f"{clean_html(title)}. {clean_html(summary)}" if summary else clean_html(title)
        lemmatized_text = lemmatize(raw_text, language)
        articles.append({
            "id":       make_id(url or title),
            "text":     lemmatized_text,
            "metadata": {
                "title":        title,
                "summary":      clean_html(summary)[:500],
                "url":          url,
                "source":       feed_config["name"],
                "language":     language,
                "published_at": parse_date(entry),
            }
        })
    print(f"     {len(articles)} articles found")
    return articles

def ingest(reset: bool = False):
    isOk = True
    print("\n[RSS] Starting ingestion...\n")
    if reset:
        reset_collection()
    else:
        create_collection()
    all_articles = []
    for feed_config in RSS_FEEDS:
        try:
            articles = fetch_articles(feed_config)
            all_articles.extend(articles)
        except Exception as e:
            isOk = False
            print(f"[RSS] Error with {feed_config['name']}: {e}")
    try:
        unique_articles = deduplicate(all_articles)
        print(f"\n[RSS] {len(all_articles)} fetched -> {len(unique_articles)} unique after deduplication")
        upsert_articles(unique_articles)
        print("\n[RSS] Ingestion complete.\n")
    except Exception as e:
        import traceback
        traceback.print_exc()
        isOk = False
        raise
    return isOk