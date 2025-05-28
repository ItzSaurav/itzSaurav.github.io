import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime, timedelta
import re # For regular expressions, useful in parsing dates/cleaning text

def get_html_content(url):
    """Fetches HTML content from a given URL with a user-agent header."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive'
    }
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None

def parse_date(date_string):
    """
    Attempts to parse various date string formats.
    Returns ISO format string or None if parsing fails.
    """
    if not date_string:
        return datetime.now().isoformat() + "Z" # Fallback if no string provided

    date_string = date_string.strip()

    formats = [
        "%Y-%m-%dT%H:%M:%SZ",       # ISO 8601 with Z (e.g., "2023-10-27T10:00:00Z")
        "%Y-%m-%dT%H:%M:%S%z",      # ISO 8601 with offset (e.g., "2023-10-27T10:00:00+00:00")
        "%Y-%m-%dT%H:%M:%S",        # ISO 8601 without Z/offset
        "%Y-%m-%d %H:%M:%S",
        "%B %d, %Y %I:%M %p",       # "May 28, 2025 10:30 AM"
        "%B %d, %Y",                # "May 28, 2025"
        "%b %d, %Y",                # "May 28, 2025"
        "%Y/%m/%d %H:%M:%S",
        "%d %B %Y",                 # "28 May 2025"
        "%d %b %Y",                 # "28 May 2025"
    ]
    for fmt in formats:
        try:
            dt_object = datetime.strptime(date_string, fmt)
            return dt_object.isoformat() + "Z" # Assume UTC if no timezone given
        except ValueError:
            pass

    # Handle "X hours/days ago" if explicitly needed, but not typical for scraped datetime attributes
    if "ago" in date_string:
        return datetime.now().isoformat() + "Z" # Treat as now for simplicity if relative

    print(f"Warning: Could not parse date string '{date_string}'. Falling back to current time.")
    return datetime.now().isoformat() + "Z" # Fallback to current time if unparseable

def scrape_the_verge_ai():
    """Scrapes AI news from The Verge's AI section."""
    url = "https://www.theverge.com/ai"
    articles = []
    html_content = get_html_content(url)
    if not html_content:
        return articles

    soup = BeautifulSoup(html_content, 'lxml')

    # Common Verge article container classes
    # Trying multiple in case one is more prevalent or changes
    article_containers = soup.find_all('div', class_=[
        'c-entry-box--compact',
        'duet--content-cards--content-card',
        'c-compact-river__item' # Older but might still exist
    ])

    for item in article_containers:
        try:
            # Title & Link
            title_tag = item.find(['h2', 'h3'], class_=lambda x: x and ('c-entry-box--compact__title' in x or 'duet--content-cards--content-card__title' in x))
            link_tag = title_tag.find('a') if title_tag else None

            if not link_tag or not link_tag.get('href'):
                continue

            title = link_tag.get_text(strip=True)
            full_url = link_tag.get('href')
            if not full_url.startswith('http'): # Make relative URLs absolute
                full_url = 'https://www.theverge.com' + full_url

            # Description
            description_tag = item.find('p', class_=lambda x: x and ('c-entry-box--compact__dek' in x or 'duet--content-cards--content-card__description' in x))
            description = description_tag.get_text(strip=True) if description_tag else "No description available."

            # Date
            time_tag = item.find('time')
            published_at = None
            if time_tag and 'datetime' in time_tag.attrs:
                published_at = time_tag['datetime']
            elif time_tag:
                published_at = time_tag.get_text(strip=True) # Fallback to text content

            iso_published_at = parse_date(published_at)

            articles.append({
                "title": title,
                "description": description,
                "url": full_url,
                "source": "The Verge",
                "publishedAt": iso_published_at
            })
        except Exception as e:
            # print(f"Error processing The Verge item: {e}") # Uncomment for more detailed debugging
            continue # Skip to next item if this one fails

    print(f"Scraped {len(articles)} articles from The Verge.")
    return articles[:10] # Limit to top 10 from this source

def scrape_techcrunch_ai():
    """Scrapes AI news from TechCrunch's AI category."""
    url = "https://techcrunch.com/category/artificial-intelligence/"
    articles = []
    html_content = get_html_content(url)
    if not html_content:
        return articles

    soup = BeautifulSoup(html_content, 'lxml')

    # Common TechCrunch article container classes
    article_containers = soup.find_all('article', class_='post-block')

    for item in article_containers:
        try:
            # Title & Link
            title_tag = item.find('h2', class_='post-block__title')
            link_tag = title_tag.find('a') if title_tag else None

            if not link_tag or not link_tag.get('href'):
                continue

            title = link_tag.get_text(strip=True)
            full_url = link_tag.get('href')

            # Description
            summary_tag = item.find('div', class_='post-block__content')
            description = summary_tag.get_text(strip=True) if summary_tag else "No description available."

            # Date
            time_tag = item.find('time', class_='post-block__meta-date')
            published_at = time_tag['datetime'] if time_tag and 'datetime' in time_tag.attrs else None
            
            iso_published_at = parse_date(published_at)

            articles.append({
                "title": title,
                "description": description,
                "url": full_url,
                "source": "TechCrunch",
                "publishedAt": iso_published_at
            })
        except Exception as e:
            # print(f"Error processing TechCrunch item: {e}") # Uncomment for more detailed debugging
            continue # Skip to next item

    print(f"Scraped {len(articles)} articles from TechCrunch.")
    return articles[:10] # Limit to top 10 from this source

