import re

from config import site
from resources import content
from resources.views.components import cards, headings, media

DECK_SLOTS = (("is-center", 0), ("is-left", 1), ("is-right", 2))
STACK_PREVIEW = 12

ARROW = (
    '<svg class="stat-arrow" viewBox="0 0 16 16" fill="none" aria-hidden="true">'
    '<path d="M5 11L11 5M11 5H6M11 5V10" stroke="currentColor" stroke-width="1.5" '
    'stroke-linecap="round" stroke-linejoin="round"/></svg>'
)


def hero():
    profile = content.load("profile")
    lede = "\n".join(
        f'              <p class="hero-lede">{text}</p>' for text in profile["lede"]
    )
    links = "\n".join(
        f'                <a href="{href}" target="_blank" rel="noopener">{name} ↗</a>'
        for name, href in site.LINKS.items()
    )
    photo = media.img(
        profile["photo"]["src"],
        alt=profile["photo"]["alt"],
        cls="hero-photo",
        priority=True,
        extra='width="469" height="469" draggable="false"',
    )
    return f"""          <div class="hero-grid">
            <div class="hero-photo-wrap">
              {photo}
            </div>
            <div class="hero-body">
              <h1 class="hero-name">{site.NAME}</h1>
{lede}
              <div class="hero-links mono">
{links}
                <a href="mailto:{site.EMAIL}">email ↗</a>
              </div>
            </div>
          </div>"""


def stat_row():
    stats = (
        (len(content.load("projects")), "projects shipped", "projects"),
        (len(content.load("certifications")), "certificates", "certifications"),
        (6, "stack", "stack"),
        (1, "internship", "experience"),
    )
    cells = "\n".join(
        f"""            <div class="stat-cell">
              <a class="stat-link" href="{site.url(route)}">
                <span class="stat-top"><span class="stat-num">{value}</span>{ARROW}</span>
                <span class="stat-label mono">{label}</span>
              </a>
            </div>"""
        for value, label, route in stats
    )
    return f'        <section class="stat-row">\n{cells}\n        </section>'


def deck():
    projects = content.load("projects")
    entries = []
    for slot, index in DECK_SLOTS:
        project = projects[index]
        tags = "\n".join(
            f'                <span class="deck-tag mono">{tag}</span>' for tag in project["meta"]
        )
        icon = (
            media.img(project["icon"]["src"], sizes="48px", alt=project["icon"]["alt"], cls="deck-icon")
            if project.get("icon")
            else ""
        )
        entries.append(
            f"""            <article class="deck-card {slot}" role="button" tabindex="0"
                     aria-label="Show {project['title']}">
              <div class="deck-tags">
{tags}
              </div>
              <div class="deck-head">
                {icon}
                <h3 class="deck-title">{project['title']}</h3>
              </div>
              <p class="deck-body">{project['body']}</p>
              <div class="deck-actions">
                <a href="{project['link']['href']}" target="_blank" rel="noopener" class="deck-link mono">{project['link']['label']} ↗</a>
              </div>
            </article>"""
        )
    return '          <div class="deck" data-deck>\n' + "\n".join(entries) + "\n          </div>"


def experience_rows():
    rows = "\n".join(
        f"""            <div class="row-item">
              <div class="row-year mono">{item['year']}</div>
              <div class="row-title">{item['title']}</div>
              <div class="row-org">{re.sub(r'\\s+', ' ', re.sub(r'<[^>]+>', ' ', item['org'])).strip()}</div>
            </div>"""
        for item in content.load("experience")
        if item["home"]
    )
    return f'          <div class="row-list">\n{rows}\n          </div>'


def stack_pills():
    items = [tag for group in content.load("stack") for tag in group["items"]]
    pills = "\n".join(f'              <span class="pill mono">{t}</span>' for t in items[:STACK_PREVIEW])
    if len(items) > STACK_PREVIEW:
        pills += f'\n              <a class="pill pill-more mono" href="{site.url("stack")}">+ more</a>'
    return f"""          <div class="stack-preview">
            <div class="stack-preview-head">
              <h3 class="stack-preview-title mono">Stack</h3>
              <a href="{site.url('stack')}" class="num-link mono">view all →</a>
            </div>
            <div class="pill-row">
{pills}
            </div>
          </div>"""


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
                {media.img(item['logo'], sizes="36px")}
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
            </a>
            <div class="gh-foot">
              <p class="gh-caption mono" id="ghCaption">
                loading contribution activity…
              </p>
            </div>
            <div class="gh-tip mono" id="ghTip" hidden></div>
          </div>"""


def render():
    certs = cards.certificates(content.load("certifications")[:3])
    return f"""        <section id="home" class="section section--hero">
{hero()}
        </section>

{stat_row()}

        <div class="ht-rule" aria-hidden="true"></div>

        <section id="blog" class="section">
          <span class="ht-accent" aria-hidden="true"></span>
{headings.numbered("01", "blog", "all posts →", site.url("blog"))}
{cards.post_rows(content.load("posts"))}
        </section>

        <section id="projects" class="section">
{headings.numbered("02", "projects", "all projects →", site.url("projects"))}
{deck()}
        </section>

        <section id="experience" class="section">
{headings.numbered("03", "experience", "full history →", site.url("experience"))}
{experience_rows()}
{stack_pills()}
        </section>

        <section id="certifications" class="section">
{headings.numbered("04", "certifications", "all certifications →", site.url("certifications"))}
          <div class="cert-grid cert-grid--flat">
{certs}
          </div>
        </section>

        <section id="affiliations" class="section">
{headings.numbered("05", "affiliations", "all affiliations →", site.url("affiliations"))}
{affiliations()}
        </section>

        <section id="github" class="section">
{headings.numbered("06", "github", f"@{site.GITHUB_USER} ↗", site.LINKS["github"])}
{github_panel()}
        </section>

        <div class="ht-fade" aria-hidden="true"></div>
"""
