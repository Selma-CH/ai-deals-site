import requests
from bs4 import BeautifulSoup

def scrape_websites():
    articles = []

    url = "https://forest.watch.impress.co.jp/docs/bookwatch/sale/2097260.html"
    res = requests.get(url)
    soup = BeautifulSoup(res.text, "html.parser")

    title = soup.find("h1").get_text(strip=True)
    paragraphs = soup.select(".main-body p")
    content = "\n".join(p.get_text(strip=True) for p in paragraphs)
    images = [img["src"] for img in soup.select(".main-body img") if "src" in img.attrs]

    articles.append({
        "title": title,
        "content": content,
        "images": images
    })

    return articles