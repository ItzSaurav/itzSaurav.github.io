import http.client
import json
import time
from datetime import datetime
import os

class SearchMonitor:
    def __init__(self):
        self.api_key = "6e34518ed9msh5837db118f9169cp1caad1jsna30cf9d75d37"
        self.host = "real-time-web-search.p.rapidapi.com"
        self.website_url = "itzsaurav.github.io"
        self.search_terms = [
            "Saurav Mishra Bangalore",
            "Saurav Mishra Python Developer",
            "Saurav Mishra AI News",
            "AI News Bangalore",
            "Python Developer Bangalore",
            "Tech Blog Bangalore"
        ]

    def search_website(self, query):
        try:
            conn = http.client.HTTPSConnection(self.host)
            headers = {
                'x-rapidapi-key': self.api_key,
                'x-rapidapi-host': self.host
            }
            
            # URL encode the query
            encoded_query = query.replace(" ", "%20")
            endpoint = f"/search-advanced-v2?q={encoded_query}&fetch_ai_overviews=false&num=10&start=0&gl=in&hl=en&nfpr=0"
            
            conn.request("GET", endpoint, headers=headers)
            response = conn.getresponse()
            data = json.loads(response.read().decode("utf-8"))
            
            # Check if our website is in the results
            results = data.get('data', {}).get('results', [])
            for idx, result in enumerate(results, 1):
                if self.website_url in result.get('url', ''):
                    return {
                        'query': query,
                        'position': idx,
                        'url': result.get('url'),
                        'title': result.get('title'),
                        'snippet': result.get('snippet')
                    }
            
            return {
                'query': query,
                'position': 'Not found in top 10',
                'url': None,
                'title': None,
                'snippet': None
            }

        except Exception as e:
            print(f"Error searching for {query}: {str(e)}")
            return None

    def save_results(self, results):
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"search_results_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2)
        
        print(f"\nResults saved to {filename}")

    def monitor(self):
        print("Starting search monitoring...")
        print(f"Monitoring website: {self.website_url}")
        print(f"Search terms: {', '.join(self.search_terms)}")
        print("\nSearching...")
        
        results = []
        for query in self.search_terms:
            print(f"\nSearching for: {query}")
            result = self.search_website(query)
            if result:
                results.append(result)
                print(f"Position: {result['position']}")
                if result['url']:
                    print(f"URL: {result['url']}")
            time.sleep(2)  # Respect API rate limits
        
        self.save_results(results)
        return results

if __name__ == "__main__":
    monitor = SearchMonitor()
    monitor.monitor() 