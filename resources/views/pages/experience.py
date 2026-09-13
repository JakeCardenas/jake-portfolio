import re

from resources import content
from resources.views.components import headings

LEDE = "Where I've been — the full entries, with what I worked on."

CHIPS_SHOWN = 2
SMALL_WORDS = {"of", "and", "the", "&amp;", "&"}


def plain(html):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html)).strip()


def initials(org):
    words = [w for w in plain(org).split() if w.lower() not in SMALL_WORDS]
    return "".join(w[0] for w in words[:2]).upper()


def entry(item, last):
    meta = item.get("meta") or []
    dates = f'\n                  <p class="xp-dates mono">{meta[0]}</p>' if meta else ""
    place = f'\n              <p class="xp-place mono">{meta[1]}</p>' if len(meta) > 1 else ""
    body = (
        f'\n                  <div class="xp-body">\n                    <p>{item["body"]}</p>\n                  </div>'
        if item.get("body")
        else ""
    )
    chips = ""
    if item.get("chips"):
        shown = "\n".join(
            f'                    <span class="xp-chip mono">{c}</span>'
            for c in item["chips"][:CHIPS_SHOWN]
        )
        extra = len(item["chips"]) - CHIPS_SHOWN
        if extra > 0:
            shown += (
                f'\n                    <span class="xp-chip xp-chip--more mono">'
                f'+{extra} skill{"s" if extra > 1 else ""}</span>'
            )
        chips = f'\n                  <div class="xp-chips">\n{shown}\n                  </div>'
    rail = "" if last else '\n              <div class="xp-line"></div>'
    return f"""          <div class="xp-item{' xp-item--last' if last else ''}">
            <div class="xp-rail">
              <div class="xp-mark">{initials(item['org'])}</div>{rail}
            </div>
            <div class="xp-content">
              <h2 class="xp-org">{item['org']}</h2>
              <p class="xp-kind mono">{item['year']}</p>{place}
              <div class="xp-roles">
                <div class="xp-role">
                  <h3 class="xp-title">{item['title']}</h3>{dates}{body}{chips}
                </div>
              </div>
            </div>
          </div>"""


def render():
    items = content.load("experience")
    entries = "\n".join(entry(item, i == len(items) - 1) for i, item in enumerate(items))
    return f"""        <section class="section reveal">
{headings.page("experience", LEDE, lede_gap="3.5rem")}
          <div class="xp-timeline">
{entries}
          </div>
        </section>
"""
