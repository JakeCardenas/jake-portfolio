const typingNode = document.getElementById("typing");

if (typingNode) {
  const wordsEl = document.getElementById("ttWords");
  const kbEl = document.getElementById("ttKeyboard");
  const field = document.getElementById("ttField");
  const verdictEl = document.getElementById("ttVerdict");
  const liveWpm = document.getElementById("ttWpm");
  const liveAcc = document.getElementById("ttAcc");
  const liveTime = document.getElementById("ttTime");
  const resWpm = document.getElementById("ttResWpm");
  const resAcc = document.getElementById("ttResAcc");
  const resRaw = document.getElementById("ttResRaw");
  const resTime = document.getElementById("ttResTime");

  const WORDS = `the and for that with have this from they what were when your said
  each their which will other about many then them these some would into time look
  more write like him two has number way could people than first water been call who
  its now find long down day did get come made may part over new sound take only
  little work know place year live back give most very after thing our just name good
  man think say great where help through much before line right too mean old any same
  tell boy follow came want show also around form three small set put end does another
  well large must big even such because turn here why ask went men read need land
  different home us move try kind hand picture again change off play spell air away
  animal house point page letter mother answer found study still learn should world
  build code system design data model screen keyboard editor project search value
  simple result active border`
    .split(/\s+/)
    .filter(Boolean);

  const KB_ROWS = ["qwertyuiop", "asdfghjkl", "zxcvbnm"];
  const COUNT = 26;
  const MAX_EXTRA = 8;
  const BEST_KEY = "tt-best-wpm";

  let words = [];
  let cells = [];
  let wi = 0;
  let ci = 0;
  let started = false;
  let finished = false;
  let startTime = 0;
  let frame = null;
  let raw = 0;
  let correct = 0;
  let showWpm = 0;
  let showAcc = 100;
  let showTime = 0;
  let lastWrite = 0;
  let confirming = false;

  const caret = document.createElement("span");
  caret.className = "tt-caret";

  const reduced = matchMedia("(prefers-reduced-motion: reduce)");

  function best() {
    const stored = Number(localStorage.getItem(BEST_KEY));
    return Number.isFinite(stored) && stored > 0 ? stored : 0;
  }

  function setConfirm(on) {
    confirming = on;
    typingNode.classList.toggle("is-confirming", on);
  }

  function buildKeyboard() {
    kbEl.textContent = "";
    let i = 0;
    const row = (keys, extra) => {
      const r = document.createElement("div");
      r.className = "tt-krow";
      keys.forEach((ch) => {
        const k = document.createElement("span");
        k.className = extra ? `tt-key ${extra}` : "tt-key";
        k.dataset.key = ch;
        k.textContent = extra ? "space" : ch;
        k.style.animationDelay = `${i * 7}ms`;
        r.appendChild(k);
        i += 1;
      });
      kbEl.appendChild(r);
    };
    KB_ROWS.forEach((keys) => row([...keys]));
    row([" "], "space");
  }

  function keyFor(ch) {
    return kbEl.querySelector(`.tt-key[data-key="${ch === " " ? " " : ch}"]`);
  }

  function flash(ch) {
    const k = keyFor(ch);
    if (!k) return;
    k.classList.add("is-down");
    setTimeout(() => k.classList.remove("is-down"), 110);
  }

  function markNext() {
    kbEl.querySelectorAll(".tt-key.is-next").forEach((k) =>
      k.classList.remove("is-next"),
    );
    if (finished) return;
    const cell = cells[wi];
    const ch =
      ci < cell.word.length
        ? cell.word[ci]
        : wi < words.length - 1
          ? " "
          : null;
    if (ch) keyFor(ch)?.classList.add("is-next");
  }

  function buildText() {
    wordsEl.textContent = "";
    cells = words.map((word) => {
      const el = document.createElement("span");
      el.className = "tt-word";
      const chars = [...word].map((ch) => {
        const c = document.createElement("span");
        c.className = "tt-char";
        c.textContent = ch;
        el.appendChild(c);
        return c;
      });
      wordsEl.appendChild(el);
      return { el, chars, word };
    });
    wordsEl.appendChild(caret);
  }

  function moveCaret() {
    const cell = cells[wi];
    const at = Math.min(ci, cell.chars.length - 1);
    const el = cell.chars[at];
    if (!el) return;
    const past = ci >= cell.chars.length;
    caret.style.left = `${el.offsetLeft + (past ? el.offsetWidth : 0)}px`;
    caret.style.top = `${el.offsetTop}px`;
  }

  function loop(now) {
    const elapsed = started ? (Date.now() - startTime) / 1000 : 0;
    const targetWpm =
      started && elapsed > 0.5 ? correct / 5 / (elapsed / 60) : 0;
    const targetAcc = raw ? (correct / raw) * 100 : 100;

    showWpm += (targetWpm - showWpm) * 0.16;
    showAcc += (targetAcc - showAcc) * 0.16;
    showTime += (elapsed - showTime) * 0.4;
    if (Math.abs(targetWpm - showWpm) < 0.5) showWpm = targetWpm;
    if (Math.abs(targetAcc - showAcc) < 0.5) showAcc = targetAcc;

    if (now - lastWrite >= 240) {
      lastWrite = now;
      liveWpm.textContent = String(Math.round(showWpm));
      liveAcc.textContent = String(Math.round(showAcc));
      liveTime.textContent = String(Math.floor(showTime + 1e-4));
    }
    if (overlays.current === typingNode && !finished) {
      frame = requestAnimationFrame(loop);
    }
  }

  function start() {
    started = true;
    startTime = Date.now();
    cancelAnimationFrame(frame);
    frame = requestAnimationFrame(loop);
  }

  function countUp(el, value, ms) {
    if (reduced.matches) {
      el.textContent = String(value);
      return;
    }
    // anchored to the first frame's own timestamp: rAF reports the frame start,
    // which can precede performance.now() and drive progress negative
    let from = null;
    const step = (now) => {
      if (from === null) from = now;
      const p = Math.min(1, Math.max(0, (now - from) / ms));
      el.textContent = String(Math.round(value * (1 - (1 - p) ** 3)));
      if (p < 1) requestAnimationFrame(step);
      else el.textContent = String(value);
    };
    requestAnimationFrame(step);
  }

  function verdict(wpm) {
    const previous = best();
    const beat = wpm > previous;
    if (beat) localStorage.setItem(BEST_KEY, String(wpm));
    const mark = beat
      ? '<svg class="tt-vicon" viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M5 12.5l4.5 4.5L19 7" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/></svg>'
      : '<svg class="tt-vicon" viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M7 7l10 10M17 7L7 17" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"/></svg>';
    const text = beat
      ? previous
        ? `new personal best · beat ${previous} wpm`
        : "new personal best"
      : `personal best · ${previous} wpm`;
    verdictEl.className = `tt-verdict mono${beat ? " is-best" : ""}`;
    verdictEl.innerHTML = `${mark}<span>${text}</span>`;
  }

  function finish() {
    if (finished) return;
    finished = true;
    cancelAnimationFrame(frame);
    const elapsed = Math.max(0.001, (Date.now() - startTime) / 1000);
    const wpm = Math.round(correct / 5 / (elapsed / 60));
    resAcc.textContent = String(raw ? Math.round((correct / raw) * 100) : 100);
    resRaw.textContent = String(Math.round(raw / 5 / (elapsed / 60)));
    resTime.textContent = elapsed.toFixed(1);
    verdict(wpm);
    typingNode.classList.add("show-results");
    countUp(resWpm, wpm, 750);
  }

  function afterInput() {
    moveCaret();
    markNext();
    if (wi === words.length - 1 && ci >= cells[wi].word.length) finish();
  }

  function typeChar(ch) {
    if (finished) return;
    if (!started) start();
    const cell = cells[wi];
    if (ci < cell.word.length) {
      const hit = ch === cell.word[ci];
      cell.chars[ci].classList.add(hit ? "is-hit" : "is-miss");
      raw += 1;
      if (hit) correct += 1;
      ci += 1;
    } else if (cell.chars.length - cell.word.length < MAX_EXTRA) {
      const extra = document.createElement("span");
      extra.className = "tt-char is-extra";
      extra.textContent = ch;
      cell.el.appendChild(extra);
      cell.chars.push(extra);
      raw += 1;
      ci += 1;
    }
    afterInput();
  }

  function typeSpace() {
    if (finished || !started || wi >= words.length - 1) return;
    wi += 1;
    ci = 0;
    afterInput();
  }

  function backspace() {
    if (finished) return;
    if (ci > 0) {
      ci -= 1;
      const cell = cells[wi];
      if (ci >= cell.word.length) cell.chars.pop()?.remove();
      else cell.chars[ci].classList.remove("is-hit", "is-miss");
    } else if (wi > 0) {
      wi -= 1;
      ci = cells[wi].chars.length;
    }
    moveCaret();
    markNext();
  }

  function reset() {
    cancelAnimationFrame(frame);
    started = false;
    finished = false;
    startTime = 0;
    wi = 0;
    ci = 0;
    raw = 0;
    correct = 0;
    showWpm = 0;
    showAcc = 100;
    showTime = 0;
    lastWrite = 0;
    typingNode.classList.remove("show-results");
    setConfirm(false);
    liveWpm.textContent = "0";
    liveAcc.textContent = "100";
    liveTime.textContent = "0";
    words = Array.from(
      { length: COUNT },
      () => WORDS[Math.floor(Math.random() * WORDS.length)],
    );
    buildText();
    requestAnimationFrame(() => {
      moveCaret();
      markNext();
    });
  }

  function open() {
    reset();
    overlays.open(typingNode);
    if (matchMedia("(pointer: coarse)").matches) {
      field.focus({ preventScroll: true });
    }
  }

  buildKeyboard();

  document.addEventListener("keydown", (e) => {
    if (overlays.current !== typingNode) return;
    if (e.key === "Escape") {
      e.preventDefault();
      if (confirming) setConfirm(false);
      else overlays.close();
      return;
    }
    if (e.metaKey || e.ctrlKey || e.altKey) return;
    if (e.key === "Tab") {
      e.preventDefault();
      if (started && !finished) setConfirm(true);
      else reset();
      return;
    }
    if (e.key === "Enter") {
      if (confirming || finished) {
        e.preventDefault();
        reset();
      }
      return;
    }
    if (confirming) return;
    if (e.key === "Backspace") {
      e.preventDefault();
      backspace();
      return;
    }
    if (e.key === " ") {
      e.preventDefault();
      flash(" ");
      if (finished) reset();
      else typeSpace();
      return;
    }
    if (e.key.length !== 1) return;
    const ch = e.key.toLowerCase();
    if (!/[a-z]/.test(ch)) return;
    e.preventDefault();
    flash(ch);
    typeChar(ch);
  });

  // touch keyboards fire input events without usable keydown values
  field.addEventListener("input", () => {
    const value = field.value;
    field.value = "";
    [...value].forEach((ch) => {
      const lower = ch.toLowerCase();
      if (ch === " ") {
        flash(" ");
        typeSpace();
      } else if (/[a-z]/.test(lower)) {
        flash(lower);
        typeChar(lower);
      }
    });
  });

  field.addEventListener("keydown", (e) => {
    if (e.key !== "Backspace") return;
    e.preventDefault();
    backspace();
  });

  typingNode
    .querySelector("[data-tt-restart]")
    .addEventListener("click", reset);

  register("j", () => {
    if (overlays.current === typingNode) overlays.close();
    else open();
  });

  document.querySelectorAll("[data-typing-open]").forEach((el) =>
    el.addEventListener("click", (e) => {
      e.preventDefault();
      open();
    }),
  );
}
