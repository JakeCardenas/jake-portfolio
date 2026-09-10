import json

from config import site
from resources import content

AFFILIATION = "St. Paul University Philippines"
JOB_TITLE = "Full-stack and AI developer"


def website():
    return {
        "@type": "WebSite",
        "@id": f"{site.URL}#website",
        "url": site.URL,
        "name": site.NAME,
        "description": site.DESCRIPTION,
        "inLanguage": "en",
        "publisher": {"@id": f"{site.URL}#person"},
    }


def person():
    return {
        "@type": "Person",
        "@id": f"{site.URL}#person",
        "name": site.NAME,
        "url": site.URL,
        "email": f"mailto:{site.EMAIL}",
        "jobTitle": JOB_TITLE,
        "description": site.TAGLINE,
        "affiliation": {"@type": "CollegeOrUniversity", "name": AFFILIATION},
        "sameAs": list(site.LINKS.values()),
    }


def profile_page(canonical, title):
    return {
        "@type": "ProfilePage",
        "@id": f"{canonical}#profile",
        "url": canonical,
        "name": title,
        "mainEntity": {"@id": f"{site.URL}#person"},
        "isPartOf": {"@id": f"{site.URL}#website"},
    }


def web_page(canonical, title, description):
    return {
        "@type": "WebPage",
        "@id": f"{canonical}#page",
        "url": canonical,
        "name": title,
        "description": description,
        "isPartOf": {"@id": f"{site.URL}#website"},
        "about": {"@id": f"{site.URL}#person"},
    }


def blog_posting(post):
    url = f"{site.URL}{site.url('posts/' + post['slug'])}"
    entry = {
        "@type": "BlogPosting",
        "@id": f"{url}#post",
        "url": url,
        "headline": post["title"],
        "description": post["excerpt"],
        "image": f"{site.URL}/{post['image']}",
        "author": {"@id": f"{site.URL}#person"},
        "publisher": {"@id": f"{site.URL}#person"},
        "isPartOf": {"@id": f"{site.URL}#website"},
        "inLanguage": "en",
    }
    date = content.published(post["date"])
    if date:
        entry["datePublished"] = date.date().isoformat()
    return entry


def render(route, item, canonical, title, description):
    graph = [website(), person()]
    if route.name == "home":
        graph.append(profile_page(canonical, title))
        graph += [blog_posting(p) for p in content.load("posts")]
    elif route.collection == "posts":
        graph.append(blog_posting(item))
    else:
        graph.append(web_page(canonical, title, description))
    payload = json.dumps(
        {"@context": "https://schema.org", "@graph": graph},
        separators=(",", ":"),
        ensure_ascii=False,
    )
    return f'    <script type="application/ld+json">{payload}</script>'
