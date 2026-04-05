import os

def save_article_html(article_title: str, article_content: str, article_path: str, affiliate_link: str):
    html = f"""
    <html>
    <head><title>{article_title}</title></head>
    <body>
        {article_content}
        <br><a href="{affiliate_link}">商品リンク</a>
    </body>
    </html>
    """
    os.makedirs(os.path.dirname(article_path), exist_ok=True)
    with open(article_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"HTML保存: {article_path}")