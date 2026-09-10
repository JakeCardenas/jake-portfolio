from config import site
from resources.views.components import icons


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


LIVE_STATS = (("wpm", "wpm", ""), ("acc", "acc", "%"), ("time", "time", "s"))

RESULT_STATS = (("Acc", "accuracy", "%"), ("Raw", "raw", ""), ("Time", "time", "s"))


def typing():
    live = "\n".join(
        f'            <div class="tt-stat"><span class="tt-stat-val">'
        f'<span class="tt-num" id="tt{key.capitalize()}">'
        f'{"100" if key == "acc" else "0"}</span>'
        f'{f"<i>{unit}</i>" if unit else ""}</span>'
        f'<span class="tt-stat-label">{label}</span></div>'
        for key, label, unit in LIVE_STATS
    )
    grid = "\n".join(
        f'              <div><b><span id="ttRes{key}">0</span>'
        f'{f"<i>{unit}</i>" if unit else ""}</b>'
        f"<label>{label}</label></div>"
        for key, label, unit in RESULT_STATS
    )
    return f"""      <div class="overlay tt-overlay" id="typing" role="dialog" aria-modal="true"
           aria-labelledby="typingTitle" tabindex="-1" data-overlay-keys="self" hidden>
        <div class="overlay-panel tt-panel" data-overlay-panel>
          <h2 class="visually-hidden" id="typingTitle">Typing test</h2>
          <div class="tt-stats mono">
{live}
          </div>

          <div class="tt-words-wrap">
            <div class="tt-words" id="ttWords" aria-hidden="true"></div>
          </div>

          <div class="tt-keyboard" id="ttKeyboard" aria-hidden="true"></div>

          <div class="tt-hint mono">
            <span><kbd>tab</kbd> restart</span>
            <span><kbd>esc</kbd> close</span>
          </div>
          <div class="tt-confirm mono" id="ttConfirm">
            restart test? <kbd>&crarr;</kbd> to confirm &middot; <kbd>esc</kbd> cancel
          </div>

          <div class="tt-results">
            <div class="tt-res-main">
              <span class="tt-res-wpm" id="ttResWpm">0</span>
              <span class="tt-res-cap mono">words per minute</span>
            </div>
            <div class="tt-res-grid mono">
{grid}
            </div>
            <p class="tt-verdict mono" id="ttVerdict" role="status" aria-live="polite"></p>
            <button type="button" class="tt-restart mono" data-tt-restart>
              <span aria-hidden="true">&#8635;</span> try again
            </button>
          </div>

          <label class="visually-hidden" for="ttField">Type the words shown</label>
          <input class="tt-field" id="ttField" autocomplete="off" autocapitalize="off"
                 autocorrect="off" spellcheck="false" inputmode="text" />
        </div>
      </div>"""


def render():
    return "\n".join([typing(), contact()])
