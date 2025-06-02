import requests
import json
import schedule
import time
from datetime import datetime, timedelta
import feedparser
from bs4 import BeautifulSoup
import logging
import os

class NewsUpdater:
    def __init__(self):
        self.news_file = 'news.json'
        self.setup_logging()
        self.setup_news_sources()
        
    def setup_logging(self):
        logging.basicConfig(
            filename='news_updater.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        
    def setup_news_sources(self):
        self.sources = {
            'research': [
                {
                    'name': 'arXiv AI',
                    'url': 'https://arxiv.org/rss/cs.AI',
                    'category': 'research'
                },
                {
                    'name': 'arXiv ML',
                    'url': 'https://arxiv.org/rss/cs.LG',
                    'category': 'research'
                }
            ],
            'industry': [
                {
                    'name': 'MIT Technology Review',
                    'url': 'https://www.technologyreview.com/topic/artificial-intelligence/feed',
                    'category': 'industry'
                },
                {
                    'name': 'ZDNet AI',
                    'url': 'https://www.zdnet.com/news/rss.xml',
                    'category': 'industry'
                }
            ],
            'startups': [
                {
                    'name': 'Unite.AI',
                    'url': 'https://www.unite.ai/feed/',
                    'category': 'startups'
                },
                {
                    'name': 'AI News',
                    'url': 'https://www.artificialintelligence-news.com/feed/',
                    'category': 'startups'
                }
            ],
            'tech': [
                {
                    'name': 'The Verge AI',
                    'url': 'https://www.theverge.com/rss/artificial-intelligence/index.xml',
                    'category': 'tech'
                },
                {
                    'name': 'Wired',
                    'url': 'https://www.wired.com/feed/rss',
                    'category': 'tech'
                }
            ]
        }

    def fetch_article_content(self, url):
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove unwanted elements
            for element in soup(['script', 'style', 'nav', 'footer', 'header']):
                element.decompose()
            
            # Get main content
            content = soup.get_text(separator=' ', strip=True)
            return content[:500] + '...' if len(content) > 500 else content
            
        except Exception as e:
            logging.error(f"Error fetching content from {url}: {str(e)}")
            return None

    def parse_date(self, date_str):
        try:
            return datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
        except:
            try:
                return datetime.strptime(date_str, '%a, %d %b %Y %H:%M:%S %z')
            except:
                return datetime.now()

    def fetch_news(self):
        logging.info("Starting news fetch")
        all_articles = []
        cutoff_time = datetime.now() - timedelta(days=1)

        for category, sources in self.sources.items():
            for source in sources:
                try:
                    feed = feedparser.parse(source['url'])
                    for entry in feed.entries:
                        try:
                            # Get article date
                            article_date = self.parse_date(entry.get('published', ''))
                            if article_date < cutoff_time:
                                continue

                            # Get article content
                            content = self.fetch_article_content(entry.link)
                            if not content:
                                continue

                            article = {
                                'title': entry.title,
                                'description': content,
                                'url': entry.link,
                                'source': source['name'],
                                'category': source['category'],
                                'publishedAt': article_date.strftime('%Y-%m-%d %H:%M:%S')
                            }
                            all_articles.append(article)
                            
                        except Exception as e:
                            logging.error(f"Error processing article: {str(e)}")
                            continue
                            
                except Exception as e:
                    logging.error(f"Error fetching from {source['name']}: {str(e)}")
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
            with open(self.news_file, 'w', encoding='utf-8') as f:
                json.dump(news_data, f, indent=2, ensure_ascii=False)
            logging.info(f"Successfully saved {len(latest_articles)} articles")
        except Exception as e:
            logging.error(f"Error saving news data: {str(e)}")

        return latest_articles

    def run_scheduler(self):
        # Run immediately on start
        self.fetch_news()
        
        # Schedule to run every 6 hours
        schedule.every(6).hours.do(self.fetch_news)
        
        while True:
            try:
                schedule.run_pending()
                time.sleep(60)
            except Exception as e:
                logging.error(f"Scheduler error: {str(e)}")
                time.sleep(300)  # Wait 5 minutes before retrying

if __name__ == "__main__":
    updater = NewsUpdater()
    updater.run_scheduler() 