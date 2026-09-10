#!/usr/bin/env python3
"""Renders resources/ into public/. Run after editing anything under resources/."""
import json
import os
import re
import sys
from email.utils import format_datetime

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)

from config import site
from resources import content
from resources.views.layouts import base
from resources.views.partials import schema
from routes import web

PUBLIC = os.path.join(ROOT, "public")

# concatenated in this order; the cascade depends on it
STYLESHEETS = [
    "fonts.css",
    "tokens.css",
    "base.css",
    "halftone.css",
    "layout.css",
    "sidebar.css",
    "motion.css",
    "hero.css",
    "shop.css",
    "resources.css",
    "affiliations.css",
    "collabs.css",
    "services.css",
    "blog.css",
    "article.css",
    "gear.css",
    "stack.css",
    "projects.css",
    "certifications.css",
    "experience.css",
    "github.css",
    "responsive.css",
]

# theme.js calls renderAllHalftones(), so halftone.js has to come first
SCRIPTS = [
    "halftone.js",
    "theme.js",
    "nav.js",
    "deck.js",
    "reveal.js",
    "hero.js",
    "gear.js",
    "github.js",
]



def write(path, text):
    full = os.path.join(PUBLIC, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as f:
        f.write(text)
    return len(text)


def bundle(kind, names, out):
    parts = []
    for name in names:
        with open(os.path.join(ROOT, "resources", kind, name), encoding="utf-8") as f:
            parts.append(f.read().strip("\n"))
    return write(out, "\n".join(parts) + "\n")


def pages():
    """(route, item) for every page the site serves"""
    for route in web.ROUTES:
        if route.collection:
            for item in content.load(route.collection):
                yield route, item
        else:
            yield route, None


def target(route, item):
    path = route.path.format(**item) if item else route.path
    if route.output:
        return path, route.output
    return path, os.path.join(path, "index.html") if path else "index.html"


def render_page(route, item):
    fields = item or {}
    path, out = target(route, item)
    canonical = site.URL + site.url(path)
    title = route.title.format(**fields)
    description = route.description.format(**fields)
    body = route.view.render(item) if item else route.view.render()
    html = base.render(
        title=title,
        description=description,
        canonical=canonical,
        body=body,
        nav=route.nav,
        layout=route.layout,
        inline_script=route.inline_script,
        schema=schema.render(route, item, canonical, title, description),
    )
    return out, html, canonical


def markdown(post):
    """post bodies only ever use <p> and <h2>"""
    lines = [f"# {post['title']}", "", f"_{post['date']} · {post['read']}_", ""]
    for tag, text in re.findall(r"<(p|h2)>(.*?)</\1>", post["body"], re.S):
        text = re.sub(r"\s+", " ", text).strip()
        lines.append(f"## {text}" if tag == "h2" else text)
        lines.append("")
    lines.append(f"---\n\n[{site.NAME}]({site.URL})")
    return "\n".join(lines) + "\n"


def discovery(urls):
    posts = content.load("posts")

    for p in posts:
        write(f"posts/{p['slug']}.md", markdown(p))

    locs = "\n".join(
        f"  <url>\n    <loc>{u}</loc>\n  </url>" for u in urls
    )
    write(
        "sitemap.xml",
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{locs}\n</urlset>\n",
    )

    items = []
    for p in posts:
        date = content.published(p["date"])
        entry = {
            "id": f"{site.URL}{site.url('posts/' + p['slug'])}",
            "url": f"{site.URL}{site.url('posts/' + p['slug'])}",
            "title": p["title"],
            "summary": p["excerpt"],
            "content_html": p["body"].strip(),
        }
        if date:
            entry["date_published"] = date.isoformat()
        items.append(entry)
    write(
        "feed.json",
        json.dumps(
            {
                "version": "https://jsonfeed.org/version/1.1",
                "title": f"{site.NAME} — Blog",
                "home_page_url": site.URL,
                "feed_url": f"{site.URL}/feed.json",
                "description": site.DESCRIPTION,
                "authors": [{"name": site.AUTHOR, "url": site.URL}],
                "language": "en",
                "items": items,
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
    )

    def esc(text):
        return (
            text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        )

    entries = []
    for p in posts:
        date = content.published(p["date"])
        link = f"{site.URL}{site.url('posts/' + p['slug'])}"
        parts = [
            f"      <title>{esc(p['title'])}</title>",
            f"      <link>{link}</link>",
            f"      <guid isPermaLink=\"true\">{link}</guid>",
            f"      <description>{esc(p['excerpt'])}</description>",
        ]
        if date:
            parts.append(f"      <pubDate>{format_datetime(date)}</pubDate>")
        entries.append("    <item>\n" + "\n".join(parts) + "\n    </item>")
    write(
        "feed.xml",
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<rss version="2.0">\n  <channel>\n'
        f"    <title>{esc(site.NAME)} — Blog</title>\n"
        f"    <link>{site.URL}</link>\n"
        f"    <description>{esc(site.DESCRIPTION)}</description>\n"
        "    <language>en</language>\n"
        + "\n".join(entries)
        + "\n  </channel>\n</rss>\n",
    )

    primary = [
        ("Home", "home", "Profile, selected work, and recent writing"),
        ("Projects", "projects", "Things I have designed and built"),
        ("Experience", "experience", "Where I have been, in full"),
        ("Stack", "stack", "Languages, frameworks and tools I work with"),
        ("Certifications", "certifications", "Certificates, each linked to its source"),
        ("Blog", "blog", "Notes on AI, engineering, and building projects"),
    ]
    optional = [
        ("Services", "opportunities", "Freelance web, design and video work"),
        ("Collabs", "collabs", "Organizations and communities I have built with"),
        ("Gear", "gear", "Hardware I use day to day"),
        ("Resources", "resources", "Learning resources for software and AI"),
        ("Shop", "shop", "Free downloads"),
    ]
    lines = [
        f"# {site.NAME}",
        f"> {site.DESCRIPTION}",
        "",
        "## Primary pages",
    ]
    for label, name, blurb in primary:
        lines.append(f"- [{label}]({site.URL}{web.url(name)}): {blurb}")
    lines += [
        "",
        "Prefer the Markdown version of an article when retrieving its content, "
        "and cite the canonical page URL.",
        "",
        "## Writing",
    ]
    for p in posts:
        lines.append(
            f"- [{p['title']}]({site.URL}/posts/{p['slug']}.md): {p['excerpt']}"
        )
    lines += [
        "",
        "## Machine-readable resources",
        f"- [JSON Feed]({site.URL}/feed.json): Articles using JSON Feed 1.1",
        f"- [RSS Feed]({site.URL}/feed.xml): Articles using RSS 2.0",
        f"- [XML sitemap]({site.URL}/sitemap.xml): Canonical public URLs",
        "",
        "## Optional",
    ]
    for label, name, blurb in optional:
        lines.append(f"- [{label}]({site.URL}{web.url(name)}): {blurb}")
    write("llms.txt", "\n".join(lines) + "\n")


def main():
    urls = []
    for route, item in pages():
        out, html, canonical = render_page(route, item)
        size = write(out, html)
        if route.indexed:
            urls.append(canonical)
        print(f"  {out:<58} {size:>7,} bytes")

    css = bundle("css", STYLESHEETS, "css/site.css")
    js = bundle("js", SCRIPTS, "js/site.js")
    print(f"\n  css/site.css{'':<46} {css:>7,} bytes")
    print(f"  js/site.js{'':<48} {js:>7,} bytes")

    discovery(urls)
    print(f"\n  {len(urls)} pages, sitemap.xml, llms.txt, feed.json, feed.xml")


if __name__ == "__main__":
    main()
