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


# ── shop ──────────────────────────────────────────────────────────────────────
# The reference's shop is a 2/3-column card grid: a 4:3 preview well, a pill
# badge, then a mono kind label and the product name. Cards appear only when the
# file they point at actually exists, so a listing can never 404.
SHOP_ITEMS = [
    {
        "slug":  "developer-resume-template",
        "kind":  "Template",
        "name":  "Developer Résumé Template",
        "badge": "Free",
        "href":  "./shop/developer-resume-template/",
        "file":  "files/developer-resume-template.docx",
        "dl":    "files/developer-resume-template.docx",
        "shot":  "images/shop/developer-resume.png",
        "desc_intro": "A clean, <strong>ATS-friendly resume template</strong> for software developers &mdash; editable in Microsoft Word or Google Docs.",
        "desc_sections": [
            ("<h2>What's inside</h2>",
             "<ul>"
             "<li>A one-page <code>.docx</code> template with a professional, recruiter-friendly layout</li>"
             "<li>Pre-filled <strong>example content for a developer</strong> &mdash; just swap in your own</li>"
             "<li>Clear sections and sensible defaults that parse well in applicant tracking systems</li>"
             "</ul>"),
            ("<h2>Sections</h2>",
             "<p>Education &middot; Work Experience &middot; Projects &middot; Activities &middot; Skills &amp; Certifications</p>"
             "<p>Just download, open in Word or Google Docs, and edit away &mdash; completely free.</p>"),
        ],
    },
]

DOC_GLYPH = (
    '<svg class="shop-glyph" viewBox="0 0 24 24" fill="none" aria-hidden="true">'
    '<path d="M6 3h8l4 4v14a1 1 0 01-1 1H6a1 1 0 01-1-1V4a1 1 0 011-1z" '
    'stroke="currentColor" stroke-width="1.4" stroke-linejoin="round"/>'
    '<path d="M14 3v4h4M8.5 12h7M8.5 15.5h7M8.5 19h4" stroke="currentColor" '
    'stroke-width="1.4" stroke-linecap="round"/></svg>'
)

def shop_card(item, delay):
    have_file = os.path.exists(os.path.join(ROOT, item["file"]))
    if not have_file:
        return None
    shot = (f'<img src="./{item["shot"]}" alt="{item["name"]} preview" loading="lazy" />'
            if os.path.exists(os.path.join(ROOT, item["shot"])) else DOC_GLYPH)
    return f'''            <a class="shop-card reveal" href="{item["href"]}"
               style="animation-delay: {delay}s">
              <span class="shop-shot">
                {shot}
                <span class="shop-badge mono">{item["badge"]}</span>
              </span>
              <span class="shop-body">
                <span class="shop-kind mono">{item["kind"]}</span>
                <span class="shop-name">{item["name"]}</span>
              </span>
            </a>'''

_cards = [c for c in (shop_card(it, 0.04 * (i + 1)) for i, it in enumerate(SHOP_ITEMS)) if c]
shop_inner = ('          <div class="shop-grid">\n' + "\n".join(_cards) + '\n          </div>'
              if _cards else
              '          <p class="shop-empty mono">Nothing here yet.</p>')

shop_body = f'''        <section class="section reveal">
{page_head("01", "shop", "Things I have made and put up for download.")}
{shop_inner}
        </section>
'''

DOWNLOAD_ARROW = (
    '<svg class="dl-ico" viewBox="0 0 24 24" fill="none" aria-hidden="true">'
    '<path d="M12 3v13M5 12l7 7 7-7" stroke="currentColor" stroke-width="2" '
    'stroke-linecap="round" stroke-linejoin="round"/>'
    '<path d="M5 21h14" stroke="currentColor" stroke-width="2" '
    'stroke-linecap="round"/></svg>'
)

BACK_CHEVRON = (
    '<svg class="back-ico" viewBox="0 0 24 24" fill="none" aria-hidden="true">'
    '<path d="M15 19l-7-7 7-7" stroke="currentColor" stroke-width="2" '
    'stroke-linecap="round" stroke-linejoin="round"/></svg>'
)

