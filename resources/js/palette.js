const paletteNode = document.getElementById("palette");

if (paletteNode) {
  const input = document.getElementById("paletteInput");
  const list = document.getElementById("paletteList");
  const status = document.getElementById("paletteStatus");
  const empty = document.getElementById("paletteEmpty");

  let index = [];
  let matches = [];
  let active = 0;
  let loaded = null;

  const RECENT_KEY = "palette-recent";
  const LIMIT = 40;

  function recent() {
    try {
      return JSON.parse(localStorage.getItem(RECENT_KEY) || "[]");
    } catch (e) {
      return [];
    }
  }

  function remember(item) {
    const kept = [item.url, ...recent().filter((u) => u !== item.url)].slice(0, 5);
    try {
      localStorage.setItem(RECENT_KEY, JSON.stringify(kept));
    } catch (e) {}
  }

  function load() {
    if (loaded) return loaded;
    loaded = fetch("/search-index.json")
      .then((r) => r.json())
      .then((data) => {
        index = data;
      })
      .catch(() => {
        index = [];
      });
    return loaded;
  }

  function score(item, query) {
    const label = item.label.toLowerCase();
    if (label === query) return 0;
    if (label.startsWith(query)) return 1;
    const word = label.split(/\s+/).some((w) => w.startsWith(query));
    if (word) return 2;
    if (label.includes(query)) return 3;
    if ((item.meta || "").toLowerCase().includes(query)) return 4;
    if ((item.terms || "").toLowerCase().includes(query)) return 5;
    return -1;
  }

  function search(query) {
    query = query.trim().toLowerCase();
    if (!query) {
      const saved = recent();
      const first = saved
        .map((url) => index.find((i) => i.url === url))
        .filter(Boolean);
      const pages = index.filter((i) => i.kind === "Page" && !saved.includes(i.url));
      return [...first, ...pages].slice(0, LIMIT);
    }
    return index
      .map((item) => ({ item, rank: score(item, query) }))
      .filter((r) => r.rank >= 0)
      .sort((a, b) => a.rank - b.rank || a.item.label.length - b.item.label.length)
      .slice(0, LIMIT)
      .map((r) => r.item);
  }

  function highlight(text, query) {
    const safe = text.replace(/[&<>]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;" }[c]));
    if (!query) return safe;
    const at = safe.toLowerCase().indexOf(query.toLowerCase());
    if (at < 0) return safe;
    return (
      safe.slice(0, at) +
      "<mark>" +
      safe.slice(at, at + query.length) +
      "</mark>" +
      safe.slice(at + query.length)
    );
  }

  function paint() {
    const query = input.value.trim();
    list.innerHTML = matches
      .map(
        (item, n) =>
          `<li role="option" id="pal-${n}" aria-selected="${n === active}" class="pal-item${
            n === active ? " is-active" : ""
          }"><a href="${item.url}" tabindex="-1"><span class="pal-kind mono">${
            item.kind
          }</span><span class="pal-label">${highlight(item.label, query)}</span>${
            item.meta ? `<span class="pal-meta">${highlight(item.meta, query)}</span>` : ""
          }</a></li>`,
      )
      .join("");
    empty.hidden = matches.length > 0;
    status.textContent = matches.length
      ? `${matches.length} result${matches.length === 1 ? "" : "s"}`
      : "No results";
    const node = list.children[active];
    if (node) node.scrollIntoView({ block: "nearest" });
    input.setAttribute("aria-activedescendant", node ? node.id : "");
  }

  function refresh() {
    matches = search(input.value);
    active = 0;
    paint();
  }

  function choose(item) {
    if (!item) return;
    remember(item);
    overlays.close();
    if (/^https?:/.test(item.url)) window.open(item.url, "_blank", "noopener");
    else window.location.href = item.url;
  }

  function open() {
    overlays.open(paletteNode);
    input.value = "";
    load().then(refresh);
  }

  register("k", open, "Search");

  document.querySelectorAll("[data-palette-open]").forEach((el) =>
    el.addEventListener("click", (e) => {
      e.preventDefault();
      open();
    }),
  );

  input.addEventListener("input", refresh);

  input.addEventListener("keydown", (e) => {
    if (e.key === "ArrowDown" || e.key === "ArrowUp") {
      e.preventDefault();
      if (!matches.length) return;
      active = (active + (e.key === "ArrowDown" ? 1 : -1) + matches.length) % matches.length;
      paint();
    } else if (e.key === "Enter") {
      e.preventDefault();
      choose(matches[active]);
    } else if (e.key === "Home" || e.key === "End") {
      e.preventDefault();
      active = e.key === "Home" ? 0 : matches.length - 1;
      paint();
    }
  });

  list.addEventListener("click", (e) => {
    const li = e.target instanceof Element && e.target.closest(".pal-item");
    if (!li) return;
    e.preventDefault();
    choose(matches[[...list.children].indexOf(li)]);
  });

  list.addEventListener("pointermove", (e) => {
    const li = e.target instanceof Element && e.target.closest(".pal-item");
    if (!li) return;
    const n = [...list.children].indexOf(li);
    if (n !== active) {
      active = n;
      paint();
    }
  });
}
