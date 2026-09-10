from config import site

PRELOAD_FONTS = ("fonts/Geist-latin.woff2", "fonts/GeistMono-latin.woff2")

# runs before first paint so a dark session never flashes white
THEME_BOOT = """    <script>
      (function () {
        var KEY = "theme-mode";
        var root = document.documentElement;
        var mq = window.matchMedia
          ? window.matchMedia("(prefers-color-scheme: dark)")
          : null;
        function pref() {
          try {
            var v = localStorage.getItem(KEY);
            return v === "dark" || v === "light" || v === "system" ? v : "system";
          } catch (e) {
            return "system";
          }
        }
        function isDark(p) {
          return p === "dark" || (p === "system" && !!mq && mq.matches);
        }
        root.classList.toggle("dark", isDark(pref()));
      })();
    </script>"""


def render(title, description, canonical, schema=""):
    structured_data = f"\n{schema}" if schema else ""
    preloads = "\n".join(
        f'    <link rel="preload" href="/{f}" as="font" type="font/woff2" crossorigin />'
        for f in PRELOAD_FONTS
    )
    return f"""    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{title}</title>
    <meta name="description" content="{description}" />
    <link rel="canonical" href="{canonical}" />
    <link rel="icon" href="/favicon.ico" sizes="16x16 32x32 48x48" />
    <link rel="icon" href="/icon-192.png" type="image/png" sizes="192x192" />
    <link rel="apple-touch-icon" href="/apple-touch-icon.png" />
    <link rel="manifest" href="/site.webmanifest" />
    <link rel="describedby" type="text/markdown" href="/llms.txt" />
    <link rel="alternate" type="application/feed+json" title="{site.NAME} — Blog (JSON Feed)" href="/feed.json" />
    <link rel="alternate" type="application/rss+xml" title="{site.NAME} — Blog (RSS)" href="/feed.xml" />
    <meta name="theme-color" content="{site.THEME_LIGHT}" media="(prefers-color-scheme: light)" />
    <meta name="theme-color" content="{site.THEME_DARK}" media="(prefers-color-scheme: dark)" />
    <meta property="og:title" content="{title}" />
    <meta property="og:description" content="{description}" />
    <meta property="og:type" content="website" />
    <meta property="og:url" content="{canonical}" />
    <meta property="og:image" content="/icon-512.png" />
    <meta name="twitter:card" content="summary" />{structured_data}
{preloads}
    <link rel="stylesheet" href="{site.asset('css/site.css')}" />
    <style>
      html {{ background-color: {site.BG_LIGHT}; }}
      html.dark {{ background-color: {site.BG_DARK}; }}
    </style>
{THEME_BOOT}"""
