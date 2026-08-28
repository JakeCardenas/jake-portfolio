const SoundManager = (() => {
  let ctx = null;
  let master = null;
  let noiseBuffer = null;
  let unlocked = false;

  let enabled = localStorage.getItem("sound-enabled");
  enabled = enabled === null ? true : enabled === "true";

  // every gain below is bryllim's measured value; this scales the lot
  const MASTER = 1.7;

  let lastHover = 0;
  const HOVER_GAP_MS = 45;

  function ensureContext() {
    if (!ctx) {
      const AC = window.AudioContext || window.webkitAudioContext;
      if (!AC) return null;
      ctx = new AC();

      const len = Math.floor(ctx.sampleRate * 0.1);
      noiseBuffer = ctx.createBuffer(1, len, ctx.sampleRate);
      const d = noiseBuffer.getChannelData(0);
      for (let i = 0; i < len; i++) d[i] = Math.random() * 2 - 1;

      // limiter catches the peak when hover and click land together
      const limiter = ctx.createDynamicsCompressor();
      limiter.threshold.value = -4;
      limiter.knee.value = 0;
      limiter.ratio.value = 20;
      limiter.attack.value = 0.002;
      limiter.release.value = 0.08;

      master = ctx.createGain();
      master.gain.value = MASTER;
      master.connect(limiter).connect(ctx.destination);
    }
    if (ctx.state === "suspended") ctx.resume();
    return ctx;
  }

  function unlock() {
    if (unlocked) return;
    unlocked = true;
    ensureContext();
  }
  ["pointerdown", "keydown", "touchstart"].forEach((e) =>
    window.addEventListener(e, unlock, { once: true, passive: true }),
  );

  function env(param, peak, at, attack, decay) {
    param.setValueAtTime(0.0001, at);
    param.exponentialRampToValueAtTime(Math.max(peak, 0.0002), at + attack);
    param.exponentialRampToValueAtTime(0.0001, at + decay);
  }

  function noise({ freq, q, peak, decay, delay = 0, out }) {
    const at = ctx.currentTime + delay;
    const src = ctx.createBufferSource();
    src.buffer = noiseBuffer;

    const bp = ctx.createBiquadFilter();
    bp.type = "bandpass";
    bp.frequency.value = freq;
    bp.Q.value = q;

    const g = ctx.createGain();
    env(g.gain, peak, at, 0.001, decay);

    src.connect(bp).connect(g).connect(out || master);
    src.start(at);
    src.stop(at + decay + 0.02);
  }

  function tone({ freq, peak, attack = 0.001, decay, delay = 0, out }) {
    const at = ctx.currentTime + delay;
    const osc = ctx.createOscillator();
    osc.type = "sine";
    osc.frequency.setValueAtTime(freq, at);

    const g = ctx.createGain();
    env(g.gain, peak, at, attack, decay);

    osc.connect(g).connect(out || master);
    osc.start(at);
    osc.stop(at + decay + 0.03);
  }

  function lowpass(freq) {
    const f = ctx.createBiquadFilter();
    f.type = "lowpass";
    f.frequency.value = freq;
    f.Q.value = 1;
    f.connect(master);
    return f;
  }

  const sounds = {
    // fires the most, so keep it short
    hover() {
      const now = performance.now();
      if (now - lastHover < HOVER_GAP_MS) return;
      lastHover = now;
      noise({ freq: 5400, q: 1.8, peak: 0.14, decay: 0.019 });
      tone({ freq: 2600, peak: 0.018, decay: 0.013 });
    },

    click() {
      noise({ freq: 2200, q: 1.6, peak: 0.12, decay: 0.017 });
      noise({ freq: 3800, q: 1.6, peak: 0.1, decay: 0.021, delay: 0.024 });
    },

    // low body and high snap together, sine tail behind
    swap() {
      noise({ freq: 1700, q: 1.4, peak: 0.13, decay: 0.021 });
      noise({ freq: 4600, q: 1.8, peak: 0.12, decay: 0.017 });
      tone({ freq: 3200, peak: 0.02, decay: 0.051, delay: 0.006 });
    },

    // panels opening — slow 528Hz swell under a low tap
    swell() {
      const lp = lowpass(2500);
      noise({ freq: 1700, q: 1.4, peak: 0.13, decay: 0.021 });
      tone({ freq: 528, peak: 0.06, attack: 0.06, decay: 0.38, out: lp });
      tone({ freq: 528, peak: 0.05, attack: 0.06, decay: 0.4, out: lp });
    },

    // C6 then G6, played when sound is switched on
    chime() {
      const lp = lowpass(4000);
      tone({ freq: 1046.5, peak: 0.09, attack: 0.006, decay: 0.226, out: lp });
      tone({
        freq: 1568,
        peak: 0.08,
        attack: 0.006,
        decay: 0.266,
        delay: 0.09,
        out: lp,
      });
    },
  };

  function play(name) {
    if (!enabled || !unlocked) return;
    if (!ensureContext()) return;
    if (sounds[name]) sounds[name]();
  }

  return {
    play,
    setEnabled(v) {
      enabled = v;
      localStorage.setItem("sound-enabled", v ? "true" : "false");
    },
    isEnabled() {
      return enabled;
    },
  };
})();
