import os
import subprocess
from fastapi import FastAPI
from apscheduler.schedulers.background import BackgroundScheduler
from discord_webhook import DiscordWebhook
from app.scraper import scrape_websites
from app.models import Article, engine, Base, SessionLocal
from app.article_html import save_article_html, update_index_html
import uvicorn

Base.metadata.create_all(bind=engine)

app = FastAPI()

DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1490044762789777639/d--WHejO5pXv9gqF9rHkddPNa_Ck9N6WYLeP60RqVCrfkfSj8RpPdrxffwe41B-n7Azc"
AMAZON_ASSOCIATE_LINK = "https://amzn.to/4duD1JY"
CLOUDFLARE_PAGES_URL = "https://8f17296a.ai-deals-site.pages.dev"
GIT_REPO_PATH = r"E:\ai-deals-site\.git"

ARTICLES_PATH = os.path.join(os.path.dirname(__file__), "articles")

scheduler = BackgroundScheduler()


def notify_discord(title: str, filename: str):
    url = f"{CLOUDFLARE_PAGES_URL}/{filename}"
    content = f"🆕 新しい記事が公開されました！\n**{title}**\n{url}"

    webhook = DiscordWebhook(url=DISCORD_WEBHOOK_URL, content=content)
    response = webhook.execute()

    if response.status_code not in [200, 204]:
        print("Discord通知失敗:", response.status_code, response.content)


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

        notify_discord(db_article.title, article_filename)

    update_index_html(ARTICLES_PATH)

    try:
        subprocess.run(
            ["git", "-C", os.path.dirname(GIT_REPO_PATH), "add", "."],
            check=True
        )
        subprocess.run(
            ["git", "-C", os.path.dirname(GIT_REPO_PATH), "commit", "-m", "Update articles"],
            check=True
        )
        subprocess.run(
            ["git", "-C", os.path.dirname(GIT_REPO_PATH), "push"],
            check=True
        )
        print("GitHub push 完了")
    except subprocess.CalledProcessError as e:
        print("Git push エラー:", e)


@app.on_event("startup")
def startup_event():
    scheduler.add_job(scheduled_scrape, "interval", minutes=60)
    scheduler.start()


@app.get("/")
def read_root():
    return {"message": "AI Deals Site is running!"}


@app.post("/scrape/")
def scrape_now():
    try:
        scheduled_scrape()
        return {"message": "記事生成が完了しました"}
    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8001)