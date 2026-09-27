/* Shared by every demo page (inlined at build time): the header buttons, the
   stepper, one drawn icon family, and numbers that count up when their pane
   comes into view. */
window.Kit = (() => {
  const still = matchMedia("(prefers-reduced-motion: reduce)").matches;

  // One drawn icon family (24-unit grid, 2.2 stroke, round joins) in place of glyphs and emoji.
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
    stop: '<path d="M8.3 3.5h7.4l4.8 4.8v7.4l-4.8 4.8H8.3l-4.8-4.8V8.3z"/><path d="M9.2 9.2l5.6 5.6M14.8 9.2l-5.6 5.6"/>',
    shield: '<path d="M12 3.5l7 2.8v5.6c0 4.3-2.9 7.3-7 8.6-4.1-1.3-7-4.3-7-8.6V6.3z"/><path d="M9 12l2.2 2.2L15.5 10"/>',
    theme: '<circle cx="12" cy="12" r="8"/><path d="M12 4a8 8 0 0 1 0 16z" fill="currentColor"/>',
    arrow: '<path d="M5 12h13.5M13 6.5l5.5 5.5-5.5 5.5"/>',
    flag: '<path d="M6 20.5V4.5M6 5h10.5l-2 3.5 2 3.5H6"/>',
  };
  const icon = (name, cls = "") => `<svg class="ico${cls ? " " + cls : ""}" viewBox="0 0 24 24" aria-hidden="true">${PATHS[name] || ""}</svg>`;
  // <span data-icon="play"></span> in a template becomes the drawn icon.
  function hydrate(root) { (root || document).querySelectorAll("[data-icon]").forEach((el) => { el.outerHTML = icon(el.dataset.icon, el.dataset.cls || ""); }); }


  // <span data-count="440" data-dp="0" data-suffix="×">440</span> counts up from zero.
  function countIn(root) {
    (root || document).querySelectorAll("[data-count]").forEach((el) => {
      const to = Number(el.dataset.count), dp = Number(el.dataset.dp || 0), suf = el.dataset.suffix || "";
      const fmt = (v) => (dp ? v.toFixed(dp) : Math.round(v).toLocaleString("en-US")) + suf;
      if (still || !isFinite(to)) { el.textContent = fmt(to); return; }
      const t0 = performance.now(), dur = 900;
      const tick = (t) => {
        const k = Math.min(1, (t - t0) / dur), e = 1 - Math.pow(1 - k, 3);
        el.textContent = fmt(to * e);
        if (k < 1) requestAnimationFrame(tick);
      };
      requestAnimationFrame(tick);
    });
  }
  const count = (v, dp = 0, suffix = "") => `<span data-count="${v}" data-dp="${dp}" data-suffix="${suffix}">${dp ? Number(v).toFixed(dp) : Number(v).toLocaleString("en-US")}${suffix}</span>`;

  // Tabs as steps: number keys and arrows move, the hash remembers, each pane animates on entry.
  function steps(n, onEnter) {
    const btns = [...document.querySelectorAll("#steps button")];
    btns.forEach((b) => {
      b.setAttribute("aria-controls", "pane-" + b.dataset.step);
      const pane = document.getElementById("pane-" + b.dataset.step);
      if (pane) { pane.setAttribute("role", "tabpanel"); pane.setAttribute("tabindex", "-1"); }
    });
    let now = 1;
    function go(k) {
      k = Number(k);
      if (k < 1 || k > n) return;
      btns.forEach((b) => {
        const on = Number(b.dataset.step) === k;
        b.setAttribute("aria-selected", String(on));
        b.tabIndex = on ? 0 : -1;
        if (Number(b.dataset.step) === now && !on) b.classList.add("seen");
      });
      for (let i = 1; i <= n; i++) document.getElementById("pane-" + i).hidden = i !== k;
      now = k;
      try { history.replaceState(null, "", "#" + k); } catch (e) {}
      const pane = document.getElementById("pane-" + k);
      countIn(pane);
      if (onEnter) onEnter(k, pane);
    }
    btns.forEach((b) => b.addEventListener("click", () => go(b.dataset.step)));
    document.addEventListener("keydown", (e) => {
      if (e.target.matches("input, select, textarea") || e.metaKey || e.ctrlKey || e.altKey) return;
      if (new RegExp(`^[1-${n}]$`).test(e.key)) go(e.key);
      else if (e.key === "ArrowRight") go(now + 1);
      else if (e.key === "ArrowLeft") go(now - 1);
    });
    const h = Number(location.hash.replace("#", ""));
    return { go, now: () => now, start: () => go(h >= 1 && h <= n ? h : 1) };
  }

  function tools() {
    const big = document.getElementById("bigger"), theme = document.getElementById("theme");
    if (big) {
      big.setAttribute("aria-label", "Larger text for a projector");
      big.setAttribute("aria-pressed", "false");
      big.addEventListener("click", () => big.setAttribute("aria-pressed", String(document.documentElement.classList.toggle("big"))));
    }
    if (theme) {
      theme.innerHTML = icon("theme");
      theme.setAttribute("aria-label", "Switch light or dark");
      theme.addEventListener("click", () => {
        const r = document.documentElement, dark = r.dataset.theme === "dark" || (!r.dataset.theme && matchMedia("(prefers-color-scheme: dark)").matches);
        r.dataset.theme = dark ? "light" : "dark";
      });
    }
  }
  tools();
  hydrate();
  return { countIn, count, steps, still, icon, hydrate };
})();
