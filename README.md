# jake-portfolio

Personal portfolio for Jake Cardenas — BSIT student majoring in
Artificial Intelligence at St. Paul University Philippines.

Static output, no framework and no runtime dependencies. The HTML is
**generated** by a small Python build so the nav, `<head>`, and page shell
are defined once instead of being copy-pasted into a dozen files.

## Running it

    python3 build/build.py       # regenerate every page
    python3 -m http.server 4173  # serve

Then open http://localhost:4173

## Important: the HTML is build output

Every `index.html` in this repo is **generated**. `build/build.py` rewrites
all of them on each run, so hand-editing one is lost on the next build.

To change a page, edit the source instead:

| To change… | Edit |
|---|---|
| Page shell, `<head>`, nav, script/style tags | `build/shell.py` |
| Page list, layout, section markup | `build/build.py` |
| Written content (projects, gear, certs, stack) | `build/content.json` |

## Structure

    index.html                  generated homepage
    <page>/index.html           generated page, one folder per route

    css/
      main.css                  @font-face, design tokens, base elements, page shell
      components.css            discrete UI pieces; each keeps its own media queries
      responsive.css            breakpoints that restructure the shell itself

    js/
      main.js                   scroll reveal, portrait swap, carousels
      theme.js                  light/dark/system + the circular reveal wipe
      nav.js                    mobile menu and scroll-spy
      cards.js                  project deck (event delegation, no inline handlers)
      halftone.js               canvas halftone renderer
      halftone-data.js          base64 portrait data, file:// fallback only
      sounds.js                 Web Audio interaction sounds (synthesised, no files)
      fetches/
        github.js               public contribution graph

    images/
      profile/  projects/  certs/  gear/  shop/

    fonts/                      self-hosted woff2 — no CDN for text
    downloads/                  files offered to visitors (résumé template)
    build/                      the generator: shell.py, build.py, content.json

There is no `sounds/` folder: interaction sounds are synthesised at runtime
with Web Audio oscillators, so there are no audio files to store.

### Script load order matters

`shell.py` emits the scripts in dependency order, and it is a real
constraint, not a preference:

    halftone-data.js -> halftone.js -> theme.js

`applyTheme()` calls `renderAllHalftones()` so the portraits repaint in the
new palette when the theme flips.

## Cache busting

`V` in `build/shell.py` is the cache-buster. Bump it after editing any CSS
or JS, then rebuild — every generated page picks it up automatically.

## Secrets

There are none, and none are needed: the site is fully static and calls only
public endpoints. `.gitignore` already covers `.env`, `*.pem`, and `*.key` so
that stays true if server-side APIs are added later.
