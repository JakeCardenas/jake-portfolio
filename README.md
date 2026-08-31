# jake-portfolio

Personal portfolio for Jake Cardenas — BSIT student majoring in
Artificial Intelligence at St. Paul University Philippines.

Static site. No build step, no dependencies, no framework.

## Running it

Any static server works:

    python3 -m http.server 4173

Then open http://localhost:4173

Opening `index.html` directly also works — `js/halftone-sources.js`
carries the portraits as data URIs so the halftone effect survives
`file://`, where reading canvas pixels from a relative path is blocked.

## Structure

    index.html              markup for every section
    gear.html               the gear page, sharing index.html's shell
    css/style.css           design tokens and all styling
    js/
      sound.js              Web Audio interaction sounds
      halftone-sources.js   grayscale portrait data, for file:// only
      script.js             halftone renderer, theme, nav, modal, GitHub graph
    assets/
      icons/                favicon set, generated from the profile photo
      images/profile/       portrait photos, rendered to canvas as halftone
      images/projects/      project screenshots
      images/gear/          product shots for the gear page
      certificates/         certificate scans shown in the modal
      resume/               CV goes here (see the README inside)

## Notes

Cache busting is manual: both pages link CSS and JS with a `?v=` query.
Bump it in `index.html` and `gear.html` together when editing either, or
browsers may pair a new file with a stale one.

`gear.html` reuses the same sidebar, controls, and stylesheet as the home
page. It skips `halftone-sources.js`, which only the hero portraits need,
and its section carries no `id` so the home page's scroll-spy cannot clear
the active GEAR link.

The GitHub section pulls live contribution data at runtime and caches
it for six hours, so it stays current without being committed.

Sound is off-by-default-safe: no audio context exists until the first
real interaction, and the toggle in the sidebar persists the choice.
