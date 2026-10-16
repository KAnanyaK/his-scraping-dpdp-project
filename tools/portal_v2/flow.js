/* The Portal v2: the recorded run as a live data flow.
   The hospital is a matrix of patients by fields. For the chosen job, each technique reads cells out
   of it; every value read is a particle that flies into the technique's lane and travels on through
   the rules, the export and the erasure. A particle's colour is its DPDP data category; a red halo is
   a value out of the job's purpose; a white diamond is an identifier that left as a token. The
   presenter steps it: Space / right arrow next, left back, Home / End, 1-3 the briefing, J the job.
   Every number is the recorded one; each lane replays one run end to end. */
(() => {
  "use strict";
  const D = JSON.parse(document.getElementById("flow-data").textContent);
  const $ = (id) => document.getElementById(id);
  const esc = (s) => String(s == null ? "" : s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const clamp = (v, a = 0, b = 1) => Math.max(a, Math.min(b, v));
  const ease = (t) => 1 - Math.pow(1 - t, 3);
  const easeIO = (t) => (t < .5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2);
  const fmt = (n) => Number(n).toLocaleString("en-IN");
  const f3 = (n) => (n == null ? "—" : Number(n).toFixed(3));
  const shortDate = (iso) => new Date(iso + "T00:00:00Z").toLocaleDateString("en-GB", { day: "numeric", month: "short", year: "numeric", timeZone: "UTC" });
  const still = () => matchMedia("(prefers-reduced-motion: reduce)").matches;
  const css = getComputedStyle(document.documentElement);
  const cv = (n) => css.getPropertyValue(n).trim();

  const CAT = { direct_identifier: "Identifier", quasi_identifier: "Quasi-identifier", contact: "Contact", clinical: "Clinical", financial: "Financial", administrative: "Administrative" };
  const CATS = Object.keys(CAT);
  const COL = Object.fromEntries(CATS.map((c) => [c, cv(`--cat-${c}`)]));
  const LANE = { a: cv("--a"), b: cv("--b"), c: cv("--c") };
  const BREACH = cv("--breach"), LIT = cv("--lit");
  const PURPOSE = { care_coordination: "Care coordination", billing_settlement: "Billing settlement", patient_registration: "Patient registration" };
  const BRIEF = [["unaided", "Task + register"], ["informed", "The Act"], ["policy", "The policy"]];
  const BRIEFW = { unaided: "task + register", informed: "told the Act", policy: "told the policy" };
  const STOPS = ["Hospital", "Gate", "Acquire", "Extract", "Score", "Pseudonymise", "Shape", "Export", "Erase"];
  const STRETCH = STOPS.slice(3);                      // a pipe's stretches, one per stop from Extract on
  const [EXTRACT, SCORE, PSEUD, SHAPE, EXPORT, ERASE] = [3, 4, 5, 6, 7, 8];
  const LAST = ERASE;
  const SEG = [0, .24, .40, .55, .70, .85, 1];        // where each stretch starts and ends along a pipe
  const COLS = SEG.slice(1).map((v, k) => `${((v - SEG[k]) * 100).toFixed(2)}%`).join(" ");
  const PAGE_T = 0.045, FLIGHT = 0.75, MOVE = 0.9;   // seconds per page load; a value's flight; a move between stretches
  const modelName = (id) => {
    const m = String(id || "").match(/^claude-([a-z]+)-(\d+)-(\d+)$/);
    if (m) return `${m[1][0].toUpperCase()}${m[1].slice(1)} ${m[2]}.${m[3]}`;
    const g = String(id || "").match(/^gemini-([\d.]+)-(.+)$/);
    if (g) return `Gemini ${g[1]} ${g[2].split("-").map((w) => w[0].toUpperCase() + w.slice(1)).join("-")}`;
    return id;
  };
  const jobName = (id) => id.replace(/-/g, " ").replace(/^./, (c) => c.toUpperCase());

  const state = { job: D.jobs[0].id, model: D.models.includes("claude-opus-5-5") ? "claude-opus-5-5" : D.models[0], briefing: "policy" };
  let step = 0, p = 0, playing = false, last = 0, lanes = [], geo = null, ctx = null, dpr = 1;
  const JOB = () => D.jobs.find((j) => j.id === state.job);

  /* ------------------------------------------------------------ glow sprites */
  const sprites = {};
  function rgba(hex, a) {
    const h = hex.replace("#", ""), n = parseInt(h.length === 3 ? h.replace(/./g, "$&$&") : h, 16);
    return `rgba(${(n >> 16) & 255},${(n >> 8) & 255},${n & 255},${a})`;
  }
  function sprite(color) {
    if (sprites[color]) return sprites[color];
    const c = document.createElement("canvas"); c.width = c.height = 64;
    const g = c.getContext("2d"), r = g.createRadialGradient(32, 32, 0, 32, 32, 32);
    r.addColorStop(0, "rgba(255,255,255,1)"); r.addColorStop(.16, rgba(color, 1)); r.addColorStop(.38, rgba(color, .42)); r.addColorStop(1, rgba(color, 0));
    g.fillStyle = r; g.fillRect(0, 0, 64, 64);
    return (sprites[color] = c);
  }

  /* ------------------------------------------------------------ the lanes for the chosen job */
  function lanesFor() {
    return [["A", "ours"], ["B", `${state.model}|${state.briefing}`], ["C", "base"]].map(([slot, id]) => {
      const L = D.lanes[id], J = L.jobs[state.job], cls = slot.toLowerCase();
      const oos = new Set(J.oos), ps = [];
      for (const r of J.rows) for (const c of J.cols) ps.push({ r, c, cat: D.columns[c].cat, oos: oos.has(c), idf: D.columns[c].cat === "direct_identifier" });
      // where a value sits inside a stretch: grouped by data category, the values out of purpose last
      [...ps.keys()].sort((x, y) => (ps[x].oos - ps[y].oos) || (CATS.indexOf(ps[x].cat) - CATS.indexOf(ps[y].cat)) || (ps[x].c - ps[y].c) || (ps[x].r - ps[y].r))
        .forEach((i, rank) => { ps[i].slot = rank; });
      // shaping groups the values by module: each module is shaped into its own messages
      const mods = [];
      D.modules.forEach((m) => {
        const items = ps.map((q, i) => i).filter((i) => ps[i].c >= m.start && ps[i].c < m.start + m.count)
          .sort((x, y) => (CATS.indexOf(ps[x].cat) - CATS.indexOf(ps[y].cat)) || (ps[x].c - ps[y].c) || (ps[x].r - ps[y].r));
        if (!items.length) return;
        items.forEach((i, w) => { ps[i].mod = mods.length; ps[i].within = w; });
        mods.push({ n: items.length, short: m.short });
      });
      return { slot, cls, id, L, J, ps, mods, E: Math.max(1, J.pages * PAGE_T), ends: !!J.erase,
               tokens: !!(J.pseud && J.pseud.on), gen: !!(J.pseud && J.pseud.generalised) };
    });
  }

  /* ------------------------------------------------------------ the header, the job bar */
  function header() {
    $("model").innerHTML = D.models.map((m) => `<option value="${esc(m)}"${m === state.model ? " selected" : ""}>${esc(modelName(m))}</option>`).join("");
    $("model").onchange = (e) => switchTo({ model: e.target.value });
    $("brief").innerHTML = BRIEF.map(([k, l], i) => `<button role="radio" aria-checked="${k === state.briefing}" data-b="${k}" data-tip="What the AI model on lane B was told (key ${i + 1})">${esc(l)}</button>`).join("");
    $("brief").querySelectorAll("button").forEach((b) => b.addEventListener("click", () => switchTo({ briefing: b.dataset.b })));
    $("jobs").innerHTML = D.jobs.map((j) => `<button role="tab" aria-selected="${j.id === state.job}" data-j="${j.id}" data-tip="${esc(j.description)}">${esc(jobName(j.id))}${j.trap ? '<span class="trapflag" aria-label="a trap"></span>' : ""}</button>`).join("");
    $("jobs").querySelectorAll("button").forEach((b) => b.addEventListener("click", () => switchTo({ job: b.dataset.j })));
    $("hosp-sub").textContent = `${D.patient.of} patients · ${D.columns.length} fields · ${fmt(D.patient.of * D.columns.length)} values`;
    $("disc").textContent = `${D.modules.length} modules found in ${D.discover} page loads`;
    $("disc").dataset.tip = "The crawler signs in, reads the home page and finds each module by the fields on its pages, never by its name";
    $("checks").innerHTML = [["TLS observed", D.meta.tls ? "TLS was observed on the browser's session" : ""], ["robots.txt", "robots.txt was read: it says Disallow: /, and the hospital's authorisation lets the crawler in"],
      ["Authorised", `Authorisation reference ${D.meta.authorisation || ""}, logged with every run`], ["Signed in", `Service account ${D.meta.account}: a username and a password, nothing else`]]
      .map(([t, tip]) => `<li data-tip="${esc(tip)}"><svg viewBox="0 0 12 12"><path d="M2.5 6.4l2.3 2.3 4.7-5.2"/></svg>${esc(t)}</li>`).join("");
    $("mods").innerHTML = D.modules.map((m) => `<span data-tip="${esc(m.title)}: ${m.count} fields">${esc(m.short)}</span>`).join("");
  }
  function purpose() {
    const j = JOB();
    $("purpose").innerHTML = `<span>Purpose <b>${esc(PURPOSE[j.purpose] || j.purpose)}</b></span><span class="cats">${CATS.map((c) =>
      `<span class="cat${j.allowed.includes(c) ? "" : " no"}" style="color:${COL[c]}" data-tip="${esc(CAT[c])}: ${j.allowed.includes(c) ? "allowed for this purpose" : "out of this purpose"}"><i style="background:${COL[c]}"></i><span style="color:var(--${j.allowed.includes(c) ? "text-2" : "text-3"})">${esc(CAT[c])}</span></span>`).join("")}</span>`;
  }

  /* ------------------------------------------------------------ the lanes, the person */
  function laneHTML(l) {
    const t = l.L, name = l.slot === "A" ? "Ours" : l.slot === "C" ? "Baseline" : modelName(t.model);
    const sub = l.slot === "A" ? "the reference: the job's expert field list" : l.slot === "C" ? "takes everything it can reach"
      : `${BRIEFW[t.briefing]} · run 1 of ${t.samples}`;
    return `<div class="lane ${l.cls}" id="lane-${l.cls}">
      <div class="lh" style="grid-row:1"><span class="rd ${l.cls}">${l.slot}</span><b class="ln">${esc(name)}</b><span class="ls">${esc(sub)}</span>
        <div class="kpis">
          <div class="kpi" data-tip="Pages the browser loaded for this job, as recorded"><span class="kv" data-k="pages">0</span><span class="kl">page loads</span></div>
          <div class="kpi" data-tip="${l.J.named ? "Patients whose rows it read" : "Rows it read without the record number: it cannot say whose they were"}"><span class="kv" data-k="pat">0</span><span class="kl">${l.J.named ? "patients" : "rows, unnamed"}</span></div>
          <div class="kpi" data-tip="Patient \u00d7 field values it read"><span class="kv" data-k="val">0</span><span class="kl">values read</span></div>
        </div></div>
      <div class="pipe" style="grid-row:2"><span class="spot"></span>${SEG.slice(1, -1).map((s) => `<i style="left:${s * 100}%"></i>`).join("")}</div>
      <div class="ro" style="grid-row:3;grid-template-columns:${COLS}">${STRETCH.map((_, k) => `<div data-r="${k + EXTRACT}">${readout(l, k + EXTRACT)}</div>`).join("")}</div>
    </div>`;
  }
  function readout(l, k) {
    const J = l.J, t = l.L, j = JOB();
    if (k === 3) {
      const oos = J.oos.length * J.rows.length, tr = t.traps[state.job];
      // on a trap job, the trap over every recorded run: held, or taken
      const held = tr && tr[0] === tr[1];
      const trap = !j.trap || !tr ? "" : `<div class="${held ? "good" : "bad"}" data-tip="${esc(j.trap)}">${tr[1] > 1 ? `trap ${held ? "held" : "taken"} in ${held ? tr[0] : tr[1] - tr[0]} of ${tr[1]} runs` : held ? "trap held" : "trap taken"}</div>`;
      return `<div><span class="big">${fmt(l.ps.length)}</span> <span class="sub">values · ${J.hit}/${J.needed} needed</span></div>`
        + (oos ? `<div class="bad" data-tip="Values whose data category is outside this job's purpose">${fmt(oos)} out of purpose</div>`
               : `<div class="sub">all within purpose</div>`) + trap;
    }
    if (k === 4) {
      const failed = D.rule_ids.filter((r) => J.rules[r] && J.rules[r][0] !== "pass");
      const lamps = D.rule_ids.map((r, i) => `<i class="${failed.includes(r) ? "no" : ""}" style="transition-delay:${120 + i * 70}ms" data-tip="${esc(r)} ${esc(D.rule_titles[r] || "")}: ${failed.includes(r) ? "broken" : "held"}"></i>`).join("");
      let extra = failed.length ? `<div class="bad">${failed.length === D.rule_ids.length ? "every rule broken" : esc(failed.join(", ")) + " broken"}</div>` : `<div class="good">7 of 7 rules held</div>`;
      if (t.samples > 1 && t.mean[state.job] != null) extra += `<div class="sub" data-tip="The mean over all ${t.samples} recorded runs; this lane replays the first">${t.samples} runs: ${f3(t.mean[state.job])}</div>`;
      return `<div><span class="big">${f3(J.score)}</span><span class="lamps">${lamps}</span></div>${extra}`;
    }
    if (k === PSEUD) {
      const ps = J.pseud || {}, ids = J.export.identifiers;
      if (!ps.on) return `<div class="bad" data-tip="Identifiers stay as they were read">left raw</div><div class="sub">${fmt(ids)} identifier${ids === 1 ? "" : "s"}</div>`;
      const k2 = ps.k == null ? `<div class="sub" data-tip="No quasi-identifier left in this export">no quasi-ids</div>`
        : `<div class="sub" data-tip="Date of birth to its year, PIN code to 3 digits; k = ${ps.k}, the smallest group of exported rows sharing them">generalised</div>`;
      return `<div><span class="big">${fmt(ids)}</span> <span class="sub">\u2192 token${ids === 1 ? "" : "s"}</span></div>${k2}`;
    }
    if (k === SHAPE) {
      const sh = J.shape || {};
      return `<div data-tip="Each record shaped into an HL7 v2 message, per module"><span class="big">${fmt(sh.hl7)}</span> <span class="sub">HL7 v2</span></div><div class="sub" data-tip="FHIR resources for the same records">${fmt(sh.fhir)} FHIR</div>`;
    }
    if (k === EXPORT) {
      const e = J.export;
      const out = e.leaked ? `<div class="bad">${fmt(e.leaked)} raw id${e.leaked === 1 ? "" : "s"} out</div>` : `<div class="good">no raw id out</div>`;
      if (e.kind === "tok") return `<div><span class="chip tok" data-tok="${esc(e.token.slice(0, 8))}\u2026" data-tip="${esc(e.token)}: identifiers leave as keyed tokens; the key stays with the hospital">${esc(e.token.slice(0, 8))}\u2026</span></div>${out}`;
      if (e.kind === "raw") return `<div><span class="chip raw" data-tip="The raw record number leaves the hospital">${esc(D.patient.mrn)}</span></div>${out}`;
      return `<div><span class="chip none">no identifier</span></div>${out}`;
    }
    if (J.erase) return `<div><span class="big date">${esc(shortDate(J.erase))}</span></div><div class="sub">after ${J.retention} days</div>`;
    return `<div class="bad strong">Never erased</div><div class="sub">no erase date</div>`;
  }
  const DASH = '<span class="dash">–</span>';
  function person() {
    const j = JOB(), P = D.patient;
    const rows = lanes.map((l) => {
      const mine = l.J.named && l.J.patients.includes(P.index);
      const others = l.J.rows.length - (mine ? 1 : 0);
      const nm = l.slot === "A" ? "Ours" : l.slot === "C" ? "Baseline" : modelName(l.L.model);
      const e = l.J.export;
      return `<tr data-l="${l.cls}"><td><span class="who"><span class="rd ${l.cls}">${l.slot}</span><span class="nm">${esc(nm)}</span></span></td>`
        + `<td data-s="3" data-v="${l.J.named ? (mine ? l.J.cols.length : 0) : "?"}">${DASH}</td>`
        + `<td data-s="3" data-v="${fmt(others)}">${DASH}</td>`
        + `<td data-s="7" data-v="${e.kind === "tok" ? "token" : e.kind === "raw" ? "raw id" : "none"}" class="${e.kind === "raw" ? "bad" : e.kind === "tok" ? "good" : ""}">${DASH}</td>`
        + `<td data-s="8" data-v="${l.J.erase ? esc(shortDate(l.J.erase)) : "never"}" class="${l.J.erase ? "" : "bad"}">${DASH}</td></tr>`;
    }).join("");
    $("person").innerHTML = `<div class="ph"><span class="pid">${esc(P.mrn)}</span><span class="pn">${esc(P.name)} \u00b7 ${j.single ? "the patient this job is about" : `one of the ${P.of} patients this job covers`}</span></div>`
      + `<table><thead><tr><th>One patient</th><th data-tip="This patient's values it read">Theirs</th><th data-tip="Other patients whose rows it read">Others</th><th data-tip="How the identifier leaves the hospital">Out as</th><th>Kept until</th></tr></thead><tbody>${rows}</tbody></table>`;
  }

  function build() {
    lanes = lanesFor();
    $("lanes").innerHTML = `<div class="stops" id="stops" style="grid-template-columns:${COLS}">${STRETCH.map((s) => `<span>${s}</span>`).join("")}</div>` + lanes.map(laneHTML).join("");
    lanes.forEach((l) => {
      l.el = $(`lane-${l.cls}`);
      l.kv = Object.fromEntries([...l.el.querySelectorAll("[data-k]")].map((e) => [e.dataset.k, e]));
      l.ro = [...l.el.querySelectorAll(".ro > div")];
      l.spot = l.el.querySelector(".spot");
      l.divs = [...l.el.querySelectorAll(".pipe i")];
      l.shown = {};
    });
    purpose(); person();
    measure();
  }

  /* ------------------------------------------------------------ geometry, in canvas pixels */
  function measure() {
    const stage = $("stage"), fx = $("fx"), st = stage.getBoundingClientRect();
    dpr = Math.min(2, window.devicePixelRatio || 1);
    fx.width = Math.round(st.width * dpr); fx.height = Math.round(st.height * dpr);
    ctx = fx.getContext("2d");
    const m = $("matrix").getBoundingClientRect(), of = D.patient.of, n = D.columns.length, gapM = 7;
    const pitch = Math.min((m.width - (D.modules.length - 1) * gapM) / n, m.height / of);
    const cell = pitch * 0.74, x0 = m.left - st.left, y0 = m.top - st.top;
    const colX = [];
    let x = x0;
    D.modules.forEach((mod) => { for (let i = 0; i < mod.count; i++) { colX.push(x); x += pitch; } x += gapM; });
    const rowY = Array.from({ length: of }, (_, r) => y0 + r * pitch);
    // the module labels sit over their columns
    [...$("mods").children].forEach((s, k) => { const mod = D.modules[k]; s.style.left = `${colX[mod.start] - x0}px`; s.style.width = `${colX[mod.start + mod.count - 1] + cell - colX[mod.start]}px`; });
    geo = { st, colX, rowY, cell, pitch, mx0: x0, mx1: x - gapM, my0: y0, my1: y0 + of * pitch };
    // every value crosses the gate at its lock, level with the middle of the hospital
    const bar = $("gate").querySelector(".gbar").getBoundingClientRect(), gt = $("gate").getBoundingClientRect();
    const beside = gt.top < m.bottom && gt.bottom > m.top;
    const ly = beside ? (geo.my0 + geo.my1) / 2 : bar.top - st.top + bar.height / 2;
    $("gate").querySelector(".glock").style.top = `${ly - (bar.top - st.top)}px`;
    geo.lock = [bar.left - st.left + bar.width / 2, ly];
    void gt;
    lanes.forEach((l) => {
      const r = l.el.querySelector(".pipe").getBoundingClientRect();
      const pipe = { x: r.left - st.left, y: r.top - st.top, w: r.width, h: r.height };
      l.pipe = pipe;
      const box = (k) => ({ x0: pipe.x + SEG[k] * pipe.w + 9, x1: pipe.x + SEG[k + 1] * pipe.w - 9, y0: pipe.y + 9, y1: pipe.y + pipe.h - 9 });
      // the first three stretches group the values by category (the out-of-purpose ones last);
      // from Shape on they sit by module, so after shaping they only ever glide
      l.boxes = STRETCH.map((_, k) => box(k));
      l.slots = STRETCH.map((_, k) => {
        if (k >= SHAPE - EXTRACT) return modular(l, box(k));
        const g = grid(l.ps.length, box(k));
        return { r: g.r, pos: (q) => g.at(q.slot) };
      });
      if (!l.ends) l.mini = mini(l, box(ERASE - EXTRACT));
    });
  }
  /* What is never erased stays as it was taken: a miniature of the hospital, row by row, field by field. */
  function mini(l, b) {
    const nc = Math.max(1, l.J.cols.length), nr = Math.max(1, l.J.rows.length);
    const pt = Math.min((b.x1 - b.x0) / nc, (b.y1 - b.y0) / nr, 9);
    const ox = b.x0 + (b.x1 - b.x0 - nc * pt) / 2, oy = b.y0 + (b.y1 - b.y0 - nr * pt) / 2;
    return { r: clamp(pt * 0.4, 1, 3.6), pt, frame: [ox - 4, oy - 4, nc * pt + 8, nr * pt + 8], at: (i) => [ox + (i % nc) * pt + pt / 2, oy + Math.floor(i / nc) * pt + pt / 2] };
  }
  /* Values grouped by module, each module a block of its own, side by side: what shaping makes of them. */
  function modular(l, b) {
    const w = b.x1 - b.x0, h = b.y1 - b.y0, G = l.mods.length;
    if (!G) return { r: 2, frames: [], pos: () => [b.x0, b.y0] };
    let pt = 10, rows = 1, widths = [], gap = 6;
    for (let guard = 0; guard < 80; guard++) {
      rows = Math.max(1, Math.floor(h / pt)); gap = Math.max(4, pt * 0.9);
      widths = l.mods.map((m) => Math.ceil(m.n / Math.min(rows, m.n)) * pt);
      if (widths.reduce((a, v) => a + v, 0) + gap * (G - 1) <= w || pt < 1.4) break;
      pt *= 0.95;
    }
    const total = widths.reduce((a, v) => a + v, 0) + gap * (G - 1), cy = (b.y0 + b.y1) / 2;
    let x = b.x0 + (w - total) / 2;
    const blocks = l.mods.map((m, k) => {
      const used = Math.min(rows, m.n), bx = x;
      x += widths[k] + gap;
      return { x: bx, y: cy - (used * pt) / 2, used, w: widths[k], h: used * pt };
    });
    const pad = Math.max(2, pt * 0.45);
    return {
      r: clamp(pt * 0.34, 1, 3.6),
      frames: blocks.map((k) => [k.x - pad, k.y - pad, k.w + pad * 2, k.h + pad * 2]),
      file: [blocks[0].x - pad * 2.2, Math.min(...blocks.map((k) => k.y)) - pad * 2.2, total + pad * 4.4, Math.max(...blocks.map((k) => k.h)) + pad * 4.4],
      pos: (q) => { const k = blocks[q.mod]; return [k.x + Math.floor(q.within / k.used) * pt + pt / 2, k.y + (q.within % k.used) * pt + pt / 2]; },
    };
  }
  /* n values packed into a box, as evenly as they go */
  function grid(n, b) {
    const w = b.x1 - b.x0, h = b.y1 - b.y0;
    let pt = Math.min(13, Math.sqrt((w * h) / Math.max(1, n))), cols, rows;
    for (let guard = 0; guard < 60; guard++) {
      cols = Math.max(1, Math.floor(w / pt)); rows = Math.max(1, Math.floor(h / pt));
      if (cols * rows >= n || pt < 2) break;
      pt *= 0.95;
    }
    const r = clamp(pt * 0.34, 1.25, 4.2);
    if (n <= cols) {                                  // a few values: one even row
      const ox = b.x0 + (w - n * pt) / 2 + pt / 2, oy = (b.y0 + b.y1) / 2;
      return { r, at: (i) => [ox + i * pt, oy] };
    }
    const used = Math.min(rows, n), wide = Math.ceil(n / used);   // many: filled column by column
    const ox = b.x0 + (w - wide * pt) / 2 + pt / 2, oy = b.y0 + (h - used * pt) / 2 + pt / 2;
    return { r, at: (i) => [ox + Math.floor(i / used) * pt, oy + (i % used) * pt] };
  }

  /* ------------------------------------------------------------ timing */
  const SETTLE = 0.65, DISSOLVE = 0.7;                // at Erase: a kept block settling, an erased one dissolving
  function duration(k) {
    if (k <= 0) return 0;
    if (k === 1) return 1.35;
    if (k === 2) return 1.5;
    if (k === EXTRACT) return Math.max(...lanes.map((l) => l.E)) + FLIGHT + 0.25;
    if (k === SHAPE) return MOVE + 1.0;
    return k === ERASE ? MOVE + 0.5 + Math.max(SETTLE, DISSOLVE) + 0.45 : 1.6;
  }
  const landed = (l) => (step > EXTRACT ? l.ps.length : step < EXTRACT ? 0 : clamp(Math.floor(((p - FLIGHT) / l.E) * l.ps.length) + 1, 0, l.ps.length));
  const started = (l) => (step > EXTRACT ? l.ps.length : step < EXTRACT ? 0 : clamp(Math.floor((p / l.E) * l.ps.length) + 1, 0, l.ps.length));
  const doneAt = (l, k) => (k === EXTRACT ? l.E + FLIGHT : k === SHAPE ? MOVE + 0.9 : MOVE + 0.5);
  /* how far value i is along the move into this step's stretch; at Shape the values go module by module */
  function moveF(l, i) {
    const q = l.ps[i], n = l.ps.length;
    let d;
    if (step === SHAPE) d = (q.mod / Math.max(1, l.mods.length)) * 0.6 + (q.within / Math.max(1, l.mods[q.mod].n)) * 0.25;
    else {                                             // a block slides as one wave: its leading edge moves first
      const k = step - SCORE, b = l.boxes[k], x = l.slots[k].pos(q)[0];
      d = (1 - (x - b.x0) / Math.max(1, b.x1 - b.x0)) * 0.45;
    }
    return clamp((p - d) / MOVE);
  }
  const reached = (l, k) => step > k || (step === k && p >= doneAt(l, k));

  /* ------------------------------------------------------------ where a value is */
  function where(l, i) {
    const n = l.ps.length, q = l.ps[i], S = l.slots;
    if (step < EXTRACT) return null;
    if (step === EXTRACT) {
      const f = clamp((p - (i / n) * l.E) / FLIGHT);
      if (f <= 0) return null;
      return { ...flight(geo.colX[q.c] + geo.cell / 2, geo.rowY[q.r] + geo.cell / 2, S[0].pos(q), ease(f), l.pipe.x), r: S[0].r + (1 - f) * 0.8, a: 1, f, fly: f < 1 };
    }
    const k = step - SCORE, from = S[k].pos(q), to = S[k + 1].pos(q);
    const f = moveF(l, i), e = easeIO(f);
    let y = from[1] + (to[1] - from[1]) * e, a = 1, r = S[k + 1].r * e + S[k].r * (1 - e);
    if (step === ERASE && l.ends) {                    // erased: it arrives whole, then dissolves where it stands
      const dz = clamp((p - (MOVE + 0.35) - (i / n) * 0.3) / DISSOLVE);
      a = 1 - ease(dz); r *= 1 - 0.5 * dz; y -= 6 * dz;
    }
    return { x: from[0] + (to[0] - from[0]) * e, y, r, a, f, fly: f < 1 };
  }
  /* A value's flight: from its cell to the gate's lock; down (or up) beside the gate to its lane's level; then
     level along into the pipe and on to its place. Near the lanes it only ever travels at pipe height. */
  function flight(x0, y0, [x1, y1], e, mouth) {
    const [gx, gy] = geo.lock, ax = Math.max(gx + 20, Math.min(x1, mouth - 28));
    if (e <= 0.4) {
      const u = e / 0.4, v = 1 - u, cx = (x0 + gx) / 2;
      return { x: v * v * x0 + 2 * v * u * cx + u * u * gx, y: v * v * y0 + 2 * v * u * y0 + u * u * gy };
    }
    if (e <= 0.74) {
      const u = (e - 0.4) / 0.34, v = 1 - u, cx = gx + 14;
      return { x: v * v * gx + 2 * v * u * cx + u * u * ax, y: v * v * gy + 2 * v * u * y1 + u * u * y1 };
    }
    const u = (e - 0.74) / 0.26;
    return { x: ax + (x1 - ax) * u, y: y1 };
  }

  /* ------------------------------------------------------------ drawing */
  function draw(time) {
    if (!ctx || !geo) return;
    const W = ctx.canvas.width, H = ctx.canvas.height;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.clearRect(0, 0, W, H);
    drawMatrix(time);
    ctx.globalCompositeOperation = "lighter";
    lanes.forEach((l) => drawLane(l, time));
    ctx.globalCompositeOperation = "source-over";
  }
  function drawMatrix() {
    const { colX, rowY, cell } = geo, of = D.patient.of, P = D.patient.index;
    const reveal = step > 2 ? 1 : step === 2 ? clamp(p / 1.25) : 0, mw = geo.mx1 - geo.mx0;
    const flash = new Map();
    if (step === EXTRACT) lanes.forEach((l) => {
      const n = l.ps.length;
      for (let i = started(l) - 1; i >= 0; i--) {
        const f = (p - (i / n) * l.E) / FLIGHT;
        if (f > 0.45) break;
        if (f > 0) { const q = l.ps[i]; flash.set(q.r * 1000 + q.c, [1 - f / 0.45, LANE[l.cls]]); }
      }
    });
    const taken = new Map();                     // cell -> which lanes have it: 1 ours, 2 the model, 4 the baseline
    lanes.forEach((l, li) => { const k = landed(l); for (let i = 0; i < k; i++) { const q = l.ps[i], key = q.r * 1000 + q.c; taken.set(key, (taken.get(key) || 0) | (1 << li)); } });
    for (let r = 0; r < of; r++) for (let c = 0; c < colX.length; c++) {
      const x = colX[c], y = rowY[r], col = COL[D.columns[c].cat], got = taken.get(r * 1000 + c) || 0;
      const lit = reveal > 0 && (x - geo.mx0) / mw <= reveal;
      ctx.fillStyle = col; ctx.strokeStyle = col;
      if (got) {                                  // read: the value has left the hospital, its cell is hollow
        ctx.globalAlpha = 0.14; ctx.beginPath(); ctx.roundRect(x, y, cell, cell, 1.6); ctx.fill();
        ctx.globalAlpha = 0.42; ctx.lineWidth = 1; ctx.beginPath(); ctx.roundRect(x + 0.5, y + 0.5, cell - 1, cell - 1, 1.4); ctx.stroke();
        const ring = got & 1 ? LANE.a : got & 2 ? LANE.b : null;
        if (ring) { ctx.globalAlpha = 0.95; ctx.strokeStyle = ring; ctx.lineWidth = 1.3; ctx.beginPath(); ctx.roundRect(x - 0.9, y - 0.9, cell + 1.8, cell + 1.8, 2.2); ctx.stroke(); }
      } else {
        ctx.globalAlpha = lit ? 0.82 : 0.34;
        ctx.beginPath(); ctx.roundRect(x, y, cell, cell, 1.6); ctx.fill();
      }
      const fl = flash.get(r * 1000 + c);
      if (fl) {
        ctx.globalAlpha = fl[0];
        ctx.fillStyle = "#fff"; ctx.beginPath(); ctx.roundRect(x - 1, y - 1, cell + 2, cell + 2, 2); ctx.fill();
        ctx.strokeStyle = fl[1]; ctx.lineWidth = 1.5; ctx.stroke();
      }
    }
    // the patient this card follows
    ctx.globalAlpha = 0.9; ctx.strokeStyle = "#fff"; ctx.lineWidth = 1.2;
    const py = rowY[P] - 2, ph = cell + 4;
    ctx.beginPath(); ctx.roundRect(geo.mx0 - 4, py, geo.mx1 - geo.mx0 + 8, ph, 3); ctx.stroke();
    ctx.fillStyle = "#fff"; ctx.beginPath(); ctx.moveTo(geo.mx0 - 10, py + ph / 2 - 4); ctx.lineTo(geo.mx0 - 5, py + ph / 2); ctx.lineTo(geo.mx0 - 10, py + ph / 2 + 4); ctx.fill();
    // the discovery beam: the crawler reads the pages and finds the modules by their fields
    if (step === 2 && reveal < 1) {
      const bx = geo.mx0 + reveal * mw;
      const g = ctx.createLinearGradient(bx - 46, 0, bx + 6, 0);
      g.addColorStop(0, "rgba(255,216,77,0)"); g.addColorStop(.85, "rgba(255,216,77,.35)"); g.addColorStop(1, "rgba(255,240,180,.9)");
      ctx.globalAlpha = 1; ctx.fillStyle = g; ctx.fillRect(bx - 46, geo.my0 - 10, 52, geo.my1 - geo.my0 + 20);
    }
    ctx.globalAlpha = 1;
  }
  function drawLane(l, time) {
    const n = l.ps.length, e = l.J.export, S = l.slots;
    // a dense lane glows less per value, so hundreds of them read as a mass, not a white-out
    const dens = clamp(Math.sqrt(36 / Math.max(1, n)), 0.2, 1), halo = n > 120 ? 2.3 : 3.4;
    ctx.globalCompositeOperation = "source-over";
    // afterimages: every stretch a value has left keeps it, faint and still, with what happened to it marked
    if (step >= SCORE) {
      const now = step - SCORE;
      for (let i = 0; i < n; i++) {
        const q = l.ps[i], upto = now - (moveF(l, i) > 0 ? 0 : 1);
        for (let k = 0; k <= upto && k < STRETCH.length - 1; k++) ghost(l, q, S[k].pos(q), S[k].r, k, dens);
      }
      // the module envelopes shaping made, and the file that left, as quiet outlines
      const shapedAt = (k) => S[k].frames && (now > k || (now === k && p >= doneAt(l, step)));
      ctx.lineWidth = 1;
      if (shapedAt(SHAPE - EXTRACT)) frames(S[SHAPE - EXTRACT].frames, now === SHAPE - EXTRACT ? 0.32 : 0.14);
      if (shapedAt(EXPORT - EXTRACT)) {
        frames(S[EXPORT - EXTRACT].frames, now === EXPORT - EXTRACT ? 0.22 : 0.1);
        const [fx, fy, fw, fh] = S[EXPORT - EXTRACT].file;
        ctx.globalAlpha = now === EXPORT - EXTRACT ? 0.75 : 0.3; ctx.strokeStyle = e.leaked ? BREACH : "#ffffff"; ctx.lineWidth = 1.2;
        ctx.beginPath(); ctx.roundRect(fx, fy, fw, fh, 5); ctx.stroke();
      }
    }
    // what is never erased settles into a still miniature of the hospital, inside one red frame drawn in
    let settle = 0;
    if (step === ERASE && !l.ends) {
      settle = clamp((p - (MOVE + 0.55)) / SETTLE);
      const M = l.mini;
      if (settle > 0) {
        for (let i = 0; i < n; i++) {
          const [x, y] = M.at(i), q = l.ps[i];
          ctx.globalAlpha = 0.9 * ease(settle); ctx.fillStyle = q.idf && !l.tokens ? BREACH : COL[q.cat];
          ctx.fillRect(x - M.pt * 0.4, y - M.pt * 0.4, M.pt * 0.8, M.pt * 0.8);
        }
        const [fx, fy, fw, fh] = M.frame, per = 2 * (fw + fh);
        ctx.globalAlpha = 1; ctx.strokeStyle = BREACH; ctx.lineWidth = 1.5; ctx.shadowColor = BREACH; ctx.shadowBlur = 10;
        ctx.setLineDash([per * ease(settle), per]);
        ctx.beginPath(); ctx.roundRect(fx, fy, fw, fh, 4); ctx.stroke();
        ctx.setLineDash([]); ctx.shadowBlur = 0;
      }
    }
    ctx.globalCompositeOperation = "lighter";
    for (let i = 0; i < n; i++) {
      const w = where(l, i);
      if (!w) continue;
      const a = w.a * (1 - ease(settle));
      if (a <= 0.01) continue;
      const q = l.ps[i];
      // what the value has become by now: a token, a generalised quasi-identifier, an identifier left raw
      const pz = step > PSEUD || (step === PSEUD && w.f >= 1);
      const token = q.idf && l.tokens && pz, coarse = q.cat === "quasi_identifier" && l.gen && pz;
      const color = token ? "#ffffff" : COL[q.cat];
      // a trail behind a value in flight from the hospital
      if (w.fly && step === EXTRACT && !still()) {
        const prev = flight(geo.colX[q.c] + geo.cell / 2, geo.rowY[q.r] + geo.cell / 2, S[0].pos(q), ease(clamp(w.f - 0.09)), l.pipe.x);
        ctx.globalAlpha = 0.5 * a; ctx.strokeStyle = color; ctx.lineWidth = Math.max(1, w.r * 0.8); ctx.lineCap = "round";
        ctx.beginPath(); ctx.moveTo(prev.x, prev.y); ctx.lineTo(w.x, w.y); ctx.stroke();
      }
      // only a value flying out of the hospital glows at full strength; a whole lane moving together is dimmed by its density
      const bright = w.fly && step === EXTRACT;
      ctx.globalAlpha = a * (bright ? 1 : 0.35 + 0.65 * dens);
      if (token) {                                         // a token: a white diamond
        const sz = w.r * 1.5;
        ctx.globalAlpha = a * 0.4 * (bright ? 1 : 0.5 + 0.5 * dens); ctx.drawImage(sprite("#ffffff"), w.x - sz * 2.6, w.y - sz * 2.6, sz * 5.2, sz * 5.2);
        ctx.globalAlpha = a; ctx.fillStyle = "#fff"; diamond(w.x, w.y, sz);
        continue;
      }
      if (coarse) {                                        // generalised: a ring, coarser than the value it was
        ctx.globalAlpha = a * 0.9; ctx.strokeStyle = color; ctx.lineWidth = Math.max(1, w.r * 0.45);
        ctx.beginPath(); ctx.arc(w.x, w.y, w.r * 1.1, 0, 6.2832); ctx.stroke();
        continue;
      }
      const sz = w.r * (bright ? 3.4 : halo);
      ctx.drawImage(sprite(color), w.x - sz, w.y - sz, sz * 2, sz * 2);
      const bad = (q.oos && (step > EXTRACT || w.f >= 1)) || (q.idf && !l.tokens && pz);
      if (bad) {
        const t = w.r * (n > 120 ? 3.2 : 5.2);
        ctx.globalAlpha = a * dens * (0.6 + (still() ? 0 : 0.2 * Math.sin(time * 4 + i)));
        ctx.drawImage(sprite(BREACH), w.x - t, w.y - t, t * 2, t * 2);
      }
    }
    ctx.globalAlpha = 1;
    ctx.globalCompositeOperation = "source-over";
  }
  function frames(list, alpha) {
    ctx.globalAlpha = alpha; ctx.strokeStyle = "#ffffff";
    for (const [x, y, w, h] of list) { ctx.beginPath(); ctx.roundRect(x, y, w, h, Math.min(4, w / 3)); ctx.stroke(); }
  }
  function diamond(x, y, s) { ctx.beginPath(); ctx.moveTo(x, y - s); ctx.lineTo(x + s, y); ctx.lineTo(x, y + s); ctx.lineTo(x - s, y); ctx.closePath(); ctx.fill(); }
  /* An afterimage: where a value was, at a station it has left. A token stays a dim diamond; a value out of
     purpose, or an identifier that left raw, keeps a red ring. */
  function ghost(l, q, [x, y], r, k, dens) {
    const rr = Math.max(1, r * 0.85), later = k >= PSEUD - EXTRACT;
    if (later && q.idf && l.tokens) { ctx.globalAlpha = 0.32; ctx.fillStyle = "#fff"; diamond(x, y, rr * 1.4); return; }
    if (later && q.cat === "quasi_identifier" && l.gen) {
      ctx.globalAlpha = 0.3; ctx.strokeStyle = COL[q.cat]; ctx.lineWidth = 1;
      ctx.beginPath(); ctx.arc(x, y, rr, 0, 6.2832); ctx.stroke(); return;
    }
    ctx.globalAlpha = 0.16; ctx.fillStyle = COL[q.cat];
    ctx.beginPath(); ctx.arc(x, y, rr, 0, 6.2832); ctx.fill();
    if (q.oos || (later && q.idf && !l.tokens)) {
      ctx.globalAlpha = 0.65 * Math.max(0.5, dens); ctx.strokeStyle = BREACH; ctx.lineWidth = 1;
      ctx.beginPath(); ctx.arc(x, y, rr + 1.4, 0, 6.2832); ctx.stroke();
    }
  }

  /* ------------------------------------------------------------ the page's state at this moment */
  function sync() {
    $("gate").classList.toggle("on", step >= 1);
    $("disc").classList.toggle("on", step > 2 || (step === 2 && p >= 1.25));
    const tickT = step > 1 ? 99 : step === 1 ? p - 0.25 : -1;
    [...$("checks").children].forEach((li, k) => li.classList.toggle("on", tickT >= k * 0.22));
    const reveal = step > 2 ? 1 : step === 2 ? clamp(p / 1.25) : 0;
    [...$("mods").children].forEach((s, k) => {
      const mod = D.modules[k], x = geo.colX[mod.start];
      s.classList.toggle("on", (x - geo.mx0) / (geo.mx1 - geo.mx0) <= reveal + 0.001 && step >= 2);
    });
    [...$("stops").children].forEach((s, k) => { s.classList.toggle("on", step === k + EXTRACT); s.classList.toggle("done", step > k + EXTRACT); });
    lanes.forEach((l) => {
      const f3s = step > EXTRACT ? 1 : step < EXTRACT ? 0 : clamp(p / l.E);
      set(l, "pages", fmt(Math.round(l.J.pages * f3s)));
      set(l, "pat", fmt(Math.ceil(started(l) / Math.max(1, l.J.cols.length))) + (l.J.named ? `/${D.patient.of}` : ""));
      set(l, "val", fmt(landed(l)));
      l.ro.forEach((div, k) => {
        const on = reached(l, k + EXTRACT);
        if (on && !div.classList.contains("on") && k + EXTRACT === EXPORT && playing && !still()) scrambleIn(div);
        div.classList.toggle("on", on);
      });
      const s = step >= EXTRACT ? step - EXTRACT : -1;
      l.spot.classList.toggle("on", s >= 0);
      if (s >= 0) { l.spot.style.left = `${SEG[s] * 100}%`; l.spot.style.width = `${(SEG[s + 1] - SEG[s]) * 100}%`; }
      l.divs.forEach((d, k) => d.classList.toggle("on", step === k + SCORE));
    });
    $("person").querySelectorAll("td[data-s]").forEach((td) => {
      const l = lanes.find((x) => x.cls === td.parentElement.dataset.l), k = Number(td.dataset.s);
      const on = reached(l, k);
      const was = td.dataset.on === "1";
      if (on !== was) {
        td.dataset.on = on ? "1" : "0";
        td.innerHTML = on ? `<span class="v${playing && !still() ? " flip" : ""}">${esc(td.dataset.v)}</span>` : DASH;
      }
    });
  }
  function set(l, k, v) {
    l.kv[k].classList.toggle("nil", step < EXTRACT);
    l.kv[k].classList.toggle("hot", step >= EXTRACT);
    v = step < EXTRACT ? "\u2013" : v;
    if (l.shown[k] === v) return;
    l.shown[k] = v; l.kv[k].textContent = v;
  }
  function scrambleIn(div) {
    const chip = div.querySelector(".chip[data-tok]");
    if (!chip) return;
    const to = chip.dataset.tok, from = D.patient.mrn, HEX = "0123456789abcdef", t0 = performance.now(), dur = 700;
    const tick = (now) => {
      const f = clamp((now - t0) / dur), fixed = Math.floor(f * to.length);
      let s = "";
      for (let k = 0; k < to.length; k++) s += k < fixed ? to[k] : f < 0.25 && k < from.length ? from[k] : HEX[(Math.random() * 16) | 0];
      chip.textContent = f < 1 ? s : to;
      if (f < 1) requestAnimationFrame(tick);
    };
    requestAnimationFrame(tick);
  }

  /* ------------------------------------------------------------ the transport, stepping */
  const ICON = {
    home: '<svg viewBox="0 0 16 16"><path d="M3 3h2.2v10H3zM13 3v10L6.2 8z"/></svg>',
    back: '<svg viewBox="0 0 16 16"><path d="M10.5 2.8L4.5 8l6 5.2z"/></svg>',
    next: '<svg viewBox="0 0 16 16"><path d="M5.5 2.8l6 5.2-6 5.2z"/></svg>',
  };
  function transport() {
    $("transport").innerHTML = `<div class="keys"><button id="k-home" aria-label="Back to the start" data-tip="Home">${ICON.home}</button><button id="k-back" aria-label="Previous station" data-tip="Left arrow">${ICON.back}</button>`
      + `<button class="go" id="k-go" aria-label="Next station">${ICON.next}<span id="go-t">Start</span><kbd>Space</kbd></button></div>`
      + `<div class="track" id="track"><span class="fill" id="fill"></span>${STOPS.map((s, k) => `<button data-k="${k}" aria-label="${s}"><i></i><span>${s}</span></button>`).join("")}</div>`
      + `<div class="hint"><kbd>1</kbd><kbd>2</kbd><kbd>3</kbd> briefing · <kbd>J</kbd> job</div>`;
    $("k-home").onclick = () => jump(0);
    $("k-back").onclick = () => jump(step - 1);
    $("k-go").onclick = next;
    $("track").querySelectorAll("button").forEach((b) => b.addEventListener("click", () => jump(Number(b.dataset.k))));
  }
  function track() {
    const bs = [...$("track").querySelectorAll("button")];
    bs.forEach((b, k) => { b.classList.toggle("done", k < step); b.classList.toggle("cur", k === step); });
    const a = bs[0], z = bs[step], e = bs[bs.length - 1];
    const span = e.offsetLeft + e.offsetWidth / 2 - a.offsetLeft - a.offsetWidth / 2;
    const fill = $("fill");
    fill.style.left = `${a.offsetLeft + a.offsetWidth / 2}px`; fill.style.width = `${span}px`;
    fill.style.transform = `scaleX(${span ? (z.offsetLeft + z.offsetWidth / 2 - a.offsetLeft - a.offsetWidth / 2) / span : 0})`;
    $("go-t").textContent = step === 0 ? "Start" : step >= LAST ? "Again" : "Next";
  }
  function status() {
    const name = STOPS[step];
    const [cls, words] = playing ? ["run", `Running · ${name}`] : step === 0 ? ["ready", "Ready"] : step === LAST ? ["done", "Run complete"] : ["at", `At ${name}`];
    $("status").className = `status ${cls}`;
    $("status").querySelector("span").textContent = words;
  }
  function next() {
    if (playing) { playing = false; p = duration(step); status(); return; }        // a second press lands the step
    if (step >= LAST) { jump(0); return; }
    step += 1; p = 0; playing = !still(); last = performance.now();
    if (!playing) p = duration(step);
    track(); status();
  }
  function jump(k) {
    step = clamp(k, 0, LAST); playing = false; p = duration(step);
    track(); status();
  }
  function switchTo(patch) {
    Object.assign(state, patch);
    $("brief").querySelectorAll("button").forEach((b) => b.setAttribute("aria-checked", String(b.dataset.b === state.briefing)));
    $("jobs").querySelectorAll("button").forEach((b) => b.setAttribute("aria-selected", String(b.dataset.j === state.job)));
    $("model").value = state.model;
    playing = false; p = duration(step);
    build(); status();
  }
  function frame(now) {
    if (playing) {
      p += Math.min(0.1, (now - last) / 1000);
      if (p >= duration(step)) { p = duration(step); playing = false; status(); }
    }
    last = now;
    sync();
    draw(now / 1000);
    requestAnimationFrame(frame);
  }

  /* ------------------------------------------------------------ keys, tooltip, resize */
  addEventListener("keydown", (e) => {
    const tag = (e.target.tagName || "").toLowerCase();
    if (tag === "select" && /Arrow/.test(e.key)) return;
    if (e.key === " " && tag !== "button") { e.preventDefault(); next(); }
    else if (e.key === "ArrowRight" || e.key === "PageDown") { e.preventDefault(); if (playing || step < LAST) next(); }
    else if (e.key === "ArrowLeft" || e.key === "PageUp") { e.preventDefault(); jump(step - 1); }
    else if (e.key === "Home") { e.preventDefault(); jump(0); }
    else if (e.key === "End") { e.preventDefault(); jump(LAST); }
    else if (e.key === "1" || e.key === "2" || e.key === "3") switchTo({ briefing: BRIEF[Number(e.key) - 1][0] });
    else if (e.key === "j" || e.key === "J") { const k = D.jobs.findIndex((j) => j.id === state.job); switchTo({ job: D.jobs[(k + 1) % D.jobs.length].id }); }
  });
  const tip = $("tip");
  document.addEventListener("mouseover", (e) => {
    const t = e.target.closest && e.target.closest("[data-tip]");
    if (!t || !t.dataset.tip) { tip.hidden = true; return; }
    tip.textContent = t.dataset.tip; tip.hidden = false;
    const r = t.getBoundingClientRect(), w = tip.offsetWidth, h = tip.offsetHeight;
    tip.style.left = `${clamp(r.left + r.width / 2 - w / 2, 6, innerWidth - w - 6)}px`;
    tip.style.top = `${r.top - h - 8 < 6 ? r.bottom + 8 : r.top - h - 8}px`;
  });
  let rz = null;
  addEventListener("resize", () => { clearTimeout(rz); rz = setTimeout(() => { measure(); track(); }, 120); });

  window.FLOW = { next, jump, switchTo, get step() { return step; }, get lanes() { return lanes; } };
  header(); transport(); build(); track(); status();
  (document.fonts && document.fonts.ready ? document.fonts.ready : Promise.resolve()).then(() => { measure(); track(); });
  requestAnimationFrame(frame);
})();
