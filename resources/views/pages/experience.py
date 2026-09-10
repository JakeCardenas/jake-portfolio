from resources import content
from resources.views.components import headings

LEDE = "Where I've been — the full entries, with what I worked on."

SEPARATOR = '<span class="meta-sep">·</span>'


def entry(item):
    parts = [
        f'                <h3 class="entry-title">{item["title"]}</h3>',
        f'                <div class="tl-org">{item["org"]}</div>',
    ]
    if item.get("meta"):
        meta = SEPARATOR.join(item["meta"])
        parts.append(f'                <div class="entry-meta mono">{meta}</div>')
    if item.get("body"):
        parts.append(f'                <p class="entry-body">{item["body"]}</p>')
    if item.get("chips"):
        chips = "\n".join(
            f'                  <span class="chip mono">{c}</span>'
            for c in item["chips"]
        )
        parts.append(f'                <div class="chip-row">\n{chips}\n                </div>')
    body = "\n".join(parts)
    return f"""            <li class="tl-item">
              <div class="tl-year mono">{item['year']}</div>
              <div class="tl-card">
{body}
              </div>
            </li>"""


def render():
    entries = "\n".join(entry(item) for item in content.load("experience"))
    return f"""        <section class="section reveal">
{headings.page("experience", LEDE)}
          <ol class="timeline stagger">
{entries}
          </ol>
        </section>
"""
