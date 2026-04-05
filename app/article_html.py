import os

def save_article_html(article_title: str, article_content: str, article_path: str, affiliate_link: str, images=[]):
    # 画像タグ生成
    html_images = "".join([f'<img src="{url}" alt="{article_title}" class="article-img">' for url in images])
    
    html_content = f"""
    <html>
    <head>
        <meta charset="utf-8">
        <title>{article_title}</title>
        <link rel="stylesheet" href="/styles.css">
    </head>
    <body>
        <h1>{article_title}</h1>
        {html_images}
        <p>{article_content}</p>
        <p>購入はこちら: <a href="{affiliate_link}" target="_blank">Amazonリンク</a></p>
    </body>
    </html>
    """
    os.makedirs(os.path.dirname(article_path), exist_ok=True)
    with open(article_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"HTML保存: {article_path}")
    return article_path