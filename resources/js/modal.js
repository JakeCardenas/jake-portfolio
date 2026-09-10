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
