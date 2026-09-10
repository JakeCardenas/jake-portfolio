from config import site
from resources import content
from resources.views.components import cards, media

COVER_SIZES = "(min-width: 1024px) 622px, calc(100vw - 2.5rem)"
RELATED = 2


def related(current):
    others = [p for p in content.load("posts") if p["slug"] != current["slug"]]
    if not others:
        return ""
    return f"""
        <section class="section article-related reveal">
          <div class="num-head">
            <h2 class="num-title">keep reading</h2>
            <a href="{site.url('blog')}" class="num-link mono">ALL POSTS →</a>
          </div>
{cards.posts(others[:RELATED], heading="h3")}
        </section>
"""


def render(post):
    return f"""        <section class="section reveal">
          <a href="{site.url('blog')}" class="article-back mono">← back to blog</a>
          <header class="article-head">
            <div class="article-meta mono">
              <span>{post['date']}</span>
              <span class="post-meta-sep">·</span>
              <span>{post['read']}</span>
            </div>
            <h1 class="article-title">{post['title']}</h1>
          </header>
          <div class="article-cover">
            {media.img(post['image'], sizes=COVER_SIZES, priority=True)}
          </div>
          <div class="prose">
{post['body']}
          </div>
        </section>
{related(post)}"""
