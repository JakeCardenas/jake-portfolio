Product shots for the Gear section.

Filenames are listed in `GEAR_GROUPS` in `build/build.py`:

  macbook-air-m2.webp          MacBook Air M2 — laptop
  aoc-24g2sp.webp              AOC 24G2SP — monitor
  aula-f75.webp                Aula F75 — keyboard
  logitech-gpx-superlight.webp Logitech G Pro X Superlight — mouse
  xiaomi-light-bar.webp        Xiaomi Monitor Light Bar
  aful-explorer.webp           AFUL Explorer — IEM
  sihoo-m57.webp               Sihoo M57 — chair
  iphone-13.webp               iPhone 13
  airpods-pro-3.webp           AirPods Pro 3
  anker-165w.webp              Anker 165W power bank
  fitbit-air.webp              Google Fitbit Air
  kodak-fz55.webp              Kodak FZ55 — camera

Shots are square (1200x1200) so they fill the tile's content box exactly.
The tile itself follows the theme, so in dark mode each shot reads as a
white square inset by the tile padding.

To add or replace one, pad it square on white first:

  sips --padToHeightWidth 1200 1200 --padColor FFFFFF shot.jpg --out sq.jpg
  cwebp -q 82 -m 6 sq.jpg -o images/gear/<name>.webp
