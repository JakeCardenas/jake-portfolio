document.addEventListener(
  "DOMContentLoaded",
  () => {
    if (
      !window.matchMedia("(prefers-reduced-motion: no-preference)").matches ||
      !("IntersectionObserver" in window)
    )
      return;
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (!entry.isIntersecting) return;
          entry.target.classList.add("page-enter-motion");
          entry.target.addEventListener(
            "animationend",
            () => entry.target.classList.remove("page-enter-motion"),
            { once: true },
          );
          observer.unobserve(entry.target);
        });
      },
      { threshold: 0.04 },
    );
    document
      .querySelectorAll("main section, main .reveal, [data-page-enter-item]")
      .forEach((item) => {
        if (
          item.getBoundingClientRect().top >= window.innerHeight &&
          !item.closest('[role="dialog"], [aria-hidden="true"]')
        )
          observer.observe(item);
      });
  },
  { once: true },
);
