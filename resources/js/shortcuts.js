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
  spring: null,

  open(node, options = {}) {
    if (this.current) this.close();
    this.lastFocus = document.activeElement;
    this.current = node;
    node.hidden = false;
    document.body.classList.add("overlay-open");
    
    const panel = node.querySelector("[data-overlay-panel]");
    
    // Check for reduced motion preference
    const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    
    if (prefersReducedMotion) {
      // Simple fade for reduced motion
      requestAnimationFrame(() => node.classList.add("is-open"));
    } else {
      // Apple-style spring animation with spatial origin
      if (panel && options.originX !== undefined && options.originY !== undefined) {
        // Set transform-origin to the trigger point
        const rect = panel.getBoundingClientRect();
        const originXPercent = ((options.originX - rect.left) / rect.width) * 100;
        const originYPercent = ((options.originY - rect.top) / rect.height) * 100;
        panel.style.transformOrigin = `${originXPercent}% ${originYPercent}%`;
      }
      
      // Start from presentation value for interruptibility
      requestAnimationFrame(() => {
        node.classList.add("is-open");
        
        // Apply spring physics to the panel
        if (panel && window.Spring) {
          const scaleSpring = new window.Spring({
            value: 0.92,
            target: 1,
            damping: 0.85,
            response: 0.35,
            onUpdate: (value) => {
              panel.style.setProperty('--spring-scale', value);
            },
            onComplete: () => {
              panel.style.removeProperty('--spring-scale');
            }
          });
          
          const opacitySpring = new window.Spring({
            value: 0,
            target: 1,
            damping: 1.0,
            response: 0.3,
            onUpdate: (value) => {
              panel.style.opacity = value;
            }
          });
          
          this.spring = { scale: scaleSpring, opacity: opacitySpring };
          scaleSpring.start();
          opacitySpring.start();
        }
      });
    }
    
    // Focus management
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
    
    // Stop any active springs
    if (this.spring) {
      this.spring.scale?.stop();
      this.spring.opacity?.stop();
      this.spring = null;
    }
    
    this.current = null;
    node.classList.remove("is-open");
    document.body.classList.remove("overlay-open");
    
    const done = () => {
      node.hidden = true;
      const panel = node.querySelector("[data-overlay-panel]");
      if (panel) {
        panel.style.transformOrigin = '';
        panel.style.opacity = '';
      }
    };
    
    if (matchMedia("(prefers-reduced-motion: reduce)").matches) {
      done();
    } else {
      setTimeout(done, 250);
    }
    
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
