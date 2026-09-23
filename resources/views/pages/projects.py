from resources import content
from resources.views.components import cards, headings, media

LEDE = "Things I've built — full-stack apps, AI work, and design."

SEPARATOR = '<span class="meta-sep">·</span>'


def card(item):
    icon = ""
    if item.get("icon"):
        glyph = media.img(
            item["icon"]["src"],
            sizes="64px",
            alt=item["icon"]["alt"],
            cls="spot-icon",
        )
        icon = f"              {glyph}\n"
    note = ""
    if item.get("note"):
        n = item["note"]
        note = f"""
            <div class="stack-note edge-fade-divider">
              <span class="stack-note-label mono">{n['label']}</span>
              <a href="{n['href']}" target="_blank" rel="noopener" class="stack-note-link mono">{n['text']} ↗</a>
            </div>"""
    badges = f"\n              {cards.store_badges()}" if item.get("stores_coming_soon") else ""
    if item.get("rank"):
        tags = "".join(f'<span class="spot-tag mono">{t}</span>' for t in item["meta"])
        meta = f'<div class="spot-tags">{cards.rank_pill(item["rank"])}{tags}</div>'
    else:
        meta = f'<div class="entry-meta mono">{SEPARATOR.join(item["meta"])}</div>'
    return f"""          <article class="spot-card reveal">
            <div class="spot-head">
{icon}              <div class="spot-text">
                {meta}
                <h3 class="entry-title">{item['title']}</h3>
                <p class="entry-body">{item['body']}</p>
              </div>
            </div>
            <div class="spot-actions">{badges}
              <a
                href="{item['link']['href']}"
                target="_blank"
                rel="noopener"
                class="link-out mono"
              >
                {item['link']['label']} ↗
              </a>
            </div>{note}
          </article>"""


def render():
    cards = "\n".join(card(p) for p in content.load("projects"))
    return f"""        <section class="section reveal">
{headings.page("projects", LEDE, lede_gap="3rem")}
{cards}
        </section>
"""
