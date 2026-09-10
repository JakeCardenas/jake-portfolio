const playNode = document.getElementById("playground");

if (playNode) {
  const canvas = document.getElementById("pgCanvas");
  const context = canvas.getContext("2d");
  const cellInput = document.getElementById("pgCell");
  const readout = document.getElementById("pgReadout");

  const pointer = { x: -999, y: -999, inside: false };
  const drops = [];
  let cell = Number(cellInput.value);
  let frame = null;
  let width = 0;
  let height = 0;
  let ratio = 1;
  let ink = "#0a0a0a";

  const REACH = 118;
  const DROP_LIFE = 2600;
  const reduced = matchMedia("(prefers-reduced-motion: reduce)");

  function measure() {
    const box = canvas.getBoundingClientRect();
    ratio = Math.min(window.devicePixelRatio || 1, 2);
    width = Math.round(box.width);
    height = Math.round(box.height);
    canvas.width = Math.round(width * ratio);
    canvas.height = Math.round(height * ratio);
    context.setTransform(ratio, 0, 0, ratio, 0, 0);
    ink = getComputedStyle(document.documentElement)
      .getPropertyValue("--fg")
      .trim() || "#0a0a0a";
  }

  function influence(x, y, now) {
    let value = 0;
    if (pointer.inside) {
      const distance = Math.hypot(x - pointer.x, y - pointer.y);
      if (distance < REACH) value += 1 - distance / REACH;
    }
    for (const drop of drops) {
      const age = (now - drop.at) / DROP_LIFE;
      if (age >= 1) continue;
      const radius = 30 + age * 210;
      const band = Math.abs(Math.hypot(x - drop.x, y - drop.y) - radius);
      if (band < 34) value += (1 - band / 34) * (1 - age) * 1.15;
    }
    return Math.min(value, 1);
  }

  function draw() {
    const now = performance.now();
    context.clearRect(0, 0, width, height);
    context.fillStyle = ink;
    const half = cell / 2;
    for (let y = half; y < height; y += cell) {
      for (let x = half; x < width; x += cell) {
        const lift = influence(x, y, now);
        const size = cell * (0.1 + lift * 0.78);
        if (size < 0.4) continue;
        context.globalAlpha = 0.22 + lift * 0.78;
        context.beginPath();
        context.arc(x, y, size / 2, 0, Math.PI * 2);
        context.fill();
      }
    }
    context.globalAlpha = 1;

    while (drops.length && now - drops[0].at > DROP_LIFE) drops.shift();
    if (readout) {
      readout.textContent = `${Math.floor(width / cell)}×${Math.floor(height / cell)} cells`;
    }
    frame = requestAnimationFrame(draw);
  }

  function start() {
    measure();
    if (frame === null) frame = requestAnimationFrame(draw);
  }

  function stop() {
    if (frame !== null) cancelAnimationFrame(frame);
    frame = null;
  }

  function locate(event) {
    const box = canvas.getBoundingClientRect();
    pointer.x = event.clientX - box.left;
    pointer.y = event.clientY - box.top;
    pointer.inside = true;
  }

  canvas.addEventListener("pointermove", locate);
  canvas.addEventListener("pointerdown", (event) => {
    locate(event);
    drops.push({ x: pointer.x, y: pointer.y, at: performance.now() });
    if (drops.length > 12) drops.shift();
    window.siteSound?.play("droplet");
  });
  canvas.addEventListener("pointerleave", () => {
    pointer.inside = false;
  });

  cellInput.addEventListener("input", () => {
    cell = Number(cellInput.value);
  });

  playNode.querySelectorAll("[data-pg-clear]").forEach((button) =>
    button.addEventListener("click", () => {
      drops.length = 0;
      pointer.inside = false;
    }),
  );

  window.addEventListener("resize", () => {
    if (frame !== null) measure();
  });

  function open() {
    overlays.open(playNode);
    start();
    if (reduced.matches) {
      stop();
      measure();
      draw();
      stop();
    }
  }

  register("/", open, "Playground");

  document.querySelectorAll("[data-playground-open]").forEach((el) =>
    el.addEventListener("click", (event) => {
      event.preventDefault();
      open();
    }),
  );

  new MutationObserver(() => {
    if (playNode.hidden) stop();
  }).observe(playNode, { attributes: true, attributeFilter: ["hidden"] });
}
