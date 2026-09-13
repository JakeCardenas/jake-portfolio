from urllib.parse import quote

from config import site
from resources.views.components import media

COVER_SIZES = "(min-width: 640px) 624px, calc(100vw - 3rem)"

BACK_ARROW = '<svg viewBox="0 0 16 16" fill="none" aria-hidden="true"><path d="M10 13L5 8l5-5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>'
LINKEDIN = '<svg fill="currentColor" viewBox="0 0 24 24" aria-hidden="true"><path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433a2.062 2.062 0 110-4.124 2.062 2.062 0 010 4.124zM7.119 20.452H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/></svg>'
LINK = '<svg fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1"/></svg>'

SCRIPT = """        <script>
          (function () {
            var bar = document.getElementById("readingProgress");
            var article = document.querySelector(".article");
            function update() {
              var h = article.offsetHeight - window.innerHeight;
              var pct = h > 0 ? ((window.scrollY - article.offsetTop) / h) * 100 : 0;
              bar.style.width = Math.min(100, Math.max(0, pct)) + "%";
            }
            window.addEventListener("scroll", update, { passive: true });
            update();
            document.querySelector("[data-copy-link]").addEventListener("click", function (e) {
              var btn = e.currentTarget;
              if (!navigator.clipboard || !window.isSecureContext) return;
              navigator.clipboard.writeText(window.location.href).then(function () {
                btn.classList.add("is-copied");
                setTimeout(function () { btn.classList.remove("is-copied"); }, 1400);
              });
            });
          })();
        </script>"""


def render(post):
    blog = site.url("blog")
    share = "https://www.linkedin.com/sharing/share-offsite/?url=" + quote(
        site.URL + site.url("posts/" + post["slug"]), safe=""
    )
    return f"""        <div id="readingProgress" class="reading-progress" style="width: 0%"></div>
        <article class="section article">
          <a href="{blog}" class="article-back mono">{BACK_ARROW} all posts</a>
          <header class="article-head">
            <div class="article-meta mono">
              <time>{post['date']}</time>
              <span class="article-meta-sep">·</span>
              <span>{post['read']} read</span>
            </div>
            <h1 class="article-title">{post['title']}</h1>
            <div class="article-author">
              <img src="/apple-touch-icon.png" alt="{site.NAME}" class="article-avatar" />
              <div class="article-author-name">{site.NAME}</div>
            </div>
          </header>
          <figure class="article-cover">
            {media.img(post['image'], sizes=COVER_SIZES, alt=post['title'], priority=True)}
          </figure>
          <div class="prose">
{post['body']}
          </div>
          <footer class="article-foot">
            <a href="{blog}" class="article-back mono">{BACK_ARROW} all posts</a>
            <div class="article-share">
              <a href="{share}" target="_blank" rel="noopener" class="article-share-btn" aria-label="Share on LinkedIn">{LINKEDIN}</a>
              <button type="button" class="article-share-btn" data-copy-link aria-label="Copy link">{LINK}</button>
            </div>
          </footer>
        </article>
{SCRIPT}
"""
