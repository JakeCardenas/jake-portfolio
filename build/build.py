import os, sys, json, re
# resolve everything relative to this file, so moving the project never breaks the build
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SP   = HERE
sys.path.insert(0, HERE)
from shell import page, V

C = json.load(open(os.path.join(HERE, "content.json")))

def num_head(num, name, link_label=None, link_href=None):
    right = (f'\n            <a href="{link_href}" class="num-link mono">{link_label}</a>'
             if link_label else "")
    return (f'          <div class="num-head">\n'
            f'            <h2 class="num-title">{num} — {name}</h2>{right}\n'
            f'          </div>')

def page_head(num, name, lede):
    return (f'          <header class="page-head">\n'
            f'            <div class="eyebrow">{num} — {name.upper()}</div>\n'
            f'            <h1 class="page-title">{name}</h1>\n'
            f'            <p class="page-lede">{lede}</p>\n'
            f'          </header>')

# ── hero: drop the old stat strip, point the CTA at the projects page ──────────
hero = C["hero_inner"]
i = hero.index('<div class="stat-strip">')
depth, end = 0, None
for m in re.finditer(r'<(/?)div\b[^>]*?(/?)>', hero[i:]):
    if m.group(2): continue
    depth += -1 if m.group(1) else 1
    if depth == 0: end = i + m.end(); break
hero = (hero[:i] + hero[end:]).replace('href="#projects"', 'href="./projects.html"')
# the profile is the landing block, not a numbered section — 01 belongs to blog
hero = re.sub(r'\s*<div class="eyebrow">01 — HOME</div>', "", hero)

# the reference paints its dissolve over the photo instead of masking it out
CLOSE = "</canvas>"
OVERLAY = CLOSE + chr(10) + " " * 16 + '<span class="halftone-white" aria-hidden="true"></span>'
# only after the last canvas in the frame
i = hero.rindex(CLOSE)
hero = hero[:i] + OVERLAY + hero[i + len(CLOSE):]

# the reference paints its dissolve over the photo instead of masking it out
# the reference sets the name on one line
hero = hero.replace("<h1 class=\"hero-name\"><span>Jake</span><span>Cardenas</span></h1>",
                    "<h1 class=\"hero-name\">Jake Cardenas</h1>")

# swap the chunky pill row for the reference's small lowercase mono links
i = hero.index('<div class="info-row">')
depth, end = 0, None
for m in re.finditer(r'<(/?)div\b[^>]*?(/?)>', hero[i:]):
    if m.group(2): continue
    depth += -1 if m.group(1) else 1
    if depth == 0: end = i + m.end(); break
LINKS = """<div class="hero-links mono">
                <a href="https://github.com/JakeCardenas" target="_blank" rel="noopener">github <span aria-hidden="true">↗</span></a>
                <a href="https://www.linkedin.com/in/jake-cardenas-710076410/" target="_blank" rel="noopener">linkedin <span aria-hidden="true">↗</span></a>
                <a href="https://instagram.com/prblynot.jky" target="_blank" rel="noopener">instagram <span aria-hidden="true">↗</span></a>
                <a href="mailto:marijakee@gmail.com">email <span aria-hidden="true">↗</span></a>
              </div>"""
hero = hero[:i] + LINKS + hero[end:]

# the reference has no solid button in the hero
i = hero.index('<div class="btn-row">')
depth, end = 0, None
for m in re.finditer(r'<(/?)div\b[^>]*?(/?)>', hero[i:]):
    if m.group(2): continue
    depth += -1 if m.group(1) else 1
    if depth == 0: end = i + m.end(); break
hero = hero[:i] + hero[end:]

# counts are derived from what the site actually contains, not hard-coded guesses
STATS = [
    ("3", "PROJECTS SHIPPED", "./projects.html"),
    ("5", "CERTIFICATES",     "./certifications.html"),
    ("6", "STACK",            "./stack.html"),
    ("1", "INTERNSHIP",       "#internships"),
]
def stat_row():
    cells = []
    for n, label, href in STATS:
        cells.append(
f'''            <a class="stat-cell" href="{href}">
              <span class="stat-num">{n}<span class="stat-arrow" aria-hidden="true">↗</span></span>
              <span class="stat-label mono">{label}</span>
            </a>''')
        
    return '          <div class="stat-row">\n' + "\n".join(cells) + '\n          </div>'

