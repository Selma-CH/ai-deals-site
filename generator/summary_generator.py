from jinja2 import Environment, FileSystemLoader
import os

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "../templates")
env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))


def render_summary_page(all_articles):
    template = env.get_template("summary.html")
    return template.render(all_articles=all_articles)