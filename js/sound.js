/* Cuelume v0.1.0 © Daniel Belyi — MIT License */
var l = {
  chime: { masterGain: .5, layers: [{ kind: "tone", waveform: "sine", frequency: 1046.5, attack: .006, decay: .22, peak: .09 }, { kind: "tone", waveform: "sine", frequency: 1568, offset: .09, attack: .006, decay: .26, peak: .08 }], shimmer: { delay: .12, feedback: .25, wet: .18, lowpass: 4e3 } },
  sparkle: { masterGain: .5, layers: [{ kind: "tone", waveform: "sine", frequency: 1760, offset: 0, attack: .003, decay: .09, peak: .045 }, { kind: "tone", waveform: "sine", frequency: 2217, offset: .045, attack: .003, decay: .09, peak: .04 }, { kind: "tone", waveform: "sine", frequency: 2637, offset: .09, attack: .003, decay: .1, peak: .038 }, { kind: "tone", waveform: "sine", frequency: 3520, offset: .135, attack: .003, decay: .12, peak: .032 }], shimmer: { delay: .07, feedback: .35, wet: .22, lowpass: 6e3 } },
  droplet: { masterGain: .55, layers: [{ kind: "tone", waveform: "sine", frequency: 1200, glideTo: 550, glideTime: .14, attack: .004, decay: .2, peak: .075 }], shimmer: { delay: .09, feedback: .2, wet: .15, lowpass: 3e3 } },
  bloom: { masterGain: .5, layers: [{ kind: "tone", waveform: "sine", frequency: 528, attack: .06, decay: .32, peak: .06 }, { kind: "tone", waveform: "sine", frequency: 528, detune: 12, attack: .06, decay: .34, peak: .05 }], shimmer: { delay: .15, feedback: .2, wet: .12, lowpass: 2500 } },
  whisper: { masterGain: .5, layers: [{ kind: "noise", filterType: "lowpass", filterFrequency: 1200, filterQ: .7, attack: .04, decay: .16, peak: .05 }] },
  tick: { masterGain: .4, layers: [{ kind: "noise", filterType: "bandpass", filterFrequency: 5400, filterQ: 1.8, attack: .001, decay: .018, peak: .14 }, { kind: "tone", waveform: "sine", frequency: 2600, attack: .001, decay: .012, peak: .018 }] },
  press: { masterGain: .4, layers: [{ kind: "noise", filterType: "bandpass", filterFrequency: 1700, filterQ: 1.4, attack: .001, decay: .02, peak: .13 }] },
  release: { masterGain: .4, layers: [{ kind: "noise", filterType: "bandpass", filterFrequency: 4600, filterQ: 1.8, attack: .001, decay: .016, peak: .12 }, { kind: "tone", waveform: "sine", frequency: 3200, offset: .006, attack: .001, decay: .05, peak: .02 }] },
  toggle: { masterGain: .4, layers: [{ kind: "noise", filterType: "bandpass", filterFrequency: 2200, filterQ: 1.6, attack: .001, decay: .016, peak: .12 }, { kind: "noise", filterType: "bandpass", filterFrequency: 3800, filterQ: 1.6, offset: .024, attack: .001, decay: .02, peak: .1 }] },
  success: { masterGain: .5, layers: [{ kind: "tone", waveform: "sine", frequency: 880, attack: .004, decay: .09, peak: .06 }, { kind: "tone", waveform: "sine", frequency: 1108.73, offset: .06, attack: .004, decay: .1, peak: .06 }, { kind: "tone", waveform: "sine", frequency: 1318.51, offset: .12, attack: .004, decay: .18, peak: .07 }], shimmer: { delay: .1, feedback: .22, wet: .16, lowpass: 4500 } }
};
function p(e) { return typeof e == "string" && Object.prototype.hasOwnProperty.call(l, e) }
var j = Object.keys(l);
var h = .05, M = .05, N = .001;
function F(e, n, t, a) {
  let r = e.createOscillator();
  if (r.type = t.waveform, r.frequency.setValueAtTime(t.frequency, a), t.detune && (r.detune.value = t.detune), t.glideTo !== void 0) {
    let i = t.glideTime ?? t.attack + t.decay;
    r.frequency.exponentialRampToValueAtTime(t.glideTo, a + i)
  }
  let o = e.createGain();
  o.gain.setValueAtTime(1e-4, a), o.gain.exponentialRampToValueAtTime(t.peak, a + t.attack), o.gain.exponentialRampToValueAtTime(1e-4, a + t.attack + t.decay), r.connect(o).connect(n), r.start(a), r.stop(a + t.attack + t.decay + h)
}
function I(e, n, t, a) {
  let r = t.attack + t.decay + h, o = Math.max(1, Math.floor(r * e.sampleRate)), i = e.createBuffer(1, o, e.sampleRate), s = i.getChannelData(0);
  for (let y = 0; y < o; y++) s[y] = 2 * Math.random() - 1;
  let c = e.createBufferSource();
  c.buffer = i;
  let d = e.createBiquadFilter();
  d.type = t.filterType, d.frequency.value = t.filterFrequency, t.filterQ !== void 0 && (d.Q.value = t.filterQ);
  let f = e.createGain();
  f.gain.setValueAtTime(1e-4, a), f.gain.exponentialRampToValueAtTime(t.peak, a + t.attack), f.gain.exponentialRampToValueAtTime(1e-4, a + t.attack + t.decay), c.connect(d).connect(f).connect(n), c.start(a), c.stop(a + r)
}
function L(e, n, t, a) {
  let r = e.createDelay(1);
  r.delayTime.value = a.delay;
  let o = e.createBiquadFilter();
  o.type = "lowpass", o.frequency.value = a.lowpass;
  let i = e.createGain();
  i.gain.value = a.feedback;
  let s = e.createGain();
  return s.gain.value = a.wet, n.connect(r), r.connect(o), o.connect(i), i.connect(r), o.connect(s), s.connect(t), [r, o, i, s]
}
function O(e) { return Math.max(...e.layers.map(n => (n.offset ?? 0) + n.attack + n.decay + h)) }
function P(e) { return !e || e.feedback <= 0 ? 0 : e.feedback >= 1 ? e.delay : e.delay * (1 + Math.ceil(Math.log(N) / Math.log(e.feedback))) }
function v(e, n) {
  let t = e.currentTime, a = e.createGain();
  a.gain.value = n.masterGain * 6, a.connect(e.destination);
  let r = n.shimmer ? L(e, a, e.destination, n.shimmer) : [];
  for (let i of n.layers) { let s = t + (i.offset ?? 0); i.kind === "tone" ? F(e, a, i, s) : I(e, a, i, s) }
  let o = (O(n) + P(n.shimmer) + M) * 1e3;
  setTimeout(() => { a.disconnect(); for (let i of r) i.disconnect() }, o)
}
var m = null, g = !0;
function w(e) { typeof e == "boolean" && (g = e) }
function Q() {
  if (m) return m;
  if (typeof window > "u") return null;
  let e = window.AudioContext ?? window.webkitAudioContext;
  if (!e) return null;
  try { m = new e } catch { return null }
  return m
}
function u(e = "chime") {
  if (!g || !p(e)) return;
  let n = Q();
  if (!n) return;
  let t = l[e];
  if (n.state === "running") v(n, t);
  else try { n.resume().then(() => { g && n.state === "running" && v(n, t) }, () => {}) } catch {}
}
var V = 150, A = new WeakSet, T = new WeakSet, S = -1 / 0;
function x(e, n, t) { let a = e.getAttribute(n); return p(a) ? a : t }
function _(e) { return e.pointerType === "mouse" && window.matchMedia("(hover: hover) and (pointer: fine)").matches }
function D(e, n, t) {
  if (!(n.target instanceof Element)) return null;
  let a = n.target.closest(`[${t}]`);
  return a && e.contains(a) ? a : null
}
function k(e, n, t, a, r = !1) {
  e.addEventListener(n, o => {
    let i = D(e, o, t);
    if (!(!i || T.has(o)) && !(r && !_(o))) {
      if (n === "pointerenter") {
        let s = o.relatedTarget;
        if (s instanceof Node && i.contains(s)) return;
        let c = performance.now();
        if (c - S < V) return;
        S = c
      }
      T.add(o), u(x(i, t, a))
    }
  }, !0)
}
function b(e) {
  if (typeof document > "u") return;
  let n = e ?? document;
  A.has(n) || (A.add(n), k(n, "pointerenter", "data-cuelume-hover", "chime", !0), k(n, "pointerdown", "data-cuelume-press", "press", !0), k(n, "pointerup", "data-cuelume-release", "release", !0), k(n, "click", "data-cuelume-toggle", "toggle"))
}
var R = "site-sounds-enabled",
  G = ["a[href]", "button:not([disabled])", 'input[type="button"]:not([disabled])', 'input[type="submit"]:not([disabled])', 'input[type="reset"]:not([disabled])', '[role="button"]', '[role="tab"]', "summary", '[tabindex="0"]'].join(",");
