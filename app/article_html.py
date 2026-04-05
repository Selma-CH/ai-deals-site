import os


def save_article_html(article_title: str, article_content: str, article_path: str, affiliate_link: str):
    html = f"""
    <!DOCTYPE html>
    <html lang="ja">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{article_title}</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 40px auto;
                line-height: 1.8;
                padding: 20px;
            }}
            h1 {{
                color: #222;
            }}
            .btn {{
                display: inline-block;
                margin-top: 20px;
                padding: 12px 20px;
                background: #0070f3;
                color: white;
                text-decoration: none;
                border-radius: 8px;
            }}
        </style>
    </head>
    <body>
        <h1>{article_title}</h1>
        <p>{article_content}</p>
        <a class="btn" href="{affiliate_link}" target="_blank">商品リンクはこちら</a>
    </body>
    </html>
    """

    os.makedirs(os.path.dirname(article_path), exist_ok=True)

    with open(article_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"HTML保存: {article_path}")


def update_index_html(articles_path: str):
    files = [
        f for f in os.listdir(articles_path)
        if f.endswith(".html") and f != "index.html"
    ]

    links = ""
    for file in sorted(files, reverse=True):
        links += f'<li><a href="{file}">{file}</a></li>\n'

    index_html = f"""
    <!DOCTYPE html>
    <html lang="ja">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>AI Deals Site</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                max-width: 900px;
                margin: 40px auto;
                padding: 20px;
            }}
            h1 {{
                margin-bottom: 30px;
            }}
            li {{
                margin: 12px 0;
                font-size: 18px;
            }}
            a {{
                text-decoration: none;
                color: #0070f3;
            }}
        </style>
    </head>
    <body>
        <h1>最新セール記事一覧</h1>
        <ul>
            {links}
        </ul>
    </body>
    </html>
    """

    with open(os.path.join(articles_path, "index.html"), "w", encoding="utf-8") as f:
        f.write(index_html)

    print("index.html 更新完了")