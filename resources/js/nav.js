const menuBtn = document.getElementById("menuBtn");
const siteNav = document.getElementById("siteNav");

function setMenuOpen(open) {
  siteNav.classList.toggle("open", open);
  menuBtn.setAttribute("aria-expanded", String(open));
  document.body.classList.toggle("menu-open", open);
}
menuBtn.addEventListener("click", () => {
  setMenuOpen(!siteNav.classList.contains("open"));
});

document.addEventListener("keydown", (e) => {
  if (e.key === "Escape" && siteNav.classList.contains("open")) {
    setMenuOpen(false);
    menuBtn.focus();
  }
});

document.addEventListener("click", (e) => {
  if (!siteNav.classList.contains("open")) return;
  if (e.target.closest(".sidebar")) return;
  setMenuOpen(false);
});

// closing here matters: the rail locks scroll, and the button is gone at this width
const desktopQuery = window.matchMedia("(min-width: 1024px)");
desktopQuery.addEventListener("change", (e) => {
  if (e.matches) setMenuOpen(false);
});

const sections = document.querySelectorAll("section[id]");
const navLinks = document.querySelectorAll("[data-nav]");
const observer = new IntersectionObserver(
  (entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        navLinks.forEach((link) => {
          link.classList.toggle(
            "active",
            link.getAttribute("href") === "#" + entry.target.id,
          );
        });
      }
    });
  },
  { rootMargin: "-40% 0px -50% 0px", threshold: 0 },
);
sections.forEach((s) => observer.observe(s));

navLinks.forEach((link) =>
  link.addEventListener("click", () => setMenuOpen(false)),
);