# ── project deck, built from the real project cards ───────────────────────────
def deck():
    slots = ["is-left", "is-center", "is-right"]
    order = [1, 0, 2]                       # Reps left, Digital Twin centre, CardenasDev right
    cards = []
    for slot, idx in zip(slots, order):
        art = C["projects"][idx]
        title = re.search(r'<h3 class="entry-title">(.*?)</h3>', art, re.S).group(1).strip()
        meta  = re.search(r'<div class="entry-meta mono">(.*?)</div>', art, re.S).group(1)
        meta  = re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' · ', meta)).strip(' ·· ')
        body  = re.search(r'<p class="entry-body">(.*?)</p>', art, re.S).group(1).strip()
        body  = re.sub(r'\s+', ' ', body)
        img   = re.search(r'<img\s+src="([^"]+)"', art).group(1)
        link  = re.search(r'href="(https://[^"]+)"', art)
        live  = (f'\n                <a href="{link.group(1)}" target="_blank" rel="noopener" '
                 f'class="deck-link mono">VIEW LIVE SITE <span aria-hidden="true">↗</span></a>'
                 if link else "")
        cards.append(
f'''              <article class="deck-card {slot}" role="button" tabindex="0"
                       aria-label="Show {re.sub(r'&amp;','and',title)}"
                       onclick="activateCard(this)"
                       onkeydown="if(event.key==='Enter'||event.key===' '){{event.preventDefault();activateCard(this);}}">
                <div class="deck-shot"><img src="{img}{V}" alt="" loading="lazy" /></div>
                <h3 class="deck-title">{title}</h3>
                <div class="deck-meta mono">{meta}</div>
                <p class="deck-body">{body}</p>{live}
              </article>''')
    return ('          <div class="deck" data-deck>\n' + "\n".join(cards) + '\n          </div>')

# ── gear preview for the homepage: real items lifted from the gear page ───────
def gear_preview():
    items = []
    for g in C["gear_groups"]:
        for m in re.finditer(r'<li>\s*<a\s+class="gear-item"(.*?)</li>', g, re.S):
            blk = m.group(0)
            name = re.search(r'<span class="gear-name">(.*?)</span>', blk, re.S)
            meta = re.search(r'<span class="gear-meta">(.*?)</span>', blk, re.S)
            img  = re.search(r'<img\s+src="([^"]+)"', blk)
            if name and img:
                items.append((name.group(1).strip(),
                              re.sub(r'\s+', ' ', meta.group(1)).strip() if meta else "",
                              img.group(1).split("?")[0]))
    picks = items[:4]
    tiles = "\n".join(
f'''            <a class="gp-item" href="./gear.html">
              <span class="gp-shot"><img src="{img}{V}" alt="" loading="lazy" /></span>
              <span class="gp-name">{name}</span>
              <span class="gp-meta mono">{meta}</span>
            </a>''' for name, meta, img in picks)
    return '          <div class="gear-preview">\n' + tiles + '\n          </div>', len(items)

gp_html, gear_count = gear_preview()

# a flat pill preview on the homepage; the full grouped list lives on stack.html
def stack_preview(limit=12):
    items = re.findall(r'<span>([^<]+)</span>', C["stack"])
    shown = items[:limit]
    pills = "\n".join(f'            <span class="pill mono">{t}</span>' for t in shown)
    more = (f'\n            <a class="pill pill-more mono" href="./stack.html">+ {len(items)-len(shown)} more</a>'
            if len(items) > len(shown) else "")
    return '          <div class="pill-row">\n' + pills + more + '\n          </div>', len(items)

sp_html, stack_total = stack_preview()



# ── compact rows, built from the same timeline entries as the full page ───────
def row(entry):
    year  = re.search(r'<div class="tl-year mono">(.*?)</div>', entry, re.S).group(1).strip()
    title = re.search(r'<h3 class="entry-title">(.*?)</h3>', entry, re.S).group(1)
    title = re.sub(r'\s+', ' ', title).strip()
    org   = re.search(r'<div class="tl-org">(.*?)</div>', entry, re.S).group(1)
    org   = re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', org)).strip()
    return (f'            <div class="row-item">\n'
            f'              <span class="row-year mono">{year}</span>\n'
            f'              <span class="row-title">{title}</span>\n'
            f'              <span class="row-org">{org}</span>\n'
            f'            </div>')

