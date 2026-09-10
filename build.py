#!/usr/bin/env python3
"""Renders resources/ into public/. Run after editing anything under resources/."""
import glob
import hashlib
import json
import os
import re
import struct
import shutil
import subprocess
import sys
from email.utils import format_datetime

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)

from config import site
from resources import content
from resources.views.components import media
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
    "presentations.css",
    "recommendations.css",
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



OPTIMIZED = "images/optimized"

# widths generated per directory; the profile portraits are excluded because the
# halftone renderer samples their pixels directly and resizing shifts the dots
IMAGE_LADDERS = {
    "images/blog": [320, 640, 1200],
    "images/projects/icons": [64, 128],
    "images/projects": [320, 640],
    "images/gear": [256, 512],
    "images/certs/logos": [56, 112],
    "images/collabs": [56, 112],
    "images/affiliations": [64, 128],
    "images/shop": [320, 640, 1024],
}

# the blog art is dithered, so it needs headroom before the dots start to smear
IMAGE_QUALITY = {"images/blog": "92"}
DEFAULT_QUALITY = "86"


def write(path, text):
    full = os.path.join(PUBLIC, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as f:
        f.write(text)
    return len(text)


def source_width(path):
    with open(path, "rb") as f:
        head = f.read(32)
        if head[:8] == b"\x89PNG\r\n\x1a\n":
            return struct.unpack(">I", head[16:20])[0]
        if head[:4] == b"RIFF" and head[8:12] == b"WEBP":
            if head[12:16] == b"VP8X":
                return int.from_bytes(head[24:27], "little") + 1
            if head[12:16] == b"VP8 ":
                return struct.unpack("<H", head[26:28])[0] & 0x3FFF
            f.seek(0)
            out = subprocess.run(
                ["cwebp", "-quiet", "-print_psnr", path, "-o", os.devnull],
                capture_output=True,
                text=True,
            )
            return 10**6 if out.returncode == 0 else 0
        if head[:2] == b"\xff\xd8":
            f.seek(2)
            while True:
                byte = f.read(1)
                while byte and byte != b"\xff":
                    byte = f.read(1)
                marker = f.read(1)
                while marker == b"\xff":
                    marker = f.read(1)
                if not marker:
                    return 0
                if marker[0] in (0xC0, 0xC1, 0xC2):
                    f.read(3)
                    _h, w = struct.unpack(">HH", f.read(4))
                    return w
                length = struct.unpack(">H", f.read(2))[0]
                f.read(length - 2)
    return 0


def lookup(table, relative, fallback=None):
    directory = os.path.dirname(relative)
    while directory:
        if directory in table:
            return table[directory]
        directory = os.path.dirname(directory)
    return fallback


def ladder_for(relative):
    return lookup(IMAGE_LADDERS, relative)


def optimise_images():
    """resources/images -> public/images: derivatives where a ladder applies,
    a straight copy for everything served as-is (svg, halftone sources)"""
    source_root = os.path.join(ROOT, "resources/images")
    out_dir = os.path.join(PUBLIC, OPTIMIZED)
    os.makedirs(out_dir, exist_ok=True)
    keep, made, saved, copied = set(), 0, 0, 0

    for path in sorted(glob.glob(os.path.join(source_root, "**/*"), recursive=True)):
        if not os.path.isfile(path):
            continue
        relative = os.path.join("images", os.path.relpath(path, source_root))
        ladder = (
            ladder_for(relative)
            if relative.rsplit(".", 1)[-1].lower() in ("png", "jpg", "jpeg", "webp")
            else None
        )
        if not ladder:
            destination = os.path.join(PUBLIC, relative)
            os.makedirs(os.path.dirname(destination), exist_ok=True)
            if not os.path.exists(destination) or os.path.getmtime(
                path
            ) > os.path.getmtime(destination):
                shutil.copy2(path, destination)
            copied += 1
            continue

        digest = hashlib.sha256(open(path, "rb").read()).hexdigest()[:12]
        native = source_width(path) or max(ladder)
        widths = [w for w in ladder if w <= native] or [min(native, min(ladder))]
        stem = os.path.basename(relative).rsplit(".", 1)[0]

        for width in widths:
            name = f"{stem}-{digest}-{width}.webp"
            keep.add(name)
            target_path = os.path.join(out_dir, name)
            if os.path.exists(target_path):
                continue
            subprocess.run(
                ["cwebp", "-quiet", "-q",
                 lookup(IMAGE_QUALITY, relative, DEFAULT_QUALITY),
                 "-sharp_yuv", "-metadata", "none",
                 "-resize", str(width), "0", path, "-o", target_path],
                check=True,
            )
            made += 1
        media.register(relative, digest, widths)
        saved += os.path.getsize(path) - os.path.getsize(
            os.path.join(out_dir, f"{stem}-{digest}-{widths[-1]}.webp")
        )

    for stale in os.listdir(out_dir):
        if stale not in keep:
            os.remove(os.path.join(out_dir, stale))

    return len(media.DERIVATIVES), made, saved, copied


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


CHROME = (
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
)


def generate_og():
    """screenshots the og template through the site's own stylesheet;
    run with --og after changing the template, the png is committed"""
    from resources.views import og

    scratch = "_og.html"
    write(scratch, og.render())
    server = subprocess.Popen(
        [sys.executable, "-m", "http.server", "8791", "--directory", PUBLIC],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        import time

        time.sleep(1.5)
        subprocess.run(
            [CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars",
             "--force-device-scale-factor=1", "--virtual-time-budget=5000",
             f"--window-size={og.WIDTH},{og.HEIGHT}",
             f"--screenshot={os.path.join(PUBLIC, 'og-image.png')}",
             "http://localhost:8791/_og.html"],
            check=True,
            capture_output=True,
        )
    finally:
        server.terminate()
        os.remove(os.path.join(PUBLIC, scratch))
    size = os.path.getsize(os.path.join(PUBLIC, "og-image.png"))
    print(f"  og-image.png {og.WIDTH}x{og.HEIGHT}, {size / 1024:,.0f} KB\n")


def main():
    if "--og" in sys.argv:
        generate_og()
    sources, made, saved, copied = optimise_images()
    print(f"  images: {sources} optimised ({made} derivatives written), "
          f"{copied} copied as-is, {saved / 1024:,.0f} KB saved\n")

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
