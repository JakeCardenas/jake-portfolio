const shortcuts = new Map();
const MAC = /Mac|iPhone|iPad/.test(navigator.platform || navigator.userAgent);

function label(key) {
  return MAC ? `⌘${key.toUpperCase()}` : `Alt+${key.toUpperCase()}`;
}

function register(key, handler, description) {
  shortcuts.set(key.toLowerCase(), { handler, description, label: label(key) });
}

function typingInto(target) {
  return (
    target instanceof HTMLElement &&
    (target.isContentEditable ||
      ["INPUT", "TEXTAREA", "SELECT"].includes(target.tagName))
  );
}

document.addEventListener("keydown", (e) => {
  const entry = shortcuts.get(e.key.toLowerCase());
  if (!entry) return;
  if (!(e.metaKey || e.altKey) || e.ctrlKey || e.shiftKey) return;
  if (typingInto(e.target) && !overlays.current) return;
  e.preventDefault();
  entry.handler();
});

document.querySelectorAll("[data-shortcut]").forEach((el) => {
  const key = el.dataset.shortcut;
  const slot = el.querySelector("[data-shortcut-label]");
  if (slot) slot.textContent = label(key);
});

const overlays = {
  current: null,
  lastFocus: null,

  open(node) {
    if (this.current) this.close();
    this.lastFocus = document.activeElement;
    this.current = node;
    node.hidden = false;
    document.body.classList.add("overlay-open");
    requestAnimationFrame(() => node.classList.add("is-open"));
    const focusable = node.querySelector(
      "input, textarea, button, [href], [tabindex]:not([tabindex='-1'])",
    );
    (focusable || node).focus({ preventScroll: true });
  },

  close() {
    const node = this.current;
    if (!node) return;
    this.current = null;
    node.classList.remove("is-open");
    document.body.classList.remove("overlay-open");
    const done = () => {
      node.hidden = true;
    };
    if (matchMedia("(prefers-reduced-motion: reduce)").matches) done();
    else setTimeout(done, 180);
    if (this.lastFocus instanceof HTMLElement) {
      this.lastFocus.focus({ preventScroll: true });
    }
  },
};

document.addEventListener("keydown", (e) => {
  const node = overlays.current;
  if (!node) return;
  if (e.key === "Escape") {
    e.preventDefault();
    overlays.close();
    return;
  }
  if (e.key !== "Tab") return;
  const items = [...node.querySelectorAll(
    "input, textarea, button:not([disabled]), [href], [tabindex]:not([tabindex='-1'])",
  )].filter((el) => el.offsetParent !== null);
  if (!items.length) return;
  const first = items[0];
  const last = items[items.length - 1];
  if (e.shiftKey && document.activeElement === first) {
    e.preventDefault();
    last.focus();
  } else if (!e.shiftKey && document.activeElement === last) {
    e.preventDefault();
    first.focus();
  }
});

