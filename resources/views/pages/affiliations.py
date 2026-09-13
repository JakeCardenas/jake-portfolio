import re
from urllib.parse import urlparse

from resources import content
from resources.views.components import headings, media

LEDE = "Programs and communities I'm part of."

ARROW = (
    '<svg viewBox="0 0 16 16" fill="none" aria-hidden="true">'
    '<path d="M5 11L11 5M11 5H6M11 5V10" stroke="currentColor" stroke-width="1.5" '
    'stroke-linecap="round" stroke-linejoin="round"/></svg>'
)


def acronym(name):
    words = re.sub(r"&\w+;", " ", name).split()
    return "".join(w[0] for w in words if w[0].isalnum()).upper()


def card(item):
    if item["href"]:
        domain = urlparse(item["href"]).netloc.removeprefix("www.")
        open_tag = f'<a href="{item["href"]}" target="_blank" rel="noopener" class="aff-card">'
        close_tag = "</a>"
        link = f'\n                <span class="aff-link mono">{domain} {ARROW}</span>'
    else:
        open_tag = '<div class="aff-card">'
        close_tag = "</div>"
        link = ""
    logo = media.img(item["logo"], sizes="56px", cls="aff-mark")
    return f"""            {open_tag}
              <span class="aff-watermark" aria-hidden="true">{acronym(item['name'])}</span>
              <div class="aff-halftone" aria-hidden="true"></div>
              <div class="aff-inner">
                {logo}
                <div class="aff-text">
                  <span class="aff-tag mono">{item['role']}</span>
                  <h2 class="aff-name">{item['name']}</h2>{link}
                </div>
              </div>
            {close_tag}"""


def render():
    cards = "\n".join(card(item) for item in content.load("affiliations"))
    return f"""        <section class="section reveal">
{headings.page("affiliations", LEDE, lede_gap="3rem")}
          <div class="aff-list">
{cards}
          </div>
        </section>
"""
