import requests
import json
import os
from datetime import datetime, timedelta
import time
import random
import feedparser
from urllib.parse import urlparse

def clean_text(text):
    """Clean and normalize text."""
    if not text:
        return ""
    # Remove HTML tags and extra whitespace
    text = ' '.join(text.split())
    return text

def fetch_rss_feed(url, source_name):
    """Fetch and parse RSS feed."""
    articles = []
    try:
        print(f"Fetching from {source_name}...")
        feed = feedparser.parse(url)
        
        for entry in feed.entries[:10]:  # Get latest 10 entries
            try:
                # Get the published date
                published = entry.get('published_parsed', entry.get('updated_parsed'))
                if published:
                    published_at = datetime(*published[:6]).isoformat()
                else:
                    published_at = datetime.now().isoformat()

                # Get the link
                link = entry.get('link', '')
                if not link:
                    continue

                # Get the title
                title = clean_text(entry.get('title', ''))
                if not title:
                    continue

                # Get the description
                description = clean_text(entry.get('description', ''))
                if not description and 'summary' in entry:
                    description = clean_text(entry.summary)

                articles.append({
                    "title": title,
                    "description": description,
                    "url": link,
                    "source": source_name,
                    "publishedAt": published_at
                })
            except Exception as e:
                print(f"Error parsing article from {source_name}: {e}")
                continue

        print(f"Successfully fetched {len(articles)} articles from {source_name}")
        return articles
    except Exception as e:
        print(f"Error fetching from {source_name}: {e}")
        return []

def main():
    all_articles = []
    print("Starting news fetching process...")

    # List of RSS feeds
    feeds = [
        {
            "url": "https://www.sciencedaily.com/rss/computers_math/artificial_intelligence.xml",
            "name": "Science Daily"
        },
        {
            "url": "https://www.artificialintelligence-news.com/feed/",
            "name": "AI News"
        },
        {
            "url": "https://www.analyticsinsight.net/category/artificial-intelligence/feed/",
            "name": "Analytics Insight"
        },
        {
            "url": "https://www.unite.ai/feed/",
            "name": "Unite.AI"
        },
        {
            "url": "https://www.artificialintelligence-news.com/feed/",
            "name": "AI News"
        },
        {
            "url": "https://www.techrepublic.com/topic/artificial-intelligence/rss.xml",
            "name": "TechRepublic"
        },
        {
            "url": "https://www.zdnet.com/news/rss.xml",
            "name": "ZDNet"
        }
    ]

    # Fetch from all feeds
    for feed in feeds:
        articles = fetch_rss_feed(feed["url"], feed["name"])
        if articles:
            all_articles.extend(articles)
        # Add a small delay between requests
        time.sleep(random.uniform(1, 2))

    # Sort articles by published date, newest first
    all_articles.sort(key=lambda x: x.get('publishedAt', datetime.min.isoformat()), reverse=True)

    # Remove duplicates based on URL
    seen_urls = set()
    unique_articles = []
    for article in all_articles:
        if article.get('url') and article['url'] not in seen_urls:
            # Only include articles from the last 24 hours
            try:
                published_at = datetime.fromisoformat(article['publishedAt'].replace('Z', '+00:00'))
                if datetime.now(published_at.tzinfo) - published_at <= timedelta(hours=24):
                    unique_articles.append(article)
                    seen_urls.add(article['url'])
            except:
                continue

    # Limit to the most recent 30 articles
    final_articles = unique_articles[:30]

    # Write the aggregated news data to news.json
    try:
        with open('news.json', 'w', encoding='utf-8') as f:
            json.dump(final_articles, f, ensure_ascii=False, indent=4)
        print(f"Successfully generated news.json with {len(final_articles)} articles.")
    except Exception as e:
        print(f"Error writing news.json: {e}")
        with open('news.json', 'w', encoding='utf-8') as f:
            json.dump([], f)
        print("Wrote empty news.json due to error.")

if __name__ == "__main__":
    main()