document.addEventListener("pointerdown", (e) => {
  const node = overlays.current;
  if (node && e.target instanceof Element && e.target.closest("[data-overlay-panel]") === null) {
    overlays.close();
  }
});
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
    drawHalftonePortrait(canvas, canvas.dataset.src, {
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

document.addEventListener("click", (e) => {
  if (!siteNav.classList.contains("open")) return;
  if (e.target.closest(".sidebar")) return;
  setMenuOpen(false);
});

// closing here matters: the rail locks scroll, and the button is gone at this width
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

navLinks.forEach((link) =>
  link.addEventListener("click", () => setMenuOpen(false)),
);
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

document.addEventListener("click", (e) => {
  const card = e.target.closest("[data-deck] .deck-card");
  if (card) activateCard(card);
});

document.addEventListener("keydown", (e) => {
  if (e.key !== "Enter" && e.key !== " ") return;
  const card = e.target.closest("[data-deck] .deck-card");
  if (!card) return;
  e.preventDefault();
  activateCard(card);
});
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

document.querySelectorAll(".reveal").forEach((el) => revealObserver.observe(el));
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
document.querySelectorAll(".gear-shot img").forEach((img) => {
  const frame = img.closest(".gear-shot");
  const markEmpty = () => frame.classList.add("is-empty");

  img.addEventListener("error", markEmpty);
  if (img.complete && !img.naturalWidth) markEmpty();
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

    // count drives the radius, not the colour — that is what reads as halftone
    const R = [1.1, 2.7, 3.8, 4.8, 5.7]; // r per level, 0 = empty
    const PITCH = 13;
    const OFFSET = 6.5;
    const cols = weeks.length;
    const w = cols * PITCH;
    const h = 7 * PITCH;

    const circles = weeks
      .map((week, x) =>
        week
          .map((d, y) => {
            if (d === null) return "";
            const lvl = Math.max(0, Math.min(4, d.level | 0));
            const cx = OFFSET + x * PITCH;
            const cy = OFFSET + y * PITCH;
            return (
              `<circle cx="${cx}" cy="${cy}" r="${R[lvl]}" fill="currentColor"` +
              ` opacity="${lvl === 0 ? 0.12 : 0.92}"` +
              ` data-date="${d.date}" data-count="${d.count}"></circle>`
            );
          })
          .join(""),
      )
      .join("");

    ghGraph.innerHTML =
      `<svg viewBox="0 0 ${w} ${h}" class="gh-svg" preserveAspectRatio="xMidYMid meet"` +
      ` aria-label="GitHub contribution graph, halftone style">${circles}</svg>`;

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

  const hideTip = () => {
    tip.hidden = true;
  };

  ghGraph.addEventListener("mouseover", (e) => {
    const cell = e.target.closest("[data-date]");
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
const paletteNode = document.getElementById("palette");

if (paletteNode) {
  const input = document.getElementById("paletteInput");
  const list = document.getElementById("paletteList");
  const status = document.getElementById("paletteStatus");
  const empty = document.getElementById("paletteEmpty");

  let index = [];
  let matches = [];
  let active = 0;
  let loaded = null;

  const RECENT_KEY = "palette-recent";
  const LIMIT = 40;

  function recent() {
    try {
      return JSON.parse(localStorage.getItem(RECENT_KEY) || "[]");
    } catch (e) {
      return [];
    }
  }

  function remember(item) {
    const kept = [item.url, ...recent().filter((u) => u !== item.url)].slice(0, 5);
    try {
      localStorage.setItem(RECENT_KEY, JSON.stringify(kept));
    } catch (e) {}
  }

  function load() {
    if (loaded) return loaded;
    loaded = fetch("/search-index.json")
      .then((r) => r.json())
      .then((data) => {
        index = data;
      })
      .catch(() => {
        index = [];
      });
    return loaded;
  }

  function score(item, query) {
    const label = item.label.toLowerCase();
    if (label === query) return 0;
    if (label.startsWith(query)) return 1;
    const word = label.split(/\s+/).some((w) => w.startsWith(query));
    if (word) return 2;
    if (label.includes(query)) return 3;
    if ((item.meta || "").toLowerCase().includes(query)) return 4;
    if ((item.terms || "").toLowerCase().includes(query)) return 5;
    return -1;
  }

  function search(query) {
    query = query.trim().toLowerCase();
    if (!query) {
      const saved = recent();
      const first = saved
        .map((url) => index.find((i) => i.url === url))
        .filter(Boolean);
      const pages = index.filter((i) => i.kind === "Page" && !saved.includes(i.url));
      return [...first, ...pages].slice(0, LIMIT);
    }
    return index
      .map((item) => ({ item, rank: score(item, query) }))
      .filter((r) => r.rank >= 0)
      .sort((a, b) => a.rank - b.rank || a.item.label.length - b.item.label.length)
      .slice(0, LIMIT)
      .map((r) => r.item);
  }

  function highlight(text, query) {
    const safe = text.replace(/[&<>]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;" }[c]));
    if (!query) return safe;
    const at = safe.toLowerCase().indexOf(query.toLowerCase());
    if (at < 0) return safe;
    return (
      safe.slice(0, at) +
      "<mark>" +
      safe.slice(at, at + query.length) +
      "</mark>" +
      safe.slice(at + query.length)
    );
  }

  function paint() {
    const query = input.value.trim();
    list.innerHTML = matches
      .map(
        (item, n) =>
          `<li role="option" id="pal-${n}" aria-selected="${n === active}" class="pal-item${
            n === active ? " is-active" : ""
          }"><a href="${item.url}" tabindex="-1"><span class="pal-kind mono">${
            item.kind
          }</span><span class="pal-label">${highlight(item.label, query)}</span>${
            item.meta ? `<span class="pal-meta">${highlight(item.meta, query)}</span>` : ""
          }</a></li>`,
      )
      .join("");
    empty.hidden = matches.length > 0;
    status.textContent = matches.length
      ? `${matches.length} result${matches.length === 1 ? "" : "s"}`
      : "No results";
    const node = list.children[active];
    if (node) node.scrollIntoView({ block: "nearest" });
    input.setAttribute("aria-activedescendant", node ? node.id : "");
  }

  function refresh() {
    matches = search(input.value);
    active = 0;
    paint();
  }

  function choose(item) {
    if (!item) return;
    remember(item);
    overlays.close();
    if (/^https?:/.test(item.url)) window.open(item.url, "_blank", "noopener");
    else window.location.href = item.url;
  }

  function open() {
    overlays.open(paletteNode);
    input.value = "";
    load().then(refresh);
  }

  register("k", open, "Search");

  document.querySelectorAll("[data-palette-open]").forEach((el) =>
    el.addEventListener("click", (e) => {
      e.preventDefault();
      open();
    }),
  );

  input.addEventListener("input", refresh);

  input.addEventListener("keydown", (e) => {
    if (e.key === "ArrowDown" || e.key === "ArrowUp") {
      e.preventDefault();
      if (!matches.length) return;
      active = (active + (e.key === "ArrowDown" ? 1 : -1) + matches.length) % matches.length;
      paint();
    } else if (e.key === "Enter") {
      e.preventDefault();
      choose(matches[active]);
    } else if (e.key === "Home" || e.key === "End") {
      e.preventDefault();
      active = e.key === "Home" ? 0 : matches.length - 1;
      paint();
    }
  });

  list.addEventListener("click", (e) => {
    const li = e.target instanceof Element && e.target.closest(".pal-item");
    if (!li) return;
    e.preventDefault();
    choose(matches[[...list.children].indexOf(li)]);
  });

  list.addEventListener("pointermove", (e) => {
    const li = e.target instanceof Element && e.target.closest(".pal-item");
    if (!li) return;
    const n = [...list.children].indexOf(li);
    if (n !== active) {
      active = n;
      paint();
    }
  });
}
const typingNode = document.getElementById("typing");

if (typingNode) {
  const stream = document.getElementById("ttStream");
  const caret = document.getElementById("ttCaret");
  const results = document.getElementById("ttResults");
  const field = document.getElementById("ttField");
  const liveWpm = document.getElementById("ttWpm");
  const liveAcc = document.getElementById("ttAcc");
  const liveTime = document.getElementById("ttTime");
  const durationButtons = [...typingNode.querySelectorAll("[data-tt-duration]")];

  const WORDS = `the of and to in is you that it he for was on are as with his they at
  be this have from one had by word but not what all were we when your can said there
  use an each which she do how their if will up other about out many then them these so
  some her would make like him into time has look two more write go see number no way
  could people my than first water been call who oil now find long down day did get come
  made may part over new sound take only little work know place year live me back give
  most very after thing our just name good sentence man think say great where help
  through much before line right too mean old any same tell boy follow came want show
  also around form three small set put end does another well large must big even such
  because turn here why ask went men read need land different home us move try kind hand
  picture again change off play spell air away animal house point page letter mother
  answer found study still learn should world build code system design data model random
  screen keyboard editor project search value simple result active border`
    .split(/\s+/)
    .filter(Boolean);

  let duration = 30;
  let target = [];
  let typed = [];
  let started = null;
  let ticker = null;
  let finished = false;

  function sample(count) {
    const out = [];
    for (let i = 0; i < count; i++) {
      out.push(WORDS[Math.floor(Math.random() * WORDS.length)]);
    }
    return out.join(" ").split("");
  }

  function reset() {
    clearInterval(ticker);
    ticker = null;
    started = null;
    finished = false;
    typed = [];
    target = sample(90);
    results.hidden = true;
    stream.hidden = false;
    liveWpm.textContent = "0";
    liveAcc.textContent = "100";
    liveTime.textContent = String(duration);
    paint();
  }

  function correctCount() {
    return typed.reduce((n, ch, i) => n + (ch === target[i] ? 1 : 0), 0);
  }

  function stats() {
    const elapsed = started ? Math.max((Date.now() - started) / 1000, 1) : duration;
    const correct = correctCount();
    return {
      wpm: Math.round(correct / 5 / (elapsed / 60)),
      raw: Math.round(typed.length / 5 / (elapsed / 60)),
      accuracy: typed.length ? Math.round((correct / typed.length) * 100) : 100,
      errors: typed.length - correct,
      characters: typed.length,
    };
  }

  function paint() {
    const window_ = 240;
    const from = Math.max(0, Math.floor(typed.length / 60) * 60);
    stream.innerHTML = target
      .slice(from, from + window_)
      .map((ch, offset) => {
        const i = from + offset;
        let cls = "tt-char";
        if (i < typed.length) cls += typed[i] === ch ? " is-hit" : " is-miss";
        else if (i === typed.length) cls += " is-next";
        const glyph = ch === " " ? "&nbsp;" : ch;
        return `<span class="${cls}">${glyph}</span>`;
      })
      .join("");
    const next = stream.querySelector(".is-next");
    if (next && caret) {
      caret.style.transform = `translate(${next.offsetLeft}px, ${next.offsetTop}px)`;
    }
  }

  function tick() {
    const left = duration - Math.round((Date.now() - started) / 1000);
    liveTime.textContent = String(Math.max(left, 0));
    const s = stats();
    liveWpm.textContent = String(s.wpm);
    liveAcc.textContent = String(s.accuracy);
    if (left <= 0) finish();
  }

  function finish() {
    clearInterval(ticker);
    ticker = null;
    finished = true;
    const s = stats();
    stream.hidden = true;
    results.hidden = false;
    results.querySelector("[data-tt-result='wpm']").textContent = String(s.wpm);
    results.querySelector("[data-tt-result='accuracy']").textContent = `${s.accuracy}%`;
    results.querySelector("[data-tt-result='raw']").textContent = String(s.raw);
    results.querySelector("[data-tt-result='errors']").textContent = String(s.errors);
    results.querySelector("[data-tt-result='characters']").textContent = String(s.characters);
  }

  function handle(key) {
    if (finished) return;
    if (key === "Backspace") {
      typed.pop();
    } else if (key.length === 1) {
      if (!started) {
        started = Date.now();
        ticker = setInterval(tick, 200);
      }
      typed.push(key);
      if (typed.length >= target.length) finish();
    } else {
      return;
    }
    paint();
    if (started) tick();
  }

  typingNode.addEventListener("keydown", (e) => {
    if (e.metaKey || e.ctrlKey || e.altKey) return;
    if (e.key === "Tab") {
      e.preventDefault();
      reset();
      return;
    }
    if (e.key === "Escape") return;
    if (e.key === "Backspace" || e.key.length === 1) {
      e.preventDefault();
      handle(e.key);
    }
  });

  // mobile keyboards emit input events rather than usable keydown values
  field.addEventListener("input", () => {
    const value = field.value;
    field.value = "";
    [...value].forEach((ch) => handle(ch));
  });

  durationButtons.forEach((button) =>
    button.addEventListener("click", () => {
      duration = Number(button.dataset.ttDuration);
      durationButtons.forEach((b) =>
        b.classList.toggle("is-active", b === button),
      );
      reset();
    }),
  );

  typingNode.querySelectorAll("[data-tt-restart]").forEach((b) =>
    b.addEventListener("click", () => {
      reset();
      field.focus({ preventScroll: true });
    }),
  );

  register("j", () => {
    reset();
    overlays.open(typingNode);
    field.focus({ preventScroll: true });
  }, "Typing test");

  document.querySelectorAll("[data-typing-open]").forEach((el) =>
    el.addEventListener("click", (e) => {
      e.preventDefault();
      reset();
      overlays.open(typingNode);
      field.focus({ preventScroll: true });
    }),
  );
}
document.querySelectorAll("[data-modal-open]").forEach((trigger) =>
  trigger.addEventListener("click", (e) => {
    const node = document.getElementById(trigger.dataset.modalOpen);
    if (!node) return;
    e.preventDefault();
    overlays.open(node);
  }),
);

document.querySelectorAll("[data-modal-close]").forEach((button) =>
  button.addEventListener("click", () => overlays.close()),
);

async function copy(text) {
  try {
    await navigator.clipboard.writeText(text);
    return true;
  } catch (e) {
    const field = document.createElement("textarea");
    field.value = text;
    field.setAttribute("readonly", "");
    field.style.cssText = "position:fixed;opacity:0";
    document.body.appendChild(field);
    field.select();
    const ok = document.execCommand && document.execCommand("copy");
    field.remove();
    return !!ok;
  }
}

document.querySelectorAll("[data-copy]").forEach((button) => {
  const feedback = button.querySelector("[data-copy-feedback]");
  const original = feedback ? feedback.textContent : "";
  let timer;

  button.addEventListener("click", async () => {
    const ok = await copy(button.dataset.copy);
    if (!feedback) return;
    feedback.textContent = ok ? "Copied" : "Press ⌘C";
    button.classList.add("is-copied");
    clearTimeout(timer);
    timer = setTimeout(() => {
      feedback.textContent = original;
      button.classList.remove("is-copied");
    }, 1600);
  });
});
