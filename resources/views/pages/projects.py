from config import site
from resources import content
from resources.views.components import headings

LEDE = "Things I've built — full-stack apps, AI work, and design."

SEPARATOR = '<span class="meta-sep">·</span>'


def card(item):
    icon = ""
    if item.get("icon"):
        icon = f"""              <img
                class="spot-icon"
                src="{site.asset(item['icon']['src'])}"
                alt="{item['icon']['alt']}"
                loading="lazy"
              />
"""
    note = ""
    if item.get("note"):
        n = item["note"]
        note = f"""
            <div class="stack-note edge-fade-divider">
              <span class="stack-note-label mono">{n['label']}</span>
              <a href="{n['href']}" target="_blank" rel="noopener" class="stack-note-link mono">{n['text']} ↗</a>
            </div>"""
    meta = SEPARATOR.join(item["meta"])
    return f"""          <article class="spot-card reveal">
            <div class="spot-head">
{icon}              <div class="spot-text">
                <div class="entry-meta mono">{meta}</div>
                <h3 class="entry-title">{item['title']}</h3>
                <p class="entry-body">{item['body']}</p>
              </div>
            </div>
            <div class="spot-actions">
              <a
                href="{item['link']['href']}"
                target="_blank"
                rel="noopener"
                class="link-out mono"
              >
                {item['link']['label']} <span aria-hidden="true">↗</span>
              </a>
            </div>{note}
          </article>"""


def render():
    cards = "\n".join(card(p) for p in content.load("projects"))
    return f"""        <section class="section reveal">
{headings.page("projects", LEDE)}
{cards}
        </section>
"""
