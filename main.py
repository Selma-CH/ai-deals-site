import os
import json
import requests
import subprocess
from datetime import datetime
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from apscheduler.schedulers.background import BackgroundScheduler

from scraper.scraper import fetch_sale_articles
from generator.article_generator import render_article_page
from generator.summary_generator import render_summary_page
from app.article_html import save_article_html

# =========================
# 固定設定
# =========================
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1490044762789777639/d--WHejO5pXv9gqF9rHkddPNa_Ck9N6WYLeP60RqVCrfkfSj8RpPdrxffwe41B-n7Azc"
BASE_DIR = r"E:\ai-deals-site"
GIT_REPO_PATH = BASE_DIR
CLOUDFLARE_PAGES_URL = "https://ai-deals-site.pages.dev/articles/"
ARTICLES_DIR = os.path.join(BASE_DIR, "articles")
STATIC_DIR = os.path.join(BASE_DIR, "static")

os.makedirs(ARTICLES_DIR, exist_ok=True)

app = FastAPI()
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

scheduler = BackgroundScheduler()

latest_status = {
    "last_run": "未実行",
    "count": 0,
    "discord": "未送信",
    "git": "未実行",
}


def get_next_article_id():
    files = [
        f for f in os.listdir(ARTICLES_DIR)
        if f.endswith(".html") and f != "index.html"
    ]
    ids = [int(f.replace(".html", "")) for f in files if f.replace(".html", "").isdigit()]
    return max(ids, default=0) + 1


def send_discord_notification(article):
    url = f"{CLOUDFLARE_PAGES_URL}{article['id']}.html"
    payload = {
        "content": f"🆕 新着セール記事\n**{article['title']}**\n{url}"
    }

    res = requests.post(
        DISCORD_WEBHOOK_URL,
        data=json.dumps(payload),
        headers={"Content-Type": "application/json"},
        timeout=20,
    )

    latest_status["discord"] = str(res.status_code)
    print("Discord:", res.status_code)


def git_push_updates():
    try:
        subprocess.run(["git", "-C", GIT_REPO_PATH, "add", "."], check=True)
        subprocess.run(
            ["git", "-C", GIT_REPO_PATH, "commit", "-m", "Auto archive sale articles"],
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
        latest_status["git"] = "成功"
    except Exception as e:
        latest_status["git"] = str(e)


def generate_archive_articles():
    articles = fetch_sale_articles()
    if not articles:
        return

    start_id = get_next_article_id()
    generated_articles = []

    for i, article in enumerate(articles):
        article["id"] = start_id + i

        html = render_article_page(article, articles)

        save_article_html(
            article_id=article["id"],
            title=article["title"],
            html_content=html,
        )

        send_discord_notification(article)
        generated_articles.append(article)

    summary_html = render_summary_page(generated_articles)

    with open(os.path.join(ARTICLES_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(summary_html)

    git_push_updates()

    latest_status["last_run"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    latest_status["count"] = len(generated_articles)


@app.on_event("startup")
def startup_event():
    scheduler.add_job(generate_archive_articles, "interval", minutes=60)
    scheduler.start()


@app.get("/", response_class=HTMLResponse)
def dashboard():
    return f"""
    <html>
    <head>
        <title>AI Deals CMS</title>
        <style>
            body {{
                background: #000;
                color: white;
                font-family: Arial;
                padding: 50px;
            }}
            .card {{
                background: #111;
                border-radius: 24px;
                padding: 30px;
                max-width: 900px;
                margin: auto;
            }}
            button {{
                background: #0071e3;
                color: white;
                border: none;
                padding: 14px 22px;
                border-radius: 14px;
                cursor: pointer;
            }}
        </style>
    </head>
    <body>
        <div class="card">
            <h1>AI Deals CMS 管理画面</h1>
            <p>最終実行: {latest_status["last_run"]}</p>
            <p>生成記事数: {latest_status["count"]}</p>
            <p>Discord: {latest_status["discord"]}</p>
            <p>Git: {latest_status["git"]}</p>
            <p><a href="{CLOUDFLARE_PAGES_URL}" target="_blank">公開一覧を見る</a></p>
            <br><br>
            <a href="/scrape"><button>今すぐ記事生成</button></a>
        </div>
    </body>
    </html>
    """


@app.get("/scrape")
def scrape_now():
    generate_archive_articles()
    return {"message": "アーカイブ記事を生成して公開しました"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)