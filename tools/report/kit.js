/* The report's shared kit: the data, small helpers, one drawn icon family, figure numbering,
   the contents rail, presenter keys and the moment each figure's marks arrive. */
window.R = (() => {
  const D = JSON.parse(document.getElementById("data").textContent);
  const $ = (id) => document.getElementById(id);
  const still = matchMedia("(prefers-reduced-motion: reduce)").matches;
  const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const num = (n) => (n === null || n === undefined) ? "–" : Number(n).toLocaleString("en-US");
  const f2 = (n) => (n === null || n === undefined) ? "–" : Number(n).toFixed(2);
  const f3 = (n) => (n === null || n === undefined) ? "–" : Number(n).toFixed(3);
  const pct = (n) => (n === null || n === undefined) ? "–" : Math.round(n * 100) + "%";
  const human = (s) => String(s || "").replace(/[_-]/g, " ");
  const cap = (s) => String(s).charAt(0).toUpperCase() + String(s).slice(1);
  const dash = (s) => String(s).replace(/ -- /g, " — ").replace(/--/g, "—");
  const wait = (ms) => still ? Promise.resolve() : new Promise((r) => setTimeout(r, ms));
  const range = (xs, f) => { const lo = Math.min(...xs), hi = Math.max(...xs); return lo === hi ? f(lo) : `${f(lo)}–${f(hi)}`; };

  // One drawn icon family: 24-unit grid, round joins, currentColor.
  const PATHS = {
    check: '<path d="M5 12.5l4.5 4.5L19 7.5"/>',
    x: '<path d="M6.5 6.5l11 11M17.5 6.5l-11 11"/>',
    play: '<path d="M8 5.8v12.4a.6.6 0 0 0 .9.5l10-6.2a.6.6 0 0 0 0-1l-10-6.2a.6.6 0 0 0-.9.5z" fill="currentColor"/>',
    pause: '<path d="M9 5.5v13M15 5.5v13"/>',
    replay: '<path d="M4.5 12a7.5 7.5 0 1 0 2.2-5.3"/><path d="M4.5 4.5v4h4"/>',
    lock: '<rect x="5" y="10.5" width="14" height="10" rx="2.2"/><path d="M8.5 10.5V8a3.5 3.5 0 0 1 7 0v2.5"/>',
    grid: '<rect x="4" y="4" width="7" height="7" rx="1.5"/><rect x="13" y="4" width="7" height="7" rx="1.5"/><rect x="4" y="13" width="7" height="7" rx="1.5"/><rect x="13" y="13" width="7" height="7" rx="1.5"/>',
    ban: '<circle cx="12" cy="12" r="8.5"/><path d="M6 6l12 12"/>',
    file: '<path d="M14 3.5H7.5a2 2 0 0 0-2 2v13a2 2 0 0 0 2 2h9a2 2 0 0 0 2-2V8z"/><path d="M14 3.5V8h4.5M9 13h6M9 16.5h4"/>',
    alert: '<path d="M12 4.2L3.2 19.5h17.6z"/><path d="M12 10v4.2M12 17.2v.1"/>',
    shield: '<path d="M12 3.5l7 2.8v5.6c0 4.3-2.9 7.3-7 8.6-4.1-1.3-7-4.3-7-8.6V6.3z"/><path d="M9 12l2.2 2.2L15.5 10"/>',
    theme: '<circle cx="12" cy="12" r="8"/><path d="M12 4a8 8 0 0 1 0 16z" fill="currentColor"/>',
    arrow: '<path d="M5 12h13.5M13 6.5l5.5 5.5-5.5 5.5"/>',
    flag: '<path d="M6 20.5V4.5M6 5h10.5l-2 3.5 2 3.5H6"/>',
    chev: '<path d="M9 6l6 6-6 6"/>',
  };
  const icon = (name) => `<svg class="ico" viewBox="0 0 24 24" aria-hidden="true">${PATHS[name] || ""}</svg>`;

  // Identity: ours is the reference arm in the house teal, the baseline the grey control arm,
  // and each AI model its own hue, the same everywhere (matched by the model id in a name).
  const MODEL_ORDER = ["gemini-3.1-flash-lite", "claude-haiku-4-5", "claude-sonnet-5-5", "claude-opus-5-5"];
  const extra = [];
  function modelColor(text) {
    const t = String(text || "").toLowerCase();
    let i = MODEL_ORDER.findIndex((m) => t.includes(m) || t.includes(m.replace(/^(gemini|claude)-/, "")));
    if (i < 0) { const id = (t.match(/[a-z]+-[\w.-]+/) || [t])[0]; if (!extra.includes(id)) extra.push(id); i = MODEL_ORDER.length + extra.indexOf(id); }
    return `var(--m${i % 6})`;
  }
  const kindColor = (kind, name) => kind === "ours" ? "var(--teal)" : kind === "baseline" ? "var(--ctrl)" : modelColor(name);

  // A 95% Wilson interval for k of n: what a sampled model's count could plausibly be.
  function wilson(k, n, z = 1.96) {
    if (!n) return [0, 1];
    const p = k / n, d = 1 + z * z / n, c = p + z * z / (2 * n), m = z * Math.sqrt(p * (1 - p) / n + z * z / (4 * n * n));
    return [Math.max(0, (c - m) / d), Math.min(1, (c + m) / d)];
  }

  // Tooltips: any element with data-t shows its text on hover.
  const tip = $("tip");
  document.addEventListener("mousemove", (e) => {
    const el = e.target.closest && e.target.closest("[data-t]");
    if (!el) { tip.classList.remove("on"); return; }
    tip.textContent = el.dataset.t; tip.style.left = e.clientX + "px"; tip.style.top = e.clientY + "px"; tip.classList.add("on");
  });

  /* ------------------------------------------------------------ figures */
  // Every figure and table is numbered in reading order before any section renders.
  let nFig = 0, nTab = 0;
  let nS = 0;
  document.querySelectorAll("figure.fig").forEach((f) => {
    const sup = f.closest("details.more");
    f.dataset.no = sup ? `${f.classList.contains("tablefig") ? "Table" : "Figure"} S${++nS}` : f.classList.contains("tablefig") ? `Table ${++nTab}` : `Figure ${++nFig}`;
  });
  // fig(el, {title, controls, body, caption}): the figure's header, body and caption.
  function fig(el, o) {
    if (typeof el === "string") el = $(el);
    el.innerHTML = `<div class="fh"><div class="ft"><span class="fno">${el.dataset.no}</span>${o.title}</div>${o.controls ? `<div class="fctl">${o.controls}</div>` : ""}</div>`
      + `<div class="fb">${o.body || ""}</div>` + (o.caption ? `<p class="cap">${o.caption}</p>` : "");
    el.setAttribute("aria-label", `${el.dataset.no}: ${o.title.replace(/<[^>]+>/g, "")}`);
    return el;
  }
  // A figure's marks arrive the first time it is on screen, and again when replay() is called.
  const io = new IntersectionObserver((es) => es.forEach((e) => { if (e.isIntersecting) { e.target.classList.add("seen"); io.unobserve(e.target); } }), { threshold: 0.18 });
  document.querySelectorAll("figure.fig").forEach((f) => io.observe(f));
  function replay(el) { if (typeof el === "string") el = $(el); if (!el.classList.contains("seen")) return; el.classList.remove("seen"); void el.offsetWidth; el.classList.add("seen"); }

  // seg(el, options [[value, label]], value, onChange): a segmented choice.
  function seg(el, options, value, onChange) {
    if (typeof el === "string") el = $(el);
    el.classList.add("seg");
    el.setAttribute("role", "group");
    el.innerHTML = options.map(([v, l]) => `<button type="button" data-v="${esc(v)}" aria-pressed="${v === value}">${l}</button>`).join("");
    el.querySelectorAll("button").forEach((b) => b.addEventListener("click", () => {
      el.querySelectorAll("button").forEach((x) => x.setAttribute("aria-pressed", String(x === b)));
      onChange(b.dataset.v);
    }));
    return el;
  }

  /* ------------------------------------------------------------ the contents rail */
  const secs = [...document.querySelectorAll("section.sec[data-sec]")];
  const toc = $("toc");
  toc.innerHTML = secs.map((s, i) => {
    const figs = [...s.querySelectorAll("figure.fig[data-fig]")];
    return `<li data-s="${s.id}"><a href="#${s.id}"><span class="tn">${i === 0 ? "" : i}</span><span>${esc(s.dataset.sec)}</span></a>`
      + (figs.length > 1 ? `<ol class="figs">${figs.map((f) => `<li><a href="#${f.id}" data-f="${f.id}">${f.dataset.no}</a></li>`).join("")}</ol>` : "") + `</li>`;
  }).join("") + `<span class="toc-ink" aria-hidden="true"></span>`;
  const ink = toc.querySelector(".toc-ink");
  let curSec = null, curFig = null;
  function markSec(id) {
    if (id === curSec) return;
    curSec = id;
    toc.querySelectorAll(":scope > li").forEach((li) => {
      const on = li.dataset.s === id;
      li.classList.toggle("open", on);
      li.querySelector(":scope > a").setAttribute("aria-current", String(on));
    });
    requestAnimationFrame(placeInk);
    // On a phone the contents are one scrolling row: keep the current section in it.
    const a = toc.querySelector(':scope > li > a[aria-current="true"]');
    if (a && toc.scrollWidth > toc.clientWidth) toc.scrollTo({ left: a.offsetLeft - toc.clientWidth / 2 + a.offsetWidth / 2, behavior: still ? "auto" : "smooth" });
  }
  function placeInk() {
    const a = toc.querySelector(':scope > li > a[aria-current="true"]');
    if (!a || !a.offsetHeight) return;
    // transform only: a 100px bar moved and scaled to the current entry
    ink.style.transform = `translateY(${a.offsetTop}px) scaleY(${a.offsetHeight / 100})`;
  }
  function markFig(id) {
    curFig = id;
    toc.querySelectorAll(".figs a").forEach((a) => a.setAttribute("aria-current", String(a.dataset.f === id)));
    document.querySelectorAll("figure.fig[data-fig]").forEach((f) => f.classList.toggle("now", f.id === id));
  }
  // The section and figure whose top is nearest above the reading line are current.
  function spy() {
    const line = innerHeight * 0.32;
    let s = secs[0];
    for (const x of secs) if (x.getBoundingClientRect().top <= line) s = x;
    markSec(s.id);
    const figs = [...document.querySelectorAll("figure.fig[data-fig]")].filter((f) => f.offsetParent);
    let f = null;
    for (const x of figs) if (x.getBoundingClientRect().top <= line) f = x;
    if (f && f.id !== curFig) markFig(f.id);
  }
  addEventListener("scroll", () => requestAnimationFrame(spy), { passive: true });
  addEventListener("resize", () => { placeInk(); spy(); });

  /* ------------------------------------------------------------ presenter keys */
  // Arrow keys step figure to figure; the current one stays lit, the rest recede, until the
  // presenter scrolls by hand or presses Escape.
  function stepFig(d) {
    const figs = [...document.querySelectorAll("figure.fig[data-fig]")].filter((f) => f.offsetParent);
    let next;
    if (document.body.classList.contains("presenting")) {
      const i = figs.findIndex((f) => f.id === curFig);
      next = figs[Math.min(figs.length - 1, Math.max(0, i + d))];
    } else {
      // First press: the next figure below the top of the screen, or the last one above it.
      next = d > 0 ? figs.find((f) => f.getBoundingClientRect().top > 40) : [...figs].reverse().find((f) => f.getBoundingClientRect().top < -40);
    }
    if (!next) return;
    document.body.classList.add("presenting");
    markFig(next.id);
    next.scrollIntoView({ behavior: still ? "auto" : "smooth", block: "start" });
  }
  document.addEventListener("keydown", (e) => {
    if (e.target.matches("input, select, textarea") || e.metaKey || e.ctrlKey || e.altKey) return;
    if (e.key === "ArrowRight" || e.key === "PageDown") { e.preventDefault(); stepFig(1); }
    else if (e.key === "ArrowLeft" || e.key === "PageUp") { e.preventDefault(); stepFig(-1); }
    else if (e.key === "Escape") document.body.classList.remove("presenting");
  });
  addEventListener("wheel", () => document.body.classList.remove("presenting"), { passive: true });
  addEventListener("touchmove", () => document.body.classList.remove("presenting"), { passive: true });

  /* ------------------------------------------------------------ tools */
  const big = $("bigger"), theme = $("theme");
  big.addEventListener("click", () => { big.setAttribute("aria-pressed", String(document.documentElement.classList.toggle("big"))); placeInk(); });
  theme.innerHTML = icon("theme");
  theme.addEventListener("click", () => {
    const r = document.documentElement, dark = r.dataset.theme === "dark" || (!r.dataset.theme && matchMedia("(prefers-color-scheme: dark)").matches);
    r.dataset.theme = dark ? "light" : "dark";
  });

  const sections = [];
  function section(fn) { sections.push(fn); }
  // A table wider than its column says so with a fading edge.
  function edges() { document.querySelectorAll(".tbl").forEach((t) => t.classList.toggle("scrolls", t.scrollWidth > t.clientWidth + 2 && t.scrollLeft + t.clientWidth < t.scrollWidth - 2)); }
  document.addEventListener("scroll", (e) => { if (e.target.classList && e.target.classList.contains("tbl")) edges(); }, true);
  addEventListener("resize", edges);
  new MutationObserver(() => requestAnimationFrame(edges)).observe(document.getElementById("report"), { childList: true, subtree: true });
  function start() {
    for (const fn of sections) { try { fn(); } catch (err) { console.error(err); } }
    spy(); placeInk(); edges();
  }
  return { D, $, still, esc, num, f2, f3, pct, human, cap, dash, wait, range, icon, modelColor, kindColor, wilson, fig, replay, seg, section, start };
})();
