function computeAutoLevels(data, cutoff = 0.01) {
  const hist = new Array(256).fill(0);
  let counted = 0;
  for (let i = 0; i < data.length; i += 4) {
    const luma =
      (0.299 * data[i] + 0.587 * data[i + 1] + 0.114 * data[i + 2]) | 0;
    hist[luma]++;
    counted++;
  }
  if (!counted) return { lo: 0, hi: 255 };
  const cutCount = counted * cutoff;
  let lo = 0,
    hi = 255,
    cum = 0;
  for (let v = 0; v < 256; v++) {
    cum += hist[v];
    if (cum > cutCount) {
      lo = v;
      break;
    }
  }
  cum = 0;
  for (let v = 255; v >= 0; v--) {
    cum += hist[v];
    if (cum > cutCount) {
      hi = v;
      break;
    }
  }
  if (hi <= lo) {
    lo = 0;
    hi = 255;
  }
  return { lo, hi };
}

function drawHalftonePortrait(
  canvas,
  src,
  {
    cell = 1.7,
    minDot = 0,
    maxDot = 1.0,
    contrast = 1.75,
    dotColor = "#0a0a0a",
    invert = false,
    zoom = 1,
    focusY = 0.5,
    shadowLift = 1,
  } = {},
) {
  const img = new Image();
  img.onload = () => {
    const parent = canvas.parentElement;
    const displayW = canvas.clientWidth || parent.clientWidth || 288;
    const displayH = canvas.clientHeight || parent.clientHeight || 384;
    // at display size the cell is ~2px: all anti-aliased edge, no solid core.
    // render at 4x and downsample instead.
    const dpr = Math.max(4, Math.min(window.devicePixelRatio || 1, 2) * 2);
    const W = Math.round(displayW * dpr);
    const H = Math.round(displayH * dpr);
    canvas.width = W;
    canvas.height = H;

    const off = document.createElement("canvas");
    off.width = W;
    off.height = H;
    const octx = off.getContext("2d", { willReadFrequently: true });
    octx.filter = "blur(0.7px)";
    const scale =
      Math.max(W / img.naturalWidth, H / img.naturalHeight) * zoom;
    const dw = img.naturalWidth * scale;
    const dh = img.naturalHeight * scale;
    octx.drawImage(img, (W - dw) / 2, (H - dh) * focusY, dw, dh);
    octx.filter = "none";

    const ctx = canvas.getContext("2d");
    let data;
    try {
      data = octx.getImageData(0, 0, W, H).data;
    } catch (err) {
      ctx.clearRect(0, 0, W, H);
      ctx.filter = "grayscale(1) contrast(1.1)";
      ctx.drawImage(off, 0, 0);
      ctx.filter = "none";
      return;
    }

    const { lo, hi } = computeAutoLevels(data, 0.01);
    const range = Math.max(hi - lo, 1);

    ctx.clearRect(0, 0, W, H);
    ctx.fillStyle = dotColor;

    // must be whole px — a fractional index into the pixel array returns undefined
    const cellPx = Math.max(2, Math.round(cell * dpr));
    const minSize = cellPx * minDot;
    const maxSize = cellPx * maxDot;

    for (let y = 0; y < H; y += cellPx) {
      for (let x = 0; x < W; x += cellPx) {
        let total = 0,
          count = 0;
        for (let dy = 0; dy < cellPx && y + dy < H; dy++) {
          for (let dx = 0; dx < cellPx && x + dx < W; dx++) {
            const idx = ((y + dy) * W + (x + dx)) * 4;
            total +=
              0.299 * data[idx] + 0.587 * data[idx + 1] + 0.114 * data[idx + 2];
            count++;
          }
        }
        const avgLuma = total / count;
        const stretched = Math.max(
          0,
          Math.min(255, ((avgLuma - lo) / range) * 255),
        );
        let tone = invert ? stretched / 255 : 1 - stretched / 255;
        if (contrast !== 1 && tone > 0 && tone < 1) {
          const a = Math.pow(tone, contrast);
          const b = Math.pow(1 - tone, contrast);
          tone = a / (a + b);
        }
        // ink-dark gets no density for free, so lift the midtones
        if (shadowLift !== 1) tone = Math.pow(tone, shadowLift);
        const size = minSize + (maxSize - minSize) * tone;
        if (size <= 0.02) continue;
        const cx = x + cellPx / 2;
        const cy = y + cellPx / 2;
        ctx.beginPath();
        ctx.arc(cx, cy, size / 2, 0, Math.PI * 2);
        ctx.fill();
      }
    }
  };
  img.onerror = () => {
    console.warn("Halftone image failed to load:", src);
  };
  img.src = src;
}

function renderAllHalftones() {
  const isDark = document.documentElement.classList.contains("dark");
  const dotColor = isDark ? "#f4f4f5" : "#0a0a0a";
  const invert = isDark;

  document.querySelectorAll(".halftone-canvas").forEach((canvas) => {
    const key = canvas.classList.contains("photo-1")
      ? "photo-1"
      : canvas.classList.contains("photo-2")
        ? "photo-2"
        : null;

    // full-res file over http, embedded copy only for file://
    const embedded = key && EMBEDDED_HALFTONE_SOURCES[key];
    const src =
      location.protocol === "file:"
        ? embedded || canvas.dataset.src
        : canvas.dataset.src || embedded;
    drawHalftonePortrait(canvas, src, {
      dotColor,
      invert,
      // crop to a bust so the subject fills the frame
      focusY: 0.15,
      zoom: 1.25,
      minDot: 0,
      // tuned by eye: 2.4/2.0 blows this backlit source out to flat white
      contrast: isDark ? 2.0 : 1.8,
      shadowLift: isDark ? 1.1 : 1.0,
    });
  });
}

let halftoneResizeTimer;
let lastHalftoneWidth = window.innerWidth;
window.addEventListener("resize", () => {
  if (window.innerWidth === lastHalftoneWidth) return;
  lastHalftoneWidth = window.innerWidth;
  clearTimeout(halftoneResizeTimer);
  halftoneResizeTimer = setTimeout(renderAllHalftones, 180);
});
