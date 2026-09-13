const root = document.documentElement;
const themeBtns = document.querySelectorAll("[data-theme-btn]");
const systemQuery = window.matchMedia("(prefers-color-scheme: dark)");
const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
let themeAnimTimer;

function savedMode() {
  try {
    const v = localStorage.getItem("theme-mode");
    return v === "dark" || v === "light" || v === "system" ? v : "system";
  } catch (e) {
    return "system";
  }
}

function isDark(mode) {
  return mode === "dark" || (mode === "system" && systemQuery.matches);
}

function setClass(mode) {
  root.classList.toggle("dark", isDark(mode));
  themeBtns.forEach((btn) =>
    btn.classList.toggle("active", btn.getAttribute("data-theme-btn") === mode),
  );
}

function crossfade(mode) {
  root.classList.add("theme-anim");
  setClass(mode);
  clearTimeout(themeAnimTimer);
  themeAnimTimer = setTimeout(() => root.classList.remove("theme-anim"), 520);
}

function reveal(mode, x, y) {
  const r = Math.hypot(Math.max(x, innerWidth - x), Math.max(y, innerHeight - y));
  const vt = document.startViewTransition(() => setClass(mode));
  vt.ready
    .then(() => {
      root.animate(
        {
          clipPath: [
            `circle(0px at ${x}px ${y}px)`,
            `circle(${r}px at ${x}px ${y}px)`,
          ],
        },
        {
          duration: 540,
          easing: "cubic-bezier(.32,.08,.24,1)",
          pseudoElement: "::view-transition-new(root)",
        },
      );
    })
    .catch(() => {});
}

function setTheme(mode, ev) {
  try {
    localStorage.setItem("theme-mode", mode);
  } catch (e) {}
  if (isDark(mode) === root.classList.contains("dark")) {
    setClass(mode);
    return;
  }
  if (reduceMotion || !document.startViewTransition) {
    crossfade(mode);
    return;
  }
  const x = (ev && ev.clientX) || innerWidth;
  const y = (ev && ev.clientY) || innerHeight;
  reveal(mode, x, y);
}

setClass(savedMode());

themeBtns.forEach((btn) =>
  btn.addEventListener("click", (e) =>
    setTheme(btn.getAttribute("data-theme-btn"), e),
  ),
);

systemQuery.addEventListener("change", () => {
  if (savedMode() === "system") crossfade("system");
});
