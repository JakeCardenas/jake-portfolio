# jake-portfolio

Personal portfolio for Jake Cardenas — BSIT student majoring in Artificial
Intelligence at St. Paul University Philippines.

Static site, no framework and no runtime dependencies. `public/` is generated
from `resources/` by a small Python build, so the layout, nav and page shell are
defined once instead of being copy-pasted into a dozen files.

## Running it

    python3 build.py                                  # regenerate public/
    python3 -m http.server 8000 --directory public    # serve

Then open http://localhost:8000

## Layout

    build.py                  renders resources/ into public/
    vercel.json               tells Vercel to serve public/
    config/
      site.py                 name, url, email, links, theme colours, asset version
    routes/
      web.py                  every route: path, view, title, description, nav group
    resources/
      views/
        layouts/base.py       the <html> document
        partials/head.py      meta, og, icons, fonts, pre-paint theme script
        partials/sidebar.py   logo, nav, theme + sound controls, contact block
        pages/*.py            one module per route
        components/           markup shared by more than one page
          cards.py            post cards, certificate cards
          headings.py         numbered section heads, page heads
          icons.py            the inline SVG set
      content/*.json          the writing and the data behind every page
      css/*.css               one file per feature, bundled into css/site.css
      js/*.js                 one file per behaviour, bundled into js/site.js
    public/                   what actually ships
      index.html              generated
      <route>/index.html      generated, one folder per route
      css/site.css            generated bundle
      js/site.js              generated bundle
      js/site-sounds.js       Cuelume (MIT), vendored as-is
      images/ fonts/ downloads/
      sitemap.xml llms.txt feed.json feed.xml     generated
      favicon.ico icon-*.png apple-touch-icon.png site.webmanifest robots.txt

## Everything in public/ is build output

`build.py` rewrites every page, `css/site.css` and `js/site.js` on each run, so
hand-editing them is lost on the next build. To change something:

| To change… | Edit |
|---|---|
| Written content, projects, gear, certs, stack, posts | `resources/content/*.json` |
| A page's markup | `resources/views/pages/<page>.py` |
| Nav, contact block, `<head>` | `resources/views/partials/` |
| A new route, or a page title / description | `routes/web.py` |
| Styling | `resources/css/<feature>.css` |
| Behaviour | `resources/js/<behaviour>.js` |
| Name, email, links, cache-buster | `config/site.py` |

## Bundle order is load-bearing

`STYLESHEETS` in `build.py` is not alphabetical, and reordering it will change
the site. Several rules rely on source order to win — `body::before`'s dot size,
the `.side-email` mobile overrides, and the sequence of `max-width: 1023.98px`
blocks in `responsive.css`, which must stay last.

For the same reason a few small-screen `@media` blocks that touch several
components at once live in the feature file they were written next to rather
than being split up.

`SCRIPTS` order matters too: `theme.js` calls `renderAllHalftones()`, so
`halftone.js` has to be bundled first.

## Cache busting

`ASSET_VERSION` in `config/site.py` is appended to every generated asset URL.
Bump it after editing anything under `resources/css` or `resources/js`, then
rebuild.

## Notes

Interaction sounds are synthesised at runtime with Web Audio, so there are no
audio files to store.

Post dates carry month precision (`"Sep 2026"`). The feeds derive an ISO date
from that, defaulting to the first of the month; add a day to the content if you
want exact `pubDate` values.
