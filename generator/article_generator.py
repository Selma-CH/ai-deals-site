from jinja2 import Environment, FileSystemLoader
import os

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "../templates")
env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))


def render_article_page(article, all_articles):
    template = env.get_template("article.html")
    return template.render(article=article, all_articles=all_articles)