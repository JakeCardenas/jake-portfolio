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
    cell = 2.0,
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
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
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
        ctx.fillRect(cx - size / 2, cy - size / 2, size, size);
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
      focusY: 0.18,
      // bright photo, so light mode needs a softer curve and a lift
      contrast: isDark ? 1.75 : 1.35,
      shadowLift: isDark ? 1 : 0.6,
    });
  });
}

const root = document.documentElement;
const themeBtns = document.querySelectorAll("[data-theme-btn]");
const systemQuery = window.matchMedia("(prefers-color-scheme: dark)");

function applyTheme(mode) {
  const isDark = mode === "dark" || (mode === "system" && systemQuery.matches);
  root.classList.toggle("dark", isDark);
  themeBtns.forEach((btn) =>
    btn.classList.toggle("active", btn.getAttribute("data-theme-btn") === mode),
  );
  localStorage.setItem("theme-mode", mode);
  renderAllHalftones();
}

function revealThemeChange(x, y, willBeDark, onComplete) {
  const prefersReducedMotion = window.matchMedia(
    "(prefers-reduced-motion: reduce)",
  ).matches;

  if (
    prefersReducedMotion ||
    !document.startViewTransition ||
    document.visibilityState !== "visible"
  ) {
    onComplete();
    return;
  }

  const maxRadius = Math.hypot(
    Math.max(x, window.innerWidth - x),
    Math.max(y, window.innerHeight - y),
  );

  const transition = document.startViewTransition(() => {
    onComplete();
  });

  transition.ready
    .then(() => {
      document.documentElement.animate(
        {
          clipPath: [
            `circle(0px at ${x}px ${y}px)`,
            `circle(${maxRadius}px at ${x}px ${y}px)`,
          ],
        },
        {
          duration: 650,
          easing: "cubic-bezier(0.65, 0, 0.35, 1)",
          pseudoElement: "::view-transition-new(root)",
        },
      );
    })
    .catch(() => {
    });

  transition.finished.catch(() => {});
}

const savedMode = localStorage.getItem("theme-mode") || "system";
applyTheme(savedMode);

themeBtns.forEach((btn) => {
  btn.addEventListener("click", (e) => {
    const mode = btn.getAttribute("data-theme-btn");
    const willBeDark =
      mode === "dark" || (mode === "system" && systemQuery.matches);
    const isCurrentlyDark = root.classList.contains("dark");

    if (willBeDark !== isCurrentlyDark) {
      const rect = btn.getBoundingClientRect();
      const x = rect.left + rect.width / 2;
      const y = rect.top + rect.height / 2;
      revealThemeChange(x, y, willBeDark, () => applyTheme(mode));
    } else {
      applyTheme(mode);
    }
  });
});

systemQuery.addEventListener("change", () => {
  if ((localStorage.getItem("theme-mode") || "system") === "system")
    applyTheme("system");
});

const menuBtn = document.getElementById("menuBtn");
const siteNav = document.getElementById("siteNav");

function setMenuOpen(open) {
  siteNav.classList.toggle("open", open);
  menuBtn.setAttribute("aria-expanded", String(open));
  document.body.classList.toggle("menu-open", open);
}
menuBtn.addEventListener("click", () => {
  setMenuOpen(!siteNav.classList.contains("open"));
});

document.addEventListener("keydown", (e) => {
  if (e.key === "Escape" && siteNav.classList.contains("open")) {
    setMenuOpen(false);
    menuBtn.focus();
  }
});

// tapping anywhere outside the rail closes it
document.addEventListener("click", (e) => {
  if (!siteNav.classList.contains("open")) return;
  if (e.target.closest(".sidebar")) return;
  setMenuOpen(false);
});

// leaving the mobile range with the rail open would strand scroll locked
const desktopQuery = window.matchMedia("(min-width: 1024px)");
desktopQuery.addEventListener("change", (e) => {
  if (e.matches) setMenuOpen(false);
});

const sections = document.querySelectorAll("section[id]");
const navLinks = document.querySelectorAll("[data-nav]");
const observer = new IntersectionObserver(
  (entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        navLinks.forEach((link) => {
          link.classList.toggle(
            "active",
            link.getAttribute("href") === "#" + entry.target.id,
          );
        });
      }
    });
  },
  { rootMargin: "-40% 0px -50% 0px", threshold: 0 },
);
sections.forEach((s) => observer.observe(s));

const revealObserver = new IntersectionObserver(
  (entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add("in");
        revealObserver.unobserve(entry.target);
      }
    });
  },
  { threshold: 0.1 },
);
document
  .querySelectorAll(".reveal")
  .forEach((el) => revealObserver.observe(el));

navLinks.forEach((link) =>
  link.addEventListener("click", () => setMenuOpen(false)),
);

const photoSwap = document.querySelector(".photo-swap");
if (photoSwap) {
  const togglePhoto = () => photoSwap.classList.toggle("is-active");
  photoSwap.addEventListener("click", togglePhoto);
  photoSwap.addEventListener("keydown", (e) => {
    if (e.key === "Enter" || e.key === " ") {
      e.preventDefault();
      togglePhoto();
    }
  });
}


document.querySelectorAll("[data-carousel]").forEach((carousel) => {
  const slides = carousel.querySelectorAll(".carousel-slide");
  const dots = carousel.querySelectorAll(".carousel-dot");
  let index = 0;

  function show(i) {
    index = (i + slides.length) % slides.length;
    slides.forEach((s, n) => s.classList.toggle("active", n === index));
    dots.forEach((d, n) => d.classList.toggle("active", n === index));
  }

  dots.forEach((d, n) => d.addEventListener("click", () => show(n)));

  slides.forEach((s, n) =>
    s.addEventListener("click", () => {
      if (n !== index) show(n);
    }),
  );
});

