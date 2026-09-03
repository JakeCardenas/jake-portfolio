import os
"""Pull the real content blocks out of the current site so nothing is retyped or invented."""
import re, json, os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
idx = open(os.path.join(ROOT, "index.html"), encoding="utf-8").read()
gear = open(os.path.join(ROOT, "gear.html"), encoding="utf-8").read()

def block(src, start_marker, end_marker, inclusive_end=False):
    i = src.index(start_marker)
    j = src.index(end_marker, i)
    return src[i:(j + len(end_marker)) if inclusive_end else j]

def tag_block(src, start_idx, tag):
    """Walk tag depth from start_idx and return the full element."""
    depth = 0
    for m in re.finditer(r'<(/?)%s\b[^>]*?(/?)>' % tag, src[start_idx:]):
        if m.group(2):
            continue
        depth += -1 if m.group(1) else 1
        if depth == 0:
            return src[start_idx:start_idx + m.end()]
    raise ValueError("unclosed " + tag)

out = {}

# hero — everything inside section#home
i = idx.index('<section id="home"')
hero = tag_block(idx, i, "section")
out["hero_inner"] = hero[hero.index(">") + 1: hero.rindex("</section>")].strip()

# skills stack
i = idx.index('<dl class="stack-list stagger">')
out["stack"] = tag_block(idx, i, "dl")

# the two timeline entries, kept separate: one is an internship, one is a forum
tl = []
for m in re.finditer(r'<li class="tl-item">', idx):
    tl.append(tag_block(idx, m.start(), "li"))
assert len(tl) == 2, len(tl)
out["internship"] = tl[0]          # Employability Advantage × AusBiz
out["experience"] = tl[1]          # PAPSAS Midyear Interactive Youth Forum

# projects
projects = []
for m in re.finditer(r'<article class="project-card">', idx):
    projects.append(tag_block(idx, m.start(), "article"))
assert len(projects) == 3, len(projects)
out["projects"] = projects

# certification cards
i = idx.index('<div class="cert-grid">')
grid = tag_block(idx, i, "div")
certs = []
for m in re.finditer(r'<a\n\s+class="cert-card"', grid):
    certs.append(tag_block(grid, m.start(), "a"))
assert len(certs) == 5, len(certs)
out["certs"] = certs

# github panel + section head
i = idx.index('<div class="section-head">')
out["gh_head"] = tag_block(idx, i, "div")
i = idx.index('<div class="gh-panel">')
out["gh_panel"] = tag_block(idx, i, "div")

# gear groups, straight out of gear.html
groups = []
for m in re.finditer(r'<div class="gear-group">', gear):
    groups.append(tag_block(gear, m.start(), "div"))
assert len(groups) == 3, len(groups)
out["gear_groups"] = groups
out["gear_intro"] = block(gear, '<h1 class="gear-title">', '<div class="gear-group">')

SP = HERE
json.dump(out, open(os.path.join(HERE, "content.json"), "w"), indent=1)
print(f"  hero            {len(out['hero_inner']):>6} chars")
print(f"  stack           {len(out['stack']):>6}")
print(f"  internship      {len(out['internship']):>6}")
print(f"  experience      {len(out['experience']):>6}")
print(f"  projects   x{len(projects)}  {sum(map(len,projects)):>6}")
print(f"  certs      x{len(certs)}  {sum(map(len,certs)):>6}")
print(f"  gear groups x{len(groups)} {sum(map(len,groups)):>6}")
print(f"  github panel    {len(out['gh_panel']):>6}")
