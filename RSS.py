import feedparser
from datetime import datetime
from config import RSS_FEEDS
import feedparser
import hashlib
import spacy
from bs4 import BeautifulSoup

nlp = spacy.load("fr_core_news_sm")

def parse_date(entry) -> str:    # is to find the date of an article. 
    if hasattr(entry, "published_parsed") and entry.published_parsed:       # has attribute / true or false
        return datetime(*entry.published_parsed[:6]).isoformat()             #used the publisheddate if exist 
    if hasattr(entry, "updated_parsed") and entry.updated_parsed:            # Use the updated date if it exists
        return datetime(*entry.updated_parsed[:6]).isoformat()
    return datetime.now().isoformat()  #if neither exist use the current date and time


def fetch_articles(feed_config: dict) -> list[dict]:
    """Fetch and parse a single RSS feed. Returns a list of article dicts."""
    print(f"  Fetching: {feed_config['name']} ({feed_config['url']})")
    parsed = feedparser.parse(feed_config["url"])

    articles = []
    for entry in parsed.entries:
        title = entry.get("title", "").strip()
        print(title)

        summary = entry.get("summary", "").strip()
        url = entry.get("link", "").strip()
        date = parse_date(entry)

        # Skip empty entries
        if not title and not summary:
            continue

        print("raw_text", title)
        lemmatized_title = lemmatize(clean_html(title))
        print("lemmatized_title", lemmatized_title)

        articles.append({
            "title":    title,
            "summary":  summary,
            "url":      url,
            "date":     date,
            "source":   feed_config["name"],
            "language": feed_config.get("language", "fr"),
        })

    print(f"     {len(articles)} articles found")
    return articles


def clean_html(text: str) -> str:
    """Remove HTML tags from text."""
    return BeautifulSoup(text, "html.parser").get_text(separator=" ").strip()

def lemmatize(text: str) -> str:
    """Reduce words to their base form using Spacy."""
    doc = nlp(text)
    return " ".join([token.lemma_ for token in doc])
    
def make_id(article: dict) -> str:
    """Unique ID based on URL."""
    key = article["url"] or article["title"]
    for feed_config in RSS_FEEDS:
        fetch_articles(feed_config)


