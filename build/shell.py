"""Shared page shell — one definition, five pages, so the nav can never drift apart."""

V = "?v=129"

# the four fonts, loaded exactly as the reference does
HEAD_FONTS = f"""    <!-- fonts are self-hosted in ./fonts — no Google/jsDelivr dependency.
         the two the page opens with are preloaded so headings don't reflow -->
    <link rel="preload" href="./fonts/Geist-latin.woff2" as="font" type="font/woff2" crossorigin />
    <link rel="preload" href="./fonts/GeistMono-latin.woff2" as="font" type="font/woff2" crossorigin />
    <link
      rel="stylesheet"
      href="https://cdn.jsdelivr.net/npm/devicon@2.17.0/devicon.min.css"
    />
    <link
      rel="stylesheet"
      href="https://cdn.jsdelivr.net/npm/simple-icons-font@v13/font/simple-icons.min.css"
    />
    <link href="./css/site.css{V}" rel="stylesheet" />
    <!-- The reference applies the theme in <head>, before first paint, so the
         page never flashes the wrong one. Ours only ran at the end of <body>. -->
    <style>
      html {{ background-color: #ffffff; }}
      html.dark {{ background-color: #0c0c0f; }}
    </style>
    <script>
      (function () {{
        var KEY = "theme-mode";
        var root = document.documentElement;
        var mq = window.matchMedia
          ? window.matchMedia("(prefers-color-scheme: dark)")
          : null;
        function pref() {{
          try {{
            var v = localStorage.getItem(KEY);
            return v === "dark" || v === "light" || v === "system" ? v : "system";
          }} catch (e) {{
            return "system";
          }}
        }}
        function isDark(p) {{
          return p === "dark" || (p === "system" && !!mq && mq.matches);
        }}
        root.classList.toggle("dark", isDark(pref()));
      }})();
    </script>
"""

ICON = {
 "shop": '<svg viewBox="0 0 24 24" fill="none"><path d="M6 8h12l-1 11a2 2 0 01-2 2H9a2 2 0 01-2-2L6 8z" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round"/><path d="M9 8V6.5a3 3 0 016 0V8" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/></svg>',
 "resources": '<svg viewBox="0 0 24 24" fill="none"><path d="M4 5.5A1.5 1.5 0 015.5 4H11v15.5H6a2 2 0 00-2 1.2V5.5z" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round"/><path d="M20 5.5A1.5 1.5 0 0018.5 4H13v15.5h5a2 2 0 012 1.2V5.5z" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round"/></svg>',
 "collabs": '<svg viewBox="0 0 24 24" fill="none"><circle cx="9" cy="8" r="3" stroke="currentColor" stroke-width="1.6"/><path d="M3.5 19c0-3 2.5-5 5.5-5s5.5 2 5.5 5" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/><path d="M16 6.2a3 3 0 010 5.6M17 19c0-2.2-.8-3.8-2.1-4.8" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/></svg>',
 "opportunities": '<svg viewBox="0 0 24 24" fill="none"><rect x="3" y="7" width="18" height="13" rx="2" stroke="currentColor" stroke-width="1.6"/><path d="M8 7V5.5A1.5 1.5 0 019.5 4h5A1.5 1.5 0 0116 5.5V7M3 12.5h18" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/></svg>',
 "blog": '<svg viewBox="0 0 24 24" fill="none"><rect x="4" y="4" width="16" height="16" rx="2" stroke="currentColor" stroke-width="1.6"/><path d="M8 9h8M8 13h8M8 17h5" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/></svg>',
 "gear": '<svg viewBox="0 0 24 24" fill="none"><rect x="5" y="5" width="14" height="10" rx="1.5" stroke="currentColor" stroke-width="1.6"/><path d="M3 19h18M9.5 15h5" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/></svg>',
 "projects": '<svg viewBox="0 0 24 24" fill="none"><path d="M4 7.5A1.5 1.5 0 015.5 6h4l2 2.5h7A1.5 1.5 0 0120 10v7.5A1.5 1.5 0 0118.5 19h-13A1.5 1.5 0 014 17.5v-10z" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round"/></svg>',
 "experience": '<svg viewBox="0 0 24 24" fill="none"><rect x="3" y="7" width="18" height="13" rx="2" stroke="currentColor" stroke-width="1.6"/><path d="M8 7V5.5A1.5 1.5 0 019.5 4h5A1.5 1.5 0 0116 5.5V7M3 12.5h18" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/></svg>',
 "stack": '<svg viewBox="0 0 24 24" fill="none"><path d="M12 3l8 4.5-8 4.5-8-4.5L12 3z" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round"/><path d="M4 12l8 4.5 8-4.5M4 16.5L12 21l8-4.5" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round"/></svg>',
 "certifications": '<svg viewBox="0 0 24 24" fill="none"><circle cx="12" cy="9" r="5" stroke="currentColor" stroke-width="1.6"/><path d="M8.5 13.5L7 21l5-2.5L17 21l-1.5-7.5" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round"/></svg>',
}

