from dataclasses import dataclass
from typing import Callable

from config import site
from resources.views.pages import (
    blog,
    certifications,
    collabs,
    experience,
    gear,
    home,
    not_found,
    post,
    projects,
    resources,
    services,
    shop,
    shop_item,
    stack,
)


@dataclass(frozen=True)
class Route:
    name: str
    path: str
    view: Callable
    title: str
    description: str
    label: str = ""
    nav: str = ""
    layout: str = ""
    collection: str = ""
    inline_script: str = ""
    output: str = ""
    indexed: bool = True

    def url(self):
        return site.url(self.path)


ROUTES = [
    Route(
        name="home",
        path="",
        view=home,
        title=f"{site.NAME} — Portfolio",
        description=site.DESCRIPTION,
    ),
    Route(
        name="shop",
        path="shop",
        view=shop,
        title=f"Shop — {site.NAME}",
        description=f"Things {site.NAME} has made and put up for download.",
        label="Shop",
        nav="shop",
        layout="wide",
    ),
    Route(
        name="resources",
        path="resources",
        view=resources,
        title=f"Resources — {site.NAME}",
        description=f"Notes, references and tools {site.NAME} keeps coming back to.",
        label="Resources",
        nav="resources",
        layout="wide",
    ),
    Route(
        name="collabs",
        path="collabs",
        view=collabs,
        title=f"Collabs — {site.NAME}",
        description=f"Projects {site.NAME} has built together with other people.",
        label="Collabs",
        nav="collabs",
        layout="roomy",
    ),
    Route(
        name="opportunities",
        path="opportunities",
        view=services,
        title=f"Services — {site.NAME}",
        description=(
            f"Freelance services from {site.NAME} — websites, web apps, "
            "portfolios, design and video editing."
        ),
        label="Services",
        nav="opportunities",
        layout="roomy",
    ),
    Route(
        name="blog",
        path="blog",
        view=blog,
        title=f"Blog — {site.NAME}",
        description=(
            "Notes on artificial intelligence, full-stack development, and the "
            "projects behind them."
        ),
        label="Blog",
        nav="blog",
        layout="wide",
        inline_script=blog.VIEW_SCRIPT,
    ),
    Route(
        name="projects",
        path="projects",
        view=projects,
        title=f"Projects — {site.NAME}",
        description=f"Full-stack apps, AI work, and design projects built by {site.NAME}.",
        label="Projects",
        nav="projects",
        layout="wide",
    ),
    Route(
        name="experience",
        path="experience",
        view=experience,
        title=f"Experience — {site.NAME}",
        description=f"{site.NAME}'s experience and internships, in full.",
        label="Experience",
        nav="experience",
    ),
    Route(
        name="stack",
        path="stack",
        view=stack,
        title=f"Stack — {site.NAME}",
        description=f"The languages, frameworks and tools {site.NAME} works with.",
        label="Stack",
        nav="stack",
    ),
    Route(
        name="certifications",
        path="certifications",
        view=certifications,
        title=f"Certifications — {site.NAME}",
        description=f"Certifications earned by {site.NAME}, each linked to its source.",
        label="Certifications",
        nav="certifications",
        layout="wide",
    ),
    Route(
        name="gear",
        path="gear",
        view=gear,
        title=f"Gear — {site.NAME}",
        description=(
            f"The hardware {site.NAME} uses day to day — desk setup, everyday "
            "carry, and camera."
        ),
        label="Gear",
        nav="gear",
        layout="wide",
    ),
    Route(
        name="posts",
        path="posts/{slug}",
        view=post,
        title="{title} — " + site.NAME,
        description="{excerpt}",
        nav="blog",
        collection="posts",
    ),
    Route(
        name="shop.item",
        path="shop/{slug}",
        view=shop_item,
        title="{name} — " + site.NAME,
        description="{name} — free download from " + site.NAME + ".",
        nav="shop",
        layout="wide",
        collection="shop",
    ),
    Route(
        name="not_found",
        path="",
        view=not_found,
        title=f"Page not found — {site.NAME}",
        description="That page does not exist.",
        output="404.html",
        indexed=False,
    ),
]

NAV_GROUPS = [
    {"icons": True, "routes": ("shop", "blog", "gear", "resources")},
    {"icons": True, "routes": ("collabs", "opportunities")},
    {"icons": False, "routes": ("projects", "experience", "stack", "certifications")},
]

BY_NAME = {r.name: r for r in ROUTES}


def find(name):
    return BY_NAME[name]


def url(name):
    return find(name).url()


def label(name):
    return find(name).label
