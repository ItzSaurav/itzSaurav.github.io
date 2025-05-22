import feedparser
from datetime import datetime

# RSS feeds (you can add more)
rss_urls = [
    "https://www.technologyreview.com/feed/",
    "https://venturebeat.com/category/ai/feed/",
    "https://news.google.com/rss/search?q=artificial+intelligence"
]

# Collect all entries
all_items = []
for url in rss_urls:
    feed = feedparser.parse(url)
    all_items.extend(feed.entries[:5])  # Get top 5 from each source

# Sort by published date (if available)
all_items.sort(key=lambda x: x.get("published_parsed", datetime.now()), reverse=True)

# Start building HTML
html = "<!DOCTYPE html><html><head><title>AI News Daily</title></head><body>"
html += f"<h1>AI News Daily — {datetime.now().strftime('%Y-%m-%d')}</h1><ul>"

for entry in all_items[:15]:  # Limit to top 15 articles
    title = entry.title
    link = entry.link
    html += f"<li><a href='{link}' target='_blank'>{title}</a></li>"

html += "</ul><p>Updated automatically every day.</p></body></html>"

# Save the HTML content to index.html
with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)

