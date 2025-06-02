from flask import Flask, request, jsonify
from flask_cors import CORS
import json
from datetime import datetime, timedelta
import os
import schedule
import time
import threading
import feedparser
import socket
import random
import re
import requests
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

app = Flask(__name__)
CORS(app)

CONTACTS_FILE = 'contacts.json'
NEWS_FILE = 'news.json'

# Configure requests session with retry strategy
session = requests.Session()
retry_strategy = Retry(
    total=3,
    backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504],
)
adapter = HTTPAdapter(max_retries=retry_strategy)
session.mount("http://", adapter)
session.mount("https://", adapter)

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

def fetch_rss_feed(url, max_retries=3):
    """Fetch and parse RSS feed with retry logic."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    for attempt in range(max_retries):
        try:
            # First try to fetch the feed content
            response = session.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            # Parse the feed content
            feed = feedparser.parse(response.content)
            if feed.entries:
                return feed.entries[:10]  # Get latest 10 entries
            return []
        except Exception as e:
            if attempt == max_retries - 1:
                print(f"Error fetching {url}: {str(e)}")
                return []
            time.sleep(2 ** attempt)  # Exponential backoff

def get_article_date(entry):
    """Extract and parse article date from different possible fields."""
    date_fields = ['published_parsed', 'updated_parsed', 'created_parsed']
    for field in date_fields:
        if hasattr(entry, field) and entry[field]:
            return datetime(*entry[field][:6])
    return datetime.now()

def scrape_news():
    print(f"Starting news scrape at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Define RSS feeds with backup sources
    feeds = {
        'research': [
            'https://arxiv.org/rss/cs.AI',
            'https://arxiv.org/rss/cs.LG',
            'https://arxiv.org/rss/cs.CL',
            'https://arxiv.org/rss/cs.NE'
        ],
        'industry': [
            'https://www.sciencedaily.com/rss/computers_math/artificial_intelligence.xml',
            'https://www.technologyreview.com/topic/artificial-intelligence/feed',
            'https://www.zdnet.com/news/rss.xml'
        ],
        'startups': [
            'https://www.unite.ai/feed/',
            'https://www.artificialintelligence-news.com/feed/',
            'https://www.analyticsinsight.net/feed/'
        ],
        'tech': [
            'https://www.theverge.com/rss/artificial-intelligence/index.xml',
            'https://www.wired.com/feed/rss',
            'https://www.techrepublic.com/rssfeeds/articles/'
        ]
    }

    all_articles = []
    seen_urls = set()

    # Get articles from the last 24 hours
    cutoff_time = datetime.now() - timedelta(hours=24)

    for category, urls in feeds.items():
        for url in urls:
            try:
                entries = fetch_rss_feed(url)
                for entry in entries:
                    try:
                        article_date = get_article_date(entry)
                        if article_date < cutoff_time:
                            continue

                        url = entry.link
                        if url in seen_urls:
                            continue
                        seen_urls.add(url)

                        # Ensure we have valid content
                        title = clean_text(entry.title)
                        description = clean_text(entry.description if hasattr(entry, 'description') else entry.summary)
                        
                        if not title or not description:
                            continue

                        article = {
                            'title': title,
                            'description': description,
                            'url': url,
                            'source': category.capitalize(),
                            'publishedAt': article_date.strftime('%Y-%m-%d %H:%M:%S')
                        }
                        all_articles.append(article)
                    except Exception as e:
                        print(f"Error processing article from {url}: {str(e)}")
                        continue
            except Exception as e:
                print(f"Error processing feed {url}: {str(e)}")
                continue

    # Sort by date and get latest 30 articles
    all_articles.sort(key=lambda x: x['publishedAt'], reverse=True)
    latest_articles = all_articles[:30]

    # Save to JSON file
    news_data = {
        'articles': latest_articles,
        'lastUpdated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }

    try:
        with open(NEWS_FILE, 'w', encoding='utf-8') as f:
            json.dump(news_data, f, indent=2, ensure_ascii=False)
        print(f"News scrape completed. Found {len(latest_articles)} articles.")
    except Exception as e:
        print(f"Error saving news data: {str(e)}")

    return latest_articles

def run_scheduler():
    while True:
        try:
            schedule.run_pending()
            time.sleep(60)
        except Exception as e:
            print(f"Scheduler error: {str(e)}")
            time.sleep(300)  # Wait 5 minutes before retrying

# Schedule news scraping
schedule.every(6).hours.do(scrape_news)  # Run every 6 hours (4 times a day)

# Start scheduler in a separate thread
scheduler_thread = threading.Thread(target=run_scheduler)
scheduler_thread.daemon = True
scheduler_thread.start()

# Initial scrape
scrape_news()

@app.route('/submit-contact', methods=['POST'])
def submit_contact():
    try:
        data = request.json
        name = data.get('name')
        email = data.get('email')
        message = data.get('message')

        if not all([name, email, message]):
            return jsonify({'error': 'All fields are required'}), 400

        contacts = load_contacts()
        
        # Add new contact with timestamp
        contacts['contacts'].append({
            'name': name,
            'email': email,
            'message': message,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })

        save_contacts(contacts)
        
        return jsonify({'message': 'Contact form submitted successfully'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

def load_contacts():
    if os.path.exists(CONTACTS_FILE):
        with open(CONTACTS_FILE, 'r') as f:
            return json.load(f)
    return {'contacts': []}

def save_contacts(contacts):
    with open(CONTACTS_FILE, 'w') as f:
        json.dump(contacts, f, indent=2)

if __name__ == '__main__':
    app.run(port=5000)
