from config import site
from resources.views.components import headings

LEDE = "That page does not exist — it may have moved, or the link may be wrong."


def render():
    return f"""        <section class="section reveal">
{headings.page("404", LEDE)}
          <div class="row-list">
            <a class="row-item" href="{site.url()}">
              <span class="row-year mono">HOME</span>
              <span class="row-title">Back to the homepage</span>
              <span class="row-org">Profile and selected work</span>
            </a>
            <a class="row-item" href="{site.url('blog')}">
              <span class="row-year mono">BLOG</span>
              <span class="row-title">Read the latest posts</span>
              <span class="row-org">Notes on AI and development</span>
            </a>
            <a class="row-item" href="{site.url('projects')}">
              <span class="row-year mono">WORK</span>
              <span class="row-title">See the projects</span>
              <span class="row-org">Full-stack apps and AI work</span>
            </a>
          </div>
        </section>
"""
