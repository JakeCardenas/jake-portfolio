from config import site
from resources.views.components import icons
from routes import web

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

            <button id="soundToggle" class="ctl-btn sound-btn" data-sound-toggle
                    aria-label="Enable interface sounds" aria-pressed="false" title="Sounds off">
              <svg class="sound-icon-on" data-sound-on viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
                <path d="M11 5 6 9H2v6h4l5 4V5Z" /><path d="M15.54 8.46a5 5 0 0 1 0 7.07" /><path d="M19.07 4.93a10 10 0 0 1 0 14.14" />
              </svg>
              <svg class="sound-icon-off" data-sound-off viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
                <path d="M11 5 6 9H2v6h4l5 4V5Z" /><line x1="23" y1="9" x2="17" y2="15" /><line x1="17" y1="9" x2="23" y2="15" />
              </svg>
            </button>
          </div>"""


ACTIONS = """        <div class="rail-actions">
          <button type="button" class="rail-action" data-palette-open data-shortcut="k">
            <svg viewBox="0 0 24 24" fill="none" aria-hidden="true">
              <circle cx="11" cy="11" r="6.5" stroke="currentColor" stroke-width="1.6" />
              <path d="M16 16l4 4" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" />
            </svg>
            Search
            <span class="keys" data-shortcut-label></span>
          </button>
          <button type="button" class="rail-action" data-typing-open data-shortcut="j">
            <svg viewBox="0 0 24 24" fill="none" aria-hidden="true">
              <rect x="2.5" y="6.5" width="19" height="11" rx="2" stroke="currentColor" stroke-width="1.5" />
              <path d="M7 10h.01M10 10h.01M13 10h.01M16 10h.01M8 14h8" stroke="currentColor"
                    stroke-width="1.5" stroke-linecap="round" />
            </svg>
            Typing test
            <span class="keys" data-shortcut-label></span>
          </button>
          <button type="button" class="rail-action" data-playground-open data-shortcut="/">
            <svg viewBox="0 0 24 24" fill="none" aria-hidden="true">
              <circle cx="7" cy="7" r="1.6" fill="currentColor" />
              <circle cx="12" cy="7" r="1" fill="currentColor" />
              <circle cx="17" cy="7" r="1.6" fill="currentColor" />
              <circle cx="7" cy="12" r="1" fill="currentColor" />
              <circle cx="12" cy="12" r="2.2" fill="currentColor" />
              <circle cx="17" cy="12" r="1" fill="currentColor" />
              <circle cx="7" cy="17" r="1.6" fill="currentColor" />
              <circle cx="12" cy="17" r="1" fill="currentColor" />
              <circle cx="17" cy="17" r="1.6" fill="currentColor" />
            </svg>
            Halftone field
            <span class="keys" data-shortcut-label></span>
          </button>
        </div>"""


def nav_group(group, active):
    rows = []
    for name in group["routes"]:
        cls = "nav-link active" if name == active else "nav-link"
        glyph = (
            f'<span class="nav-ico" aria-hidden="true">{icons.NAV[name]}</span>'
            if group["icons"]
            else ""
        )
        rows.append(
            f'            <a href="{web.url(name)}" class="{cls}" data-nav>'
            f"{glyph}{web.label(name)}</a>"
        )
    return "\n".join(rows)


def render(active):
    groups = f"\n          </div>\n          <span class=\"nav-rule\" aria-hidden=\"true\"></span>\n          <div class=\"nav-group\">\n".join(
        nav_group(g, active) for g in web.NAV_GROUPS
    )
    contact = (
        '          <p class="side-note">For work, collabs and everything else, '
        "reach me at</p>\n"
        f'          <a href="mailto:{site.EMAIL}" class="side-email mono">'
        f"{icons.MAIL}{site.EMAIL}</a>"
    )
    return f"""      <aside class="sidebar">
        <a href="{site.url()}" class="side-logo" data-nav-logo>{site.NAME}</a>

{ACTIONS}

        <nav class="side-nav mono" id="siteNav" aria-label="Sections">
          <div class="nav-group">
{groups}
          </div>
        </nav>

        <div class="side-foot">
{CONTROLS}

{contact}
        </div>

        <button id="menuBtn" class="menu-btn mono" aria-controls="siteNav"
                aria-expanded="false" aria-label="Toggle navigation">
          <span class="menu-bars" aria-hidden="true"><i></i><i></i><i></i></span>
          <span class="menu-label">MENU</span>
        </button>
      </aside>"""
