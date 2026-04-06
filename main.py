import os
import json
import requests
import subprocess
from datetime import datetime
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from apscheduler.schedulers.background import BackgroundScheduler

from scraper.scraper import fetch_sale_articles
from generator.article_generator import render_article_page

# ===== 固定設定 =====
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1490044762789777639/d--WHejO5pXv9gqF9rHkddPNa_Ck9N6WYLeP60RqVCrfkfSj8RpPdrxffwe41B-n7Azc"
BASE_DIR = r"E:\ai-deals-site"
GIT_REPO_PATH = BASE_DIR
CLOUDFLARE_PAGES_URL = "https://ai-deals-site.pages.dev/"
ARTICLES_DIR = os.path.join(BASE_DIR, "articles")
LATEST_HTML = os.path.join(ARTICLES_DIR, "index.html")

os.makedirs(ARTICLES_DIR, exist_ok=True)

app = FastAPI()
scheduler = BackgroundScheduler()

latest_status = {
    "last_run": "未実行",
    "title": "なし",
    "cloudflare_url": CLOUDFLARE_PAGES_URL,
    "discord": "未送信",
    "git": "未実行",
}


def save_latest_article(html: str):
    with open(LATEST_HTML, "w", encoding="utf-8") as f:
        f.write(html)
    print("HTML保存:", LATEST_HTML)


def send_discord_notification(title: str):
    payload = {
        "content": f"🆕 新着セール記事\n**{title}**\n{CLOUDFLARE_PAGES_URL}"
    }

    res = requests.post(
        DISCORD_WEBHOOK_URL,
        data=json.dumps(payload),
        headers={"Content-Type": "application/json"},
        timeout=20,
    )

    latest_status["discord"] = f"{res.status_code}"
    print("Discord:", res.status_code)


def git_push_updates():
    try:
        subprocess.run(["git", "-C", GIT_REPO_PATH, "add", "."], check=True)
        subprocess.run(
            ["git", "-C", GIT_REPO_PATH, "commit", "-m", "Auto update latest sale article"],
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


def generate_latest_article():
    articles = fetch_sale_articles()

    if not articles:
        latest_status["title"] = "記事なし"
        return

    article = articles[0]  # 最新1件のみ
    article["id"] = 1

    html = render_article_page(article, [article])

    save_latest_article(html)
    send_discord_notification(article["title"])
    git_push_updates()

    latest_status["last_run"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    latest_status["title"] = article["title"]


@app.on_event("startup")
def startup_event():
    scheduler.add_job(generate_latest_article, "interval", minutes=60)
    scheduler.start()


@app.get("/", response_class=HTMLResponse)
def dashboard():
    return f"""
    <html>
    <head>
        <title>AI Deals CMS</title>
        <style>
            body {{
                background: #0a0a0a;
                color: white;
                font-family: Arial;
                padding: 50px;
            }}
            .card {{
                background: #1c1c1e;
                padding: 30px;
                border-radius: 24px;
                max-width: 900px;
                margin: auto;
            }}
            a {{
                color: #4da3ff;
            }}
            button {{
                padding: 14px 24px;
                border-radius: 12px;
                border: none;
                background: #4da3ff;
                color: white;
                cursor: pointer;
                font-size: 16px;
            }}
        </style>
    </head>
    <body>
        <div class="card">
            <h1>AI Deals CMS 管理画面</h1>
            <p>最終生成: {latest_status["last_run"]}</p>
            <p>最新記事: {latest_status["title"]}</p>
            <p>Discord: {latest_status["discord"]}</p>
            <p>Git: {latest_status["git"]}</p>
            <p><a href="{CLOUDFLARE_PAGES_URL}" target="_blank">公開サイトを見る</a></p>
            <br>
            <a href="/scrape"><button>今すぐ記事生成</button></a>
        </div>
    </body>
    </html>
    """


@app.get("/scrape")
def scrape_now():
    generate_latest_article()
    return {"message": "最新記事を生成して公開しました"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)