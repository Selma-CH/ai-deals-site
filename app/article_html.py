import os

def save_article_html(article_id: int, html_content: str):
    """
    HTMLファイルを保存する関数
    - article_id: HTMLファイル名に使うID
    - html_content: ファイルに書き込むHTML文字列
    """
    # 保存先フォルダ
    output_dir = os.path.join(os.path.dirname(__file__), '..', 'articles')
    os.makedirs(output_dir, exist_ok=True)

    # ファイルパス作成
    file_path = os.path.join(output_dir, f"{article_id}.html")

    # HTML保存
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"HTML保存: {file_path}")
    return file_path
