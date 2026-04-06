import os, random, json
from fastapi import FastAPI
from apscheduler.schedulers.background import BackgroundScheduler
from app.scraper import scrape_websites
from app.article_generator import generate_article_html, generate_summary_page
from app.affiliate import get_affiliate_link
from discord_webhook import DiscordWebhook
from git import Repo

# --------------------------
# 設定
# --------------------------
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1490044762789777639/d--WHejO5pXv9gqF9rHkddPNa_Ck9N6WYLeP60RqVCrfkfSj8RpPdrxffwe41B-n7Azc"
GIT_REPO_PATH = r"E:\ai-deals-site\.git"
CLOUDFLARE_PAGES_URL = "https://ai-deals-site.pages.dev/"
ARTICLES_PATH = os.path.join(os.path.dirname(__file__), "articles")
SUMMARIES_PATH = os.path.join(os.path.dirname(__file__), "summaries")

os.makedirs(ARTICLES_PATH, exist_ok=True)
os.makedirs(SUMMARIES_PATH, exist_ok=True)

app = FastAPI()
scheduler = BackgroundScheduler()

# --------------------------
# 記事生成関数
# --------------------------
def generate_articles():
    articles_data = scrape_websites()
    all_articles = []
    for idx, article in enumerate(articles_data, start=1):
        article['id'] = idx
        article['affiliate_link'] = get_affiliate_link(article['title'])
        html = generate_article_html(article, articles_data)
        filename = os.path.join(ARTICLES_PATH, f"{idx}.html")
        with open(filename, "w", encoding="utf-8") as f:
            f.write(html)
        all_articles.append(article)

    # まとめページ生成
    summary_html = generate_summary_page(all_articles)
    summary_file = os.path.join(SUMMARIES_PATH, "index.html")
    with open(summary_file, "w", encoding="utf-8") as f:
        f.write(summary_html)

    # Discord通知
    webhook = DiscordWebhook(url=DISCORD_WEBHOOK_URL, content=f"記事生成が完了しました！まとめページ: {CLOUDFLARE_PAGES_URL}summaries/index.html")
    webhook.execute()

    # Git Push
    repo = Repo(GIT_REPO_PATH)
    repo.git.add(ARTICLES_PATH)
    repo.git.add(SUMMARIES_PATH)
    repo.index.commit(f"Update articles and summary")
    origin = repo.remote(name='origin')
    origin.push()

# --------------------------
# スケジューラで定期実行（毎日1回など）
# --------------------------
scheduler.add_job(generate_articles, 'interval', hours=24)
scheduler.start()

@app.get("/")
def root():
    return {"message": "AI Deals Site is running!"}