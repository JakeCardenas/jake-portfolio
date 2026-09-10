import re

from config import site
from resources import content
from resources.views.components import cards, headings

DECK_SLOTS = (("is-left", 1), ("is-center", 0), ("is-right", 2))
STACK_PREVIEW = 12


def hero():
    profile = content.load("profile")
    photos = "\n".join(
        f"""                <canvas
                  class="photo-{n} halftone-canvas"
                  data-src="{site.asset(p['src'])}"
                  aria-label="{p['alt']}"
                ></canvas>"""
        for n, p in enumerate(profile["photos"], start=1)
    )
    lede = "\n".join(
        f'              <p class="hero-lede">{text}</p>' for text in profile["lede"]
    )
    links = "\n".join(
        f'                <a href="{href}" target="_blank" rel="noopener">{name} <span aria-hidden="true">↗</span></a>'
        for name, href in site.LINKS.items()
    )
    return f"""          <div class="hero-grid">
            <div
              class="photo-swap"
              role="button"
              tabindex="0"
              aria-label="Toggle profile photo"
            >
              <div class="photo-frame">
{photos}
                <span class="halftone-white" aria-hidden="true"></span>
              </div>
              <div class="photo-dots" aria-hidden="true">
                <span class="dot"></span><span class="dot-2"></span>
              </div>
            </div>
            <div class="hero-body">
              <div class="status mono">
                <span class="status-dot" aria-hidden="true"></span> {profile['status']}
              </div>
              <h1 class="hero-name">{site.NAME}</h1>
{lede}
              <div class="hero-links mono">
{links}
                <a href="mailto:{site.EMAIL}">email <span aria-hidden="true">↗</span></a>
              </div>
            </div>
          </div>"""


def stat_row():
    stats = (
        (len(content.load("projects")), "PROJECTS SHIPPED", "projects"),
        (len(content.load("certifications")), "CERTIFICATES", "certifications"),
        (6, "STACK", "stack"),
        (1, "INTERNSHIP", "experience"),
    )
    cells = "\n".join(
        f"""            <a class="stat-cell" href="{site.url(route)}">
              <span class="stat-num">{value}<span class="stat-arrow" aria-hidden="true">↗</span></span>
              <span class="stat-label mono">{label}</span>
            </a>"""
        for value, label, route in stats
    )
    return f'          <div class="stat-row">\n{cells}\n          </div>'


def deck():
    projects = content.load("projects")
    featured = content.load("featured")
    entries = []
    for slot, index in DECK_SLOTS:
        project = projects[index]
        meta = " · ".join(project["meta"])
        entries.append(
            f"""            <article class="deck-card {slot}" role="button" tabindex="0"
                     aria-label="Show {project['title']}">
              <div class="deck-shot"><img src="{site.asset(featured[project['title']])}" alt="" loading="lazy" /></div>
              <h3 class="deck-title">{project['title']}</h3>
              <div class="deck-meta mono">{meta}</div>
              <p class="deck-body">{project['body']}</p>
              <a href="{project['link']['href']}" target="_blank" rel="noopener" class="deck-link mono">VIEW LIVE SITE <span aria-hidden="true">↗</span></a>
            </article>"""
        )
    return '          <div class="deck" data-deck>\n' + "\n".join(entries) + "\n          </div>"


def experience_rows():
    rows = "\n".join(
        f"""            <div class="row-item">
              <span class="row-year mono">{item['year']}</span>
              <span class="row-title">{item['title']}</span>
              <span class="row-org">{re.sub(r'\\s+', ' ', re.sub(r'<[^>]+>', ' ', item['org'])).strip()}</span>
            </div>"""
        for item in content.load("experience")
        if item["home"]
    )
    return f'          <div class="row-list">\n{rows}\n          </div>'


def stack_pills():
    items = [tag for group in content.load("stack") for tag in group["items"]]
    shown = items[:STACK_PREVIEW]
    pills = "\n".join(f'            <span class="pill mono">{t}</span>' for t in shown)
    if len(items) > len(shown):
        pills += (
            f'\n            <a class="pill pill-more mono" href="{site.url("stack")}">'
            f"+ {len(items) - len(shown)} more</a>"
        )
    return f'          <div class="pill-row">\n{pills}\n          </div>'


def affiliations():
    entries = []
    for item in content.load("affiliations"):
        if item["href"]:
            open_tag = f'<a class="affil-item" href="{item["href"]}" target="_blank" rel="noopener"'
            close_tag = "</a>"
        else:
            open_tag = '<div class="affil-item"'
            close_tag = "</div>"
        entries.append(
            f"""            {open_tag}>
              <span class="affil-mark" aria-hidden="true">
                <img src="{site.asset(item['logo'])}" alt="" loading="lazy" />
              </span>
              <span>
                <span class="affil-name">{item['name']}</span>
                <span class="affil-role mono">{item['role']}</span>
              </span>
            {close_tag}"""
        )
    return '          <div class="affil-row">\n' + "\n".join(entries) + "\n          </div>"


def github_panel():
    return f"""          <div class="gh-panel">
            <a
              class="gh-graph-link"
              href="{site.LINKS['github']}"
              target="_blank"
              rel="noopener"
              aria-label="View {site.GITHUB_USER} on GitHub"
            >
              <span class="gh-graph" id="ghGraph" aria-hidden="true"></span>
              <span class="gh-graph-hint mono" aria-hidden="true"
                >VIEW PROFILE <span>↗</span></span
              >
            </a>
            <div class="gh-foot">
              <p class="gh-caption mono" id="ghCaption">
                LOADING CONTRIBUTION ACTIVITY…
              </p>
            </div>
            <div class="gh-tip mono" id="ghTip" hidden></div>
          </div>"""


def render():
    certs = cards.certificates(content.load("certifications")[:3])
    return f"""        <section id="home" class="section section--hero reveal">
{hero()}
        </section>

{stat_row()}

        <div class="ht-rule" aria-hidden="true"></div>

        <section id="blog" class="section reveal" style="position:relative">
          <span class="ht-accent" aria-hidden="true"></span>
{headings.numbered("01", "blog", "ALL POSTS →", site.url("blog"))}
{cards.posts(content.load("posts"), heading="h3")}
        </section>

        <section id="projects" class="section reveal">
{headings.numbered("02", "projects", "ALL PROJECTS →", site.url("projects"))}
{deck()}
        </section>

        <section id="experience" class="section reveal">
{headings.numbered("03", "experience", "FULL HISTORY →", site.url("experience"))}
{experience_rows()}
        </section>

        <section id="stack" class="section reveal">
{headings.numbered("04", "stack", "VIEW ALL →", site.url("stack"))}
{stack_pills()}
        </section>

        <section id="certifications" class="section reveal">
{headings.numbered("05", "certifications", "ALL CERTIFICATIONS →", site.url("certifications"))}
          <div class="cert-grid cert-grid--flat">
{certs}
          </div>
        </section>

        <section id="affiliations" class="section reveal">
{headings.numbered("06", "affiliations")}
{affiliations()}
        </section>

        <section id="github" class="section reveal">
{headings.numbered("07", "github", f"@{site.GITHUB_USER.upper()} ↗", site.LINKS["github"])}
{github_panel()}
        </section>

        <div class="ht-fade" aria-hidden="true"></div>
"""
