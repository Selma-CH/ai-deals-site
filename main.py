import os
import json
import requests
import subprocess
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from scraper.scraper import fetch_sale_articles
from generator.article_generator import render_article_page
from generator.summary_generator import render_summary_page
from app.article_html import save_article_html

# ===== 固定設定 =====
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1490044762789777639/d--WHejO5pXv9gqF9rHkddPNa_Ck9N6WYLeP60RqVCrfkfSj8RpPdrxffwe41B-n7Azc"
BASE_DIR = r"E:\ai-deals-site"
GIT_REPO_PATH = BASE_DIR
CLOUDFLARE_PAGES_URL = "https://ai-deals-site.pages.dev/"
ARTICLES_DIR = os.path.join(BASE_DIR, "articles")
SUMMARY_DIR = os.path.join(BASE_DIR, "summary")

os.makedirs(ARTICLES_DIR, exist_ok=True)
os.makedirs(SUMMARY_DIR, exist_ok=True)

app = FastAPI()


def send_discord_notification(article):
    url = f"{CLOUDFLARE_PAGES_URL}{article['id']}"
    payload = {
        "content": (
            f"🆕 新着セール記事\n"
            f"**{article['title']}**\n"
            f"{url}\n"
            f"参考: {article.get('source_url', '')}"
        )
    }

    res = requests.post(
        DISCORD_WEBHOOK_URL,
        data=json.dumps(payload),
        headers={"Content-Type": "application/json"},
        timeout=20,
    )
    print("Discord:", res.status_code, res.text)


def git_push_updates():
    subprocess.run(["git", "-C", GIT_REPO_PATH, "add", "."], check=True)

    subprocess.run(
        ["git", "-C", GIT_REPO_PATH, "commit", "-m", "Auto update sale articles"],
        check=False,
    )

    subprocess.run(
        ["git", "-C", GIT_REPO_PATH, "pull", "origin", "main", "--rebase"],
        check=False,
    )

    subprocess.run(
        ["git", "-C", GIT_REPO_PATH, "push", "origin", "main"],
        check=True,
    )


def generate_all_articles():
    articles = fetch_sale_articles()

    if not articles:
        return {"status": "no articles"}

    generated = []

    for idx, article in enumerate(articles, start=1):
        article["id"] = idx

        html = render_article_page(article, articles)

        saved_path = save_article_html(
            article_id=article["id"],
            title=article["title"],
            html_content=html,
        )

        send_discord_notification(article)

        generated.append({
            "id": article["id"],
            "title": article["title"],
            "path": saved_path,
        })

    summary_html = render_summary_page(articles)
    with open(os.path.join(SUMMARY_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(summary_html)

    git_push_updates()
    return generated


@app.get("/")
def home():
    return {"status": "AI Deals Site Server Running"}


@app.get("/generate", response_class=HTMLResponse)
def generate_dashboard():
    generated = generate_all_articles()

    if isinstance(generated, dict):
        return f"<h1>{generated['status']}</h1>"

    cards = "".join(
        f"""
        <div class='card'>
            <h2>{item['title']}</h2>
            <p>ID: {item['id']}</p>
            <p>保存先: {item['path']}</p>
            <a href='{CLOUDFLARE_PAGES_URL}{item['id']}' target='_blank'>公開記事を見る</a>
        </div>
        """
        for item in generated
    )

    return f"""
    <html>
    <head>
        <title>AI Deals 管理画面</title>
        <style>
            body {{ font-family: Arial; background:#111; color:white; padding:40px; }}
            .card {{ background:#1c1c1e; padding:20px; border-radius:20px; margin-bottom:20px; }}
            a {{ color:#4da3ff; }}
        </style>
    </head>
    <body>
        <h1>AI Deals 管理画面</h1>
        <p>生成完了 / Discord通知 / GitHub push / Cloudflare公開 完了</p>
        {cards}
    </body>
    </html>
    """


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)