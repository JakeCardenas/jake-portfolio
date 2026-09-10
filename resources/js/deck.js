/**
 * Project deck with spring-based transitions
 * Implements Apple Design principles: momentum, springs, interruptibility
 */

import { Spring } from './spring.js';

// Store active springs per card for interruption
const cardSprings = new WeakMap();

function activateCard(card) {
  if (card.classList.contains("is-center")) return;
  const deck = card.closest("[data-deck]");
  if (!deck) return;
  
  const center = deck.querySelector(".deck-card.is-center");
  const slot = card.classList.contains("is-left") ? "is-left" : "is-right";
  
  // Update classes immediately for CSS to take over initial positioning
  center.classList.remove("is-center");
  center.classList.add(slot);
  card.classList.remove("is-left", "is-right");
  card.classList.add("is-center");
  
  // Apply spring animation for smooth, interruptible motion
  // Using slight bounce (damping 0.85) since this is a momentum-driven interaction
  animateCardWithSpring(card, {
    damping: 0.85,
    response: 0.35
  });
  
  window.siteSound?.play("toggle");
}

function animateCardWithSpring(card, config) {
  // Cancel any existing spring on this card (interruptibility)
  const existingSpring = cardSprings.get(card);
  if (existingSpring) {
    existingSpring.stop();
  }
  
  // Read current transform values from CSS
  const computedStyle = window.getComputedStyle(card);
  const matrix = new DOMMatrix(computedStyle.transform);
  
  // Create springs for each transform property
  const springs = {
    x: new Spring({
      value: matrix.m41,
      target: 0,
      damping: config.damping ?? 0.85,
      response: config.response ?? 0.35,
      onUpdate: () => updateCardTransform(card, springs),
      onComplete: () => {
        cardSprings.delete(card);
        // Clean up inline transform, let CSS take over
        card.style.transform = '';
      }
    }),
    y: new Spring({
      value: matrix.m42,
      target: 0,
      damping: config.damping ?? 0.85,
      response: config.response ?? 0.35
    }),
    scale: new Spring({
      value: matrix.a,
      target: 1,
      damping: config.damping ?? 0.85,
      response: config.response ?? 0.35
    })
  };
  
  cardSprings.set(card, springs);
  
  // Start all springs
  Object.values(springs).forEach(spring => spring.start());
}

function updateCardTransform(card, springs) {
  const x = springs.x.getCurrentValue();
  const y = springs.y.getCurrentValue();
  const scale = springs.scale.getCurrentValue();
  
  // Get rotation from CSS (we don't animate rotation independently)
  const computedStyle = window.getComputedStyle(card);
  const matrix = new DOMMatrix(computedStyle.transform);
  const rotation = Math.atan2(matrix.b, matrix.a) * (180 / Math.PI);
  
  card.style.transform = `translateX(${x}px) translateY(${y}px) scale(${scale}) rotate(${rotation}deg)`;
}

function deckCard(target) {
  return target instanceof Element
    ? target.closest("[data-deck] .deck-card")
    : null;
}

// Respond on pointer-down (Apple principle: kill latency)
document.addEventListener("pointerdown", (e) => {
  const card = deckCard(e.target);
  if (card && !card.classList.contains("is-center")) {
    // Add instant visual feedback
    card.style.transition = 'transform 0.1s ease-out';
    card.style.transform = 'scale(0.98)';
  }
});

document.addEventListener("pointerup", (e) => {
  const card = deckCard(e.target);
  if (card) {
    // Remove instant feedback styling
    card.style.transition = '';
    if (!card.classList.contains("is-center")) {
      card.style.transform = '';
    }
  }
});

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