# page links first, then the sections that live on the homepage
# The reference's rail is three groups: two icon groups, then a plain text
# group with no icons at all. Two hairlines separate them.
NAV_GROUP_1 = [
    ("shop",      "Shop",      "./shop/"),
    ("blog",      "Blog",      "./blog/"),
    ("gear",      "Gear",      "./gear/"),
    ("resources", "Resources", "./resources/"),
]
NAV_GROUP_2 = [
    ("collabs",       "Collabs",       "./collabs/"),
    ("opportunities", "Opportunities", "./opportunities/"),
]
NAV_GROUP_3 = [   # no icons here, exactly as the reference does it
    ("projects",       "Projects",       "./projects/"),
    ("experience",     "Experience",     "./experience/"),
    ("stack",          "Stack",          "./stack/"),
    ("certifications", "Certifications", "./certifications/"),
]

def nav(active, on_index):
    def rows(items, icons):
        out = []
        for key, label, href in items:
            cls = "nav-link active" if key == active else "nav-link"
            ico = f'<span class="nav-ico" aria-hidden="true">{ICON[key]}</span>' if icons else ""
            out.append(f'            <a href="{href}" class="{cls}" data-nav>{ico}{label}</a>')
        return "\n".join(out)
    return rows(NAV_GROUP_1, True), rows(NAV_GROUP_2, True), rows(NAV_GROUP_3, False)

CONTROLS = """          <div class="control-pill">
            <div class="theme-switch" role="group" aria-label="Theme">
              <button class="ctl-btn" data-theme-btn="system" aria-label="Match system theme" title="System">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
                  <rect x="2" y="4" width="20" height="13" rx="2" /><path d="M8 21h8M12 17v4" />
                </svg>
              </button>
              <button class="ctl-btn" data-theme-btn="light" aria-label="Light mode" title="Light">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
                  <circle cx="12" cy="12" r="4" />
                  <path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M4.93 19.07l1.41-1.41M17.66 6.34l1.41-1.41" />
                </svg>
              </button>
              <button class="ctl-btn" data-theme-btn="dark" aria-label="Dark mode" title="Dark">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79Z" />
                </svg>
              </button>
            </div>

            <span class="pill-divider" aria-hidden="true"></span>

            <button id="soundToggle" class="ctl-btn sound-btn" data-sound-toggle
                    aria-label="Enable interface sounds" aria-pressed="false" title="Sounds off">
              <svg class="sound-icon-on" data-sound-on viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
                <path d="M11 5 6 9H2v6h4l5 4V5Z" /><path d="M15.54 8.46a5 5 0 0 1 0 7.07" /><path d="M19.07 4.93a10 10 0 0 1 0 14.14" />
              </svg>
              <svg class="sound-icon-off" data-sound-off viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
                <path d="M11 5 6 9H2v6h4l5 4V5Z" /><line x1="23" y1="9" x2="17" y2="15" /><line x1="17" y1="9" x2="23" y2="15" />
              </svg>
            </button>
          </div>

          <a href="mailto:marijakee@gmail.com" class="side-email mono">marijakee@gmail.com</a>"""

def page(*, title, desc, active, on_index, body, extra_scripts="", wide=False):
    group_a, group_b, group_c = nav(active, on_index)
    main_mod = ' main--wide' if wide else ''
    return f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{title}</title>
    <meta name="description" content="{desc}" />
    <link rel="icon" href="./favicon.ico" sizes="16x16 32x32 48x48" />
    <link rel="icon" href="./icon-192.png" type="image/png" sizes="192x192" />
    <link rel="apple-touch-icon" href="./apple-touch-icon.png" />
    <link rel="manifest" href="./site.webmanifest" />
    <meta name="theme-color" content="#f4f4f2" media="(prefers-color-scheme: light)" />
    <meta name="theme-color" content="#0c0c0f" media="(prefers-color-scheme: dark)" />
    <meta property="og:title" content="{title}" />
    <meta property="og:description" content="{desc}" />
    <meta property="og:type" content="website" />
    <meta property="og:image" content="./icon-512.png" />
    <meta name="twitter:card" content="summary" />
{HEAD_FONTS}
  </head>
  <body>
    <div aria-hidden="true" class="page-halftone">
      <span class="ht ht-tr"></span><span class="ht ht-bl"></span>
    </div>

    <div class="shell">
      <aside class="sidebar">
        <a href="./index.html" class="side-logo" data-nav-logo>jakecardenas.com</a>

        <nav class="side-nav mono" id="siteNav" aria-label="Sections">
          <div class="nav-group">
{group_a}
          </div>
          <span class="nav-rule" aria-hidden="true"></span>
          <div class="nav-group">
{group_b}
          </div>
          <span class="nav-rule" aria-hidden="true"></span>
          <div class="nav-group">
{group_c}
          </div>
        </nav>

        <div class="side-foot">
{CONTROLS}
        </div>

        <button id="menuBtn" class="menu-btn mono" aria-controls="siteNav"
                aria-expanded="false" aria-label="Toggle navigation">
          <span class="menu-bars" aria-hidden="true"><i></i><i></i><i></i></span>
          <span class="menu-label">MENU</span>
        </button>
      </aside>

      <main class="main{main_mod}">
{body}
        <div class="site-foot mono">
          © 2026 JAKECARDENAS.COM — BUILT STATIC, HOSTED ANYWHERE.
        </div>
      </main>
    </div>

    <script src="./js/site-sounds.js{V}"></script>
{extra_scripts}    <script src="./js/site.js{V}"></script>
  </body>
</html>
"""
