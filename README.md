# jake-portfolio

Personal portfolio for Jake Cardenas — BSIT student majoring in
Artificial Intelligence at St. Paul University Philippines.

Static site. No build step, no dependencies, no framework.

## Running it

Any static server works:

    python3 -m http.server 4173

Then open http://localhost:4173

Opening `index.html` directly also works — the profile photos are
embedded as data URIs so the halftone effect survives `file://`, where
reading canvas pixels from a relative path is blocked.

## Structure

    index.html              markup for every section
    style.css               design tokens and all styling
    js/
      sound.js              Web Audio interaction sounds
      script.js             halftone renderer, theme, nav, modal, GitHub graph
    assets/
      icons/                favicon set, generated from the profile photo
      images/profile/       portrait photos, rendered to canvas as halftone
      images/projects/      project screenshots
      resume/               CV goes here (see the README inside)
    certificates/           certificate scans shown in the modal

## Notes

Cache busting is manual: `index.html` links CSS and JS with a `?v=`
query. Bump it when editing either, or browsers may pair a new file
with a stale one.

The GitHub section pulls live contribution data at runtime and caches
it for six hours, so it stays current without being committed.

Sound is off-by-default-safe: no audio context exists until the first
real interaction, and the toggle in the sidebar persists the choice.
