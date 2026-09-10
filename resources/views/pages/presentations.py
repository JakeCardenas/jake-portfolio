from config import site
from resources import content
from resources.views.components import headings

LEDE = (
    "Slide decks, capstone material and project walkthroughs from the work on "
    "this site."
)

EMPTY = (
    "No presentation material published yet. Decks and recordings will appear "
    "here as they are added."
)

KINDS = {
    "capstone": "CAPSTONE",
    "project": "PROJECT",
    "technical": "TECHNICAL",
    "demo": "DEMONSTRATION",
    "talk": "TALK",
}

LINKS = (
    ("deck", "VIEW DECK"),
    ("slides", "OPEN SLIDES"),
    ("video", "WATCH"),
    ("demo", "LIVE DEMO"),
)


def card(entry):
    meta = [KINDS.get(entry.get("kind", ""), "")]
    for key in ("date", "venue"):
        if entry.get(key):
            meta.append(entry[key])
    meta_line = '<span class="meta-sep">·</span>'.join(part for part in meta if part)

    actions = "\n".join(
        f'              <a href="{entry[key]}" target="_blank" rel="noopener" '
        f'class="link-out mono">{label} <span aria-hidden="true">↗</span></a>'
        for key, label in LINKS
        if entry.get(key)
    )
    if actions:
        actions = f'\n            <div class="pres-actions">\n{actions}\n            </div>'
    else:
        actions = (
            '\n            <p class="pres-pending mono">Material not published yet</p>'
        )

    summary = ""
    if entry.get("summary"):
        summary = f'\n              <p class="entry-body">{entry["summary"]}</p>'
    project = ""
    if entry.get("project"):
        project = (
            f'\n              <span class="pres-project mono">{entry["project"]}</span>'
        )

    return f"""          <article class="pres-card reveal">
            <div class="pres-head">
              <div class="entry-meta mono">{meta_line}</div>
              <h2 class="entry-title">{entry['title']}</h2>{project}{summary}
            </div>{actions}
          </article>"""


def render():
    entries = content.load("presentations")
    if entries:
        body = (
            '          <div class="pres-list">\n'
            + "\n".join(card(e) for e in entries)
            + "\n          </div>"
        )
    else:
        body = f'          <p class="section-empty mono">{EMPTY}</p>'
    return f"""        <section class="section reveal">
{headings.page("presentations", LEDE)}
{body}
        </section>
"""
