from config import site
from resources.views.partials import head, overlays, sidebar


def render(
    *, title, description, canonical, body, nav="", layout="", inline_script="", schema=""
):
    modifier = f" main--{layout}" if layout else ""
    # a page script runs before site.js so any class it sets lands before the
    # first paint; deferring it lets the styled state transition in visibly
    page_script = f"{inline_script.rstrip()}\n" if inline_script else ""
    return f"""<!doctype html>
<html lang="en">
  <head>
{head.render(title, description, canonical, schema)}
  </head>
  <body>
    <div aria-hidden="true" class="page-halftone">
      <span class="ht ht-tr"></span><span class="ht ht-bl"></span>
    </div>

    <div class="shell">
{sidebar.render(nav)}

      <main class="main{modifier}">
{body}
      </main>
    </div>

{overlays.render()}

    <script src="{site.asset('js/site-sounds.js')}"></script>
{page_script}    <script src="{site.asset('js/site.js')}"></script>
  </body>
</html>
"""
