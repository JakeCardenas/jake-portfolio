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
