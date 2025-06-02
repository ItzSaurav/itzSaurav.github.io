import requests
import json
import os
from datetime import datetime, timedelta
import time
import random
import feedparser
from urllib.parse import urlparse, urljoin
import socket
import ssl
import re

# Set longer timeout for feedparser
socket.setdefaulttimeout(30)

def clean_text(text):
    """Clean and normalize text content."""
    if not text:
        return ""
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    # Remove extra whitespace
    text = ' '.join(text.split())
    return text

def is_valid_article(article):
    """Validate article data."""
    required_fields = ['title', 'url', 'publishedAt']
    return all(article.get(field) for field in required_fields)

def fetch_rss_feed(url, source_name, max_retries=3):
    """Fetch and parse RSS feed with retry logic."""
    for attempt in range(max_retries):
        try:
            feed = feedparser.parse(url)
            if feed.entries:
                return feed.entries[:10]  # Get latest 10 entries
            return []
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(random.uniform(1, 3))  # Random delay between retries
                continue
            print(f"Error fetching from {source_name}: {str(e)}")
            return []

def get_article_date(entry):
    """Extract and parse article date from different possible fields."""
    date_fields = ['published', 'updated', 'pubDate', 'date']
    for field in date_fields:
        if hasattr(entry, field):
            try:
                return datetime(*entry[field].timetuple()[:6])
            except:
                continue
    return None

def main():
    # List of RSS feeds with their categories
    feeds = [
        # AI Research & Development
        {
            'url': 'https://arxiv.org/rss/cs.AI',
            'name': 'arXiv AI',
            'category': 'research'
        },
        {
            'url': 'https://www.sciencedaily.com/rss/computers_math/artificial_intelligence.xml',
            'name': 'Science Daily AI',
            'category': 'research'
        },
        # Industry News
        {
            'url': 'https://www.artificialintelligence-news.com/feed/',
            'name': 'AI News',
            'category': 'industry'
        },
        {
            'url': 'https://www.analyticsinsight.net/category/artificial-intelligence/feed/',
            'name': 'Analytics Insight',
            'category': 'industry'
        },
        # Startups & Innovation
        {
            'url': 'https://www.unite.ai/feed/',
            'name': 'Unite.AI',
            'category': 'startups'
        },
        {
            'url': 'https://www.artificialintelligence-news.com/category/startups/feed/',
            'name': 'AI News Startups',
            'category': 'startups'
        },
        # Tech News
        {
            'url': 'https://www.zdnet.com/news/rss.xml',
            'name': 'ZDNet',
            'category': 'industry'
        },
        {
            'url': 'https://www.techrepublic.com/rssfeeds/articles/',
            'name': 'TechRepublic',
            'category': 'industry'
        }
    ]

    articles = []
    seen_urls = set()

    # Get current date
    now = datetime.now()
    # Set time to start of day
    today_start = datetime(now.year, now.month, now.day)
    # Get articles from last 24 hours
    cutoff_time = today_start - timedelta(days=1)

    for feed in feeds:
        entries = fetch_rss_feed(feed['url'], feed['name'])
        
        for entry in entries:
            # Get article date
            article_date = get_article_date(entry)
            if not article_date:
                continue

            # Skip if article is older than 24 hours
            if article_date < cutoff_time:
                continue

            # Get article URL
            url = entry.get('link', '')
            if not url or url in seen_urls:
                continue

            # Get article title and description
            title = clean_text(entry.get('title', ''))
            description = clean_text(entry.get('description', ''))

            # Skip if no title or description
            if not title or not description:
                continue

            # Add to articles list
            articles.append({
                'title': title,
                'description': description,
                'url': url,
                'source': feed['name'],
                'category': feed['category'],
                'date': article_date.strftime('%Y-%m-%d %H:%M:%S')
            })
            seen_urls.add(url)

    # Sort articles by date (newest first)
    articles.sort(key=lambda x: x['date'], reverse=True)

    # Write to JSON file
    with open('news.json', 'w', encoding='utf-8') as f:
        json.dump({
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'articles': articles[:30]  # Limit to 30 most recent articles
        }, f, indent=2, ensure_ascii=False)

    print(f"Successfully fetched {len(articles)} articles")
    print(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
