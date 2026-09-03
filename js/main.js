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
document
  .querySelectorAll(".reveal")
  .forEach((el) => revealObserver.observe(el));

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

document.querySelectorAll("[data-carousel]").forEach((carousel) => {
  const slides = carousel.querySelectorAll(".carousel-slide");
  const dots = carousel.querySelectorAll(".carousel-dot");
  let index = 0;

  function show(i) {
    index = (i + slides.length) % slides.length;
    slides.forEach((s, n) => s.classList.toggle("active", n === index));
    dots.forEach((d, n) => d.classList.toggle("active", n === index));
  }

  dots.forEach((d, n) => d.addEventListener("click", () => show(n)));

  slides.forEach((s, n) =>
    s.addEventListener("click", () => {
      if (n !== index) show(n);
    }),
  );
});

document.querySelectorAll(".gear-shot img").forEach((img) => {
  const frame = img.closest(".gear-shot");
  const miss = () => frame.classList.add("is-empty");
  img.addEventListener("error", miss);
  if (img.complete && !img.naturalWidth) miss();
});
