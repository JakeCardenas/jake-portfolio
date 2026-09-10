from resources import content
from resources.views.components import cards, headings, icons

LEDE = (
    "Notes on what I am learning — building projects, working with AI, and the "
    "lessons that come out of both."
)

VIEW_SCRIPT = """    <script>
      (function () {
        const box = document.getElementById("postsContainer");
        if (!box) return;
        const btns = document.querySelectorAll(".view-btn");
        const cards = Array.from(box.querySelectorAll(".post-card"));
        const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;
        let current = null;

        function paint(v) {
          btns.forEach((b) => b.classList.toggle("is-active", b.dataset.view === v));
        }
        function apply(v) {
          box.classList.remove("view-list", "view-grid");
          box.classList.add("view-" + v);
        }
        function setView(v, animate) {
          v = v === "grid" ? "grid" : "list";
          paint(v);
          if (v === current) return;
          try { localStorage.setItem("blogView", v); } catch (e) {}
          if (!animate || reduce) { apply(v); current = v; return; }

          box.classList.add("switching");
          setTimeout(() => {
            apply(v);
            current = v;
            cards.forEach((c) => c.classList.add("card-enter"));
            box.classList.remove("switching");
            requestAnimationFrame(() =>
              requestAnimationFrame(() => {
                cards.forEach((c, i) => {
                  c.style.transitionDelay = Math.min(i * 25, 280) + "ms";
                  c.classList.remove("card-enter");
                });
              })
            );
            setTimeout(() => cards.forEach((c) => (c.style.transitionDelay = "")), 800);
          }, 200);
        }

        let saved = "list";
        try { saved = localStorage.getItem("blogView") || "list"; } catch (e) {}
        setView(saved, false);
        btns.forEach((b) => b.addEventListener("click", () => setView(b.dataset.view, true)));
      })();
    </script>
"""


def render():
    return f"""        <section class="section reveal">
          <div class="blog-head">
{headings.page("blog", LEDE)}
            <div class="view-toggle" role="group" aria-label="Layout">
              <button type="button" class="view-btn is-active" data-view="list" title="List view" aria-label="List view">{icons.VIEW['list']}</button>
              <button type="button" class="view-btn" data-view="grid" title="Grid view" aria-label="Grid view">{icons.VIEW['grid']}</button>
            </div>
          </div>
{cards.posts(content.load("posts"), container_id="postsContainer")}
        </section>
"""
