from config import site
from resources.views.components import icons
from routes import web

THEME_SWITCH = """<div class="theme-switch" role="group" aria-label="Theme">
              <button type="button" class="ctl-btn" data-theme-btn="system" aria-label="System theme" title="System">
                <svg viewBox="0 0 24 24" fill="none"><rect x="3" y="4" width="18" height="13" rx="2" stroke="currentColor" stroke-width="1.7"/><path d="M9 21h6M12 17v4" stroke="currentColor" stroke-width="1.7" stroke-linecap="round"/></svg>
              </button>
              <button type="button" class="ctl-btn" data-theme-btn="light" aria-label="Light theme" title="Light">
                <svg viewBox="0 0 24 24" fill="none"><circle cx="12" cy="12" r="4" stroke="currentColor" stroke-width="1.7"/><path d="M12 2v2M12 20v2M2 12h2M20 12h2M5 5l1.4 1.4M17.6 17.6L19 19M19 5l-1.4 1.4M6.4 17.6L5 19" stroke="currentColor" stroke-width="1.7" stroke-linecap="round"/></svg>
              </button>
              <button type="button" class="ctl-btn" data-theme-btn="dark" aria-label="Dark theme" title="Dark">
                <svg viewBox="0 0 24 24" fill="none"><path d="M20 13.6A8 8 0 1 1 10.4 4a6.2 6.2 0 0 0 9.6 9.6z" stroke="currentColor" stroke-width="1.7" stroke-linejoin="round"/></svg>
              </button>
            </div>"""

SOUND_TOGGLE = """<button type="button" class="sound-btn" data-sound-toggle data-cuelume-silent
                    aria-pressed="false" aria-label="Enable interface sounds" title="Sounds off">
              <svg data-sound-on viewBox="0 0 24 24" fill="none" aria-hidden="true" hidden><path d="M5 10v4h3l4 3V7L8 10H5zM16 9a4 4 0 010 6M18.5 6.5a7.5 7.5 0 010 11" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"/></svg>
              <svg data-sound-off viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M5 10v4h3l4 3V7L8 10H5zM16 10l5 5M21 10l-5 5" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"/></svg>
            </button>"""

CONTROLS = f"""          <div class="control-pill">
            {THEME_SWITCH}
            {SOUND_TOGGLE}
          </div>"""

ACTIVE_ARROW = (
    '<svg class="nav-arrow" viewBox="0 0 24 24" fill="none" aria-hidden="true">'
    '<path d="M5 12h14M13 6l6 6-6 6" stroke="currentColor" stroke-width="2" '
    'stroke-linecap="round" stroke-linejoin="round"/></svg>'
)

MENU_OPEN = '<svg viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M4 7h16M4 12h16M4 17h16" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/></svg>'
MENU_CLOSE = '<svg viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M5 5l14 14M19 5L5 19" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/></svg>'

ACTIONS = """        <div class="rail-actions">
          <button type="button" class="rail-action" data-typing-open data-shortcut="j">
            <span>Typing test</span>
            <span class="keys" data-shortcut-label></span>
          </button>
        </div>"""


def nav_group(group, active, indent="            "):
    rows = []
    for name in group["routes"]:
        is_active = name == active
        cls = "nav-link active" if is_active else "nav-link"
        glyph = (
            f'<span class="nav-ico" aria-hidden="true">{icons.NAV[name]}</span>'
            if group["icons"]
            else ""
        )
        arrow = ACTIVE_ARROW if is_active else ""
        rows.append(
            f'{indent}<a href="{web.url(name)}" class="{cls}" data-nav>'
            f"{glyph}{web.label(name)}{arrow}</a>"
        )
    return "\n".join(rows)


def contact(cls=""):
    return (
        f'          <p class="side-note">For work, collabs &amp; everything else, '
        "reach me at</p>\n"
        f'          <a href="mailto:{site.EMAIL}" class="side-email mono{cls}">'
        f"{icons.MAIL}{site.EMAIL}</a>"
    )


def mobile(active):
    groups = "\n            <span class=\"mnav-rule\" aria-hidden=\"true\"></span>\n".join(
        f'            <div class="mnav-group" style="transition-delay: {0.05 + i * 0.06:.2f}s">\n'
        f"{nav_group(g, active, indent='              ')}\n"
        "            </div>"
        for i, g in enumerate(web.NAV_GROUPS)
    )
    delay = 0.05 + len(web.NAV_GROUPS) * 0.06
    return f"""      <header class="mobile-bar">
        <div class="mobile-bar-inner">
          <a href="{site.url()}" class="mobile-logo">{site.NAME}</a>
          <button type="button" class="mobile-menu-btn" data-mobile-nav-open aria-label="Open menu"
                  aria-controls="mobileNav" aria-expanded="false">{MENU_OPEN}</button>
        </div>
      </header>

      <div id="mobileNav" class="mobile-nav" hidden>
        <div class="mobile-bar-inner mobile-nav-head">
          <a href="{site.url()}" class="mobile-logo">{site.NAME}</a>
          <button type="button" class="mobile-menu-btn" data-mobile-nav-close aria-label="Close menu">{MENU_CLOSE}</button>
        </div>
        <nav class="mobile-nav-body mono" aria-label="Sections">
{groups}
            <span class="mnav-rule" aria-hidden="true"></span>
            <div class="mnav-group mnav-foot" style="transition-delay: {delay:.2f}s">
              <div class="control-pill">
                {THEME_SWITCH}
                {SOUND_TOGGLE}
              </div>
{contact(" mnav-email")}
            </div>
        </nav>
      </div>"""


def render(active):
    groups = f"\n          </div>\n          <span class=\"nav-rule\" aria-hidden=\"true\"></span>\n          <div class=\"nav-group\">\n".join(
        nav_group(g, active) for g in web.NAV_GROUPS
    )
    return f"""      <aside class="sidebar">
        <a href="{site.url()}" class="side-logo" data-nav-logo>{site.NAME}</a>

        <nav class="side-nav mono" id="siteNav" aria-label="Sections">
          <div class="nav-group">
{groups}
          </div>
        </nav>

{ACTIONS}

        <div class="side-foot">
{CONTROLS}

{contact()}
        </div>
      </aside>

{mobile(active)}"""