def row_list(*entries):
    return ('          <div class="row-list">\n'
            + "\n".join(row(e) for e in entries) + '\n          </div>')

# ── homepage ──────────────────────────────────────────────────────────────────
home_body = f'''        <section id="home" class="section section--hero reveal">
{hero}
        </section>

{stat_row()}

        <div class="ht-rule" aria-hidden="true"></div>

        <section id="blog" class="section reveal" style="position:relative">
          <span class="ht-accent" aria-hidden="true"></span>
{num_head("01", "blog", "ALL POSTS →", "./blog.html")}
          <p class="empty-note">
            Notes on what I'm learning — AI, full-stack work, and the projects
            behind them. First posts are on the way.
          </p>
        </section>

        <section id="projects" class="section reveal">
{num_head("02", "projects", "ALL PROJECTS →", "./projects.html")}
{deck()}
        </section>

        <section id="experience" class="section reveal">
{num_head("03", "experience", "FULL HISTORY →", "./experience.html")}
{row_list(C["experience_psg"], C["experience"])}
        </section>

        <section id="stack" class="section reveal">
{num_head("04", "stack", "VIEW ALL →", "./stack.html")}
{sp_html}
        </section>

        <section id="certifications" class="section reveal">
{num_head("05", "certifications", "ALL CERTIFICATIONS →", "./certifications.html")}
          <div class="cert-grid cert-grid--flat">
{chr(10).join(C["certs"][:3])}
          </div>
        </section>

        <section id="internships" class="section reveal">
{num_head("06", "internships", "FULL HISTORY →", "./experience.html")}
          <div class="affil-row">
            <a class="affil-item" href="./experience.html">
              <span class="affil-mark" aria-hidden="true">
                <img src="./images/certs/logos/employability-advantage.png" alt="" loading="lazy" />
              </span>
              <span>
                <span class="affil-name">Full Stack &amp; Agentic AI Developer Intern</span>
                <span class="affil-role mono">2026 · Employability Advantage &times; AusBiz Consulting</span>
              </span>
            </a>
          </div>
        </section>

        <section id="github" class="section reveal">
{num_head("07", "github", "@JAKECARDENAS ↗", "https://github.com/JakeCardenas")}
{C["gh_panel"]}
        </section>

        <div class="ht-fade" aria-hidden="true"></div>
'''

# ── dedicated pages ───────────────────────────────────────────────────────────
blog_body = f'''        <section class="section reveal">
{page_head("02", "blog", "Notes on what I'm learning — artificial intelligence, full-stack development, and the projects behind them.")}
          <div class="post-list" id="postList">
            <p class="empty-note">
              No posts published yet. This is where they'll appear.
            </p>
          </div>
        </section>
'''

projects_body = f'''        <section class="section reveal">
{page_head("07", "projects", "Things I've built — full-stack apps, AI work, and design.")}
{chr(10).join(C["projects"])}
        </section>
'''

experience_body = f'''        <section class="section reveal">
{page_head("08", "experience", "Where I've been — the full entries, with what I worked on.")}
          <ol class="timeline stagger">
{C["experience_psg"]}
{C["experience"]}
{C["internship"]}
          </ol>
        </section>
'''

stack_body = f'''        <section class="section reveal">
{page_head("09", "stack", "The languages, frameworks and tools I work with, grouped by what they're for.")}
{C["stack"]}
        </section>
'''

certs_body = f'''        <section class="section reveal">
{page_head("10", "certifications", "Certificates I've earned, each one linked to its source.")}
          <div class="cert-grid">
{chr(10).join(C["certs"])}
          </div>
        </section>
'''

gear_body = f'''        <section class="section reveal">
{page_head("03", "gear", "The hardware I actually use day to day — desk setup, everyday carry, and the camera I shoot on.")}
{chr(10).join(C["gear_groups"])}
        </section>
'''


shop_body = f'''        <section class="section reveal">
{page_head("01", "shop", "Things I have made and put up for sale. Nothing listed just yet.")}
          <p class="empty-note">
            No items yet. This is where they'll appear.
          </p>
        </section>
'''

