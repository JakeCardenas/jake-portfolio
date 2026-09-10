document.querySelectorAll(".gear-shot img").forEach((img) => {
  const frame = img.closest(".gear-shot");
  const markEmpty = () => frame.classList.add("is-empty");

  img.addEventListener("error", markEmpty);
  if (img.complete && !img.naturalWidth) markEmpty();
});
