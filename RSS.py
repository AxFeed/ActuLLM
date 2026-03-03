import feedparser
from datetime import datetime
from config import RSS_FEEDS

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

        summary = entry.get("summary", entry.get("description", "")).strip()
        url = entry.get("link", "").strip()
        date = parse_date(entry)

        # Skip empty entries
        if not title and not summary:
            continue

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



if __name__ == "__main__":

    for feed_config in RSS_FEEDS:
        fetch_articles(feed_config)







