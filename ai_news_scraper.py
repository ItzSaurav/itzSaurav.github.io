import feedparser
import json
from datetime import datetime, timedelta
import os
import schedule
import time
import threading
import logging
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup
import re

# Set up logging
logging.basicConfig(
    filename='ai_news.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class AINewsScraper:
    def __init__(self):
        self.news_file = 'ai_news.json'
        self.feeds = {
            'research': [
                'https://arxiv.org/rss/cs.AI',
                'https://arxiv.org/rss/cs.LG',
                'https://arxiv.org/rss/cs.CL',
                'https://arxiv.org/rss/cs.CV',
                'https://arxiv.org/rss/cs.NE',
                'https://arxiv.org/rss/cs.RO'
            ],
            'industry': [
                'https://www.sciencedaily.com/rss/computers_math/artificial_intelligence.xml',
                'https://www.technologyreview.com/topic/artificial-intelligence/feed',
                'https://www.artificialintelligence-news.com/feed/',
                'https://www.analyticsinsight.net/feed/',
                'https://www.aitimes.com/feed/',
                'https://www.zdnet.com/news/rss.xml'
            ],
            'startups': [
                'https://www.unite.ai/feed/',
                'https://www.artificialintelligence-news.com/feed/',
                'https://www.analyticsinsight.net/feed/',
                'https://www.aitimes.com/feed/',
                'https://www.zdnet.com/news/rss.xml'
            ],
            'ethics': [
                'https://www.artificialintelligence-news.com/feed/',
                'https://www.analyticsinsight.net/feed/',
                'https://www.aitimes.com/feed/'
            ],
            'applications': [
                'https://www.sciencedaily.com/rss/computers_math/artificial_intelligence.xml',
                'https://www.technologyreview.com/topic/artificial-intelligence/feed',
                'https://www.artificialintelligence-news.com/feed/'
            ]
        }
        self.max_articles = 50
        self.cache_duration = timedelta(hours=12)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

    def clean_text(self, text):
        """Clean and normalize text content."""
        if not text:
            return ""
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        # Remove extra whitespace
        text = ' '.join(text.split())
        # Remove special characters
        text = re.sub(r'[^\w\s.,!?-]', '', text)
        return text

    def extract_image(self, entry, url):
        """Extract image URL from entry or webpage."""
        try:
            # Try to get image from entry
            if hasattr(entry, 'media_content'):
                for media in entry.media_content:
                    if 'url' in media:
                        return media['url']
            
            # Try to get image from webpage
            response = self.session.get(url, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                # Look for Open Graph image
                og_image = soup.find('meta', property='og:image')
                if og_image:
                    return og_image.get('content')
                # Look for first image
                first_image = soup.find('img')
                if first_image:
                    return first_image.get('src')
        except Exception as e:
            logging.error(f"Error extracting image: {str(e)}")
        return None

    def get_article_date(self, entry):
        """Extract and parse article date from different possible fields."""
        date_fields = ['published_parsed', 'updated_parsed', 'created_parsed']
        for field in date_fields:
            if hasattr(entry, field) and entry[field]:
                return datetime(*entry[field][:6])
        return datetime.now()

    def fetch_feed(self, url):
        """Fetch and parse a single RSS feed."""
        try:
            feed = feedparser.parse(url)
            if feed.entries:
                return feed.entries[:10]  # Get latest 10 entries
            return []
        except Exception as e:
            logging.error(f"Error fetching {url}: {str(e)}")
            return []

    def scrape_news(self):
        """Scrape news from all feeds and save to JSON."""
        logging.info("Starting news scrape")
        all_articles = []
        seen_urls = set()

        # Get articles from the last 24 hours
        cutoff_time = datetime.now() - timedelta(hours=24)

        for category, urls in self.feeds.items():
            for url in urls:
                entries = self.fetch_feed(url)
                for entry in entries:
                    try:
                        article_date = self.get_article_date(entry)
                        if article_date < cutoff_time:
                            continue

                        url = entry.link
                        if url in seen_urls:
                            continue
                        seen_urls.add(url)

                        # Clean and validate content
                        title = self.clean_text(entry.title)
                        description = self.clean_text(entry.description if hasattr(entry, 'description') else entry.summary)
                        
                        if not title or not description:
                            continue

                        # Extract domain for source
                        domain = urlparse(url).netloc
                        
                        # Extract image
                        image_url = self.extract_image(entry, url)

                        article = {
                            'title': title,
                            'description': description,
                            'url': url,
                            'source': domain,
                            'category': category,
                            'publishedAt': article_date.strftime('%Y-%m-%d %H:%M:%S'),
                            'image': image_url,
                            'readingTime': self.estimate_reading_time(description)
                        }
                        all_articles.append(article)
                    except Exception as e:
                        logging.error(f"Error processing article from {url}: {str(e)}")
                        continue

        # Sort by date and get latest articles
        all_articles.sort(key=lambda x: x['publishedAt'], reverse=True)
        latest_articles = all_articles[:self.max_articles]

        # Save to JSON file
        news_data = {
            'articles': latest_articles,
            'lastUpdated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'totalArticles': len(latest_articles),
            'categories': list(self.feeds.keys())
        }

        try:
            with open(self.news_file, 'w', encoding='utf-8') as f:
                json.dump(news_data, f, indent=2, ensure_ascii=False)
            logging.info(f"Successfully saved {len(latest_articles)} articles")
        except Exception as e:
            logging.error(f"Error saving news data: {str(e)}")

        return latest_articles

    def estimate_reading_time(self, text):
        """Estimate reading time in minutes."""
        words = len(text.split())
        return max(1, round(words / 200))  # Assuming 200 words per minute

    def run_scheduler(self):
        """Run the scheduler in a separate thread."""
        while True:
            try:
                schedule.run_pending()
                time.sleep(60)
            except Exception as e:
                logging.error(f"Scheduler error: {str(e)}")
                time.sleep(300)  # Wait 5 minutes before retrying

def main():
    scraper = AINewsScraper()
    
    # Schedule news scraping to run every 6 hours
    schedule.every(6).hours.do(scraper.scrape_news)
    
    # Initial scrape
    scraper.scrape_news()
    
    # Start scheduler in a separate thread
    scheduler_thread = threading.Thread(target=scraper.run_scheduler)
    scheduler_thread.daemon = True
    scheduler_thread.start()
    
    # Keep the main thread alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logging.info("Scraper stopped by user")

if __name__ == "__main__":
    main() 