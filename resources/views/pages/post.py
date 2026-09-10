from config import site
from resources.views.components import media

COVER_SIZES = "(min-width: 1024px) 622px, calc(100vw - 2.5rem)"


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
"""
