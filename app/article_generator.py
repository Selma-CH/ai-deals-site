import random
import os
from datetime import datetime

def generate_article_html(title: str, content: str, affiliate_link: str) -> str:
    """
    記事内容に応じて HTML/CSS/JS を自動生成
    """

    # ランダムカラー・フォントなどで高級感
    bg_color = random.choice(["#fefefe", "#ffffff", "#f4f4f8"])
    accent_color = random.choice(["#0070f3", "#ff6f61", "#00c853"])
    font_family = random.choice(["'Helvetica Neue', Helvetica, Arial, sans-serif",
                                 "'Roboto', sans-serif",
                                 "'Inter', sans-serif"])
    image_url = f"https://picsum.photos/seed/{random.randint(1,1000)}/1200/600"

    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    html = f"""
    <!DOCTYPE html>
    <html lang="ja">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{title}</title>
        <style>
            body {{
                margin:0;
                padding:0;
                font-family:{font_family};
                background-color:{bg_color};
                color:#111;
                overflow-x:hidden;
            }}
            header {{
                width:100%;
                height:60vh;
                background: url('{image_url}') center/cover no-repeat;
                display:flex;
                align-items:center;
                justify-content:center;
                color:white;
                font-size:3rem;
                text-shadow: 0 0 20px rgba(0,0,0,0.7);
                transition: transform 1s ease;
            }}
            main {{
                padding:2rem;
                max-width:900px;
                margin:auto;
            }}
            article {{
                margin-bottom:3rem;
            }}
            h1,h2 {{
                color:{accent_color};
            }}
            a.affiliate {{
                display:inline-block;
                padding:0.5rem 1rem;
                background:{accent_color};
                color:white;
                text-decoration:none;
                border-radius:6px;
                transition:0.3s;
            }}
            a.affiliate:hover {{
                opacity:0.8;
            }}
        </style>
    </head>
    <body>
        <header id="hero">{title}</header>
        <main>
            <article>
                <p>{content}</p>
                <p><a class="affiliate" href="{affiliate_link}" target="_blank">チェックする</a></p>
                <p>公開日時: {now}</p>
            </article>
        </main>
        <script>
            // スクロールでヘッダー拡大縮小
            const hero = document.getElementById('hero');
            window.addEventListener('scroll', () => {{
                hero.style.transform = 'translateY(' + window.scrollY * 0.5 + 'px)';
            }});
        </script>
    </body>
    </html>
    """
    return html