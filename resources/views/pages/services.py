from config import site
from resources import content
from resources.views.components import headings, icons

LEDE = (
    "I help individuals, creators, and businesses bring ideas to life through "
    "modern web development, creative design, and engaging digital experiences."
)


def card(entry):
    features = "\n".join(
        f"                  <li>{icons.CHECK}{f}</li>" for f in entry["features"]
    )
    return f"""            <article class="svc-card reveal">
              <span class="svc-dither" aria-hidden="true"></span>
              <span class="svc-mark" aria-hidden="true">
                <svg viewBox="0 0 24 24" fill="none">{icons.SERVICE[entry['icon']]}</svg>
              </span>
              <div class="svc-body">
                <div class="svc-head">
                  <h2 class="svc-title">{entry['title']}</h2>
                  <span class="svc-tag mono">{entry['tag']}</span>
                </div>
                <p class="svc-desc">{entry['description']}</p>
                <div class="svc-rule"></div>
                <ul class="svc-list">
{features}
                </ul>
              </div>
            </article>"""


def render():
    cards = "\n".join(card(s) for s in content.load("services"))
    return f"""        <section class="section reveal">
{headings.page("services", LEDE)}
          <div class="svc-grid">
{cards}
          </div>

          <div class="svc-cta">
            <div>
              <h2 class="svc-cta-title">let's work together</h2>
              <p class="svc-cta-body">
                Tell me about your project, brand, or idea and I'll come back with
                how I can help and a simple way to start.
              </p>
            </div>
            <div class="svc-cta-actions">
              <a href="mailto:{site.EMAIL}?subject=Project%20inquiry" class="svc-cta-btn">{icons.MAIL}Get in touch</a>
              <a href="mailto:{site.EMAIL}" class="svc-cta-mail mono">{site.EMAIL}</a>
            </div>
          </div>
        </section>
"""
