from config import site
from resources.views.components import icons


def palette():
    return """      <div class="overlay" id="palette" role="dialog" aria-modal="true"
           aria-labelledby="paletteTitle" hidden>
        <div class="overlay-panel pal-panel" data-overlay-panel>
          <h2 class="visually-hidden" id="paletteTitle">Search this site</h2>
          <div class="pal-field">
            <svg viewBox="0 0 24 24" fill="none" aria-hidden="true">
              <circle cx="11" cy="11" r="6.5" stroke="currentColor" stroke-width="1.6" />
              <path d="M16 16l4 4" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" />
            </svg>
            <input id="paletteInput" type="text" role="combobox" autocomplete="off"
                   aria-expanded="true" aria-controls="paletteList" aria-autocomplete="list"
                   placeholder="Search pages, projects, skills, writing…" />
            <button type="button" class="pal-esc mono" data-modal-close>ESC</button>
          </div>
          <ul class="pal-list" id="paletteList" role="listbox" aria-labelledby="paletteTitle"></ul>
          <p class="pal-empty mono" id="paletteEmpty" hidden>Nothing matches that yet.</p>
          <p class="visually-hidden" id="paletteStatus" role="status" aria-live="polite"></p>
          <div class="pal-foot mono">
            <span><kbd>↑</kbd><kbd>↓</kbd> navigate</span>
            <span><kbd>↵</kbd> open</span>
            <span><kbd>esc</kbd> close</span>
          </div>
        </div>
      </div>"""


def contact():
    return f"""      <div class="overlay" id="contactModal" role="dialog" aria-modal="true"
           aria-labelledby="contactTitle" hidden>
        <div class="overlay-panel modal-panel" data-overlay-panel>
          <div class="modal-head">
            <h2 class="modal-title" id="contactTitle">Get in touch</h2>
            <button type="button" class="modal-close" data-modal-close aria-label="Close">
              <svg viewBox="0 0 24 24" fill="none" aria-hidden="true">
                <path d="M6 6l12 12M18 6L6 18" stroke="currentColor" stroke-width="1.6"
                      stroke-linecap="round" />
              </svg>
            </button>
          </div>
          <p class="modal-body">
            Open to internships, freelance work and joining a team. Email is the
            quickest way to reach me.
          </p>
          <button type="button" class="modal-copy" data-copy="{site.EMAIL}">
            {icons.MAIL}
            <span class="modal-copy-value mono">{site.EMAIL}</span>
            <span class="modal-copy-hint mono" data-copy-feedback>Copy</span>
          </button>
          <div class="modal-links mono">
            <a href="mailto:{site.EMAIL}">Open mail app <span aria-hidden="true">↗</span></a>
            <a href="{site.LINKS['linkedin']}" target="_blank" rel="noopener">LinkedIn <span aria-hidden="true">↗</span></a>
            <a href="{site.LINKS['github']}" target="_blank" rel="noopener">GitHub <span aria-hidden="true">↗</span></a>
          </div>
        </div>
      </div>"""


DURATIONS = (15, 30, 60)

RESULTS = (
    ("wpm", "WPM"),
    ("accuracy", "ACCURACY"),
    ("raw", "RAW"),
    ("errors", "ERRORS"),
    ("characters", "CHARACTERS"),
)


