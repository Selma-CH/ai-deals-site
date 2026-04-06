from .parsers import parse_rss_feed, parse_sale_page
import json
import os


def fetch_sale_articles():
    base = os.path.dirname(__file__)
    sites_path = os.path.join(base, "sites.json")

    with open(sites_path, "r", encoding="utf-8") as f:
        sites = json.load(f)

    results = []

    for site in sites:
        site_type = site.get("type")
        url = site.get("url")

        try:
            if site_type == "rss":
                results.extend(parse_rss_feed(url))
            else:
                results.extend(parse_sale_page(url))
        except Exception as e:
            print("取得失敗:", url, e)

    return results