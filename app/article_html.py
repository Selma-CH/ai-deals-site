import os

def save_article_html(article_title: str, article_content: str, article_path: str, affiliate_link: str):
    html_content = f"""
    <html>
    <head>
        <meta charset="UTF-8">
        <title>{article_title}</title>
    </head>
    <body>
        <h1>{article_title}</h1>
        <p>{article_content}</p>
        <a href="{affiliate_link}">Amazonリンク</a>
    </body>
    </html>
    """

    os.makedirs(os.path.dirname(article_path), exist_ok=True)

    with open(article_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"HTML保存: {article_path}")
    return article_path