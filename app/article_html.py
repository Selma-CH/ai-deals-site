import os

ARTICLES_DIR = r"E:\ai-deals-site\articles"
os.makedirs(ARTICLES_DIR, exist_ok=True)


def save_article_html(article_id: int, title: str, html_content: str):
    article_path = os.path.join(ARTICLES_DIR, f"{article_id}.html")

    with open(article_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"HTML保存: {article_path}")
    return article_path