def typing():
    durations = "\n".join(
        f'            <button type="button" class="tt-chip mono'
        f'{" is-active" if seconds == 30 else ""}" data-tt-duration="{seconds}">'
        f"{seconds}s</button>"
        for seconds in DURATIONS
    )
    cells = "\n".join(
        f'              <div class="tt-cell"><span class="tt-value" '
        f'data-tt-result="{key}">0</span>'
        f'<span class="tt-label mono">{label}</span></div>'
        for key, label in RESULTS
    )
    return f"""      <div class="overlay" id="typing" role="dialog" aria-modal="true"
           aria-labelledby="typingTitle" tabindex="-1" hidden>
        <div class="overlay-panel tt-panel" data-overlay-panel>
          <div class="tt-head">
            <h2 class="tt-title" id="typingTitle">Typing test</h2>
            <div class="tt-chips">
{durations}
            </div>
            <button type="button" class="modal-close" data-modal-close aria-label="Close">
              <svg viewBox="0 0 24 24" fill="none" aria-hidden="true">
                <path d="M6 6l12 12M18 6L6 18" stroke="currentColor" stroke-width="1.6"
                      stroke-linecap="round" />
              </svg>
            </button>
          </div>
          <div class="tt-meters mono">
            <span><b id="ttTime">30</b> left</span>
            <span><b id="ttWpm">0</b> wpm</span>
            <span><b id="ttAcc">100</b>% accuracy</span>
          </div>
          <div class="tt-stage">
            <div class="tt-stream" id="ttStream" aria-hidden="true"></div>
            <span class="tt-caret" id="ttCaret" aria-hidden="true"></span>
            <div class="tt-results" id="ttResults" hidden>
              <div class="tt-grid">
{cells}
              </div>
              <button type="button" class="tt-again mono" data-tt-restart>
                Run it again
              </button>
            </div>
          </div>
          <label class="visually-hidden" for="ttField">Type the words shown</label>
          <input class="tt-field" id="ttField" autocomplete="off" autocapitalize="off"
                 autocorrect="off" spellcheck="false" inputmode="text" />
          <div class="tt-foot mono">
            <span><kbd>tab</kbd> restart</span>
            <span><kbd>esc</kbd> close</span>
          </div>
        </div>
      </div>"""


def playground():
    return """      <div class="overlay" id="playground" role="dialog" aria-modal="true"
           aria-labelledby="playgroundTitle" tabindex="-1" hidden>
        <div class="overlay-panel pg-panel" data-overlay-panel>
          <div class="pg-head">
            <h2 class="pg-title" id="playgroundTitle">Halftone field</h2>
            <button type="button" class="pg-clear mono" data-pg-clear>Clear</button>
            <button type="button" class="modal-close" data-modal-close aria-label="Close">
              <svg viewBox="0 0 24 24" fill="none" aria-hidden="true">
                <path d="M6 6l12 12M18 6L6 18" stroke="currentColor" stroke-width="1.6"
                      stroke-linecap="round" />
              </svg>
            </button>
          </div>
          <div class="pg-stage">
            <canvas id="pgCanvas" aria-label="Interactive halftone dot field"
                    role="img"></canvas>
            <span class="pg-hint mono">Move to disturb · click to ripple</span>
          </div>
          <div class="pg-controls">
            <label class="pg-slider mono" for="pgCell">
              Cell
              <input type="range" id="pgCell" min="8" max="26" step="2" value="14" />
            </label>
            <span class="pg-readout mono" id="pgReadout"></span>
          </div>
        </div>
      </div>"""


def shortcuts():
    rows = "\n".join(
        f'            <div class="keys-row"><span>{label}</span>'
        f'<span class="keys-combo" data-shortcut="{key}">'
        f"<kbd data-shortcut-label></kbd></span></div>"
        for key, label in (
            ("k", "Search everything"),
            ("j", "Typing test"),
            ("/", "Halftone field"),
        )
    )
    return f"""      <div class="overlay" id="shortcuts" role="dialog" aria-modal="true"
           aria-labelledby="shortcutsTitle" hidden>
        <div class="overlay-panel modal-panel" data-overlay-panel>
          <div class="modal-head">
            <h2 class="modal-title" id="shortcutsTitle">Shortcuts</h2>
            <button type="button" class="modal-close" data-modal-close aria-label="Close">
              <svg viewBox="0 0 24 24" fill="none" aria-hidden="true">
                <path d="M6 6l12 12M18 6L6 18" stroke="currentColor" stroke-width="1.6"
                      stroke-linecap="round" />
              </svg>
            </button>
          </div>
          <div class="keys-list mono">
{rows}
          </div>
        </div>
      </div>"""


def render():
    return "\n".join([palette(), typing(), playground(), shortcuts(), contact()])
