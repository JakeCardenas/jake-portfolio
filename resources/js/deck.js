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
