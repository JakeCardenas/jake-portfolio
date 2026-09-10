from resources import content
from resources.views.components import cards, headings

LEDE = "Certificates I've earned, each one linked to its source."


def render():
    return f"""        <section class="section reveal">
{headings.page("certifications", LEDE)}
          <div class="cert-grid">
{cards.certificates(content.load("certifications"))}
          </div>
        </section>
"""
