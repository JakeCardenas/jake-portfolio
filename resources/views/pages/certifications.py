from resources import content
from resources.views.components import cards, headings

LEDE = "Certificates I've earned, each one linked to its source."

# the reference wall repeats one tilt sequence per section, so every group starts the same way
TILTS = (("-4deg", "6px"), ("3deg", "-4px"), ("-2deg", "3px"), ("4deg", "-6px"), ("-3deg", "4px"), ("2deg", "-3px"))


def sections():
    groups = {}
    for cert in content.load("certifications"):
        groups.setdefault(cert["category"], []).append(cert)
    blocks = []
    for name, certs in groups.items():
        tilted = [
            dict(cert, rot=TILTS[i % len(TILTS)][0], ty=TILTS[i % len(TILTS)][1])
            for i, cert in enumerate(certs)
        ]
        blocks.append(
            f"""          <section class="cert-section">
            <h2 class="cert-section-title mono">{name}</h2>
            <div class="cert-grid">
{cards.certificates(tilted)}
            </div>
          </section>"""
        )
    return "\n".join(blocks)


def render():
    return f"""        <section class="section reveal">
{headings.page("certifications", LEDE, lede_gap="2.5rem")}
          <div class="cert-sections">
{sections()}
          </div>
        </section>
"""
