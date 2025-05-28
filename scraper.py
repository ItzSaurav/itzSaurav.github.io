import requests
import json
import os
from datetime import datetime

def fetch_gnews(api_key, query, lang='en', max_results=10, sort_by='publishedAt'):
    """Fetches news articles using the GNews API."""
    articles = []
    # GNews API endpoint for searching news
    url = f"https://gnews.io/api/v4/search?q={query}&lang={lang}&max={max_results}&sortby={sort_by}&token={api_key}"

    try:
        response = requests.get(url)
        response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
        data = response.json()

        for article_data in data.get('articles', []):
            title = article_data.get('title')
            description = article_data.get('description')
            url = article_data.get('url')
            source_name = article_data.get('source', {}).get('name', 'GNews API')
            published_at_str = article_data.get('publishedAt')

            # GNews 'publishedAt' is usually in ISO 8601 format, which is perfect.
            # Use current time as a fallback if published_at_str is missing.
            published_at = published_at_str if published_at_str else datetime.now().isoformat() + "Z"

            # Ensure we have essential data before adding the article
            if title and url:
                articles.append({
                    "title": title,
                    "description": description if description else "No description available.",
                    "url": url,
                    "source": source_name,
                    "publishedAt": published_at
                })
        print(f"Fetched {len(articles)} articles from GNews API for query '{query}'.")

    except requests.exceptions.RequestException as e:
        print(f"Error fetching from GNews API: {e}")
    except json.decoder.JSONDecodeError as e:
        print(f"Error decoding JSON response from GNews API: {e}")
        # If JSON decoding fails, try to print the raw response for debugging
        if 'response' in locals() and hasattr(response, 'text'):
            print(f"Raw API Response Content: {response.text}")
    return articles

def main():
    all_articles = []
    print("Starting GNews API news fetching process...")

    # Retrieve the GNews API key from GitHub Secrets (environment variable)
    gnews_api_key = os.getenv('GNEWS_API_KEY')
    if not gnews_api_key:
        print("Error: GNEWS_API_KEY environment variable not set. Please add it to GitHub Secrets.")
        # Ensure an empty news.json is still created to prevent website errors
        with open('news.json', 'w', encoding='utf-8') as f:
            json.dump([], f)
        return

    # Fetch AI news using the GNews API
    # The query "artificial intelligence news" is broad.
    # You can adjust 'max_results' up to 10 per query for the free tier.
    # You can make multiple calls with different queries if needed, but watch the 100 req/day limit.
    all_articles.extend(fetch_gnews(gnews_api_key, "artificial intelligence news", max_results=10))

    # --- Standard sorting and de-duplication (this part remains the same) ---
    # Sort articles by published date, newest first
    # Use a safe fallback for comparison if 'publishedAt' is missing or invalid
    all_articles.sort(key=lambda x: x.get('publishedAt', datetime.min.isoformat() + "Z"), reverse=True)

    # Remove duplicates based on URL
    seen_urls = set()
    unique_articles = []
    for article in all_articles:
        # Only process articles with a valid URL and if it hasn't been seen before
        if article.get('url') and article['url'] not in seen_urls:
            unique_articles.append(article)
            seen_urls.add(article['url'])

    # Limit to a reasonable number of articles for display on the page
    # Adjust as needed, e.g., if you fetch more than 30 unique articles
    final_articles = unique_articles[:30]

    # Write the aggregated news data to news.json
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
