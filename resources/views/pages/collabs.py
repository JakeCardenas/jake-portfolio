from config import site
from resources import content
from resources.views.components import headings, icons, media

LEDE = (
    "I have collaborated, created, learned and built across organizations, "
    "platforms and communities throughout my journey in technology and creativity."
)

LOGO_SIZES = "(min-width: 641px) 56px, 48px"


def render():
    logos = "\n".join(
        "            "
        + media.img(c["logo"], sizes=LOGO_SIZES, alt=c["name"], cls="collab-logo")
        for c in content.load("collabs")
    )
    return f"""        <section class="section reveal">
{headings.page("collabs", LEDE)}
          <div class="collab-row">
{logos}
          </div>
          <div class="collab-map" aria-hidden="true"></div>
          <p class="collab-map-note mono">Learning and building from the Philippines</p>

          <div class="collab-cta">
            <div>
              <h2 class="collab-cta-title">let's work together</h2>
              <p class="collab-cta-body">
                Open to internships, freelance work and joining a team. If you
                have something you'd like to build, the quickest way to reach me
                is email.
              </p>
            </div>
            <div class="collab-cta-actions">
              <a href="mailto:{site.EMAIL}?subject=Collaboration" class="collab-cta-btn">{icons.MAIL}Get in touch</a>
              <a href="mailto:{site.EMAIL}" class="collab-cta-mail mono">{site.EMAIL}</a>
            </div>
          </div>
        </section>
"""
