import os
import subprocess
from fastapi import FastAPI
from apscheduler.schedulers.background import BackgroundScheduler
from discord_webhook import DiscordWebhook
from app.scraper import scrape_websites
from app.models import Article, engine, Base, SessionLocal
from app.article_html import save_article_html, update_index_html
import uvicorn

# ------------------------------
# DB 初期化
# ------------------------------
Base.metadata.create_all(bind=engine)

app = FastAPI()

# ------------------------------
# 設定
# ------------------------------
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1490044762789777639/d--WHejO5pXv9gqF9rHkddPNa_Ck9N6WYLeP60RqVCrfkfSj8RpPdrxffwe41B-n7Azc"
AMAZON_ASSOCIATE_LINK = "https://amzn.to/4duD1JY"

# 🚨 ここは固定URLを使う
CLOUDFLARE_PAGES_URL = "https://ai-deals-site.pages.dev"

GIT_REPO_PATH = r"E:\ai-deals-site\.git"
ARTICLES_PATH = os.path.join(os.path.dirname(__file__), "articles")

scheduler = BackgroundScheduler()

# ------------------------------
# Discord通知
# ------------------------------
def notify_discord(title: str, article_id: int):
    # pretty URL対応
    url = f"{CLOUDFLARE_PAGES_URL}/{article_id}"

    content = f"🆕 新しい記事が公開されました！\n**{title}**\n{url}"

    webhook = DiscordWebhook(url=DISCORD_WEBHOOK_URL, content=content)
    response = webhook.execute()

    if response.status_code not in [200, 204]:
        print("Discord通知失敗:", response.status_code, response.content)

# ------------------------------
# DB保存
# ------------------------------
def generate_article(title: str, content: str) -> Article:
    session = SessionLocal()
    try:
        article = Article(title=title, content=content)
        session.add(article)
        session.commit()
        session.refresh(article)
        return article
    finally:
        session.close()

# ------------------------------
# GitHub push
# ------------------------------
def push_to_github():
    try:
        repo_dir = os.path.dirname(GIT_REPO_PATH)

        subprocess.run(["git", "-C", repo_dir, "add", "."], check=True)
        subprocess.run(
            ["git", "-C", repo_dir, "commit", "-m", "Update articles"],
            check=True
        )
        subprocess.run(["git", "-C", repo_dir, "push"], check=True)

        print("✅ GitHub push 完了")

    except subprocess.CalledProcessError as e:
        print("❌ Git push エラー:", e)

# ------------------------------
# スクレイピング実行
# ------------------------------
def scheduled_scrape():
    articles = scrape_websites()
    print(f"取得記事数: {len(articles)}")

    for article in articles:
        db_article = generate_article(article["title"], article["content"])

        article_filename = f"{db_article.id}.html"
        article_path = os.path.join(ARTICLES_PATH, article_filename)

        save_article_html(
            article_title=db_article.title,
            article_content=db_article.content,
            article_path=article_path,
            affiliate_link=AMAZON_ASSOCIATE_LINK
        )

        # Discord通知（IDベース）
        notify_discord(db_article.title, db_article.id)

    # index更新
    update_index_html(ARTICLES_PATH)

    # GitHub push
    push_to_github()

# ------------------------------
# 起動時スケジューラ
# ------------------------------
@app.on_event("startup")
def startup_event():
    scheduler.add_job(scheduled_scrape, "interval", minutes=60)
    scheduler.start()

# ------------------------------
# API
# ------------------------------
@app.get("/")
def root():
    return {"message": "AI Deals Site is running"}

@app.post("/scrape/")
def scrape_now():
    try:
        scheduled_scrape()
        return {"message": "記事生成が完了しました"}
    except Exception as e:
        return {"error": str(e)}

# ------------------------------
# 起動
# ------------------------------
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8001)