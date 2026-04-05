import os
import subprocess
from fastapi import FastAPI
from apscheduler.schedulers.background import BackgroundScheduler
from discord_webhook import DiscordWebhook
from app.scraper import scrape_websites
from app.models import Article, engine, Base, SessionLocal
from app.article_html import save_article_html
import uvicorn

# ------------------------------
# DB初期化
# ------------------------------
Base.metadata.create_all(bind=engine)

# ------------------------------
# FastAPIアプリ
# ------------------------------
app = FastAPI()

# ------------------------------
# 設定
# ------------------------------
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/xxx/yyy"
AMAZON_ASSOCIATE_LINK = "https://amzn.to/4duD1JY"
GIT_REPO_PATH = r"E:\ai-deals-site\.git"  # 正しいパスに修正
CLOUDFLARE_PAGES_URL = "https://1497f113.ai-deals-site.pages.dev"
ARTICLES_PATH = os.path.join(os.path.dirname(__file__), "articles")

# ------------------------------
# スケジューラ
# ------------------------------
scheduler = BackgroundScheduler()

# ------------------------------
# Discord通知
# ------------------------------
def notify_discord(title: str, url: str):
    content = f"新しい記事が公開されました: [{title}]({url})\nアフィリエイトリンク: {AMAZON_ASSOCIATE_LINK}"
    webhook = DiscordWebhook(url=DISCORD_WEBHOOK_URL, content=content)
    response = webhook.execute()
    if response.status_code != 204:
        print(f"Discord通知に失敗しました: {response.status_code}, {response.content}")

# ------------------------------
# DBに記事保存
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
# スクレイピング＆記事生成
# ------------------------------
def scheduled_scrape():
    articles = scrape_websites()
    print(f"取得記事数: {len(articles)}")

    for article in articles:
        # DBに保存
        db_article = generate_article(article["title"], article["content"])

        # HTML生成
        article_filename = f"{db_article.id}.html"
        article_path = os.path.join(ARTICLES_PATH, article_filename)
        save_article_html(
            article_title=db_article.title,
            article_content=db_article.content,
            article_path=article_path,
            affiliate_link=AMAZON_ASSOCIATE_LINK
        )
        print("HTML保存:", article_path)

        # Discord通知
        notify_discord(
            db_article.title,
            f"{CLOUDFLARE_PAGES_URL}/articles/{article_filename}"
        )

        # Git push
        try:
            subprocess.run(["git", "-C", os.path.dirname(GIT_REPO_PATH), "add", "."], check=True)
            subprocess.run(["git", "-C", os.path.dirname(GIT_REPO_PATH), "commit", "-m", f"Add article {db_article.id}"], check=True)
            subprocess.run(["git", "-C", os.path.dirname(GIT_REPO_PATH), "push"], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Git push エラー: {e}")

# ------------------------------
# FastAPI起動時にスケジューラ開始
# ------------------------------
@app.on_event("startup")
def startup_event():
    scheduler.add_job(scheduled_scrape, "interval", minutes=60)
    scheduler.start()

# ------------------------------
# ルート
# ------------------------------
@app.get("/")
def read_root():
    return {"message": "AI Deals Site is running!"}

# ------------------------------
# 手動でスクレイプ
# ------------------------------
@app.post("/scrape/")
def scrape_now():
    try:
        scheduled_scrape()
        return {"message": "記事生成が完了しました"}
    except Exception as e:
        return {"error": str(e)}

# ------------------------------
# Uvicorn起動
# ------------------------------
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8001, reload=False)