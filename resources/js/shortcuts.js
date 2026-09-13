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
