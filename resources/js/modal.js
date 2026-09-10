/**
 * Modal system with Apple-style spring animations
 * Spatial consistency: modals scale from their trigger point
 */

import { Spring } from './spring.js';

const modalSprings = new WeakMap();

document.querySelectorAll("[data-modal-open]").forEach((trigger) =>
  trigger.addEventListener("click", (e) => {
    const node = document.getElementById(trigger.dataset.modalOpen);
    if (!node) return;
    e.preventDefault();
    
    // Store trigger position for spatial anchoring
    const triggerRect = trigger.getBoundingClientRect();
    const originX = triggerRect.left + triggerRect.width / 2;
    const originY = triggerRect.top + triggerRect.height / 2;
    
    overlays.open(node, { originX, originY });
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
    
    // Spring-based feedback animation
    feedback.textContent = ok ? "Copied" : "Press ⌘C";
    button.classList.add("is-copied");
    
    // Add a subtle spring bounce on the button
    const scaleSpring = new Spring({
      value: 1,
      target: 1.05,
      damping: 0.7,
      response: 0.15,
      onUpdate: (value) => {
        button.style.transform = `scale(${value})`;
      },
      onComplete: () => {
        // Spring back to normal
        const returnSpring = new Spring({
          value: 1.05,
          target: 1,
          damping: 0.8,
          response: 0.2,
          onUpdate: (value) => {
            button.style.transform = `scale(${value})`;
          },
          onComplete: () => {
            button.style.transform = '';
          }
        });
        returnSpring.start();
      }
    });
    scaleSpring.start();
    
    clearTimeout(timer);
    timer = setTimeout(() => {
      feedback.textContent = original;
      button.classList.remove("is-copied");
    }, 1600);
  });
});
