const mobileNav = document.getElementById("mobileNav");
const mobileOpenBtn = document.querySelector("[data-mobile-nav-open]");
let mobileNavTimer;

function openMobileNav() {
  clearTimeout(mobileNavTimer);
  mobileNav.hidden = false;
  document.documentElement.style.overflow = "hidden";
  mobileOpenBtn.setAttribute("aria-expanded", "true");
  requestAnimationFrame(() => mobileNav.classList.add("is-open"));
}

function closeMobileNav() {
  mobileNav.classList.remove("is-open");
  document.documentElement.style.overflow = "";
  mobileOpenBtn.setAttribute("aria-expanded", "false");
  mobileNavTimer = setTimeout(() => {
    mobileNav.hidden = true;
  }, 300);
}

mobileOpenBtn.addEventListener("click", openMobileNav);
document
  .querySelector("[data-mobile-nav-close]")
  .addEventListener("click", closeMobileNav);

document.addEventListener("keydown", (e) => {
  if (e.key === "Escape" && !mobileNav.hidden) closeMobileNav();
});

// the menu locks page scroll, and it can't be reached again at desktop width
window.matchMedia("(min-width: 1024px)").addEventListener("change", (e) => {
  if (e.matches && !mobileNav.hidden) closeMobileNav();
});