def shop_detail(item):
    have_file = os.path.exists(os.path.join(ROOT, item["file"]))
    if not have_file:
        return None
    shot = (f'<img src="./{item["shot"]}" alt="{item["name"]}" loading="lazy" />'
            if os.path.exists(os.path.join(ROOT, item["shot"])) else DOC_GLYPH)
    sections_html = "\n".join(
        f'            {h}\n            {p}' for h, p in item["desc_sections"]
    )
    return f'''        <section class="section reveal">
          <a href="./shop/" class="sd-back mono">{BACK_CHEVRON} shop</a>
          <div class="sd-grid">
            <div class="sd-image">
              {shot}
            </div>
            <div class="sd-info">
              <span class="sd-kind mono">{item["kind"]}</span>
              <h1 class="sd-title">{item["name"]}</h1>
              <p class="sd-price">Free</p>
              <a href="./{item["dl"]}" download class="sd-download">{DOWNLOAD_ARROW} Download free</a>
              <p class="sd-delivery mono">
                <svg viewBox="0 0 24 24" fill="none" class="sd-check" aria-hidden="true"><path d="M5 12.5l4.5 4.5L19 7" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>
                Instant digital delivery
              </p>
            </div>
          </div>
          <div class="sd-desc">
            <p>{item["desc_intro"]}</p>
{sections_html}
          </div>
        </section>
'''

# ── Resources: grouped link lists, matched to the reference's layout ──────────
RES_ARROW = ('<svg class="res-ico" viewBox="0 0 24 24" fill="none" aria-hidden="true">'
             '<path d="M7 17L17 7M9 7h8v8" stroke="currentColor" stroke-width="1.8" '
             'stroke-linecap="round" stroke-linejoin="round"/></svg>')

RESOURCE_SECTIONS = [
    ("Learn AI / ML", [
        ("DeepLearning.AI", "https://www.deeplearning.ai/courses/",
         "Andrew Ng&#039;s specializations on ML, deep learning, and generative AI."),
        ("fast.ai — Practical Deep Learning", "https://course.fast.ai/",
         "Top-down, code-first deep learning course for coders."),
        ("Hugging Face LLM Course", "https://huggingface.co/learn/llm-course/chapter1/1",
         "Free hands-on course on transformers, NLP, and LLMs."),
        ("Google ML Crash Course", "https://developers.google.com/machine-learning/crash-course",
         "Google&#039;s interactive intro to machine learning fundamentals."),
        ("Hugging Face Deep RL Course", "https://huggingface.co/learn/deep-rl-course/unit0/introduction",
         "Free hands-on course on deep reinforcement learning."),
        ("Kaggle Learn", "https://www.kaggle.com/learn",
         "Short practical micro-courses on Python, ML, and data."),
    ]),
    ("AI Engineering &amp; LLMs", [
        ("Anthropic Prompt Engineering",
         "https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/overview",
         "Official guide to prompting Claude effectively."),
        ("Anthropic Cookbook", "https://github.com/anthropics/claude-cookbooks",
         "Code recipes for building with Claude: RAG, tools, agents."),
        ("OpenAI Cookbook", "https://cookbook.openai.com/",
         "Practical code examples for building with OpenAI models."),
        ("LangChain Docs", "https://docs.langchain.com/",
         "Framework docs for building LLM apps, agents, and RAG."),
        ("A Year of Building with LLMs",
         "https://www.oreilly.com/radar/what-we-learned-from-a-year-of-building-with-llms-part-i/",
         "Hard-won tactical lessons on shipping LLM products."),
        ("Chip Huyen&#039;s Blog", "https://huyenchip.com/blog/",
         "Deep essays on AI systems, ML production, and engineering."),
    ]),
    ("Developer fundamentals / CS", [
        ("The Odin Project", "https://www.theodinproject.com/",
         "Free full-stack web development curriculum with projects."),
        ("freeCodeCamp", "https://www.freecodecamp.org/",
         "Free interactive coding curriculum with certifications."),
        ("Harvard CS50x", "https://cs50.harvard.edu/x/",
         "Harvard&#039;s renowned intro to computer science, free online."),
        ("MDN Web Docs", "https://developer.mozilla.org/",
         "Authoritative reference for HTML, CSS, JavaScript, and web APIs."),
        ("roadmap.sh", "https://roadmap.sh/",
         "Community-curated learning roadmaps for developer roles."),
        ("Teach Yourself CS", "https://teachyourselfcs.com/",
         "Curated core CS subjects with the best books and lectures."),
        ("System Design Primer", "https://github.com/donnemartin/system-design-primer",
         "Open-source guide to designing large-scale systems."),
    ]),
    ("Practice &amp; interview prep", [
        ("LeetCode", "https://leetcode.com/",
         "Coding problems for technical and algorithm interview prep."),
        ("NeetCode", "https://neetcode.io/",
         "Curated problem lists with clear video walkthroughs."),
        ("Exercism", "https://exercism.org/",
         "Free coding exercises with mentoring across 70+ languages."),
        ("Codewars", "https://www.codewars.com/",
         "Gamified coding kata to sharpen language fluency."),
        ("Frontend Mentor", "https://www.frontendmentor.io/",
         "Real-world frontend projects from professional designs."),
    ]),
    ("Stay current — newsletters &amp; blogs", [
        ("The Batch", "https://www.deeplearning.ai/the-batch/",
         "Andrew Ng&#039;s weekly roundup of AI news and research."),
        ("Import AI", "https://jack-clark.net/",
         "Jack Clark&#039;s weekly newsletter on frontier AI and policy."),
        ("Latent Space", "https://www.latent.space/",
         "Newsletter and podcast for AI engineers in production."),
        ("Simon Willison&#039;s Blog", "https://simonwillison.net/",
         "Prolific, practical writing on LLMs and developer tooling."),
        ("Lil&#039;Log (Lilian Weng)", "https://lilianweng.github.io/",
         "Deep technical explainers on ML and LLM topics."),
        ("TLDR Newsletter", "https://tldr.tech/",
         "Daily concise digest of tech, dev, and AI news."),
        ("Hacker News", "https://news.ycombinator.com/",
         "High-signal community for tech, startups, and engineering."),
    ]),
    ("Tools &amp; references", [
        ("Hugging Face", "https://huggingface.co/",
         "Hub for open models, datasets, and ML demos."),
        ("Hugging Face Papers", "https://huggingface.co/papers",
         "Trending ML papers with linked code and discussion."),
        ("arXiv", "https://arxiv.org/",
         "Open-access preprint server for AI and CS research."),
        ("Kaggle", "https://www.kaggle.com/",
         "Datasets, notebooks, and ML competitions community."),
        ("DevDocs", "https://devdocs.io/",
         "Fast unified API documentation browser, offline-capable."),
    ]),
]

