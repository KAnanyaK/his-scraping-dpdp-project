/* The Portal v2: the recorded run as a live data flow.
   The hospital is a matrix of patients by fields. For the chosen job, each technique reads cells out
   of it; every value read is a particle that flies into the technique's lane and travels on through
   the rules, the export and the erasure. A particle's colour is its DPDP data category; a red halo is
   a value out of the job's purpose; a white diamond is an identifier that left as a token. The
   presenter steps it: Space / right arrow next, left back, Home / End, 1-3 the briefing, M the model, J the job.
   Beside the hospital, the working shows each station's calculation as the report makes it, live.
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
  let step = 0, p = 0, playing = false, last = 0, lanes = [], geo = null, ctx = null, dpr = 1, leaving = [];
  const SWAP_OUT = 220, SWAP_IN = 320;                 // ms: a swapped lane's old run fading out, its new run fading in
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

  /* ------------------------------------------------------------ the lanes */
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
      let extra = !failed.length ? `<div class="good">${D.rule_ids.length} of ${D.rule_ids.length} rules held</div>`
        : `<div class="bad" data-tip="Broken: ${esc(failed.join(", "))}">${failed.length === D.rule_ids.length ? "every rule broken" : failed.length === 1 ? `${esc(failed[0])} broken` : `${failed.length} rules broken`}</div>`;
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
  /* ------------------------------------------------------------ the working: each station's calculation, live
     The panel follows the station. Its first line is the formula the report uses there; each row is one factor,
     worked for the three lanes with the recorded run's own figures, and each figure arrives when its lane does.
     At Score the seven rule scores land one by one and their sum is divided out in front of the presenter. */
  const DASH = "–";
  const RULE = { "DM-01": "Minimisation", "LB-01": "Lawful basis", "SL-01": "Storage limit", "SS-01": "Safeguards", "PL-01": "Purpose limit", "NT-01": "Notice", "AC-01": "Accountability" };
  const f2 = (n) => (n == null ? DASH : Number(n).toFixed(2));
  const times = (n) => (n == null ? DASH : `${Number(n) >= 10 ? Number(n).toFixed(1) : Number(n).toFixed(2)}×`);
  const RULE_AT = (i) => 0.2 + i * 0.13;               // seconds into Score when rule i lands
  const named = (l) => l.J.named && l.J.patients.includes(D.patient.index);
  const leaves = (l) => (l.J.export.kind === "tok" ? ["token", "good"] : l.J.export.kind === "raw" ? ["raw id", "bad"] : ["none", ""]);
  const workKey = () => `${step}|${state.job}|${state.model}|${state.briefing}`;
  function station() {
    const j = JOB(), P = D.patient, A = lanes[0].J;
    const span = (label, v, tip, at) => ({ label, tip, span: () => v, at });
    const row = (label, tip, cell, opt = {}) => ({ label, tip, cell, ...opt });
    if (step === 0) return {
      formula: `values = patients × fields = ${P.of} × ${D.columns.length}`, note: "Every value the hospital holds, each coloured by its DPDP data category",
      rows: [span("Patients", [fmt(P.of)]), span(`Fields, in ${D.modules.length} modules`, [fmt(D.columns.length)]),
        span("Values held", [fmt(P.of * D.columns.length)]),
        span("This job's purpose", [PURPOSE[j.purpose] || j.purpose]),
        span("Categories it allows", [`${j.allowed.length} of ${CATS.length}`], j.allowed.map((c) => CAT[c]).join(", ")),
        span("Retention ceiling", [`${j.ceiling} days`]),
        span("Fields the job needs", [fmt(A.cost.needed)], "The job's expert field list: every field with a reason"),
        span("Patient followed", [P.mrn], j.single ? "The patient this job is about" : `One of the ${P.of} patients this job covers`)],
    };
    if (step === 1) {
      const at = (k) => () => step > 1 || p - 0.25 >= k * 0.22;
      return {
        formula: "pass = TLS ∧ robots ∧ authorised ∧ signed in", note: "A run passes the gate only when every check holds",
        rows: [span("TLS on the session", [D.meta.tls ? "observed" : "absent", D.meta.tls ? "good" : "bad"], "Observed on the browser's own session, not declared", at(0)),
          span("robots.txt", ["Disallow: /"], "Read and honoured: only the hospital's authorisation lets the crawler in", at(1)),
          span("Authorisation", [D.meta.authorisation || DASH], "Logged with every run", at(2)),
          span("Signed in as", [D.meta.account || DASH], "A service account: a username and a password, nothing else", at(3)),
          span("Every run", ["audit-logged"], "Written to the hash-chained audit log at the metering boundary", at(3))],
      };
    }
    if (step === 2) return {
      formula: "module = found by its fields, never its URL", note: "The crawler reads each page's column headers and infers the module's HIS layer from the fields it finds",
      rows: [span("Pages the crawl loaded", [fmt(D.discover)], "", () => p >= 0.3),
        span("Modules found", [fmt(D.modules.length)], D.modules.map((m) => m.title).join(", "), () => p >= 1.25),
        span("Fields mapped", [fmt(D.columns.length)], "Each column header read and matched to the catalogue", () => p >= 1.25)],
    };
    if (step === EXTRACT) {
      const on = (l) => reached(l, EXTRACT);
      return {
        formula: "coverage = got ÷ need;  excess = read ÷ need", note: "Coverage: the needed fields obtained ÷ the fields the job needs. Excess: the distinct fields read ÷ the fields the job needs. Both as the meter saw them at the adapter boundary",
        rows: [
          row("Values read", "Patient × field values that left the hospital", (l) => [fmt(landed(l))], { live: true }),
          row(`Fields read, of ${D.columns.length}`, "Distinct fields the meter saw", (l) => [fmt(l.J.cost.distinct)], { at: on }),
          row("Coverage", "Needed fields obtained ÷ the fields the job needs", (l) => [f2(l.J.cost.coverage), l.J.cost.coverage < 1 ? "warn" : "", null, `${l.J.cost.matched} of ${l.J.cost.needed} needed fields`], { at: on }),
          row("Excess ratio", "Fields read ÷ the fields the job needs (1.00× is exactly the list)", (l) => [times(l.J.cost.excess), "", null, `${l.J.cost.distinct} read ÷ ${l.J.cost.needed} needed`], { at: on }),
          row("Records ÷ patient's own", "Records read ÷ the patient's own records in the modules the job needs (one-patient jobs)", (l) => l.J.cost.rec_needed == null
            ? ["n/a", "nil", null, "Not a one-patient job: no record count to compare"]
            : [times(l.J.cost.rec_excess), l.J.cost.rec_excess > 1 ? "bad" : "", null, `${l.J.cost.records} records read; the patient's own are ${l.J.cost.rec_needed}`], { at: on }),
          row("This patient's values", `Values of ${P.mrn} it read`, (l) => [l.J.named ? fmt(named(l) ? l.J.cols.length : 0) : "?", "", null, l.J.named ? "" : "Read without the record number: it cannot say whose they were"], { at: on }),
          row("Other patients read", "Other patients whose rows it read", (l) => { const o = l.J.rows.length - (named(l) ? 1 : 0); return [fmt(o), o && j.single ? "bad" : ""]; }, { at: on }),
          row("Out of purpose", "Values whose data category is outside this job's purpose", (l) => { const o = l.J.oos.length * l.J.rows.length; return [fmt(o), o ? "bad" : "good"]; }, { at: on })],
      };
    }
    if (step === SCORE) {
      const ids = D.rule_ids.filter((r) => A.rules[r] && A.rules[r][0] !== "not_applicable");
      const landedRules = () => (step > SCORE ? ids.length : ids.filter((_, i) => p >= RULE_AT(i)).length);
      return {
        formula: `score = (${ids.map((r) => r.slice(0, 2)).join("+")}) ÷ ${ids.length}`, note: "Each rule scores the run from 0 to 1; every rule weighs the same, so the score is their mean. Hover a figure for how its rule reached it",
        rows: [...ids.map((r, i) => row(`<span class="rid">${esc(r)}</span>${esc(RULE[r] || D.rule_titles[r] || "")}`, `${r} ${D.rule_titles[r] || ""}`,
          (l) => { const v = l.J.rules[r]; return [f3(v[1]), v[0] === "pass" ? "" : "bad", v[1], l.J.why[r]]; }, { at: () => p >= RULE_AT(i), html: true })),
        row("Score", "The sum of the rule scores ÷ the number of rules: the run's compliance score", (l) => {
          const k = landedRules();
          if (k < ids.length) return [k ? `${ids.slice(0, k).reduce((a, r) => a + l.J.rules[r][1], 0).toFixed(2)} ÷ ${ids.length}` : DASH, "nil"];
          return [f3(l.J.score), l.J.score < 1 ? "bad" : "good", null, `${ids.reduce((a, r) => a + l.J.rules[r][1], 0).toFixed(3)} ÷ ${ids.length}`];
        }, { live: true, total: true }),
        row("Mean of all runs", "The benchmark's figure for this job: every recorded run scored", (l) => {
          const n = l.L.samples, m = l.L.mean[state.job], rg = l.L.range[state.job];
          return [f3(m ?? l.J.score), "", null, n > 1 ? `${n} runs${rg ? `, from ${f3(rg[0])} to ${f3(rg[1])}` : ""}` : "Deterministic: one run, the same every time"];
        }, { at: () => p >= RULE_AT(ids.length) })],
      };
    }
    const on = (l) => reached(l, step);
    if (step === PSEUD) return {
      formula: "token = HMAC-SHA-256(key, id), first 48 bits", note: "Each identifier is replaced by a keyed hash before export; the key stays with the hospital, apart from the export",
      rows: [row("Identifiers read", "Direct identifier values in what it read", (l) => [fmt(l.J.export.identifiers)], { at: on }),
        row("Left as tokens", "Identifiers replaced by keyed tokens before export", (l) => (l.J.pseud.on ? [fmt(l.J.export.identifiers), "good"] : ["none", "bad"]), { at: on }),
        row("Birth date, PIN coarsened", "Quasi-identifiers generalised: the date of birth to its year, the PIN code to its first 3 digits", (l) => (l.J.pseud.generalised ? ["yes", "good"] : ["no", l.J.pseud.on ? "" : "bad"]), { at: on }),
        row("k-anonymity", "k: the smallest group of exported rows sharing one combination of quasi-identifiers; k = 1 means a row is unique", (l) => {
          const { k, k_rows: n } = l.J.pseud;
          if (k == null) return ["none left", "good", null, "No quasi-identifier left in this export"];
          if (n <= 1) return ["1 row", "", null, "One patient's export: k cannot exceed 1"];
          return [`k = ${k}`, k === 1 ? "bad" : "", null, `k = ${k} over ${n} exported rows`];
        }, { at: on }),
        row("This patient, out as", `How ${P.mrn} leaves the hospital`, leaves, { at: on })],
    };
    if (step === SHAPE) return {
      formula: "HL7 v2: one message per record, per module", note: "Each record is shaped into an HL7 v2 message for its module, and into FHIR resources for the same records",
      rows: [row("Modules", "Modules its values came from", (l) => [fmt(l.mods.length)], { at: on }),
        row("HL7 v2 messages", "", (l) => [fmt(l.J.shape.hl7)], { at: on }),
        row("FHIR resources", "", (l) => [fmt(l.J.shape.fhir)], { at: on }),
        row("Values carried", "", (l) => [fmt(l.ps.length)], { at: on })],
    };
    if (step === EXPORT) return {
      formula: "leaks = raw identifiers found in the export", note: "The export is searched for every raw identifier the run read; digits are matched within one field",
      rows: [row("Identifiers read", "", (l) => [fmt(l.J.export.identifiers)], { at: on }),
        row("Found raw in the export", "Raw identifier values the audit found in the HL7 and FHIR it made", (l) => [fmt(l.J.export.leaked), l.J.export.leaked ? "bad" : "good"], { at: on }),
        row("Leak rate", "Raw identifiers found ÷ identifiers read", (l) => { const e = l.J.export; return e.identifiers ? [`${Math.round((100 * e.leaked) / e.identifiers)}%`, e.leaked ? "bad" : "good"] : [DASH, "nil"]; }, { at: on }),
        row("This patient, out as", `How ${P.mrn} leaves the hospital`, leaves, { at: on })],
    };
    // Erase, then the job as the report gives it
    const mean = (l) => l.L.mean[state.job] ?? l.J.score;
    const rows = [
      row("Retention declared", `Must not exceed the purpose's ceiling of ${j.ceiling} days`, (l) => (l.J.retention == null ? ["none", "bad"]
        : [`${l.J.retention} d`, l.J.retention > j.ceiling ? "bad" : ""]), { at: on }),
      row("Erased on", "The run's date + the retention it declared; the purge runs as the pipeline's last stage", (l) => (l.J.erase ? [shortDate(l.J.erase).replace(/ \d{4}$/, "")] : ["never", "bad"]), { at: on }),
      { sub: "This job, as the report gives it" },
      row("Score, all runs", "The mean over every recorded run of this job", (l) => [f3(mean(l)), mean(l) < 1 ? "bad" : "good", mean(l)], { at: on }),
      row("Behaviour", "DM-01, PL-01 and a retention within the ceiling: what it pulled and decided; the mean of its runs", (l) => [f2(l.J.behaviour), l.J.behaviour < 1 ? "bad" : ""], { at: on }),
      row("Coverage", "Agreement with the expert field list: needed fields obtained ÷ needed", (l) => [f2(l.J.cost.coverage), l.J.cost.coverage < 1 ? "warn" : ""], { at: on }),
      row("Excess ratio", "Fields read ÷ the fields the job needs", (l) => [times(l.J.cost.excess)], { at: on }),
      row("Distinct decisions", "How many different decisions its recorded runs made for this job: the fields pulled and the manifest filed", (l) => (l.L.samples > 1
        ? [`${l.L.decisions[state.job] ?? DASH} in ${l.L.samples}`, (l.L.decisions[state.job] || 1) > 1 ? "warn" : ""] : ["1, fixed"]), { at: on }),
    ];
    if (j.trap) rows.push(row("Trap held, all runs", j.trap, (l) => {
      const t = l.L.traps[state.job], w = l.L.wilson && l.L.wilson[state.job];
      if (!t) return [DASH, "nil"];
      return [`${t[0]} of ${t[1]}`, t[0] === t[1] ? "good" : "bad", null, w ? `95% Wilson interval: ${Math.round(w[0] * 100)}% to ${Math.round(w[1] * 100)}%` : "Deterministic: one run"];
    }, { at: on }));
    return { formula: `erase on = run date + retention ≤ ${j.ceiling} days`, note: `The retention a run declares must not exceed this purpose's ceiling of ${j.ceiling} days; the purge runs as the pipeline's last stage`, rows };
  }
  let work = null;
  function working() {
    const S = station(), key = workKey();
    const lanesOn = S.rows.some((r) => r.cell);
    // one header row: the station's name over the label column, each lane's badge over its column
    const head = `<thead><tr class="wh"><th><span class="wt">Working</span><span class="ws">${esc(STOPS[step])}</span></th>${lanes.map((l) =>
      `<th${lanesOn ? "" : ' class="off"'} data-tip="${esc(l.slot === "A" ? "Ours" : l.slot === "C" ? "Baseline" : `${modelName(l.L.model)}, ${BRIEFW[l.L.briefing]}`)}"><span class="rd ${l.cls}">${l.slot}</span></th>`).join("")}</tr>`
      + `<tr class="fm"><td colspan="4"><div class="wf"${S.note ? ` data-tip="${esc(S.note)}"` : ""}>${esc(S.formula)}</div></td></tr></thead>`;
    const cells = [];
    const body = S.rows.map((r) => {
      if (r.sub) return `<tr class="sub"><td colspan="4">${esc(r.sub)}</td></tr>`;
      const label = `<th scope="row"${r.tip ? ` data-tip="${esc(r.tip)}"` : ""}>${r.html ? r.label : esc(r.label)}</th>`;
      if (r.span) {
        cells.push({ f: () => (r.at && !r.at() ? [DASH, "nil"] : r.span()) });
        return `<tr>${label}<td colspan="3" class="span" data-c="${cells.length - 1}"></td></tr>`;
      }
      return `<tr${r.total ? ' class="total"' : ""}>${label}${lanes.map((l) => {
        cells.push({ f: () => (r.live || !r.at || r.at(l) ? r.cell(l) : [DASH, "nil"]) });
        return `<td data-l="${l.cls}" data-c="${cells.length - 1}"></td>`;
      }).join("")}</tr>`;
    }).join("");
    const el = $("work");
    el.innerHTML = `<table><colgroup><col><col class="ln"><col class="ln"><col class="ln"></colgroup>${head}<tbody>${body}</tbody></table>`;
    // a new station's working sets in place; the same station re-set for another run does not blink
    el.classList.remove("in");
    if (!still() && work && work.key.split("|")[0] !== key.split("|")[0]) { void el.offsetWidth; el.classList.add("in"); }
    el.querySelectorAll("td[data-c]").forEach((td) => { cells[Number(td.dataset.c)].el = td; });
    work = { key, cells };
  }
  function syncWork() {
    if (!work || work.key !== workKey()) working();
    for (const c of work.cells) {
      const [t, cls = "", bar = null, tip = ""] = c.f();
      const sig = `${t}|${cls}|${bar}|${tip}`;
      if (c.sig === sig) continue;
      const fresh = c.sig != null && c.was === DASH && t !== DASH && !still();
      c.sig = sig; c.was = t;
      c.el.className = `${c.el.colSpan > 1 ? "span" : ""}${cls ? ` ${cls}` : ""}${bar != null ? " meter" : ""}`;
      c.el.innerHTML = `<span class="v${fresh ? " flip" : ""}">${esc(t)}</span>`;
      if (bar != null) c.el.style.setProperty("--w", clamp(bar).toFixed(3)); else c.el.style.removeProperty("--w");
      if (tip) c.el.dataset.tip = tip; else delete c.el.dataset.tip;
    }
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
    purpose(); work = null;
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
    if (leaving.length) drawLeaving(performance.now());
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
    // a lane whose run was just swapped comes in over the old one as it goes (see switchTo)
    const fade = l.born == null || still() ? 1 : clamp((performance.now() - l.born) / SWAP_IN);
    // a dense lane glows less per value, so hundreds of them read as a mass, not a white-out
    const dens = clamp(Math.sqrt(36 / Math.max(1, n)), 0.2, 1), halo = n > 120 ? 2.3 : 3.4;
    ctx.globalCompositeOperation = "source-over";
    // A value is drawn only where it is: a stretch it has left keeps nothing of it. The module envelopes shaping
    // makes, and the file that leaves, are outlines round the values inside them, so they come with the values
    // and go with them.
    if (step >= SHAPE && fade > 0) {
      const sh = SHAPE - EXTRACT, ex = EXPORT - EXTRACT;
      const arrive = clamp((p - MOVE * 0.8) / 0.6), leave = 1 - ease(clamp(p / MOVE));
      ctx.lineWidth = 1;
      if (step === SHAPE) frames(S[sh].frames, 0.32 * arrive * fade);
      if (step === EXPORT) frames(S[sh].frames, 0.32 * leave * fade);
      const fileA = step === EXPORT ? arrive : step === ERASE ? leave : 0;
      if (fileA > 0) {
        frames(S[ex].frames, 0.22 * fileA * fade);
        const [fx, fy, fw, fh] = S[ex].file;
        ctx.globalAlpha = 0.75 * fileA * fade; ctx.strokeStyle = e.leaked ? BREACH : "#ffffff"; ctx.lineWidth = 1.2;
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
          ctx.globalAlpha = 0.9 * ease(settle) * fade; ctx.fillStyle = q.idf && !l.tokens ? BREACH : COL[q.cat];
          ctx.fillRect(x - M.pt * 0.4, y - M.pt * 0.4, M.pt * 0.8, M.pt * 0.8);
        }
        const [fx, fy, fw, fh] = M.frame, per = 2 * (fw + fh);
        ctx.globalAlpha = fade; ctx.strokeStyle = BREACH; ctx.lineWidth = 1.5; ctx.shadowColor = BREACH; ctx.shadowBlur = 10;
        ctx.setLineDash([per * ease(settle), per]);
        ctx.beginPath(); ctx.roundRect(fx, fy, fw, fh, 4); ctx.stroke();
        ctx.setLineDash([]); ctx.shadowBlur = 0;
      }
    }
    ctx.globalCompositeOperation = "lighter";
    for (let i = 0; i < n; i++) {
      const w = where(l, i);
      if (!w) continue;
      const a = w.a * (1 - ease(settle)) * fade;
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
  /* The run a lane showed before a switch, held as it last looked and faded out over the new one. */
  function drawLeaving(now) {
    leaving = leaving.filter((s) => now - s.t0 < SWAP_OUT);
    for (const s of leaving) {
      ctx.globalAlpha = 1 - ease((now - s.t0) / SWAP_OUT);
      ctx.drawImage(s.img, s.x, s.y, s.w, s.h);
    }
    ctx.globalAlpha = 1;
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
    syncWork();
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
      + `<div class="hint"><kbd>1</kbd><kbd>2</kbd><kbd>3</kbd> briefing · <kbd>M</kbd> model · <kbd>J</kbd> job</div>`;
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
    const was = { job: state.job, ids: lanes.map((l) => l.id) };
    Object.assign(state, patch);
    $("brief").querySelectorAll("button").forEach((b) => b.setAttribute("aria-checked", String(b.dataset.b === state.briefing)));
    $("jobs").querySelectorAll("button").forEach((b) => b.setAttribute("aria-selected", String(b.dataset.j === state.job)));
    $("model").value = state.model;
    // A lane whose run changes lets go of the old one at once: what it drew is kept only as a picture that
    // fades out over the new run fading in, and nothing of the old run moves again.
    const swapped = (k) => was.job !== state.job || was.ids[k] !== lanesIdFor(k);
    const fx = $("fx"), now = performance.now();
    leaving = [];
    if (!still() && step >= EXTRACT && fx.width) lanes.forEach((l, k) => {
      if (!swapped(k) || !l.pipe) return;
      const pad = 10, x = l.pipe.x - pad, y = l.pipe.y - pad, w = l.pipe.w + 2 * pad, h = l.pipe.h + 2 * pad;
      const img = document.createElement("canvas");
      img.width = Math.max(1, Math.round(w * dpr)); img.height = Math.max(1, Math.round(h * dpr));
      img.getContext("2d").drawImage(fx, Math.round(x * dpr), Math.round(y * dpr), img.width, img.height, 0, 0, img.width, img.height);
      leaving.push({ img, x, y, w, h, t0: now });
    });
    playing = false; p = duration(step);
    build(); status();
    lanes.forEach((l, k) => { l.born = was.job !== state.job || was.ids[k] !== l.id ? now : null; });
  }
  const lanesIdFor = (k) => (k === 0 ? "ours" : k === 2 ? "base" : `${state.model}|${state.briefing}`);
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
    else if (e.key === "m" || e.key === "M") { const k = D.models.indexOf(state.model); switchTo({ model: D.models[(k + 1) % D.models.length] }); }
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
  // On a phone the stage grows with what it holds (the working is taller at some stations than at others), so
  // the canvas is re-measured whenever the stage's size changes, never left stretched over a new layout.
  if (window.ResizeObserver) {
    let seen = "";
    new ResizeObserver(([e]) => {
      const sz = `${Math.round(e.contentRect.width)}x${Math.round(e.contentRect.height)}`;
      if (sz !== seen) { seen = sz; if (geo) measure(); }
    }).observe($("stage"));
  }

  window.FLOW = { next, jump, switchTo, get step() { return step; }, get lanes() { return lanes; } };
  header(); transport(); build(); track(); status();
  (document.fonts && document.fonts.ready ? document.fonts.ready : Promise.resolve()).then(() => { measure(); track(); });
  requestAnimationFrame(frame);
})();
