def save_article_html(article_id: int, html_content: str):
    """
    HTMLファイルを articles/ に保存する
    """
    import os
    ARTICLES_PATH = os.path.join(os.path.dirname(__file__), "..", "articles")
    os.makedirs(ARTICLES_PATH, exist_ok=True)
    file_path = os.path.join(ARTICLES_PATH, f"{article_id}.html")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    return file_path