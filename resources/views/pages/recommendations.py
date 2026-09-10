from config import site
from resources import content
from resources.views.components import headings, media

LEDE = "What the people I have studied and built with say about working together."

EMPTY = (
    "No recommendations published yet. If we have worked together and you would "
    f'like to add one, <a href="mailto:{site.EMAIL}?subject=Recommendation">get in touch</a>.'
)


def card(entry):
    mark = ""
    if entry.get("avatar"):
        mark = (
            '            <span class="rec-mark" aria-hidden="true">'
            f'{media.img(entry["avatar"], sizes="44px")}</span>\n'
        )
    meta = [entry["role"], entry.get("organization", "")]
    line = " · ".join(part for part in meta if part)
    source = ""
    if entry.get("source"):
        source = (
            f'\n              <a href="{entry["source"]}" target="_blank" '
            'rel="noopener" class="rec-source mono">VIEW SOURCE '
            '<span aria-hidden="true">↗</span></a>'
        )
    relationship = ""
    if entry.get("relationship"):
        relationship = (
            f'\n              <span class="rec-relationship mono">'
            f'{entry["relationship"]}</span>'
        )
    return f"""          <figure class="rec-card reveal">
            <blockquote class="rec-quote">{entry['quote']}</blockquote>
{mark}            <figcaption class="rec-by">
              <span class="rec-name">{entry['name']}</span>
              <span class="rec-role">{line}</span>{relationship}{source}
            </figcaption>
          </figure>"""


def render():
    entries = content.load("recommendations")
    if entries:
        body = (
            '          <div class="rec-grid">\n'
            + "\n".join(card(e) for e in entries)
            + "\n          </div>"
        )
    else:
        body = f'          <p class="section-empty mono">{EMPTY}</p>'
    return f"""        <section class="section reveal">
{headings.page("recommendations", LEDE)}
{body}
        </section>
"""
