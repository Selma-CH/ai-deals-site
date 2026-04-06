import os
from jinja2 import Environment, FileSystemLoader

env = Environment(loader=FileSystemLoader("templates"))

def generate_article_html(article: dict, all_articles: list) -> str:
    template = env.get_template("article_template.html")
    return template.render(article=article, all_articles=all_articles)

def generate_summary_page(all_articles: list) -> str:
    template = env.get_template("summary_template.html")
    return template.render(all_articles=all_articles)