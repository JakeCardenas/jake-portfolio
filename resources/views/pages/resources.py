from config import site
from resources import content
from resources.views.components import headings, icons

LEDE = (
    "A hand-picked list of the resources I keep coming back to — for learning to "
    "build software, getting into AI engineering, and staying current. Free or "
    "freemium, and genuinely worth your time."
)


def group(entry, index):
    links = "\n".join(
        f"""              <a href="{link['href']}" target="_blank" rel="noopener" class="res-link">
                <span class="res-name">{link['name']}{icons.ARROW_RES}</span>
                <span class="res-desc">{link['description']}</span>
              </a>"""
        for link in entry["links"]
    )
    return f"""          <section class="res-group reveal" style="animation-delay: {0.05 * index:.2f}s">
            <h2 class="res-head mono">{entry['heading']}</h2>
            <div class="res-grid">
{links}
            </div>
          </section>"""


def render():
    groups = "\n".join(
        group(g, i) for i, g in enumerate(content.load("resources"), start=1)
    )
    return f"""        <section class="section reveal">
{headings.page("resources", LEDE)}
{groups}
          <p class="res-foot mono reveal" style="animation-delay: .4s">
            Missing something great? <a href="mailto:{site.EMAIL}">Send me a link →</a>
          </p>
        </section>
"""
