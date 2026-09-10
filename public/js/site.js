const shortcuts = new Map();
const MAC = /Mac|iPhone|iPad/.test(navigator.platform || navigator.userAgent);
const MOD = MAC ? "⌘" : "Alt";

function register(key, handler) {
  shortcuts.set(key.toLowerCase(), handler);
}

function typingInto(target) {
  return (
    target instanceof HTMLElement &&
    (target.isContentEditable ||
      ["INPUT", "TEXTAREA", "SELECT"].includes(target.tagName))
  );
}

document.addEventListener("keydown", (e) => {
  const handler = shortcuts.get(e.key.toLowerCase());
  if (!handler) return;
  if (!(e.metaKey || e.altKey) || e.ctrlKey || e.shiftKey) return;
  if (typingInto(e.target) && !overlays.current) return;
  e.preventDefault();
  handler();
});

document.querySelectorAll("[data-shortcut]").forEach((el) => {
  const slot = el.querySelector("[data-shortcut-label]");
  if (!slot) return;
  slot.innerHTML = "";
  const mod = document.createElement("kbd");
  mod.textContent = MOD;
  const plus = document.createElement("span");
  plus.textContent = "+";
  plus.setAttribute("aria-hidden", "true");
  const key = document.createElement("kbd");
  key.textContent = el.dataset.shortcut.toUpperCase();
  slot.append(mod, plus, key);
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
    // an overlay carrying its own tabindex takes focus itself; the rest hand it
    // to their first control
    const focusable =
      node.getAttribute("tabindex") === "-1"
        ? node
        : node.querySelector(
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
  // the typing test binds esc and tab to its own confirm/restart flow
  if (node.dataset.overlayKeys === "self") return;
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
  if (!(e.target instanceof Element) || e.target.closest(".sidebar")) return;
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

function deckCard(target) {
  return target instanceof Element
    ? target.closest("[data-deck] .deck-card")
    : null;
}

document.addEventListener("click", (e) => {
  const card = deckCard(e.target);
  if (card) activateCard(card);
});

document.addEventListener("keydown", (e) => {
  if (e.key !== "Enter" && e.key !== " ") return;
  const card = deckCard(e.target);
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
const typingNode = document.getElementById("typing");

if (typingNode) {
  const wordsEl = document.getElementById("ttWords");
  const kbEl = document.getElementById("ttKeyboard");
  const field = document.getElementById("ttField");
  const verdictEl = document.getElementById("ttVerdict");
  const liveWpm = document.getElementById("ttWpm");
  const liveAcc = document.getElementById("ttAcc");
  const liveTime = document.getElementById("ttTime");
  const resWpm = document.getElementById("ttResWpm");
  const resAcc = document.getElementById("ttResAcc");
  const resRaw = document.getElementById("ttResRaw");
  const resTime = document.getElementById("ttResTime");

  const WORDS = `the and for that with have this from they what were when your said
  each their which will other about many then them these some would into time look
  more write like him two has number way could people than first water been call who
  its now find long down day did get come made may part over new sound take only
  little work know place year live back give most very after thing our just name good
  man think say great where help through much before line right too mean old any same
  tell boy follow came want show also around form three small set put end does another
  well large must big even such because turn here why ask went men read need land
  different home us move try kind hand picture again change off play spell air away
  animal house point page letter mother answer found study still learn should world
  build code system design data model screen keyboard editor project search value
  simple result active border`
    .split(/\s+/)
    .filter(Boolean);

  const KB_ROWS = ["qwertyuiop", "asdfghjkl", "zxcvbnm"];
  const COUNT = 26;
  const MAX_EXTRA = 8;
  const BEST_KEY = "tt-best-wpm";

  let words = [];
  let cells = [];
  let wi = 0;
  let ci = 0;
  let started = false;
  let finished = false;
  let startTime = 0;
  let frame = null;
  let raw = 0;
  let correct = 0;
  let showWpm = 0;
  let showAcc = 100;
  let showTime = 0;
  let lastWrite = 0;
  let confirming = false;

  const caret = document.createElement("span");
  caret.className = "tt-caret";

  const reduced = matchMedia("(prefers-reduced-motion: reduce)");

  function best() {
    const stored = Number(localStorage.getItem(BEST_KEY));
    return Number.isFinite(stored) && stored > 0 ? stored : 0;
  }

  function setConfirm(on) {
    confirming = on;
    typingNode.classList.toggle("is-confirming", on);
  }

  function buildKeyboard() {
    kbEl.textContent = "";
    let i = 0;
    const row = (keys, extra) => {
      const r = document.createElement("div");
      r.className = "tt-krow";
      keys.forEach((ch) => {
        const k = document.createElement("span");
        k.className = extra ? `tt-key ${extra}` : "tt-key";
        k.dataset.key = ch;
        k.textContent = extra ? "space" : ch;
        k.style.animationDelay = `${i * 7}ms`;
        r.appendChild(k);
        i += 1;
      });
      kbEl.appendChild(r);
    };
    KB_ROWS.forEach((keys) => row([...keys]));
    row([" "], "space");
  }

  function keyFor(ch) {
    return kbEl.querySelector(`.tt-key[data-key="${ch === " " ? " " : ch}"]`);
  }

  function flash(ch) {
    const k = keyFor(ch);
    if (!k) return;
    k.classList.add("is-down");
    setTimeout(() => k.classList.remove("is-down"), 110);
  }

  function markNext() {
    kbEl.querySelectorAll(".tt-key.is-next").forEach((k) =>
      k.classList.remove("is-next"),
    );
    if (finished) return;
    const cell = cells[wi];
    const ch =
      ci < cell.word.length
        ? cell.word[ci]
        : wi < words.length - 1
          ? " "
          : null;
    if (ch) keyFor(ch)?.classList.add("is-next");
  }

  function buildText() {
    wordsEl.textContent = "";
    cells = words.map((word) => {
      const el = document.createElement("span");
      el.className = "tt-word";
      const chars = [...word].map((ch) => {
        const c = document.createElement("span");
        c.className = "tt-char";
        c.textContent = ch;
        el.appendChild(c);
        return c;
      });
      wordsEl.appendChild(el);
      return { el, chars, word };
    });
    wordsEl.appendChild(caret);
  }

  function moveCaret() {
    const cell = cells[wi];
    const at = Math.min(ci, cell.chars.length - 1);
    const el = cell.chars[at];
    if (!el) return;
    const past = ci >= cell.chars.length;
    caret.style.left = `${el.offsetLeft + (past ? el.offsetWidth : 0)}px`;
    caret.style.top = `${el.offsetTop}px`;
  }

  function loop(now) {
    const elapsed = started ? (Date.now() - startTime) / 1000 : 0;
    const targetWpm =
      started && elapsed > 0.5 ? correct / 5 / (elapsed / 60) : 0;
    const targetAcc = raw ? (correct / raw) * 100 : 100;

    showWpm += (targetWpm - showWpm) * 0.16;
    showAcc += (targetAcc - showAcc) * 0.16;
    showTime += (elapsed - showTime) * 0.4;
    if (Math.abs(targetWpm - showWpm) < 0.5) showWpm = targetWpm;
    if (Math.abs(targetAcc - showAcc) < 0.5) showAcc = targetAcc;

    if (now - lastWrite >= 240) {
      lastWrite = now;
      liveWpm.textContent = String(Math.round(showWpm));
      liveAcc.textContent = String(Math.round(showAcc));
      liveTime.textContent = String(Math.floor(showTime + 1e-4));
    }
    if (overlays.current === typingNode && !finished) {
      frame = requestAnimationFrame(loop);
    }
  }

  function start() {
    started = true;
    startTime = Date.now();
    cancelAnimationFrame(frame);
    frame = requestAnimationFrame(loop);
  }

  function countUp(el, value, ms) {
    if (reduced.matches) {
      el.textContent = String(value);
      return;
    }
    // anchored to the first frame's own timestamp: rAF reports the frame start,
    // which can precede performance.now() and drive progress negative
    let from = null;
    const step = (now) => {
      if (from === null) from = now;
      const p = Math.min(1, Math.max(0, (now - from) / ms));
      el.textContent = String(Math.round(value * (1 - (1 - p) ** 3)));
      if (p < 1) requestAnimationFrame(step);
      else el.textContent = String(value);
    };
    requestAnimationFrame(step);
  }

  function verdict(wpm) {
    const previous = best();
    const beat = wpm > previous;
    if (beat) localStorage.setItem(BEST_KEY, String(wpm));
    const mark = beat
      ? '<svg class="tt-vicon" viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M5 12.5l4.5 4.5L19 7" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/></svg>'
      : '<svg class="tt-vicon" viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M7 7l10 10M17 7L7 17" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"/></svg>';
    const text = beat
      ? previous
        ? `new personal best · beat ${previous} wpm`
        : "new personal best"
      : `personal best · ${previous} wpm`;
    verdictEl.className = `tt-verdict mono${beat ? " is-best" : ""}`;
    verdictEl.innerHTML = `${mark}<span>${text}</span>`;
  }

  function finish() {
    if (finished) return;
    finished = true;
    cancelAnimationFrame(frame);
    const elapsed = Math.max(0.001, (Date.now() - startTime) / 1000);
    const wpm = Math.round(correct / 5 / (elapsed / 60));
    resAcc.textContent = String(raw ? Math.round((correct / raw) * 100) : 100);
    resRaw.textContent = String(Math.round(raw / 5 / (elapsed / 60)));
    resTime.textContent = elapsed.toFixed(1);
    verdict(wpm);
    typingNode.classList.add("show-results");
    countUp(resWpm, wpm, 750);
  }

  function afterInput() {
    moveCaret();
    markNext();
    if (wi === words.length - 1 && ci >= cells[wi].word.length) finish();
  }

  function typeChar(ch) {
    if (finished) return;
    if (!started) start();
    const cell = cells[wi];
    if (ci < cell.word.length) {
      const hit = ch === cell.word[ci];
      cell.chars[ci].classList.add(hit ? "is-hit" : "is-miss");
      raw += 1;
      if (hit) correct += 1;
      ci += 1;
    } else if (cell.chars.length - cell.word.length < MAX_EXTRA) {
      const extra = document.createElement("span");
      extra.className = "tt-char is-extra";
      extra.textContent = ch;
      cell.el.appendChild(extra);
      cell.chars.push(extra);
      raw += 1;
      ci += 1;
    }
    afterInput();
  }

  function typeSpace() {
    if (finished || !started || wi >= words.length - 1) return;
    wi += 1;
    ci = 0;
    afterInput();
  }

  function backspace() {
    if (finished) return;
    if (ci > 0) {
      ci -= 1;
      const cell = cells[wi];
      if (ci >= cell.word.length) cell.chars.pop()?.remove();
      else cell.chars[ci].classList.remove("is-hit", "is-miss");
    } else if (wi > 0) {
      wi -= 1;
      ci = cells[wi].chars.length;
    }
    moveCaret();
    markNext();
  }

  function reset() {
    cancelAnimationFrame(frame);
    started = false;
    finished = false;
    startTime = 0;
    wi = 0;
    ci = 0;
    raw = 0;
    correct = 0;
    showWpm = 0;
    showAcc = 100;
    showTime = 0;
    lastWrite = 0;
    typingNode.classList.remove("show-results");
    setConfirm(false);
    liveWpm.textContent = "0";
    liveAcc.textContent = "100";
    liveTime.textContent = "0";
    words = Array.from(
      { length: COUNT },
      () => WORDS[Math.floor(Math.random() * WORDS.length)],
    );
    buildText();
    requestAnimationFrame(() => {
      moveCaret();
      markNext();
    });
  }

  function open() {
    reset();
    overlays.open(typingNode);
    if (matchMedia("(pointer: coarse)").matches) {
      field.focus({ preventScroll: true });
    }
  }

  buildKeyboard();

  document.addEventListener("keydown", (e) => {
    if (overlays.current !== typingNode) return;
    if (e.key === "Escape") {
      e.preventDefault();
      if (confirming) setConfirm(false);
      else overlays.close();
      return;
    }
    if (e.metaKey || e.ctrlKey || e.altKey) return;
    if (e.key === "Tab") {
      e.preventDefault();
      if (started && !finished) setConfirm(true);
      else reset();
      return;
    }
    if (e.key === "Enter") {
      if (confirming || finished) {
        e.preventDefault();
        reset();
      }
      return;
    }
    if (confirming) return;
    if (e.key === "Backspace") {
      e.preventDefault();
      backspace();
      return;
    }
    if (e.key === " ") {
      e.preventDefault();
      flash(" ");
      if (finished) reset();
      else typeSpace();
      return;
    }
    if (e.key.length !== 1) return;
    const ch = e.key.toLowerCase();
    if (!/[a-z]/.test(ch)) return;
    e.preventDefault();
    flash(ch);
    typeChar(ch);
  });

  // touch keyboards fire input events without usable keydown values
  field.addEventListener("input", () => {
    const value = field.value;
    field.value = "";
    [...value].forEach((ch) => {
      const lower = ch.toLowerCase();
      if (ch === " ") {
        flash(" ");
        typeSpace();
      } else if (/[a-z]/.test(lower)) {
        flash(lower);
        typeChar(lower);
      }
    });
  });

  field.addEventListener("keydown", (e) => {
    if (e.key !== "Backspace") return;
    e.preventDefault();
    backspace();
  });

  typingNode
    .querySelector("[data-tt-restart]")
    .addEventListener("click", reset);

  register("j", () => {
    if (overlays.current === typingNode) overlays.close();
    else open();
  });

  document.querySelectorAll("[data-typing-open]").forEach((el) =>
    el.addEventListener("click", (e) => {
      e.preventDefault();
      open();
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