def scrape_zdnet_ai():
    """Scrapes AI news from ZDNET AI section."""
    # UPDATED ZDNET URL
    url = "https://www.zdnet.com/topic/artificial-intelligence/"
    articles = []
    html_content = get_html_content(url)
    if not html_content:
        return articles

    soup = BeautifulSoup(html_content, 'lxml')

    # ZDNET article container classes (trying common ones)
    article_containers = soup.find_all('article', class_=[
        'river-item', # Often used for lists of articles
        'story-article', # Common for individual articles
        'story-wrapper' # Sometimes the wrapper
    ])

    for item in article_containers:
        try:
            # Title & Link
            title_tag = item.find(['h2', 'h3'], class_=lambda x: x and ('river-item__title' in x or 'story-article__title' in x))
            link_tag = title_tag.find('a') if title_tag else None

            if not link_tag or not link_tag.get('href'):
                continue

            title = link_tag.get_text(strip=True)
            full_url = link_tag.get('href')
            if not full_url.startswith('http'): # ZDNET often uses relative paths
                full_url = 'https://www.zdnet.com' + full_url


            # Description
            description_tag = item.find('p', class_=lambda x: x and ('river-item__deck' in x or 'story-article__deck' in x))
            description = description_tag.get_text(strip=True) if description_tag else "No description available."

            # Date
            time_tag = item.find('time')
            published_at = None
            if time_tag and 'datetime' in time_tag.attrs:
                published_at = time_tag['datetime']
            elif time_tag:
                # Regex to extract date from text, e.g., "May 28, 2025 8:30 a.m. PST"
                date_text = time_tag.get_text(strip=True)
                match = re.search(r'(\w+\s+\d{1,2},\s+\d{4}(?:\s+\d{1,2}:\d{2}\s*(?:a\.m\.|p\.m\.|AM|PM)?)?)', date_text, re.IGNORECASE)
                if match:
                    published_at = match.group(1).replace('a.m.', 'AM').replace('p.m.', 'PM') # Normalize AM/PM
                else: # Try simpler date format if no time
                     match = re.search(r'(\w+\s+\d{1,2},\s+\d{4})', date_text)
                     if match:
                         published_at = match.group(1)

            iso_published_at = parse_date(published_at)

            articles.append({
                "title": title,
                "description": description,
                "url": full_url,
                "source": "ZDNET",
                "publishedAt": iso_published_at
            })
        except Exception as e:
            # print(f"Error processing ZDNET item: {e}") # Uncomment for more detailed debugging
            continue # Skip to next item

    print(f"Scraped {len(articles)} articles from ZDNET.")
    return articles[:10] # Limit to top 10 from this source


def main():
    all_articles = []

    print("Starting scraping process...")
    all_articles.extend(scrape_the_verge_ai())
    all_articles.extend(scrape_techcrunch_ai())
    all_articles.extend(scrape_zdnet_ai())

    # Sort articles by published date, newest first
    # Use a safe fallback for comparison if publishedAt is missing or invalid
    all_articles.sort(key=lambda x: x.get('publishedAt', datetime.min.isoformat() + "Z"), reverse=True)

    # Remove duplicates based on URL
    seen_urls = set()
    unique_articles = []
    for article in all_articles:
        # Only process articles with a valid URL
        if article.get('url') and article['url'] not in seen_urls:
            unique_articles.append(article)
            seen_urls.add(article['url'])

    # Limit to a reasonable number of articles for the page
    final_articles = unique_articles[:30] # Display top 30 latest unique articles (across all sources)

    # Write to news.json
    try:
        with open('news.json', 'w', encoding='utf-8') as f:
            json.dump(final_articles, f, ensure_ascii=False, indent=4)
        print(f"Successfully generated news.json with {len(final_articles)} articles.")
    except Exception as e:
        print(f"Error writing news.json: {e}")
        # In case of write error, ensure an empty JSON is still created to avoid breaking the site
        with open('news.json', 'w', encoding='utf-8') as f:
            json.dump([], f)
        print("Wrote empty news.json due to error.")


if __name__ == "__main__":
    main()