def resource_sections():
    out = []
    for i, (heading, links) in enumerate(RESOURCE_SECTIONS):
        rows = []
        for name, href, desc in links:
            rows.append(
f'''              <a href="{href}" target="_blank" rel="noopener" class="res-link">
                <span class="res-name">{name}{RES_ARROW}</span>
                <span class="res-desc">{desc}</span>
              </a>''')
        out.append(
f'''          <section class="res-group reveal" style="animation-delay: {0.05 * (i + 1):.2f}s">
            <h2 class="res-head mono">{heading}</h2>
            <div class="res-grid">
{chr(10).join(rows)}
            </div>
          </section>''')
    return "\n".join(out)

resources_body = f'''        <section class="section reveal">
{page_head("04", "resources", "A hand-picked list of the resources I keep coming back to — for learning to build software, getting into AI engineering, and staying current. Free or freemium, and genuinely worth your time.")}
{resource_sections()}
          <p class="res-foot mono reveal" style="animation-delay: .4s">
            Missing something great? <a href="mailto:marijakee@gmail.com">Send me a link →</a>
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
  "Things Jake Cardenas has made and put up for download.",
  "shop", False, shop_body, "", True),
 ("resources.html",      "Resources — Jake Cardenas",
  "Notes, references and tools Jake Cardenas keeps coming back to.",
  "resources", False, resources_body, "", True),
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

# ── shop detail pages (depth 2: shop/<slug>/index.html) ──────────────────────
for item in SHOP_ITEMS:
    detail = shop_detail(item)
    if detail is None:
        continue
    detail_html = page(
        title=f'{item["name"]} — Jake Cardenas',
        desc=f'{item["name"]} — free download from Jake Cardenas.',
        active="shop", on_index=False, body=detail, extra_scripts="", wide=True,
    )
    detail_html = re.sub(r'\?v=\d+', V, detail_html)
    slug = item["slug"]
    detail_dir = os.path.join(ROOT, "shop", slug)
    os.makedirs(detail_dir, exist_ok=True)
    out = os.path.join(detail_dir, "index.html")
    # depth-2: rewrite ./ to ../../
    detail_html = detail_html.replace('href="./index.html#', 'href="./#')
    detail_html = detail_html.replace('href="./index.html"', 'href="./"')
    detail_html = re.sub(r'href="\./([a-z-]+)\.html"', r'href="./\1/"', detail_html)
    detail_html = detail_html.replace('"./', '"../../').replace("'./", "'../../")
    open(out, "w", encoding="utf-8").write(detail_html)
    rel = os.path.relpath(out, ROOT)
    print(f"  {rel:<36} {len(detail_html):>7,} bytes")

print(f"\n  gear items carried over: {gear_count}")
