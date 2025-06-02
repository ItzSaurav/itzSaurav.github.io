import requests
import json
import os
from datetime import datetime, timedelta
import time
from bs4 import BeautifulSoup
import random
import re
from urllib.parse import urljoin

def clean_text(text):
    """Clean and normalize text."""
    if not text:
        return ""
    # Remove extra whitespace and newlines
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def get_random_user_agent():
    """Get a random user agent to avoid detection."""
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
    ]
    return random.choice(user_agents)

def fetch_with_retry(url, max_retries=3):
    """Fetch URL with retry logic."""
    headers = {
        'User-Agent': get_random_user_agent(),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
    }
    
    for attempt in range(max_retries):
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            return response
        except Exception as e:
            if attempt == max_retries - 1:
                raise e
            time.sleep(random.uniform(2, 5))  # Random delay between retries
    return None

def fetch_techcrunch():
    """Fetch AI news from TechCrunch."""
    articles = []
    try:
        url = "https://techcrunch.com/tag/artificial-intelligence/"
        response = fetch_with_retry(url)
        if not response:
            return articles
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        for article in soup.find_all('article', class_='post-block')[:10]:
            try:
                title_elem = article.find('h2', class_='post-block__title')
                if not title_elem:
                    continue
                    
                title = clean_text(title_elem.get_text())
                link = title_elem.find('a')['href']
                
                desc_elem = article.find('div', class_='post-block__content')
                description = clean_text(desc_elem.get_text()) if desc_elem else ""
                
                time_elem = article.find('time')
                published_at = time_elem['datetime'] if time_elem else datetime.now().isoformat()
                
                articles.append({
                    "title": title,
                    "description": description,
                    "url": link,
                    "source": "TechCrunch",
                    "publishedAt": published_at
                })
            except Exception as e:
                print(f"Error parsing TechCrunch article: {e}")
                continue
                
    except Exception as e:
        print(f"Error fetching from TechCrunch: {e}")
    return articles

def fetch_analyticsinsight():
    """Fetch AI news from Analytics Insight."""
    articles = []
    try:
        url = "https://www.analyticsinsight.net/category/artificial-intelligence/"
        response = fetch_with_retry(url)
        if not response:
            return articles
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        for article in soup.find_all('article')[:10]:
            try:
                title_elem = article.find('h2', class_='entry-title')
                if not title_elem:
                    continue
                    
                title = clean_text(title_elem.get_text())
                link = title_elem.find('a')['href']
                
                desc_elem = article.find('div', class_='entry-content')
                description = clean_text(desc_elem.get_text()) if desc_elem else ""
                
                time_elem = article.find('time')
                published_at = time_elem['datetime'] if time_elem else datetime.now().isoformat()
                
                articles.append({
                    "title": title,
                    "description": description,
                    "url": link,
                    "source": "Analytics Insight",
                    "publishedAt": published_at
                })
            except Exception as e:
                print(f"Error parsing Analytics Insight article: {e}")
                continue
                
    except Exception as e:
        print(f"Error fetching from Analytics Insight: {e}")
    return articles

def fetch_unite_ai():
    """Fetch AI news from Unite.AI."""
    articles = []
    try:
        url = "https://www.unite.ai/news/"
        response = fetch_with_retry(url)
        if not response:
            return articles
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        for article in soup.find_all('article')[:10]:
            try:
                title_elem = article.find('h2', class_='entry-title')
                if not title_elem:
                    continue
                    
                title = clean_text(title_elem.get_text())
                link = title_elem.find('a')['href']
                
                desc_elem = article.find('div', class_='entry-content')
                description = clean_text(desc_elem.get_text()) if desc_elem else ""
                
                time_elem = article.find('time')
                published_at = time_elem['datetime'] if time_elem else datetime.now().isoformat()
                
                articles.append({
                    "title": title,
                    "description": description,
                    "url": link,
                    "source": "Unite.AI",
                    "publishedAt": published_at
                })
            except Exception as e:
                print(f"Error parsing Unite.AI article: {e}")
                continue
                
    except Exception as e:
        print(f"Error fetching from Unite.AI: {e}")
    return articles

def fetch_ai_news():
    """Fetch AI news from AI-News.org."""
    articles = []
    try:
        url = "https://ai-news.org/"
        response = fetch_with_retry(url)
        if not response:
            return articles
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        for article in soup.find_all('article')[:10]:
            try:
                title_elem = article.find('h2', class_='entry-title')
                if not title_elem:
                    continue
                    
                title = clean_text(title_elem.get_text())
                link = title_elem.find('a')['href']
                
                desc_elem = article.find('div', class_='entry-content')
                description = clean_text(desc_elem.get_text()) if desc_elem else ""
                
                time_elem = article.find('time')
                published_at = time_elem['datetime'] if time_elem else datetime.now().isoformat()
                
                articles.append({
                    "title": title,
                    "description": description,
                    "url": link,
                    "source": "AI-News.org",
                    "publishedAt": published_at
                })
            except Exception as e:
                print(f"Error parsing AI-News.org article: {e}")
                continue
                
    except Exception as e:
        print(f"Error fetching from AI-News.org: {e}")
    return articles

def main():
    all_articles = []
    print("Starting news fetching process...")

    # Fetch from all sources
    sources = [
        fetch_techcrunch,
        fetch_analyticsinsight,
        fetch_unite_ai,
        fetch_ai_news
    ]
    
    for source in sources:
        try:
            print(f"Fetching from {source.__name__}...")
            articles = source()
            if articles:
                print(f"Successfully fetched {len(articles)} articles from {source.__name__}")
                all_articles.extend(articles)
            # Add a small delay between requests to be respectful
            time.sleep(random.uniform(2, 4))
        except Exception as e:
            print(f"Error fetching from source {source.__name__}: {e}")
            continue

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