resources_body = f'''        <section class="section reveal">
{page_head("04", "resources", "Notes, references and tools I keep coming back to.")}
          <p class="empty-note">
            Nothing collected here yet. This is where it'll appear.
          </p>
        </section>
'''

collabs_body = f'''        <section class="section reveal">
{page_head("05", "collabs", "Projects I have built together with other people.")}
          <p class="empty-note">
            No collaborations listed yet. This is where they'll appear.
          </p>
        </section>
'''

opportunities_body = f'''        <section class="section reveal">
{page_head("06", "opportunities", "What I am open to right now — internships, freelance work and team projects.")}
          <p class="empty-note">
            Open to internships, freelance work and joining a team. The quickest
            way to reach me is the email in the sidebar.
          </p>
        </section>
'''

PAGES = [
 ("index.html",          "Jake Cardenas — Portfolio",
  "Jake Cardenas — BSIT (Artificial Intelligence) student at St. Paul University Philippines. Full-stack and AI developer.",
  None, True, home_body, '    <script src="./js/site-halftones.js%s"></script>\n' % V),
 ("shop.html",           "Shop — Jake Cardenas",
  "Things Jake Cardenas has made and put up for sale.",
  "shop", False, shop_body, ""),
 ("resources.html",      "Resources — Jake Cardenas",
  "Notes, references and tools Jake Cardenas keeps coming back to.",
  "resources", False, resources_body, ""),
 ("collabs.html",        "Collabs — Jake Cardenas",
  "Projects Jake Cardenas has built together with other people.",
  "collabs", False, collabs_body, ""),
 ("opportunities.html",  "Opportunities — Jake Cardenas",
  "What Jake Cardenas is open to right now — internships, freelance work and team projects.",
  "opportunities", False, opportunities_body, ""),
 ("blog.html",           "Blog — Jake Cardenas",
  "Notes on artificial intelligence, full-stack development, and the projects behind them.",
  "blog", False, blog_body, ""),
 ("projects.html",       "Projects — Jake Cardenas",
  "Full-stack apps, AI work, and design projects built by Jake Cardenas.",
  "projects", False, projects_body, "", True),
 ("experience.html",     "Experience — Jake Cardenas",
  "Jake Cardenas's experience and internships, in full.",
  "experience", False, experience_body, ""),
 ("stack.html",          "Stack — Jake Cardenas",
  "The languages, frameworks and tools Jake Cardenas works with.",
  "stack", False, stack_body, ""),
 ("certifications.html", "Certifications — Jake Cardenas",
  "Certifications earned by Jake Cardenas, each linked to its source.",
  "certifications", False, certs_body, "", True),
 ("gear.html",           "Gear — Jake Cardenas",
  "The hardware Jake Cardenas uses day to day — desk setup, everyday carry, and camera.",
  "gear", False, gear_body, "", True),
]

for fname, title, desc, active, on_index, body, extra, *w in PAGES:
    html = page(title=title, desc=desc, active=active, on_index=on_index,
                body=body, extra_scripts=extra, wide=bool(w and w[0]))
    # blocks lifted from the old pages carry their old cache buster
    html = re.sub(r'\?v=\d+', V, html)
    # The reference serves /blog, /projects … with no .html. On a static host the
    # equivalent is a directory index: blog/index.html is served at /blog.
    # index.html stays at the root so / still works.
    if fname == "index.html":
        out, depth = os.path.join(ROOT, "index.html"), 0
    else:
        slug = fname[:-5]
        os.makedirs(os.path.join(ROOT, slug), exist_ok=True)
        out, depth = os.path.join(ROOT, slug, "index.html"), 1

    # .html links become directory links: ./blog.html -> ./blog/ , ./index.html -> ./
    html = html.replace('href="./index.html#', 'href="./#')
    html = html.replace('href="./index.html"', 'href="./"')
    html = re.sub(r'href="\./([a-z-]+)\.html"', r'href="./\1/"', html)

    # a page one level down reaches shared assets through ../
    if depth:
        html = html.replace('"./', '"../').replace("'./", "'../")

    open(out, "w", encoding="utf-8").write(html)
    rel = os.path.relpath(out, ROOT)
    print(f"  {rel:<26} {len(html):>7,} bytes")
print(f"\n  gear items carried over: {gear_count}")
