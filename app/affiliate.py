def get_affiliate_link(title: str) -> str:
    """
    タイトル内容に沿ったAmazonリンクを生成
    実際はAmazon API等で取得可能
    """
    keyword = title.split()[0] if title else "book"
    return f"https://amzn.to/4c1Yyas?tag={keyword}"