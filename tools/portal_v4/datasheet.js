/* The Datasheet (Portal v4): each extraction technique specified like a component.
   Four pages per part: 1 front page (features, applications, pin configuration, device comparison),
   2 specifications (absolute maximum ratings, recommended operating conditions, characteristics MIN/TYP/MAX),
   3 typical characteristics (curves), 4 application information (register map, package, ordering, revisions).
   Parts: a ours (the reference design), b an AI model at a briefing, c the baseline.
   Keys: Space / arrows page, 1-4 a page, a b c a part, J job, M model, T what the model was told.
   Every figure is the recorded one, computed by the project's code. */
(() => {
  "use strict";
  const D = JSON.parse(document.getElementById("datasheet-data").textContent);
  const $ = (id) => document.getElementById(id);
  const esc = (s) => String(s == null ? "" : s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const fmt = (n) => Number(n).toLocaleString("en-IN");
  const day = (iso) => new Date(String(iso).slice(0, 10) + "T00:00:00Z").toLocaleDateString("en-GB", { day: "numeric", month: "short", year: "numeric", timeZone: "UTC" });
  const still = () => matchMedia("(prefers-reduced-motion: reduce)").matches;
  const NS = "http://www.w3.org/2000/svg";

  const COLS = D.columns, PTS = D.patients, HOLD = COLS.length * PTS.length;
  const MODS = D.modules, RULES = D.rules, BRIEF = D.briefings;
  const SHORT = { "patient-summary": "summary", "ward-census": "census", "appointment-reminder": "reminder", "claim-reconciliation": "claim" };
  const PAGES = [["Front page", 1], ["Specifications", 2], ["Typical characteristics", 3], ["Application information", 4]];

  const state = { part: "a", page: 1, job: D.jobs[0].id, model: (D.models.find((m) => m.id === "claude-opus-5-5") || D.models[0]).id, brief: "policy" };
  const tidOf = (x) => (x === "a" ? "ours" : x === "c" ? "base" : `${state.model}|${state.brief}`);
  const TECH = (x = state.part) => D.techniques[tidOf(x)];
  const SHEET = (x = state.part) => D.sheets[tidOf(x)];
  const JOB = () => D.jobs.find((j) => j.id === state.job);
  const RUNS = (x = state.part) => TECH(x).jobs[state.job];
  const MODEL = () => D.models.find((m) => m.id === state.model);
  const briefLabel = (b = state.brief) => (BRIEF.find((x) => x.id === b) || {}).label || "";
  const values = (r) => r.cols.length * (r.named ? r.patients.length : r.rows);
  const pct = (v) => (v == null ? "n/a" : `${Math.round(v * 100)}%`);
  const plural = (n, one, many) => `${fmt(n)} ${n === 1 ? one : many}`;
  const span = (txt) => {        // "2026-10-05 to 2026-10-06" -> "5–6 Oct 2026"; across months "18 Sep – 7 Oct 2026"
    const m = String(txt).match(/(\d{4})-(\d{2})-(\d{2}) to (\d{4})-(\d{2})-(\d{2})/);
    if (!m) return txt;
    const a = new Date(Date.UTC(+m[1], +m[2] - 1, +m[3])), b = new Date(Date.UTC(+m[4], +m[5] - 1, +m[6]));
    const mon = (d) => ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"][d.getUTCMonth()];
    if (m[1] === m[4] && m[2] === m[5]) return `${+m[3]}–${+m[6]} ${mon(b)} ${m[4]}`;
    if (m[1] === m[4]) return `${+m[3]} ${mon(a)} – ${+m[6]} ${mon(b)} ${m[4]}`;
    return `${day(a.toISOString())} – ${day(b.toISOString())}`;
  };

  function partNo(x = state.part) {
    const t = TECH(x);
    return t.kind === "ours" ? "compliance-aware" : t.kind === "base" ? "unconstrained" : `${t.model}-${t.briefing}`;
  }
  function partTitle(x = state.part) {
    const t = TECH(x);
    if (t.kind === "ours") return "Reference design: compliance-aware HIS extraction";
    if (t.kind === "base") return "Coverage-optimised baseline: reads every module, every record";
    return `AI model: ${t.model_name}, ${t.briefing_label}`;
  }
  const partName = (x) => (x === "a" ? "Reference design" : x === "c" ? "Baseline" : MODEL().name);

  /* ------------------------------------------------------------ the masthead and the sheet's foot */
  function mastHTML() {
    return `<div><span class="pnum">${esc(partNo())}</span><span class="ptitle">${esc(partTitle())}</span></div>
      <div class="docline"><b>Datasheet</b>Application: ${esc(JOB().name)}<br>Rev. ${day(D.meta.generated)}</div>`;
  }
  function footHTML() {
    return `<span><b>${esc(partNo())}</b> · extraction technique</span>
      <span>Synthetic hospital, ${D.meta.records} records a module · recorded ${day(D.meta.generated)}</span>
      <span>${state.page} of 4</span>`;
  }
  const sec = (n, title) => `<h3><i>${n}</i>${esc(title)}</h3>`;
  const sym = (s) => `${esc(s[0])}${s[1] ? `<sub>${esc(s[1])}</sub>` : ""}`;

  /* ------------------------------------------------------------ page 1: front page */
  function features() {
    const r = RUNS()[0], row = SHEET().row, t = TECH(), j = JOB();
    const [h, n] = row.traps, [s, rep] = row.stable;
    const items = [
      `<b>${fmt(values(r))} of ${fmt(HOLD)} values</b> read for ${esc(j.name.toLowerCase())}`,
      `<b>${pct(row.coverage)}</b> of the fields the four jobs need`,
      `<b>${row.excess == null ? "n/a" : row.excess.toFixed(2) + "×"}</b> the fields the jobs need`,
      `<b class="${h < n ? "bad" : ""}">${h} of ${n}</b> trap ${n === 1 ? "run" : "runs"} held`,
      `Same decision in <b>${s} of ${rep}</b> repeated runs`,
      `<b>${fmt(row.pages)} page loads</b> a run, all four jobs`,
      r.export.kind === "tok" ? `Identifiers leave as <b>keyed tokens</b>` : r.export.kind === "raw" ? `<b class="${j.pseudonymise ? "bad" : ""}">${plural(r.export.leaked, "raw identifier", "raw identifiers")}</b> in the export` : `<b>No identifier</b> in the export`,
      r.erase ? `<b>Erased after ${r.retention} days</b> by ${esc(r.mechanism)}` : `<b class="bad">No erasure:</b> no retention declared`,
    ];
    return `<ul class="feat">${items.map((i) => `<li>${i}</li>`).join("")}</ul>`;
  }
  function description() {
    const t = TECH();
    if (t.kind === "ours") return "Executes each job's expert field list, declares its manifest from the hospital's register, pseudonymises identifiers on export and schedules their erasure.";
    if (t.kind === "base") return "Reads every module and every record it can reach, declares almost nothing, exports identifiers as read and keeps everything.";
    return `${t.model_name} decides, from the job, its purpose and the field names, which fields to read and what manifest to declare. It never sees a patient value; the pipeline fetches.`;
  }
  function comparison() {
    const rows = [["a", D.sheets.ours.row], ...D.models.map((m) => ["b", D.sheets[`${m.id}|${state.brief}`].row, m]), ["c", D.sheets.base.row]];
    const body = rows.map(([x, row, m]) => {
      const name = m ? m.name : x === "a" ? "Reference design" : "Baseline";
      const cur = (x === state.part && (!m || m.id === state.model));
      const [h, n] = row.traps, [s, rep] = row.stable;
      return `<tr class="${cur ? "cur" : ""}" data-part="${x}" ${m ? `data-model="${esc(m.id)}"` : ""}><td class="pt">${esc(name)}</td>
        <td class="num">${pct(row.coverage)}</td><td class="num hide-s">${row.excess == null ? "" : row.excess.toFixed(2) + "×"}</td>
        <td class="num ${h < n ? "over" : ""}">${h}/${n}</td><td class="num hide-s">${s}/${rep}</td>
        <td class="num">${fmt(row.pages)}</td><td class="num">${row.score.toFixed(3)}</td></tr>`;
    }).join("");
    return `<table class="tbl cmp"><thead><tr><th>Part</th><th class="num">Need<sup>1</sup></th><th class="num hide-s">Read<sup>2</sup></th><th class="num">Traps<sup>3</sup></th><th class="num hide-s">Same<sup>4</sup></th><th class="num">Loads<sup>5</sup></th><th class="num">Score</th></tr></thead><tbody>${body}</tbody></table>`;
  }
  function pinFunctions() {      // the drawing's table form; on a phone it stands in for the drawing
    const r = RUNS()[0], job = JOB(), on = new Set(r.cols), oos = new Set(r.oos), need = new Set(job.needed.map((n) => n.col));
    const rows = COLS.map((c, i) => {
      const st = oos.has(i) ? ["outside the purpose", "over"] : on.has(i) ? ["connected", ""] : need.has(i) ? ["needed, not connected", "dim"] : ["not connected", "nil"];
      return `<tr><td class="num">${i + 1}</td><td class="fld">${esc(c.field)}</td><td class="dim">${esc(MODS.find((m) => i >= m.start && i < m.start + m.count).short)}</td><td class="${st[1]}">${st[0]}</td></tr>`;
    }).join("");
    return `<table class="tbl pinfn"><thead><tr><th class="num">Pin</th><th>Name</th><th>Module</th><th>Run 1</th></tr></thead><tbody>${rows}</tbody></table>`;
  }
  function page1() {
    const j = JOB();
    return `<div class="cols p1">
      <div class="col">
        <section>${sec(1, "Features")}${features()}</section>
        <section>${sec(2, "Applications")}<ul class="apps">${D.jobs.map((x) => `<li class="${x.id === j.id ? "on" : ""}">${esc(x.name)}<small>${esc(x.purpose_label.toLowerCase())}${x.trap ? ", trap" : ""}</small></li>`).join("")}</ul></section>
        <section>${sec(3, "Description")}<p class="txt">${esc(description())}</p></section>
      </div>
      <div class="col"><section class="fig pins">${sec(4, "Pin configuration")}<div class="draw" id="pins"></div>
        <p class="legend"><span><i></i>connected</span><span><i class="oos"></i>outside the purpose</span><span><i class="miss"></i>needed, not connected</span><span><i class="nc"></i>not connected</span></p>
        <p class="figcap"><b>Figure 1.</b>${esc(j.name)}: ${RUNS()[0].cols.length} of ${COLS.length} pins connected, run 1. One pin a field, five modules.</p>
        ${pinFunctions()}</section></div>
      <div class="col"><section>${sec(5, "Device comparison")}
        <p class="condl">Models <b>${esc(briefLabel())}</b>; five runs each; all four jobs</p><div class="cmp-wrap"><i class="hl" aria-hidden="true"></i>${comparison()}</div>
        <p class="tcap"><b>Table 1.</b>Select a row to read its datasheet.</p>
        <ol class="notes"><li><b>1</b>Needed fields obtained, of the jobs' expert lists.</li><li class="hide-s"><b>2</b>Fields read for each field needed.</li><li><b>3</b>Trap runs held, of the runs on the trap job.</li><li class="hide-s"><b>4</b>Repeats that gave run 1's decision. Ours and the baseline are run here five times; a model's five runs are recorded.</li><li><b>5</b>Page loads a run, all four jobs (a model: mean of five).</li></ol>
      </section></div></div>`;
  }

  /* ------------------------------------------------------------ page 2: specifications */
  function shown(v, unit) {
    if (v == null) return "";
    if (unit === "") return Number(v).toFixed(3);
    return fmt(v);
  }
  function page2() {
    const j = JOB(), spec = SHEET().spec[state.job], t = TECH();
    const ratings = spec.ratings.map((r) => `<tr><td>${esc(r.param)}${r.note ? `<small class="dim">${esc(r.note)}</small>` : ""}</td><td class="sym hide-s">${sym(r.sym)}</td><td class="num">${r.max == null ? "" : fmt(r.max)}</td><td class="dim">${esc(r.unit)}</td><td class="rule">${esc(r.rule)}</td></tr>`).join("");
    const byMod = [];
    for (const n of j.needed) {
      const mod = MODS.find((m) => n.col >= m.start && n.col < m.start + m.count).short;
      let g = byMod.find((x) => x.mod === mod);
      if (!g) byMod.push(g = { mod, fields: [] });
      g.fields.push(COLS[n.col].field);
    }
    const need = byMod.map((g) => `<li><small>${esc(g.mod)}</small><span>${g.fields.map(esc).join(", ")}</span></li>`).join("");
    const chars = spec.chars.map((c) => {
      const [mn, ty, mx] = c.spread || [null, null, null];
      const none = c.id === "retention";
      const cell = (v, side) => {
        if (c.id === "pages" || c.id === "decisions") return side === "typ" ? fmt(v) : "";
        if (v == null) return none && ((side === "max") || (side === "typ" && ty == null) || (side === "min" && mn == null)) ? "none" : "";
        return shown(v, c.unit);
      };
      const red = c.cells || [false, false, false];
      const broke = c.id === "held" && c.broken && c.broken.length ? `<small class="dim why">${esc(c.broken.join(", "))} not held</small>` : "";
      return `<tr class="${c.over ? "over" : ""}"><td>${esc(c.param)}${c.note ? `<sup>${c.note}</sup>` : ""}${broke}</td><td class="sym hide-s">${sym(c.sym)}</td>
        <td class="num ${red[0] ? "over" : ""}">${cell(mn, "min")}</td><td class="num ${red[1] ? "over" : ""}">${cell(ty, "typ")}</td><td class="num ${red[2] ? "over" : ""}">${cell(mx, "max")}</td>
        <td class="dim">${esc(c.unit)}</td><td class="num dim hide-s">${c.limit == null ? "" : (c.id === "held" ? "≥ " : "≤ ") + fmt(c.limit)}</td></tr>`;
    }).join("");
    const told = t.kind === "model" ? esc(briefLabel()) : "not briefed";
    return `<div class="cols p2">
      <div class="col">
        <section>${sec("6.1", "Absolute maximum ratings")}<p class="condl">${esc(j.name)} · purpose <b>${esc(j.purpose_label.toLowerCase())}</b></p>
          <table class="tbl"><thead><tr><th>Parameter</th><th class="hide-s">Symbol</th><th class="num">Max</th><th>Unit</th><th>Rule</th></tr></thead><tbody>${ratings}</tbody></table>
          <p class="tcap"><b>Table 2.</b>Beyond these ratings a run breaches the hospital's purpose policy.</p></section>
        <section>${sec("6.2", "Recommended operating conditions")}<p class="condl">The job's expert field list: ${j.needed.length} fields${j.single ? ", one patient" : ", every patient"}</p>
          <ul class="needs">${need}</ul></section>
      </div>
      <div class="col">
        <section>${sec("6.3", "Characteristics")}<p class="condl">${esc(j.name)} · ${told} · ${RUNS().length} runs${t.sampled ? ", recorded" : ", run here"}<sup>3</sup></p>
          <table class="tbl"><thead><tr><th>Parameter</th><th class="hide-s">Symbol</th><th class="num">Min</th><th class="num">Typ<sup>1</sup></th><th class="num">Max</th><th>Unit</th><th class="num hide-s">Limit</th></tr></thead><tbody>${chars}</tbody></table>
          <p class="tcap"><b>Table 3.</b>Red: beyond an absolute maximum rating, or a rule not held.</p>
          <ol class="notes"><li><b>1</b>The median of the runs; for the score, their mean, as the benchmark reports it.</li><li><b>2</b>The first run, the one the portal replays.</li><li><b>3</b>Ours and the baseline are run here five times; a model's five runs are its recorded samples.</li></ol></section>
      </div></div>`;
  }

  /* ------------------------------------------------------------ page 3: typical characteristics */
  function page3() {
    const t = TECH(), model = t.kind === "model";
    const figs = model
      ? [["Figure 2.", "Compliance score vs what the model was told; five-run mean, each job"],
         ["Figure 3.", "Needed fields obtained vs what the model was told; five runs, each job"],
         ["Figure 4.", `Fields read, run by run; ${briefLabel()}, each job`]]
      : [["Figure 2.", "Page loads vs records per module; all four jobs, one run each size"],
         ["Figure 3.", "Records read per record needed vs records per module; patient jobs"],
         ["Figure 4.", "Fields read, run by run; each job"]];
    return `<div class="cols p3">
      <div style="grid-column:1/-1">${sec(7, "Typical characteristics")}<p class="condl">${model ? `${esc(t.model_name)}; ${D.runs_here ? "five recorded runs a job and briefing" : ""}` : `The scale run: the portal at 20 to 160 records a module; ${esc(partName(state.part))} in blue, the other in grey`}</p></div>
      ${figs.map((f, i) => `<section class="fig"><div class="draw" id="ch${i + 2}"></div><p class="figcap"><b>${f[0]}</b>${esc(f[1])}</p></section>`).join("")}
    </div>`;
  }

  /* ------------------------------------------------------------ page 4: application information */
  const REG = [
    ["purpose", null], ["retention_days", null], ["secondary_uses", null], ["lawful_basis.reference", "lawful-basis reference"],
    ["security.transport_encrypted", "transport encryption"], ["security.at_rest_encrypted", "encryption at rest"],
    ["security.access_controlled", "access control"], ["security.identifiers_pseudonymised", "pseudonymisation on export"],
    ["deletion_mechanism", "deletion mechanism"], ["notice.reference", "privacy notice"], ["notice.machine_readable", "machine-readable notice"],
    ["governance.audit_log_enabled", "audit log"], ["governance.accountable_party", "accountable party"], ["governance.processing_record_kept", "record of processing"],
  ];
  function page4() {
    const r = RUNS()[0], t = TECH(), j = JOB();
    const claims = Object.fromEntries((r.claims || []).map((c) => [c.control, c]));
    const reg = (key) => { const v = D.register[key]; return key === "lawful-basis reference" ? (v || {})[j.purpose] : v; };
    const map = REG.map(([name, ctl]) => {
      let value, backed = "";
      if (name === "purpose") value = r.specified ? j.purpose : "unspecified";
      else if (name === "retention_days") value = r.retention == null ? "null" : String(r.retention);
      else if (name === "secondary_uses") value = r.onward.length ? `[${r.onward.join(", ")}]` : "[]";
      else {
        const c = claims[ctl];
        if (!c) value = name.startsWith("security.") || name.startsWith("governance.") && !name.endsWith("party") || name === "notice.machine_readable" ? "false" : "null";
        else {
          value = c.declared === "True" ? "true" : c.declared.split(/\s+--\s+|\s+/)[0];
          const g = reg(ctl) || {};
          backed = c.ok ? `<span class="${c.basis === "demonstrated" ? "dem" : "att"}">${esc(g.id || "")}</span><small>${esc(c.basis)}</small>` : `<span class="no">nothing</span><small>${esc(c.note)}</small>`;
        }
      }
      const nil = value === "null" || value === "false" || value === "unspecified";
      return `<tr><td class="reg">${esc(name)}</td><td class="reg ${nil ? "nil" : ""}">${esc(value)}</td><td class="backed">${backed}</td></tr>`;
    }).join("");
    const e = r.export, s = r.sidecar || {};
    const quasi = r.cols.some((i) => COLS[i].cat === "quasi_identifier" && COLS[i].field !== "sex");
    const pkg = [
      ["Format", "HL7 v2.5 messages, FHIR R4 bundle"],
      ["Contents", `${fmt(e.messages)} messages · ${fmt(e.resources)} resources`],
      ["Record number", e.kind === "tok" ? `keyed token <span class="tkn">${esc(e.token)}</span>` : e.kind === "raw" ? `<span class="${j.pseudonymise ? "bad" : ""}">as read, ${plural(e.leaked, "raw identifier", "raw identifiers")}</span>` : "not exported"],
      ["Quasi-identifiers", !quasi ? "none read" : e.generalised ? "coarsened: year of birth, 3-digit PIN" : `<span class="bad">as read</span>`],
      ["Key", s.key_holder ? `kept apart, held by ${esc(s.key_holder)}` : "none"],
      ["Erase after", r.erase ? day(r.erase) : `<span class="bad">never: no retention declared</span>`],
    ].map(([k, v]) => `<tr><td>${esc(k)}</td><td>${v}</td></tr>`).join("");
    let order;
    if (t.kind === "model") {
      order = BRIEF.map((b) => {
        const sh = D.sheets[`${t.model}|${b.id}`];
        if (!sh) return "";
        const row = sh.row;
        return `<tr class="${b.id === state.brief ? "cur" : ""}" data-brief="${b.id}"><td class="reg">${esc(`${t.model}-${b.id}`)}</td><td>${esc(b.label)}</td><td class="num">${row.score.toFixed(3)}</td><td class="num ${row.traps[0] < row.traps[1] ? "over" : ""}">${row.traps[0]}/${row.traps[1]}</td><td class="num hide-s">${pct(row.coverage)}</td></tr>`;
      }).join("");
    } else {
      const row = SHEET().row;
      order = `<tr class="cur"><td class="reg">${esc(partNo())}</td><td>not briefed</td><td class="num">${row.score.toFixed(3)}</td><td class="num ${row.traps[0] < row.traps[1] ? "over" : ""}">${row.traps[0]}/${row.traps[1]}</td><td class="num hide-s">${pct(row.coverage)}</td></tr>`;
    }
    const rec = (D.meta.recorded || {})[t.model];
    const revs = [
      t.kind === "model" && rec ? [span(rec), "five samples recorded per job and briefing: the model's decisions, no patient value"] : null,
      [day(D.meta.generated), "the portal run this sheet replays; ours and the baseline run five times on its source"],
    ].filter(Boolean).map(([d, w]) => `<tr><td class="num" style="text-align:left;white-space:nowrap">${esc(d)}</td><td>${esc(w)}</td></tr>`).join("");
    return `<div class="cols p4">
      <div class="col"><section>${sec("8.1", "Register map")}<p class="condl">The manifest run 1 declared, checked against the hospital's register</p>
        <table class="tbl regmap"><thead><tr><th>Register</th><th>Value</th><th>Backed by</th></tr></thead><tbody>${map}</tbody></table>
        <p class="tcap"><b>Table 4.</b>Solid: demonstrated by the pipeline. Dashed: attested by the hospital. Struck: not backed.</p></section></div>
      <div class="col">
        <section>${sec("8.2", "Package")}<p class="condl">The export of run 1</p><table class="tbl"><tbody>${pkg}</tbody></table></section>
        <section>${sec(9, "Ordering information")}<table class="tbl"><thead><tr><th>Part number</th><th>Told</th><th class="num">Score</th><th class="num">Traps</th><th class="num hide-s">Need</th></tr></thead><tbody>${order}</tbody></table></section>
        <section>${sec(10, "Revision history")}<table class="tbl"><tbody>${revs}</tbody></table></section>
      </div></div>`;
  }

  /* ------------------------------------------------------------ drawings */
  function el(tag, attrs, parent, text) {
    const n = document.createElementNS(NS, tag);
    for (const [k, v] of Object.entries(attrs || {})) n.setAttribute(k, v);
    if (text != null) n.textContent = text;
    if (parent) parent.appendChild(n);
    return n;
  }

  function drawPins() {
    const box = $("pins");
    if (!box) return;
    box.innerHTML = "";
    box.style.height = ""; box.style.flex = "";
    const W = box.clientWidth, H = box.clientHeight;
    if (W < 10 || H < 10) return;
    const r = RUNS()[0], job = JOB();
    const on = new Set(r.cols), oos = new Set(r.oos), need = new Set(job.needed.map((n) => n.col));
    const svg = el("svg", { viewBox: `0 0 ${W} ${H}`, role: "img", "aria-label": `Pin configuration: ${r.cols.length} of ${COLS.length} fields connected` }, box);
    const rem = parseFloat(getComputedStyle(document.documentElement).fontSize);
    const side = 17, pitch = Math.min(1.7 * rem, (H - 24) / (side + 0.8));
    const probe = el("text", { class: "pname on", x: 0, y: -100 }, svg);
    let label = 0;
    for (const c of COLS) { probe.textContent = c.field; label = Math.max(label, probe.getComputedTextLength()); }
    probe.remove();
    const stub = 1.125 * rem, gap = .375 * rem;
    const pw = Math.max(96, Math.min(140, W - 2 * (label + gap + stub) - 8));
    const ph = pitch * (side + 0.8), px = (W - pw) / 2, py = 4;
    box.style.flex = "none"; box.style.height = `${Math.ceil(ph + 10)}px`;   // the legend and caption sit right under the package
    svg.setAttribute("viewBox", `0 0 ${W} ${Math.ceil(ph + 10)}`);
    el("rect", { class: "pkg", x: px, y: py, width: pw, height: ph, rx: 3 }, svg);
    el("path", { class: "pkg", d: `M ${px + pw / 2 - 11} ${py} a 11 11 0 0 0 22 0`, fill: "none" }, svg);
    const cls = (i) => (oos.has(i) ? "oos" : on.has(i) ? "on" : need.has(i) ? "miss" : "nc");
    const yAt = (k) => py + pitch * (k + 0.9);
    // left side: pins 1-17 top to bottom; right side: pins 18-34 bottom to top, as a package is numbered
    for (let i = 0; i < COLS.length; i++) {
      const left = i < side, k = left ? i : side - 1 - (i - side), y = yAt(k), c = cls(i);
      const x0 = left ? px - stub : px + pw, x1 = left ? px : px + pw + stub;
      el("line", { class: `pin ${c}`, x1: x0, y1: y, x2: x1, y2: y, style: `transform-origin:${left ? "100%" : "0%"} 50%` }, svg);
      el("text", { class: `pname ${c}`, x: left ? x0 - gap : x1 + gap, y, "dominant-baseline": "central", "text-anchor": left ? "end" : "start" }, svg, COLS[i].field);
      el("text", { class: "pno", x: left ? px + 5 : px + pw - 5, y, "dominant-baseline": "central", "text-anchor": left ? "start" : "end" }, svg, String(i + 1));
    }
    // the five modules as pin groups, divided inside the package
    for (const m of MODS) {
      const left = m.start < side;
      const ks = [...Array(m.count).keys()].map((q) => { const i = m.start + q; return left ? i : side - 1 - (i - side); });
      const k0 = Math.min(...ks), k1 = Math.max(...ks), mid = (yAt(k0) + yAt(k1)) / 2;
      if (k0 > 0) el("line", { class: "pkg-div", x1: left ? px : px + pw / 2, y1: yAt(k0) - pitch / 2, x2: left ? px + pw / 2 : px + pw, y2: yAt(k0) - pitch / 2 }, svg);
      const tx = left ? px + 1.625 * rem : px + pw - 1.625 * rem;
      el("text", { class: "grp", x: tx, y: mid, transform: `rotate(${left ? -90 : 90} ${tx} ${mid})`, "text-anchor": "middle", "dominant-baseline": "middle" }, svg, m.short.toUpperCase());
    }
  }

  function lineChart(id, spec) {
    const box = $(id);
    if (!box) return;
    box.innerHTML = "";
    const W = box.clientWidth, H = box.clientHeight;
    if (W < 10 || H < 10) return;
    const m = { l: 60, r: spec.right || 74, t: 12, b: 38 };
    const svg = el("svg", { viewBox: `0 0 ${W} ${H}`, role: "img", "aria-label": spec.aria }, box);
    const iw = W - m.l - m.r, ih = H - m.t - m.b;
    const xs = spec.x.values, X = (i) => m.l + (xs.length === 1 ? iw / 2 : (iw * i) / (xs.length - 1));
    const lg = (v) => Math.log10(v);
    const Y = (v) => {
      const [a, b] = spec.y.log ? [lg(spec.y.min), lg(spec.y.max)] : [spec.y.min, spec.y.max];
      const t = ((spec.y.log ? lg(v) : v) - a) / (b - a);
      return m.t + ih * (1 - t);
    };
    for (const t of spec.y.ticks) {
      el("line", { class: "grid-l", x1: m.l, y1: Y(t), x2: m.l + iw, y2: Y(t) }, svg);
      el("text", { class: "tick", x: m.l - 6, y: Y(t) + 4.5, "text-anchor": "end" }, svg, spec.y.fmt(t));
    }
    xs.forEach((v, i) => {
      el("line", { class: "grid-l", x1: X(i), y1: m.t, x2: X(i), y2: m.t + ih }, svg);
      el("text", { class: "tick", x: X(i), y: m.t + ih + 17, "text-anchor": i === 0 ? "start" : i === xs.length - 1 ? "end" : "middle" }, svg, spec.x.fmt(v));
    });
    el("line", { class: "axis-l", x1: m.l, y1: m.t + ih, x2: m.l + iw, y2: m.t + ih }, svg);
    el("line", { class: "axis-l", x1: m.l, y1: m.t, x2: m.l, y2: m.t + ih }, svg);
    el("text", { class: "ax-t", x: m.l + iw / 2, y: H - 3, "text-anchor": "middle" }, svg, spec.x.title);
    // end labels, nudged apart so none collide
    const labels = spec.series.map((s) => ({ s, y: Y(s.pts[s.pts.length - 1]) }));
    labels.sort((a, b) => a.y - b.y);
    for (let i = 1; i < labels.length; i++) if (labels[i].y - labels[i - 1].y < 15) labels[i].y = labels[i - 1].y + 15;
    for (const s of [...spec.series].sort((a, b) => (a.me ? 1 : 0) - (b.me ? 1 : 0))) {
      const d = s.pts.map((v, i) => `${i ? "L" : "M"} ${X(i).toFixed(1)} ${Y(v).toFixed(1)}`).join(" ");
      el("path", { class: `crv ${s.me ? "me" : s.dash || ""}`, d }, svg);
    }
    for (const l of labels) el("text", { class: `clab ${l.s.me ? "me" : ""}`, x: m.l + iw + 6, y: l.y + 4.5 }, svg, l.s.label);
    el("text", { class: "ax-t", x: 12, y: m.t + ih / 2, transform: `rotate(-90 12 ${m.t + ih / 2})`, "text-anchor": "middle" }, svg, spec.y.title);
  }

  function drawCharts() {
    if (state.page !== 3) return;
    const t = TECH(), jobs = D.jobs.map((j) => j.id), dash = ["d1", "d2", "d3"];
    const jobSeries = (fn) => { let k = 0; return jobs.map((j) => ({ label: SHORT[j], me: j === state.job, dash: j === state.job ? "" : dash[k++ % 3], pts: fn(j) })); };
    if (t.kind === "model") {
      const sw = D.sweeps[t.model], bs = ["unaided", "informed", "policy"].filter((b) => sw[b]);
      const scores = bs.flatMap((b) => jobs.map((j) => sw[b][j].score));
      const lo = Math.max(0, Math.floor((Math.min(...scores) - 0.02) * 20) / 20);
      const step = 1 - lo > 0.3 ? 0.1 : 0.05, ticks = [];
      for (let v = lo; v <= 1.0001; v += step) ticks.push(Math.round(v * 100) / 100);
      const xcat = { values: bs, fmt: (b) => briefLabel(b).replace(/^told /, ""), title: "what the model was told" };
      lineChart("ch2", { aria: "Compliance score by briefing", x: xcat, y: { min: lo, max: 1, ticks, fmt: (v) => v.toFixed(2), title: "score" },
        series: jobSeries((j) => bs.map((b) => sw[b][j].score)) });
      lineChart("ch3", { aria: "Needed fields obtained by briefing", x: xcat, y: { min: 0, max: 100, ticks: [0, 25, 50, 75, 100], fmt: (v) => `${v}%`, title: "needed fields obtained" },
        series: jobSeries((j) => bs.map((b) => sw[b][j].needed)) });
    } else {
      const rows = D.scale, me = t.kind === "ours" ? "ours" : "baseline";
      const xs = { values: rows.map((r) => r.records), fmt: (v) => String(v), title: "records a module" };
      lineChart("ch2", { aria: "Page loads by hospital size", x: xs, y: { min: 10, max: 10000, log: true, ticks: [10, 100, 1000, 10000], fmt: (v) => fmt(v), title: "page loads" },
        series: [{ label: `reference ${fmt(rows[rows.length - 1].ours.page_loads)}`, me: me === "ours", dash: "d1", pts: rows.map((r) => r.ours.page_loads) },
                 { label: `baseline ${fmt(rows[rows.length - 1].baseline.page_loads)}`, me: me === "baseline", dash: "d1", pts: rows.map((r) => r.baseline.page_loads) }], right: 104 });
      lineChart("ch3", { aria: "Records read per record needed by hospital size", x: xs, y: { min: 1, max: 1000, log: true, ticks: [1, 10, 100, 1000], fmt: (v) => fmt(v), title: "records read per record needed" },
        series: [{ label: `reference ${fmt(rows[rows.length - 1].ours.record_excess)}`, me: me === "ours", dash: "d1", pts: rows.map((r) => r.ours.record_excess) },
                 { label: `baseline ${fmt(Math.round(rows[rows.length - 1].baseline.record_excess))}`, me: me === "baseline", dash: "d1", pts: rows.map((r) => r.baseline.record_excess) }], right: 104 });
    }
    const runs = (j) => t.jobs[j].map((r) => r.cols.length);
    const n = t.jobs[state.job].length;
    lineChart("ch4", { aria: "Fields read in each run", x: { values: [...Array(n).keys()], fmt: (i) => `run ${i + 1}`, title: "run" },
      y: { min: 0, max: COLS.length, ticks: [0, 10, 20, 30], fmt: (v) => String(v), title: "fields read" }, series: jobSeries(runs) });
  }

  /* ------------------------------------------------------------ chrome */
  function chrome() {
    $("job").innerHTML = D.jobs.map((j) => `<option value="${esc(j.id)}">${esc(j.name)}${j.trap ? " (trap)" : ""}</option>`).join("");
    $("brief").innerHTML = BRIEF.map((b) => `<button type="button" role="radio" data-brief="${b.id}">${esc(b.label.replace(/^told /, ""))}</button>`).join("");
    $("parts").innerHTML = `<i class="ptab" aria-hidden="true"></i><button class="part" type="button" data-part="a"><span class="k">a</span>Reference design</button>
      <span class="part" data-part="b" role="button" tabindex="0"><span class="k">b</span><select id="model" aria-label="AI model">${D.models.map((m) => `<option value="${esc(m.id)}">${esc(m.name)}</option>`).join("")}</select></span>
      <button class="part" type="button" data-part="c"><span class="k">c</span>Baseline</button>`;
    $("pages").innerHTML = PAGES.map(([name, n]) => `<button type="button" data-page="${n}"><b>${n}</b><span>${esc(name)}</span></button>`).join("") + `<i class="pgm" aria-hidden="true"></i>`;
    $("model").addEventListener("change", (e) => { state.model = e.target.value; state.part = "b"; render("respec"); });
    $("model").addEventListener("click", (e) => e.stopPropagation());
  }
  function sync() {
    $("job").value = state.job;
    $("model").value = state.model;
    document.querySelectorAll(".part").forEach((p) => p.setAttribute("aria-pressed", String(p.dataset.part === state.part)));
    document.querySelectorAll("#brief button").forEach((b) => b.setAttribute("aria-checked", String(b.dataset.brief === state.brief)));
    document.querySelector(".seg").classList.toggle("off", state.part !== "b");
    document.querySelectorAll("#pages button").forEach((b) => { b.removeAttribute("aria-current"); if (+b.dataset.page === state.page) b.setAttribute("aria-current", "page"); });
    $("next").querySelector("span").textContent = state.page === 4 ? "Front page" : "Next page";
    stack();
    marks();
    history.replaceState(null, "", `#${state.part}${state.page}`);
  }
  function stack() {              // the pages still to read lie beneath the sheet, edge on edge
    const n = 4 - state.page, layers = [];
    for (let i = 1; i <= n; i++) layers.push(`${i * 5}px ${i}px 0 -1px var(--sheet)`, `${i * 5}px ${i}px 0 0 rgba(var(--slate), .32)`, `${i * 5 + 1}px ${i + 1}px 4px -1px rgba(var(--slate), .18)`);
    layers.push("0 1px 2px rgba(var(--slate), .14)", `${n * 5}px ${14 + n}px 30px -14px rgba(var(--slate), .38)`);
    $("sheet").style.boxShadow = layers.join(", ");
  }
  function marks() {              // the part's white tab and the page's rule travel to where they now belong
    const pb = document.querySelector('.part[aria-pressed="true"]'), tab = document.querySelector(".parts .ptab");
    if (pb && tab) { tab.style.height = `${pb.offsetHeight}px`; slideTo(tab, pb.offsetLeft, pb.offsetWidth, pb.offsetTop); }
    const gb = document.querySelector('#pages button[aria-current="page"]'), pg = document.querySelector("#pages .pgm");
    if (gb && pg) slideTo(pg, gb.offsetLeft, gb.offsetWidth);
  }
  function slideTo(m, x, w, y = 0) {      // a marker travels by transform: it is set in place, then played from where it was (FLIP)
    const ox = +m.dataset.x, ow = +m.dataset.w, oy = +(m.dataset.y || 0);
    m.style.width = `${w}px`;
    m.style.transform = `translate(${x}px, ${y}px)`;
    Object.assign(m.dataset, { x, w, y });
    if (ow > 0 && (ox !== x || ow !== w || oy !== y) && !still()) {
      m.animate([{ transform: `translate(${ox}px, ${oy}px) scaleX(${ow / w})` }, { transform: `translate(${x}px, ${y}px)` }], { duration: 580, easing: "cubic-bezier(.16, 1, .3, 1)" });
    }
  }
  function markHL(from) {         // the comparison's current row: its wash slides to the part chosen
    const w = $("body").querySelector(".cmp-wrap");
    if (!w) return;
    const hl = w.querySelector(".hl"), cur = w.querySelector("tr.cur");
    if (!cur) { hl.style.height = "0"; return; }
    const y = cur.getBoundingClientRect().top - w.getBoundingClientRect().top;
    hl.style.height = `${cur.offsetHeight}px`;
    hl.style.transform = `translateY(${y}px)`;
    hl.dataset.y = String(y);
    if (from != null && from !== y) anim(hl, [{ transform: `translateY(${from}px)` }, { transform: `translateY(${y}px)` }], { duration: 580 });
  }

  /* ------------------------------------------------------------ motion: each step plays; a second press lands it */
  const EASE = "cubic-bezier(.16, 1, .3, 1)";
  const easeOut = (t) => 1 - Math.pow(1 - t, 3);
  const tweens = new Set();
  let until = 0;
  const now = () => performance.now();
  const busy = () => now() < until;
  const hold = (ms) => { until = Math.max(until, now() + ms); };
  function anim(el, frames, o = {}) {      // holds its first frame until its delay is up, then lands on the sheet's own style
    if (!el || still()) return null;
    const opt = { duration: 420, easing: EASE, fill: "backwards", ...o };
    hold((opt.delay || 0) + opt.duration);
    return el.animate(frames, opt);
  }
  const rise = (el, delay, duration = 380, by = ".3em") => anim(el, [{ opacity: 0, transform: `translateY(${by})` }, { opacity: 1, transform: "none" }], { delay, duration });
  const fade = (el, delay, duration = 340) => anim(el, [{ opacity: 0 }, { opacity: 1 }], { delay, duration, easing: "ease-out" });
  const print = (el, delay, duration = 160) => anim(el, [{ opacity: 0, transform: "translateY(1px)" }, { opacity: 1, transform: "none" }], { delay, duration, easing: "ease-out" });   // a reading inks in whole
  const flash = (el, delay, colour, duration = 1100) => anim(el, [{ backgroundColor: colour }, { backgroundColor: "rgba(0, 0, 0, 0)" }], { delay, duration, easing: "ease-out" });
  const gap = (n, total, most) => (n > 1 ? Math.min(most, total / (n - 1)) : 0);
  const RED_WASH = "rgba(192, 39, 27, .2)", BLUE_WASH = "rgba(10, 88, 168, .16)";
  function holdRed(tr, at) {               // a row's label stays in ink, and its reason unwritten, until its readings have earned the red
    if (!tr.classList.contains("over")) return;
    const lab = tr.querySelector("td:first-child");
    if (lab) anim(lab, [{ color: getComputedStyle(document.body).color }, { color: getComputedStyle(lab).color }], { delay: at, duration: 320, easing: "ease-out" });
    tr.querySelectorAll(".why").forEach((w) => anim(w, [{ opacity: 0 }, { opacity: 1 }], { delay: at, duration: 320, easing: "ease-out" }));
  }
  function tween(ms, delay, step) {
    if (still()) { step(1); return null; }
    const t0 = now() + delay, tw = { raf: 0, finish() { cancelAnimationFrame(tw.raf); tweens.delete(tw); step(1); } };
    const tick = () => {
      const f = Math.min(1, Math.max(0, (now() - t0) / ms));
      step(f);
      if (f < 1) tw.raf = requestAnimationFrame(tick); else tweens.delete(tw);
    };
    tweens.add(tw); step(0); tw.raf = requestAnimationFrame(tick); hold(delay + ms);
    return tw;
  }
  function land() {
    for (const tw of [...tweens]) tw.finish();
    for (const a of document.getAnimations()) {
      try { if (a.effect && a.effect.getComputedTiming().endTime !== Infinity) a.finish(); } catch (e) { /* left to run */ }
    }
    until = 0;
  }

  /* the pin configuration: the package outline, then each pin in its number order */
  function pinsIn(d, k) {
    const svg = $("pins") && $("pins").querySelector("svg");
    if (!svg) return;
    const pkg = svg.querySelector("rect.pkg");
    if (pkg) {
      const len = pkg.getTotalLength();
      anim(pkg, [{ strokeDasharray: `${len}`, strokeDashoffset: `${len}`, fillOpacity: 0 }, { strokeDasharray: `${len}`, strokeDashoffset: "0", fillOpacity: 1 }], { delay: d, duration: 720 * k, easing: "cubic-bezier(.6, 0, .3, 1)" });
    }
    svg.querySelectorAll("path.pkg, .pkg-div, .grp").forEach((n) => fade(n, d + 520 * k, 420));
    const pins = [...svg.querySelectorAll(".pin")], names = [...svg.querySelectorAll(".pname")], nos = [...svg.querySelectorAll(".pno")];
    const g = gap(pins.length, 980 * k, 32);
    pins.forEach((p, i) => {
      const at = d + 300 * k + i * g;
      anim(p, [{ transform: "scaleX(0)" }, { transform: "scaleX(1)" }], { delay: at, duration: 340 });
      fade(nos[i], at + 30, 260);
      fade(names[i], at + 90, 320);
    });
  }
  /* the typical curves: grid and axes, the other series, then this part's curve traced */
  function curvesIn(d, k, quick) {
    ["ch2", "ch3", "ch4"].forEach((id, c) => {
      const svg = $(id) && $(id).querySelector("svg");
      if (!svg) return;
      const at = d + c * 170 * k;
      if (!quick) svg.querySelectorAll(".grid-l, .tick, .ax-t, .axis-l").forEach((n) => fade(n, at, 380));
      const crvs = [...svg.querySelectorAll(".crv")];
      crvs.forEach((p, i) => {
        if (p.classList.contains("me")) {
          const len = p.getTotalLength();
          anim(p, [{ strokeDasharray: `${len} ${len}`, strokeDashoffset: `${len}` }, { strokeDasharray: `${len} ${len}`, strokeDashoffset: "0" }], { delay: at + (quick ? 80 : 320), duration: (quick ? 760 : 1100) * k, easing: "cubic-bezier(.45, 0, .25, 1)" });
        } else fade(p, at + (quick ? 0 : 180) + i * 70, 460);
      });
      svg.querySelectorAll(".clab").forEach((n, i) => fade(n, at + (quick ? 80 + 760 * k : 320 + 1100 * k) + 60 + i * 60, 380));
    });
  }

  /* each page sets itself the way a datasheet is read: d is when it starts, k how fast */
  const qb = (sel) => [...$("body").querySelectorAll(sel)];
  const PLAY = {
    1(d, k) {
      qb("h3").forEach((h, i) => rise(h, d + i * 70, 420));
      qb(".feat li").forEach((li, i) => rise(li, d + 120 + i * 70 * k, 380));
      qb(".apps li").forEach((li, i) => rise(li, d + 700 * k + i * 60, 360));
      fade($("body").querySelector(".txt"), d + 900 * k, 480);
      pinsIn(d + 160, k);
      fade($("body").querySelector(".cmp thead"), d + 220, 360);
      qb(".cmp tbody tr").forEach((tr, i) => { const at = d + 320 + i * 75 * k; rise(tr, at, 380); tr.querySelectorAll("td.num").forEach((td, j) => print(td, at + 80 + j * 40, 260)); });
      fade($("body").querySelector(".cmp-wrap .hl"), d + 900 * k, 420);
      qb(".legend, .figcap, .tcap, .notes, .condl").forEach((n, i) => fade(n, d + 1000 * k + i * 60, 420));
    },
    2(d, k) {
      qb("h3, .condl").forEach((h, i) => rise(h, d + i * 60, 400));
      qb(".p2 .col:first-child .tbl tbody tr").forEach((tr, i) => { const at = d + 160 + i * 70 * k; rise(tr, at, 380); tr.querySelectorAll("td.num").forEach((td) => print(td, at + 100, 260)); });
      qb(".needs li").forEach((li, i) => rise(li, d + 600 * k + i * 70, 380));
      const rows = qb(".p2 .col:last-child .tbl tbody tr");
      rows.forEach((tr, i) => {
        const at = d + 260 + i * 95 * k, nums = tr.querySelectorAll("td.num"), done = at + 120 + Math.max(0, nums.length - 1) * 90 + 200;
        rise(tr, at, 400);
        nums.forEach((td, j) => print(td, at + 120 + j * 90));       // MIN, TYP, MAX read off in turn
        holdRed(tr, done);                                            // the row is named a breach once its readings are down
        tr.querySelectorAll("td.over").forEach((td) => flash(td, done, RED_WASH, 1300));
      });
      qb(".tcap, .notes").forEach((n, i) => fade(n, d + 1200 * k + i * 80, 420));
    },
    3(d, k) {
      qb("h3, .condl").forEach((h, i) => rise(h, d + i * 60, 400));
      curvesIn(d + 120, k, false);
      qb(".figcap").forEach((n, i) => fade(n, d + 300 + i * 170 * k, 420));
    },
    4(d, k) {
      qb("h3, .condl").forEach((h, i) => rise(h, d + i * 60, 400));
      const rows = qb(".regmap tbody tr");
      rows.forEach((tr, i) => [...tr.children].forEach((td, j) => print(td, d + 160 + i * 55 * k + j * 70, 300)));
      const backed = qb(".backed .dem, .backed .att, .backed .no"), t1 = d + 300 + rows.length * 55 * k;
      backed.forEach((s, i) => {
        const end = getComputedStyle(s).backgroundSize;
        anim(s, [{ backgroundSize: end.replace(/^\S+/, "0%") }, { backgroundSize: end }], { delay: t1 + i * 80 * k, duration: 440, easing: "cubic-bezier(.65, 0, .25, 1)" });
      });
      qb(".p4 .col:last-child tbody tr").forEach((tr, i) => rise(tr, d + 300 + i * 70 * k, 380));
      qb(".tcap").forEach((n) => fade(n, t1 + 400, 420));
    },
  };
  function play(d) { if (!still()) PLAY[state.page](d, 1); }

  /* re-specifying the sheet in place: another part, job or briefing. A print head runs down the sheet: above it the new
     datasheet, below it the last one, so no reading ever sits under the wrong part number */
  const SWEEP = 840;
  const inOut = (t) => (t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2);
  function atSweep(y) { let lo = 0, hi = 1; for (let i = 0; i < 22; i++) { const m = (lo + hi) / 2; if (inOut(m) < y) lo = m; else hi = m; } return lo; }
  function keepSheet() {                   // a still copy of the sheet as it stands
    const c = $("sheet").cloneNode(true);
    c.removeAttribute("id"); c.removeAttribute("aria-live");
    c.querySelectorAll("[id]").forEach((n) => n.removeAttribute("id"));
    c.classList.add("still");
    return c;
  }
  function respec() {
    const hlEl = $("body").querySelector(".cmp-wrap .hl"), hl = hlEl && hlEl.dataset.y != null ? +hlEl.dataset.y : null;
    if (still() || matchMedia("(max-width: 860px)").matches) {
      draw();
      if (!still()) { const b = $("body"); b.classList.remove("paging-in"); void b.offsetWidth; b.classList.add("paging-in"); }
      return;
    }
    const desk = document.querySelector(".desk"), S = $("sheet"), db = desk.getBoundingClientRect(), sb = S.getBoundingClientRect();
    const old = keepSheet();
    old.style.boxShadow = "none";
    draw();
    markHL(hl);
    const ghost = document.createElement("div"), head = document.createElement("i");
    ghost.className = "leaf"; ghost.setAttribute("aria-hidden", "true"); ghost.append(old);
    head.className = "printhead"; head.setAttribute("aria-hidden", "true");
    Object.assign(ghost.style, { left: `${sb.left - db.left}px`, top: `${sb.top - db.top}px`, width: `${sb.width}px`, height: `${sb.height}px` });
    Object.assign(head.style, { left: `${sb.left - db.left}px`, top: `${sb.top - db.top}px`, width: `${sb.width}px` });
    desk.append(ghost, head);
    const H = sb.height, W = sb.width;
    const LINES = "td, th, li, h3, p, .pnum, .ptitle, .docline, .sfoot > span, text, .legend span";
    const boxes = [...old.querySelectorAll(LINES), ...$("sheet").querySelectorAll(LINES)].map((el) => {
      const b = el.getBoundingClientRect(), o = el.closest(".leaf") ? ghost.getBoundingClientRect() : sb;
      return [b.left - o.left, b.top - o.top, b.right - o.left, b.bottom - o.top];
    }).filter((b) => b[3] - b[1] > 0 && b[3] - b[1] < H * 0.5);
    tween(SWEEP, 0, (f) => {
      if (f >= 1) { ghost.remove(); head.remove(); return; }
      const y = H * inOut(f);
      // the last sheet below the head, and every line the head is still crossing (on either sheet), whole
      let path = `M0 ${y.toFixed(1)}H${W}V${H}H0Z`;
      for (const [l, t, r, b] of boxes) if (t < y && b > y) path += `M${l.toFixed(1)} ${t.toFixed(1)}H${r.toFixed(1)}V${b.toFixed(1)}H${l.toFixed(1)}Z`;
      ghost.style.clipPath = `path("${path}")`;
      head.style.transform = `translateY(${y.toFixed(1)}px)`;
      head.style.opacity = String(f > 0.9 ? (1 - f) / 0.1 : 1);
    });
    // each reading beyond a rating flashes as the head prints it; this part's curve is traced once its chart is printed
    const at = (el) => SWEEP * atSweep(Math.min(1, Math.max(0, (el.getBoundingClientRect().top - sb.top) / H)));
    qb("td.over").forEach((td) => flash(td, at(td) + 120, RED_WASH, 1200));
    qb("tr.over").forEach((tr) => holdRed(tr, at(tr) + 120));
    qb(".feat .bad").forEach((b) => flash(b, at(b) + 120, RED_WASH, 1200));
    if (state.page === 3) qb(".crv.me").forEach((p) => {
      const len = p.getTotalLength();
      anim(p, [{ strokeDasharray: `${len} ${len}`, strokeDashoffset: `${len}` }, { strokeDasharray: `${len} ${len}`, strokeDashoffset: "0" }], { delay: at(p.closest(".draw")) + 140, duration: 900, easing: "cubic-bezier(.45, 0, .25, 1)" });
    });
    if (state.page === 4) qb(".backed .dem, .backed .att, .backed .no").forEach((s) => {
      const end = getComputedStyle(s).backgroundSize;
      anim(s, [{ backgroundSize: end.replace(/^\S+/, "0%") }, { backgroundSize: end }], { delay: at(s) + 100, duration: 420, easing: "cubic-bezier(.65, 0, .25, 1)" });
    });
  }
  /* paging: the sheet lifts over its top edge and away; going back, the last one comes down again */
  const FLIP = 760;
  function flipSheet(dir, drawFn) {
    if (still() || matchMedia("(max-width: 860px)").matches) return false;
    const desk = document.querySelector(".desk"), S = $("sheet");
    const db = desk.getBoundingClientRect(), sb = S.getBoundingClientRect();
    const keep = () => { const c = keepSheet(); c.style.boxShadow = "0 1px 2px rgba(18, 20, 23, .2), 0 12px 26px -12px rgba(18, 20, 23, .4)"; return c; };
    const old = keep();
    drawFn();
    const box = [sb.left - db.left, sb.top - db.top, sb.width, sb.height];
    const place = (o) => Object.assign(o.style, { left: `${box[0]}px`, top: `${box[1]}px`, width: `${box[2]}px`, height: `${box[3]}px` });
    const leaf = (page, cls) => {
      const o = document.createElement("div");
      o.className = `leaf ${cls}`; o.setAttribute("aria-hidden", "true"); place(o); o.append(page);
      const s = document.createElement("i"); s.className = "shade"; o.append(s);
      desk.append(o);
      return o;
    };
    const parts = [];
    let last;
    if (dir > 0) {
      const cast = document.createElement("i");
      cast.className = "cast"; cast.setAttribute("aria-hidden", "true"); place(cast); desk.append(cast);
      const f = leaf(old, "up");
      parts.push(f, cast);
      last = f.animate([{ transform: "rotateX(0deg) scale(1)", opacity: 1 }, { transform: "rotateX(64deg) translateY(-1%) scale(.94)", opacity: 1, offset: 0.78 }, { transform: "rotateX(80deg) translateY(-2%) scale(.92)", opacity: 0 }], { duration: FLIP, easing: "cubic-bezier(.42, .02, .72, .5)", fill: "forwards" });
      f.querySelector(".shade").animate([{ opacity: 0 }, { opacity: 0.6 }], { duration: FLIP, easing: "ease-in", fill: "forwards" });
      cast.animate([{ opacity: 0.2 }, { opacity: 1, offset: 0.3 }, { opacity: 0 }], { duration: FLIP, easing: "ease-out", fill: "forwards" });
    } else {
      const nu = keep();
      const under = leaf(old, "under"), f = leaf(nu, "down");
      parts.push(under, f);
      last = f.animate([{ transform: "rotateX(80deg) translateY(-2%) scale(.92)", opacity: 0 }, { transform: "rotateX(64deg) translateY(-1%) scale(.94)", opacity: 1, offset: 0.22 }, { transform: "rotateX(0deg) scale(1)", opacity: 1 }], { duration: FLIP, easing: "cubic-bezier(.22, .6, .3, 1)", fill: "both" });
      f.querySelector(".shade").animate([{ opacity: 0.6 }, { opacity: 0 }], { duration: FLIP, easing: "ease-out", fill: "both" });
      under.querySelector(".shade").animate([{ opacity: 0 }, { opacity: 0.25 }], { duration: FLIP, easing: "ease-in", fill: "both" });
    }
    hold(FLIP);
    const done = () => parts.forEach((p) => p.remove());
    last.finished.then(done, done);
    return true;
  }

  /* ------------------------------------------------------------ render */
  function draw() {
    $("mast").innerHTML = mastHTML();
    $("body").innerHTML = [page1, page2, page3, page4][state.page - 1]();
    $("sfoot").innerHTML = footHTML();
    drawPins();
    drawCharts();
    sync();
    markHL();
  }
  function render(kind, dir = 1) {   // "page" pages the sheet; "respec" re-specifies it in place; "open" the first view; "now" no motion
    land();
    if (kind === "respec") { respec(); return; }
    if (kind === "page") {
      if (flipSheet(dir, draw)) { if (dir > 0) play(200); return; }
      draw();
      if (!still()) {
        const b = $("body");
        b.classList.remove("paging-in"); void b.offsetWidth; b.classList.add("paging-in");
        b.addEventListener("animationend", () => b.classList.remove("paging-in"), { once: true });
        play(120);
      }
      return;
    }
    draw();
    if (kind === "open") play(240);
  }

  function page(n, dir) {
    n = ((n - 1 + 4) % 4) + 1;
    if (n === state.page) return;
    const d = dir || (n > state.page ? 1 : -1);
    state.page = n;
    render("page", d);
  }
  function nextPage() { if (busy()) { land(); return; } page(state.page + 1); }   // a second press lands the page that is playing
  function part(x) { if (x === state.part) return; state.part = x; render("respec"); }
  const cycle = (list, cur, d) => list[(list.indexOf(cur) + d + list.length) % list.length];

  document.addEventListener("click", (e) => {
    const t = e.target.closest("[data-part],[data-page],[data-brief]");
    if (!t || t.tagName === "SELECT" || t.closest(".leaf")) return;
    if (t.dataset.page) page(+t.dataset.page);
    else if (t.dataset.brief) { state.brief = t.dataset.brief; render("respec"); }
    else if (t.dataset.part) {
      if (t.dataset.model) state.model = t.dataset.model;
      if (t.dataset.part === state.part && !t.dataset.model) return;
      state.part = t.dataset.part; render("respec");
    }
  });
  $("job").addEventListener("change", (e) => { state.job = e.target.value; render("respec"); });
  $("next").addEventListener("click", nextPage);
  $("prev").addEventListener("click", () => page(state.page - 1));
  document.addEventListener("keydown", (e) => {
    if (e.ctrlKey || e.metaKey || e.altKey) return;
    if ((e.target.tagName || "").toLowerCase() === "select") return;
    const k = e.key;
    let done = true;
    if (k === " " && e.shiftKey) page(state.page - 1);
    else if (k === " " || k === "PageDown" || k === "ArrowRight" || k === "ArrowDown") nextPage();
    else if (k === "PageUp" || k === "ArrowLeft" || k === "ArrowUp" || k === "Backspace") page(state.page - 1);
    else if (k === "Home") page(1);
    else if (k === "End") page(4);
    else if (/^[1-4]$/.test(k)) page(+k);
    else if (/^[abc]$/i.test(k)) part(k.toLowerCase());
    else if (k === "j" || k === "J") { state.job = cycle(D.jobs.map((j) => j.id), state.job, e.shiftKey ? -1 : 1); render("respec"); }
    else if (k === "m" || k === "M") { state.model = cycle(D.models.map((m) => m.id), state.model, e.shiftKey ? -1 : 1); state.part = "b"; render("respec"); }
    else if (k === "t" || k === "T") { state.brief = cycle(BRIEF.map((b) => b.id), state.brief, e.shiftKey ? -1 : 1); render("respec"); }
    else done = false;
    if (done) e.preventDefault();
  });
  document.addEventListener("keydown", (e) => {     // the model tab is a span: Enter or Space on it selects part b
    if ((e.key === "Enter" || e.key === " ") && e.target.matches && e.target.matches(".part[data-part='b']")) { e.preventDefault(); e.stopImmediatePropagation(); part("b"); }
  }, true);
  let rt = 0;
  addEventListener("resize", () => { clearTimeout(rt); rt = setTimeout(() => { land(); drawPins(); drawCharts(); marks(); markHL(); }, 120); });

  const m = location.hash.match(/^#([abc])([1-4])$/);
  if (m) { state.part = m[1]; state.page = +m[2]; }
  chrome();
  let opened = false;
  const open = () => { if (opened) return; opened = true; render("open"); };
  (document.fonts ? document.fonts.ready : Promise.resolve()).then(open);
  setTimeout(open, 1200);
})();
