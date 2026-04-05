def scrape_websites():
    articles = []

    # サンプル記事
    articles.append({
        "title": "Steamで人気ゲームがセール中",
        "content": "今だけ人気ゲームが50%OFFで購入できます。"
    })

    articles.append({
        "title": "UdemyのAI講座が期間限定セール",
        "content": "PythonとAI自動化を学べる講座が激安です。"
    })

    return articles
from app.article_html import save_article_html, update_index_html