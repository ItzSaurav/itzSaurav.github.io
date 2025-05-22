# scripts/fetch_news.py
import feedparser

rss_url = "https://news.google.com/rss/search?q=artificial+intelligence&hl=en-US&gl=US&ceid=US:en"
feed = feedparser.parse(rss_url)

html_content = "<html><head><title>AI News Daily</title></head><body>"
html_content += "<h1>Daily AI News</h1><ul>"

for entry in feed.entries[:10]:  # get top 10 news
    html_content += f'<li><a href="{entry.link}">{entry.title}</a></li>'

html_content += "</ul></body></html>"

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html_content)
