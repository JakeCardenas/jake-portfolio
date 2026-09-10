from resources import content
from resources.views.components import headings, icons, media

LEDE = (
    "The hardware I actually use day to day — desk setup, everyday carry, "
    "and the camera I shoot on."
)

SHOT_SIZES = "(min-width: 641px) 222px, 172px"


def item(entry):
    tag = "a" if entry["href"] else "div"
    attrs = f' href="{entry["href"]}" target="_blank" rel="noopener"' if entry["href"] else ""
    arrow = icons.ARROW_OUT if entry["href"] else ""
    return f"""              <{tag} class="gear-item"{attrs}>
                <span class="gear-shot">
                  {media.img(entry['image'], sizes=SHOT_SIZES, alt=entry['name'])}
                </span>
                <span class="gear-body">
                  <span class="gear-head">
                    <span class="gear-name">{entry['name']}</span>{arrow}
                  </span>
                  <span class="gear-meta">{entry['meta']}</span>
                </span>
              </{tag}>"""


def group(entry, index):
    items = "\n".join(item(i) for i in entry["items"])
    return f"""          <section class="gear-group reveal" style="animation-delay: {0.05 * index:.2f}s">
            <h2 class="gear-group-head mono">{entry['heading']}</h2>
            <div class="gear-grid">
{items}
            </div>
          </section>"""


def render():
    groups = "\n".join(
        group(g, i) for i, g in enumerate(content.load("gear"), start=1)
    )
    return f"""        <section class="section reveal">
{headings.page("gear", LEDE)}
{groups}
        </section>
"""
