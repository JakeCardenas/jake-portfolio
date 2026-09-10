const typingNode = document.getElementById("typing");

if (typingNode) {
  const stream = document.getElementById("ttStream");
  const caret = document.getElementById("ttCaret");
  const results = document.getElementById("ttResults");
  const field = document.getElementById("ttField");
  const liveWpm = document.getElementById("ttWpm");
  const liveAcc = document.getElementById("ttAcc");
  const liveTime = document.getElementById("ttTime");
  const durationButtons = [...typingNode.querySelectorAll("[data-tt-duration]")];

  const WORDS = `the of and to in is you that it he for was on are as with his they at
  be this have from one had by word but not what all were we when your can said there
  use an each which she do how their if will up other about out many then them these so
  some her would make like him into time has look two more write go see number no way
  could people my than first water been call who oil now find long down day did get come
  made may part over new sound take only little work know place year live me back give
  most very after thing our just name good sentence man think say great where help
  through much before line right too mean old any same tell boy follow came want show
  also around form three small set put end does another well large must big even such
  because turn here why ask went men read need land different home us move try kind hand
  picture again change off play spell air away animal house point page letter mother
  answer found study still learn should world build code system design data model random
  screen keyboard editor project search value simple result active border`
    .split(/\s+/)
    .filter(Boolean);

  let duration = 30;
  let target = [];
  let typed = [];
  let started = null;
  let ticker = null;
  let finished = false;

  function sample(count) {
    const out = [];
    for (let i = 0; i < count; i++) {
      out.push(WORDS[Math.floor(Math.random() * WORDS.length)]);
    }
    return out.join(" ").split("");
  }

  function reset() {
    clearInterval(ticker);
    ticker = null;
    started = null;
    finished = false;
    typed = [];
    target = sample(90);
    results.hidden = true;
    stream.hidden = false;
    liveWpm.textContent = "0";
    liveAcc.textContent = "100";
    liveTime.textContent = String(duration);
    paint();
  }

  function correctCount() {
    return typed.reduce((n, ch, i) => n + (ch === target[i] ? 1 : 0), 0);
  }

  function stats() {
    const elapsed = started ? Math.max((Date.now() - started) / 1000, 1) : duration;
    const correct = correctCount();
    return {
      wpm: Math.round(correct / 5 / (elapsed / 60)),
      raw: Math.round(typed.length / 5 / (elapsed / 60)),
      accuracy: typed.length ? Math.round((correct / typed.length) * 100) : 100,
      errors: typed.length - correct,
      characters: typed.length,
    };
  }

  function paint() {
    const window_ = 240;
    const from = Math.max(0, Math.floor(typed.length / 60) * 60);
    stream.innerHTML = target
      .slice(from, from + window_)
      .map((ch, offset) => {
        const i = from + offset;
        let cls = "tt-char";
        if (i < typed.length) cls += typed[i] === ch ? " is-hit" : " is-miss";
        else if (i === typed.length) cls += " is-next";
        const glyph = ch === " " ? "&nbsp;" : ch;
        return `<span class="${cls}">${glyph}</span>`;
      })
      .join("");
    const next = stream.querySelector(".is-next");
    if (next && caret) {
      caret.style.transform = `translate(${next.offsetLeft}px, ${next.offsetTop}px)`;
    }
  }

  function tick() {
    const left = duration - Math.round((Date.now() - started) / 1000);
    liveTime.textContent = String(Math.max(left, 0));
    const s = stats();
    liveWpm.textContent = String(s.wpm);
    liveAcc.textContent = String(s.accuracy);
    if (left <= 0) finish();
  }

  function finish() {
    clearInterval(ticker);
    ticker = null;
    finished = true;
    const s = stats();
    stream.hidden = true;
    results.hidden = false;
    results.querySelector("[data-tt-result='wpm']").textContent = String(s.wpm);
    results.querySelector("[data-tt-result='accuracy']").textContent = `${s.accuracy}%`;
    results.querySelector("[data-tt-result='raw']").textContent = String(s.raw);
    results.querySelector("[data-tt-result='errors']").textContent = String(s.errors);
    results.querySelector("[data-tt-result='characters']").textContent = String(s.characters);
  }

  function handle(key) {
    if (finished) return;
    if (key === "Backspace") {
      typed.pop();
    } else if (key.length === 1) {
      if (!started) {
        started = Date.now();
        ticker = setInterval(tick, 200);
      }
      typed.push(key);
      if (typed.length >= target.length) finish();
    } else {
      return;
    }
    paint();
    if (started) tick();
  }

  typingNode.addEventListener("keydown", (e) => {
    if (e.metaKey || e.ctrlKey || e.altKey) return;
    if (e.key === "Tab") {
      e.preventDefault();
      reset();
      return;
    }
    if (e.key === "Escape") return;
    if (e.key === "Backspace" || e.key.length === 1) {
      e.preventDefault();
      handle(e.key);
    }
  });

  // mobile keyboards emit input events rather than usable keydown values
  field.addEventListener("input", () => {
    const value = field.value;
    field.value = "";
    [...value].forEach((ch) => handle(ch));
  });

  durationButtons.forEach((button) =>
    button.addEventListener("click", () => {
      duration = Number(button.dataset.ttDuration);
      durationButtons.forEach((b) =>
        b.classList.toggle("is-active", b === button),
      );
      reset();
    }),
  );

  typingNode.querySelectorAll("[data-tt-restart]").forEach((b) =>
    b.addEventListener("click", () => {
      reset();
      field.focus({ preventScroll: true });
    }),
  );

  register("j", () => {
    reset();
    overlays.open(typingNode);
    field.focus({ preventScroll: true });
  }, "Typing test");

  document.querySelectorAll("[data-typing-open]").forEach((el) =>
    el.addEventListener("click", (e) => {
      e.preventDefault();
      reset();
      overlays.open(typingNode);
      field.focus({ preventScroll: true });
    }),
  );
}
