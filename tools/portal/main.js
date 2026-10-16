/* The controller: one step per station. Space (or the yellow key) sends the trains to the next
   station; the arrows step back and on; the header switches the model and what it was told. */
(() => {
  const { D, $, esc, f3 } = PT;
  const M = PT.map;
  const T = Object.fromEntries(D.techniques.map((t) => [t.id, t]));
  const MODELS = [];
  for (const id of D.headline) { const t = T[id]; if (t && t.model && !MODELS.includes(t.model)) MODELS.push(t.model); }
  for (const t of D.techniques) if (t.model && !MODELS.includes(t.model)) MODELS.push(t.model);
  const BRIEF = [["unaided", "Task + register"], ["informed", "The Act"], ["policy", "The policy"]];
  const state = { model: MODELS.includes("claude-opus-5-5") ? "claude-opus-5-5" : MODELS[0], briefing: "policy" };
  let step = 0, p = 0, playing = false, last = 0, lines = [];
  const LAST = M.STATIONS.length - 1;

  const ids = () => ({ A: "ours", B: `${state.model}|${state.briefing}`, C: "base" });
  const short = (m) => m.replace(/^(claude|gemini)-/, "");

  /* ------------------------------------------------------------ header */
  function header() {
    $("sub").textContent = `Recorded run, ${PT.shortDate(D.meta.generated)} ${String(D.meta.generated || "").slice(0, 4)}`;
    $("lines").innerHTML = `<span class="badge a"><span class="k">A</span>Ours</span>`
      + `<span class="badge b"><span class="k">B</span><select id="model" aria-label="Line B: the AI model">${MODELS.map((m) => `<option value="${esc(m)}"${m === state.model ? " selected" : ""}>${esc(PT.modelName(m))}</option>`).join("")}</select></span>`
      + `<span class="badge c"><span class="k">C</span>Baseline</span>`;
    $("model").addEventListener("change", (e) => setLine({ model: e.target.value }));
    $("brief").innerHTML = BRIEF.map(([k, l], i) => `<button role="radio" aria-checked="${k === state.briefing}" data-b="${k}" title="Key ${i + 1}">${esc(l)}</button>`).join("");
    $("brief").querySelectorAll("button").forEach((b) => b.addEventListener("click", () => setLine({ briefing: b.dataset.b })));
  }
  function setLine(patch) {
    Object.assign(state, patch);
    $("brief").querySelectorAll("button").forEach((b) => b.setAttribute("aria-checked", String(b.dataset.b === state.briefing)));
    $("model").value = state.model;
    build();
    M.flash("B");
  }

  /* ------------------------------------------------------------ the passenger ticket: one patient, the job about them */
  const JOB = (D.tasks.find((t) => t.single) || D.tasks[0]).id;
  function ticketRows() {
    const cell = (slot, fn) => { const id = ids()[slot]; return fn((D.ledger[id] || {})[JOB] || {}, D.export[id], T[id]); };
    const v = (slot, fn) => { const [val, bad] = cell(slot, fn); return `<span class="v ${slot.toLowerCase()}${bad ? " bad" : ""}" data-v="${esc(val)}">\u2014</span>`; };
    const all = (fn) => ["A", "B", "C"].map((s) => v(s, fn)).join("");
    const fields = (L) => Object.values(L.fields || {}).reduce((n, fs) => n + fs.length, 0);
    return [
      ["Hospital", `<span class="one" data-v="${D.patient.of} patients in the system">\u2014</span>`],
      ["Gate", `<span class="one" data-v="under ${esc(D.meta.authorisation || "authorisation")}">\u2014</span>`],
      ["Acquire", all((L) => { const n = (L.patients || []).length; return [`${n}/${D.patient.of}`, n > 1]; }), "patients read, this job"],
      ["Extract", all((L) => [String(fields(L)), false]), "fields taken, this job"],
      ["Score", all((L, ex, t) => [t ? f3(t.per_task[JOB]) : "—", t && t.per_task[JOB] < 0.9])],
      ["Export", all((L, ex) => { if (!ex) return ["—", false]; return ex.leaked > 0 ? ["raw", true] : /PSN-/.test(ex.pid) ? ["token", false] : ["no id", false]; })],
      ["Erased", all((L, ex) => ex && ex.retention ? [PT.shortDate(ex.erase_after), false] : ["never", true])],
    ];
  }
  function ticket() {
    $("ticket").innerHTML = `<div class="tk"><div class="tk-h"><div class="tk-id">${esc(D.patient.mrn)}</div><div class="tk-job">${esc(JOB.replace(/-/g, " ").replace(/^./, (c) => c.toUpperCase()))} job</div><div class="tk-who">${esc(D.patient.name)} \u00b7 the patient this job is about</div></div>`
      + `<div class="tk-band" aria-hidden="true"><i class="a"></i><i class="b"></i><i class="c"></i></div>`
      + `<div class="tk-cols"><span>Station</span>${["A", "B", "C"].map((s) => `<span class="rdl ${s.toLowerCase()}" title="${esc(s === "A" ? "Ours" : s === "B" ? PT.modelName(state.model) : "Baseline")}">${s}</span>`).join("")}</div>`
      + `<ol class="tk-rows">${ticketRows().map(([n, cells, hint], k) => `<li data-k="${k}"${hint ? ` title="${esc(hint)}"` : ""}><span class="st"><i class="hole" aria-hidden="true"></i>${esc(n)}</span>${cells}</li>`).join("")}</ol>`
      + `<div class="tk-perf" aria-hidden="true"></div>`
      + `<div class="tk-stub"><div class="zones">${[1, 2, 3].map((z) => `<span class="zs z${z}" data-z="${z}">${z}</span>`).join("")}</div><div class="valid"><span>Zones travelled</span><b id="tk-valid">\u2014</b></div></div></div>`
      + `<p class="tk-note">Masked record number and name; every figure is the recorded run's. The map counts all four jobs, this ticket the one about this patient.</p>`;
    ticketState();
  }
  function ticketState() {
    $("ticket").querySelectorAll(".tk-rows li").forEach((li) => {
      const k = Number(li.dataset.k), on = k <= step;
      li.classList.toggle("on", on);
      li.classList.toggle("cur", k === step && step > 0);
      li.querySelectorAll("[data-v]").forEach((el, i) => {
        const was = el.classList.contains("shown");
        el.textContent = on ? el.dataset.v : "\u2014"; el.classList.toggle("shown", on);
        if (on && !was && !PT.still()) { el.style.animationDelay = `${i * 70}ms`; el.classList.remove("flip"); void el.offsetWidth; el.classList.add("flip"); }
      });
    });
    const zone = step >= 5 ? 3 : step >= 2 ? 2 : 1;
    $("ticket").querySelectorAll(".zs").forEach((z) => z.classList.toggle("punched", Number(z.dataset.z) <= zone && step > 0));
    const v = $("tk-valid");
    if (v) v.textContent = step === 0 ? "\u2014" : `1\u2013${zone}`;
  }

  /* ------------------------------------------------------------ the route strip */
  const ICON = {
    back: '<svg viewBox="0 0 16 16"><path d="M10.5 2.5L4.5 8l6 5.5z"/></svg>',
    next: '<svg viewBox="0 0 16 16"><path d="M5.5 2.5l6 5.5-6 5.5z"/></svg>',
    home: '<svg viewBox="0 0 16 16"><path d="M3 3h2.5v10H3zM13 3v10L6.5 8z"/></svg>',
  };
  function route() {
    $("route").innerHTML = `<div class="keys"><button id="k-home" aria-label="Back to the start" title="Home">${ICON.home}</button><button id="k-back" aria-label="Previous station" title="Left arrow">${ICON.back}</button>`
      + `<button class="go" id="k-go" aria-label="Next station">${ICON.next}<span id="go-t">Start</span><kbd>Space</kbd></button></div>`
      + `<div class="strip" id="strip"><span class="fill" id="strip-fill"></span>${M.STATIONS.map((s, k) => `<button data-k="${k}" aria-label="${esc(s.name)}"><i></i><span>${esc(s.name)}</span></button>`).join("")}</div>`;
    $("k-home").onclick = () => jump(0);
    $("k-back").onclick = () => jump(step - 1);
    $("k-go").onclick = next;
    $("strip").querySelectorAll("button").forEach((b) => b.addEventListener("click", () => jump(Number(b.dataset.k))));
  }
  function routeState() {
    const bs = [...$("strip").querySelectorAll("button")];
    bs.forEach((b, k) => { b.classList.toggle("done", k < step); b.classList.toggle("cur", k === step); });
    const a = bs[0], z = bs[step], e = bs[bs.length - 1];
    if (a && z && e) {
      const span = e.offsetLeft + e.offsetWidth / 2 - a.offsetLeft - a.offsetWidth / 2;
      const fill = $("strip-fill");
      fill.style.left = `${a.offsetLeft + a.offsetWidth / 2}px`;
      fill.style.width = `${span}px`;
      fill.style.transform = `scaleX(${span ? (z.offsetLeft + z.offsetWidth / 2 - a.offsetLeft - a.offsetWidth / 2) / span : 0})`;
    }
    $("go-t").textContent = step === 0 ? "Start" : step >= LAST ? "Again" : "Next";
  }

  /* ------------------------------------------------------------ stepping */
  let first = true;
  function build() {
    lines = [["A", ids().A], ["B", ids().B], ["C", ids().C]].map(([s, id]) => M.lineData(s, id));
    M.build(lines, first);
    first = false;
    ticket();
    M.draw(step, playing ? p : M.duration(step), false);
  }
  /* The run's state, as a deploy page shows it: ready, running to a station, at a station, complete. */
  function status() {
    const el = $("status"); if (!el) return;
    const name = M.STATIONS[step].name;
    const [cls, words] = playing ? ["run", `Running to ${name}`] : step === 0 ? ["ready", "Ready"] : step === LAST ? ["done", "Run complete"] : ["at", `At ${name}`];
    el.className = `status ${cls}`;
    el.querySelector("span").textContent = words;
  }
  function next() {
    if (playing) { playing = false; p = M.duration(step); M.draw(step, p, false); status(); return; }    // a second press lands the step
    if (step >= LAST) { jump(0); return; }
    step += 1; p = 0; playing = !PT.still(); last = performance.now();
    if (!playing) p = M.duration(step);
    M.draw(step, p, playing);
    ticketState(); routeState(); status();
  }
  function jump(k) {
    step = Math.max(0, Math.min(LAST, k)); playing = false; p = M.duration(step);
    M.draw(step, p, false);
    ticketState(); routeState(); status();
  }
  function frame(now) {
    if (playing) {
      p += Math.min(0.1, (now - last) / 1000); last = now;
      const d = M.duration(step);
      if (p >= d) { p = d; playing = false; }
      M.draw(step, p, true);
      if (!playing) status();
    }
    requestAnimationFrame(frame);
  }
  addEventListener("keydown", (e) => {
    const tag = (e.target.tagName || "").toLowerCase();
    if (tag === "select" && /Arrow/.test(e.key)) return;
    if (e.key === " " && tag !== "button") { e.preventDefault(); next(); }
    else if (e.key === "ArrowRight" || e.key === "PageDown") { e.preventDefault(); if (playing || step < LAST) next(); }
    else if (e.key === "ArrowLeft" || e.key === "PageUp") { e.preventDefault(); jump(step - 1); }
    else if (e.key === "Home") { e.preventDefault(); jump(0); }
    else if (e.key === "End") { e.preventDefault(); jump(LAST); }
    else if (e.key === "1" || e.key === "2" || e.key === "3") setLine({ briefing: BRIEF[Number(e.key) - 1][0] });
  });
  let rz = null;
  addEventListener("resize", () => { clearTimeout(rz); rz = setTimeout(() => { build(); routeState(); }, 120); });

  PT.app = { jump, next, setLine, get step() { return step; } };
  header(); route(); build(); routeState(); status();
  requestAnimationFrame(frame);
})();
