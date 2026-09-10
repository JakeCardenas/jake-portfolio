import os

from config import site
from resources import content
from resources.views.components import headings, icons

LEDE = "Things I have made and put up for download."

PUBLIC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../../public")


def available(item):
    return os.path.exists(os.path.join(PUBLIC, item["file"]))


def card(item, delay):
    shot = (
        f'<img src="{site.asset(item["shot"])}" alt="{item["name"]} preview" loading="lazy" />'
        if os.path.exists(os.path.join(PUBLIC, item["shot"]))
        else icons.DOC
    )
    return f"""            <a class="shop-card reveal" href="{site.url('shop/' + item['slug'])}"
               style="animation-delay: {delay}s">
              <span class="shop-shot">
                {shot}
                <span class="shop-badge mono">{item['badge']}</span>
              </span>
              <span class="shop-body">
                <span class="shop-kind mono">{item['kind']}</span>
                <span class="shop-name">{item['name']}</span>
              </span>
            </a>"""


def render():
    items = [i for i in content.load("shop") if available(i)]
    if items:
        cards = "\n".join(
            card(item, round(0.04 * (n + 1), 2)) for n, item in enumerate(items)
        )
        inner = f'          <div class="shop-grid">\n{cards}\n          </div>'
    else:
        inner = '          <p class="shop-empty mono">Nothing here yet.</p>'
    return f"""        <section class="section reveal">
{headings.page("shop", LEDE)}
{inner}
        </section>
"""
