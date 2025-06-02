import requests
import json
import os
from datetime import datetime, timedelta
import time
from bs4 import BeautifulSoup
import random
import re

def clean_text(text):
    """Clean and normalize text."""
    if not text:
        return ""
    # Remove extra whitespace and newlines
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def fetch_techcrunch():
    """Fetch AI news from TechCrunch."""
    articles = []
    try:
        url = "https://techcrunch.com/tag/artificial-intelligence/"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
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

def fetch_venturebeat():
    """Fetch AI news from VentureBeat."""
    articles = []
    try:
        url = "https://venturebeat.com/category/ai/"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        for article in soup.find_all('article', class_='ArticleListing')[:10]:
            try:
                title_elem = article.find('h2', class_='ArticleListing-title')
                if not title_elem:
                    continue
                    
                title = clean_text(title_elem.get_text())
                link = title_elem.find('a')['href']
                
                desc_elem = article.find('div', class_='ArticleListing-excerpt')
                description = clean_text(desc_elem.get_text()) if desc_elem else ""
                
                time_elem = article.find('time')
                published_at = time_elem['datetime'] if time_elem else datetime.now().isoformat()
                
                articles.append({
                    "title": title,
                    "description": description,
                    "url": link,
                    "source": "VentureBeat",
                    "publishedAt": published_at
                })
            except Exception as e:
                print(f"Error parsing VentureBeat article: {e}")
                continue
                
    except Exception as e:
        print(f"Error fetching from VentureBeat: {e}")
    return articles

def fetch_artificialintelligence_news():
    """Fetch news from artificialintelligence-news.com."""
    articles = []
    try:
        url = "https://www.artificialintelligence-news.com/"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
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
                    "source": "AI News",
                    "publishedAt": published_at
                })
            except Exception as e:
                print(f"Error parsing AI News article: {e}")
                continue
                
    except Exception as e:
        print(f"Error fetching from AI News: {e}")
    return articles

def main():
    all_articles = []
    print("Starting news fetching process...")

    # Fetch from all sources
    sources = [
        fetch_techcrunch,
        fetch_venturebeat,
        fetch_artificialintelligence_news
    ]
    
    for source in sources:
        try:
            articles = source()
            all_articles.extend(articles)
            # Add a small delay between requests to be respectful
            time.sleep(random.uniform(1, 2))
        except Exception as e:
            print(f"Error fetching from source: {e}")
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
