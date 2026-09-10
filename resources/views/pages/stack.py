from resources import content
from resources.views.components import headings

LEDE = (
    "The languages, frameworks and tools I reach for — across the front end, "
    "back end, data, and AI."
)


def group(item):
    tags = "\n".join(
        f'              <span class="stack-tag mono">{t}</span>' for t in item["items"]
    )
    return f"""          <section class="stack-group reveal">
            <h2 class="stack-head mono">{item['label']}</h2>
            <div class="stack-tags">
{tags}
            </div>
          </section>"""


def render():
    groups = "\n".join(group(g) for g in content.load("stack"))
    return f"""        <section class="section reveal">
{headings.page("stack", LEDE)}
{groups}
        </section>
"""
