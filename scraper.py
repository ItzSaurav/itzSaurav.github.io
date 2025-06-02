import requests
import json
import os
from datetime import datetime, timedelta
import time
import random
import feedparser
from urllib.parse import urlparse
import socket
import ssl

# Set longer timeout for feedparser
socket.setdefaulttimeout(30)

def clean_text(text):
    """Clean and normalize text."""
    if not text:
        return ""
    # Remove HTML tags and extra whitespace
    text = ' '.join(text.split())
    return text

def is_valid_article(article):
    """Validate article data."""
    required_fields = ['title', 'url', 'publishedAt']
    return all(article.get(field) for field in required_fields)

def fetch_rss_feed(url, source_name, max_retries=3):
    """Fetch and parse RSS feed with retry logic."""
    articles = []
    for attempt in range(max_retries):
        try:
            print(f"Fetching from {source_name} (attempt {attempt + 1}/{max_retries})...")
            
            # Create a custom SSL context that's more permissive
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            # Parse the feed with custom SSL context
            feed = feedparser.parse(url, ssl_context=ssl_context)
            
            if feed.bozo:  # Check for feed parsing errors
                print(f"Warning: Feed parsing issues for {source_name}: {feed.bozo_exception}")
            
            if not feed.entries:
                print(f"No entries found in feed for {source_name}")
                if attempt < max_retries - 1:
                    time.sleep(random.uniform(2, 4))
                    continue
                return articles

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

                    article = {
                        "title": title,
                        "description": description,
                        "url": link,
                        "source": source_name,
                        "publishedAt": published_at
                    }

                    if is_valid_article(article):
                        articles.append(article)

                except Exception as e:
                    print(f"Error parsing article from {source_name}: {e}")
                    continue

            if articles:
                print(f"Successfully fetched {len(articles)} articles from {source_name}")
                return articles
            else:
                print(f"No valid articles found in feed for {source_name}")
                if attempt < max_retries - 1:
                    time.sleep(random.uniform(2, 4))
                    continue

        except Exception as e:
            print(f"Error fetching from {source_name} (attempt {attempt + 1}): {e}")
            if attempt < max_retries - 1:
                time.sleep(random.uniform(2, 4))
                continue
            return articles

    return articles

def main():
    all_articles = []
    print("Starting news fetching process...")

    # List of RSS feeds with fallbacks
    feeds = [
        # Primary sources
        {
            "url": "https://www.sciencedaily.com/rss/computers_math/artificial_intelligence.xml",
            "name": "Science Daily",
            "fallback": "https://www.sciencedaily.com/rss/top/technology.xml"
        },
        {
            "url": "https://www.artificialintelligence-news.com/feed/",
            "name": "AI News",
            "fallback": "https://www.artificialintelligence-news.com/category/ai-news/feed/"
        },
        {
            "url": "https://www.analyticsinsight.net/category/artificial-intelligence/feed/",
            "name": "Analytics Insight",
            "fallback": "https://www.analyticsinsight.net/feed/"
        },
        {
            "url": "https://www.unite.ai/feed/",
            "name": "Unite.AI",
            "fallback": "https://www.unite.ai/category/news/feed/"
        },
        {
            "url": "https://www.techrepublic.com/topic/artificial-intelligence/rss.xml",
            "name": "TechRepublic",
            "fallback": "https://www.techrepublic.com/rssfeeds/topic/artificial-intelligence/"
        },
        # Backup sources
        {
            "url": "https://www.zdnet.com/news/rss.xml",
            "name": "ZDNet"
        },
        {
            "url": "https://www.artificialintelligence-news.com/category/ai-news/feed/",
            "name": "AI News Backup"
        },
        {
            "url": "https://www.analyticsinsight.net/feed/",
            "name": "Analytics Insight Backup"
        }
    ]

    # Fetch from all feeds
    for feed in feeds:
        articles = fetch_rss_feed(feed["url"], feed["name"])
        
        # Try fallback if main feed fails
        if not articles and "fallback" in feed:
            print(f"Trying fallback feed for {feed['name']}...")
            articles = fetch_rss_feed(feed["fallback"], f"{feed['name']} (Fallback)")
        
        if articles:
            all_articles.extend(articles)
        
        # Add a small delay between requests
        time.sleep(random.uniform(1, 2))

    if not all_articles:
        print("Warning: No articles were fetched from any source!")
        # Create a default article to prevent empty feed
        all_articles.append({
            "title": "Unable to fetch news at this time",
            "description": "Please try again later. We're working on fixing the issue.",
            "url": "https://github.com/ItzSaurav/itzsaurav.github.io",
            "source": "System",
            "publishedAt": datetime.now().isoformat()
        })

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
        # Create a minimal valid news.json even if there's an error
        with open('news.json', 'w', encoding='utf-8') as f:
            json.dump([{
                "title": "Error occurred while updating news",
                "description": "Please try again later.",
                "url": "https://github.com/ItzSaurav/itzsaurav.github.io",
                "source": "System",
                "publishedAt": datetime.now().isoformat()
            }], f, ensure_ascii=False, indent=4)
        print("Created fallback news.json due to error.")

if __name__ == "__main__":
    main()
