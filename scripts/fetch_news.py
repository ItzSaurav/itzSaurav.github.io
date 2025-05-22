import feedparser
from datetime import datetime

# Define RSS feeds to use
rss_urls = [
    "https://www.technologyreview.com/feed/",
    "https://venturebeat.com/category/ai/feed/",
    "https://news.google.com/rss/search?q=artificial+intelligence"
]

# Gather news items
all_items = []
for url in rss_urls:
    feed = feedparser.parse(url)
    all_items.extend(feed.entries[:5])  # top 5 from each feed

# Sort by date if possible
all_items.sort(key=lambda x: x.get("published_parsed", datetime.now()), reverse=True)

# Start HTML
html = "<!DOCTYPE html><html><head><meta charset='UTF-8'><title>AI News Daily</title></head><body>"
html += f"<h1>📰 AI News Daily — {datetime.now().strftime('%Y-%m-%d')}</h1><ul>"

# Add top 15 links
for entry in all_items[:15]:
    title = entry.title
    link = entry.link
    html += f"<li><a href='{link}' target='_blank'>{title}</a></li>"

html += "</ul><p>Last updated automatically by GitHub Actions.</p></body></html>"

# Save the file
with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)
