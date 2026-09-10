NAME = "Jake Cardenas"
URL = "https://jakecardenas.vercel.app"
AUTHOR = "Jake Cardenas"
TAGLINE = "BSIT (Artificial Intelligence) student at St. Paul University Philippines"
DESCRIPTION = (
    "Jake Cardenas — BSIT (Artificial Intelligence) student at St. Paul "
    "University Philippines. Full-stack and AI developer."
)
EMAIL = "jakez.cardenas@gmail.com"

# browser chrome colour, and the pre-paint page background (these differ)
THEME_LIGHT = "#f4f4f2"
THEME_DARK = "#0c0c0f"
BG_LIGHT = "#ffffff"
BG_DARK = "#0c0c0f"

# bump after editing anything under resources/css or resources/js
ASSET_VERSION = "?v=178"

LINKS = {
    "github": "https://github.com/JakeCardenas",
    "linkedin": "https://www.linkedin.com/in/jake-cardenas-710076410/",
    "instagram": "https://instagram.com/prblynot.jky",
}

GITHUB_USER = "JakeCardenas"


def asset(path):
    return f"/{path}{ASSET_VERSION}"


def url(path=""):
    return f"/{path}/" if path else "/"