// canvas is a fixed bitmap, so it needs a redraw when the box changes
let halftoneResizeTimer;
let lastHalftoneWidth = window.innerWidth;
window.addEventListener("resize", () => {
  if (window.innerWidth === lastHalftoneWidth) return;
  lastHalftoneWidth = window.innerWidth;
  clearTimeout(halftoneResizeTimer);
  halftoneResizeTimer = setTimeout(renderAllHalftones, 180);
});

// gear shots fall back to the line icon until the photo is dropped in
document.querySelectorAll(".gear-shot img").forEach((img) => {
  const frame = img.closest(".gear-shot");
  const miss = () => frame.classList.add("is-empty");
  img.addEventListener("error", miss);
  if (img.complete && !img.naturalWidth) miss();
});

const ghGraph = document.getElementById("ghGraph");
if (ghGraph) {
  const caption = document.getElementById("ghCaption");
  const tip = document.getElementById("ghTip");
  const USER = "JakeCardenas";
  const API = `https://github-contributions-api.jogruber.de/v4/${USER}?y=last`;
  const CACHE_KEY = "gh-contrib";
  const CACHE_MAX_AGE = 6 * 60 * 60 * 1000;

  const fmt = (iso) =>
    new Date(iso + "T00:00:00").toLocaleDateString("en-GB", {
      day: "numeric",
      month: "short",
      year: "numeric",
    });

  function render(data) {
    const days = data.contributions || [];
    if (!days.length) return fail();

    // pad to a whole week so every column has seven cells
    const lead = new Date(days[0].date + "T00:00:00").getDay();
    const cells = Array.from({ length: lead }, () => null).concat(days);

    const weeks = [];
    for (let i = 0; i < cells.length; i += 7) weeks.push(cells.slice(i, i + 7));

    ghGraph.innerHTML = weeks
      .map(
        (week) =>
          `<div class="gh-week">` +
          week
            .map((d) =>
              d === null
                ? `<span class="gh-cell is-pad"></span>`
                : `<span class="gh-cell" data-level="${d.level}" data-date="${d.date}" data-count="${d.count}"></span>`,
            )
            .join("") +
          `</div>`,
      )
      .join("");

    // stagger the columns so the grid draws itself in
    ghGraph.querySelectorAll(".gh-week").forEach((w, i) => {
      w.style.animationDelay = Math.min(i * 12, 620) + "ms";
    });

    const total = (data.total && data.total.lastYear) || 0;
    caption.textContent = `${total.toLocaleString()} CONTRIBUTION${total === 1 ? "" : "S"} IN THE LAST YEAR`;
    const link = ghGraph.closest(".gh-graph-link");
    if (link) {
      link.setAttribute(
        "aria-label",
        `View JakeCardenas on GitHub — ${total} contributions in the last year`,
      );
    }
  }

  function fail() {
    ghGraph.classList.add("is-unavailable");
    caption.textContent = "CONTRIBUTION ACTIVITY UNAVAILABLE — VIEW ON GITHUB";
  }

  // hover readout, positioned against the panel
  const hideTip = () => {
    tip.hidden = true;
  };

  ghGraph.addEventListener("mouseover", (e) => {
    const cell = e.target.closest(".gh-cell[data-date]");
    if (!cell) return hideTip();
    const n = Number(cell.dataset.count);
    tip.textContent = `${n} contribution${n === 1 ? "" : "s"} · ${fmt(cell.dataset.date)}`;
    tip.hidden = false;

    const g = ghGraph.getBoundingClientRect();
    const c = cell.getBoundingClientRect();
    const half = tip.offsetWidth / 2;
    // clamp to the panel or an edge cell widens the whole page
    const x = c.left - g.left + c.width / 2;
    tip.style.left = Math.min(Math.max(x, half), g.width - half) + "px";
    tip.style.top = c.top - g.top - 8 + "px";
  });

  ghGraph.addEventListener("mouseleave", hideTip);
  window.addEventListener("scroll", hideTip, { passive: true });
  window.addEventListener("resize", hideTip);

  (async () => {
    try {
      const cached = JSON.parse(sessionStorage.getItem(CACHE_KEY) || "null");
      if (cached && Date.now() - cached.at < CACHE_MAX_AGE) {
        render(cached.data);
        return;
      }
    } catch (err) {
      /* cache unreadable, just fetch */
    }
    try {
      const res = await fetch(API);
      if (!res.ok) throw new Error(res.status);
      const data = await res.json();
      render(data);
      try {
        sessionStorage.setItem(
          CACHE_KEY,
          JSON.stringify({ at: Date.now(), data }),
        );
      } catch (err) {
        /* storage full or blocked */
      }
    } catch (err) {
      fail();
    }
  })();
}


// ── project deck: clicking a side card brings it to the centre ──
function activateCard(card) {
  if (card.classList.contains("is-center")) return;
  const deck = card.closest("[data-deck]");
  if (!deck) return;
  const center = deck.querySelector(".deck-card.is-center");
  const slot = card.classList.contains("is-left") ? "is-left" : "is-right";
  center.classList.remove("is-center");
  center.classList.add(slot);
  card.classList.remove("is-left", "is-right");
  card.classList.add("is-center");
  window.siteSound?.play("toggle");
}
window.activateCard = activateCard;
