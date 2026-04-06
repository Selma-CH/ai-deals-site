import requests
from bs4 import BeautifulSoup
import feedparser


def parse_rss_feed(url):
    articles = []
    feed = feedparser.parse(url)

    for entry in feed.entries[:5]:
        articles.append({
            "title": entry.get("title", "No title"),
            "content": entry.get("summary", ""),
            "source_url": entry.get("link", url),
            "image": "",
            "category": "rss",
        })

    return articles


def parse_sale_page(url):
    articles = []

    res = requests.get(url, timeout=20)
    soup = BeautifulSoup(res.text, "html.parser")

    title = soup.title.get_text(strip=True) if soup.title else "Sale Info"
    paragraphs = soup.find_all("p")
    content = "\n".join([p.get_text(strip=True) for p in paragraphs[:10]])

    image = ""
    img = soup.find("img")
    if img and img.get("src"):
        image = img["src"]

    articles.append({
        "title": title,
        "content": content,
        "source_url": url,
        "image": image,
        "category": "sale",
    })

    return articles