const root = document.documentElement;
const themeBtns = document.querySelectorAll("[data-theme-btn]");
const systemQuery = window.matchMedia("(prefers-color-scheme: dark)");

function applyTheme(mode) {
  const isDark = mode === "dark" || (mode === "system" && systemQuery.matches);
  root.classList.toggle("dark", isDark);
  themeBtns.forEach((btn) =>
    btn.classList.toggle("active", btn.getAttribute("data-theme-btn") === mode),
  );
  localStorage.setItem("theme-mode", mode);
  renderAllHalftones();
}

function revealThemeChange(x, y, willBeDark, onComplete) {
  const prefersReducedMotion = window.matchMedia(
    "(prefers-reduced-motion: reduce)",
  ).matches;

  if (
    prefersReducedMotion ||
    !document.startViewTransition ||
    document.visibilityState !== "visible"
  ) {
    onComplete();
    return;
  }

  const maxRadius = Math.hypot(
    Math.max(x, window.innerWidth - x),
    Math.max(y, window.innerHeight - y),
  );

  const transition = document.startViewTransition(() => {
    onComplete();
  });

  transition.ready
    .then(() => {
      document.documentElement.animate(
        {
          clipPath: [
            `circle(0px at ${x}px ${y}px)`,
            `circle(${maxRadius}px at ${x}px ${y}px)`,
          ],
        },
        {
          duration: 650,
          easing: "cubic-bezier(0.65, 0, 0.35, 1)",
          pseudoElement: "::view-transition-new(root)",
        },
      );
    })
    .catch(() => {
    });

  transition.finished.catch(() => {});
}

const savedMode = localStorage.getItem("theme-mode") || "system";
applyTheme(savedMode);

themeBtns.forEach((btn) => {
  btn.addEventListener("click", (e) => {
    const mode = btn.getAttribute("data-theme-btn");
    const willBeDark =
      mode === "dark" || (mode === "system" && systemQuery.matches);
    const isCurrentlyDark = root.classList.contains("dark");

    if (willBeDark !== isCurrentlyDark) {
      const rect = btn.getBoundingClientRect();
      const x = rect.left + rect.width / 2;
      const y = rect.top + rect.height / 2;
      revealThemeChange(x, y, willBeDark, () => applyTheme(mode));
    } else {
      applyTheme(mode);
    }
  });
});

systemQuery.addEventListener("change", () => {
  if ((localStorage.getItem("theme-mode") || "system") === "system")
    applyTheme("system");
});