function E() { try { return localStorage.getItem(R) === "true" } catch { return !1 } }
function q(e, n = !1) {
  w(e);
  try { localStorage.setItem(R, String(e)) } catch {}
  document.querySelectorAll("[data-sound-toggle]").forEach(t => {
    t.setAttribute("aria-pressed", String(e)),
    t.setAttribute("aria-label", e ? "Mute interface sounds" : "Enable interface sounds"),
    t.setAttribute("title", e ? "Sounds on" : "Sounds off"),
    t.querySelector("[data-sound-on]")?.toggleAttribute("hidden", !e),
    t.querySelector("[data-sound-off]")?.toggleAttribute("hidden", e)
  }),
  e && n && u("chime")
}
function B(e) {
  let n = (e.getAttribute("aria-label") || "").toLowerCase(), t = (e.getAttribute("onclick") || "").toLowerCase();
  return n.startsWith("close") || n.startsWith("dismiss") || /close[a-z]*\(/.test(t)
}
function W(e) {
  let n = (e.getAttribute("onclick") || "").toLowerCase();
  return e.getAttribute("aria-haspopup") === "dialog" || /open[a-z]*\(/.test(n)
}
function C(e = document) {
  let n = [];
  e instanceof Element && e.matches(G) && n.push(e),
  e.querySelectorAll?.(G).forEach(t => n.push(t)),
  n.forEach(t => {
    t.closest("[data-cuelume-silent]") || t.hasAttribute("data-sound-toggle") || (t.dataset.cuelumeHover ||= "tick", t.dataset.cuelumePress ||= "press", t.dataset.cuelumeRelease ||= "release", t.matches('[role="tab"], [role="switch"], [data-theme-opt]') ? (delete t.dataset.cuelumePress, delete t.dataset.cuelumeRelease, t.dataset.cuelumeToggle ||= "toggle") : B(t) ? t.dataset.cuelumeRelease = "droplet" : W(t) && (t.dataset.cuelumeRelease = "bloom"))
  })
}
q(E());
C();
b();
document.addEventListener("click", e => { e.target.closest("[data-sound-toggle]") && q(!E(), !0) });
document.addEventListener("change", e => { e.target.matches('select, input[type="checkbox"], input[type="radio"]') && u("toggle") });
new MutationObserver(e => { e.forEach(({ addedNodes: n }) => { n.forEach(t => { t.nodeType === Node.ELEMENT_NODE && C(t) }) }) }).observe(document.documentElement, { childList: !0, subtree: !0 });
window.siteSound = { play: u, setEnabled: e => q(!!e), isEnabled: E };
document.dispatchEvent(new CustomEvent("site-sound-ready"));
