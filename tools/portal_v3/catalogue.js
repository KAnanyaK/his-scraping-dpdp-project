/* The Catalogue (Portal v3): the recorded run catalogued, a plate at a time.
   Each view is a spread: on the left a plate, one real object the run left behind; on the right its
   catalogue entry, one fact set large. Comparanda a / b / c (ours, an AI model, the baseline) flip in place.
   Keys: Space next (through a, b, c, then the next plate), Shift+Space back, arrows, a b c, 1-9 and 0 for
   a plate, J job, M model, T what the model was told, Home / End. Every figure is the recorded one. */
(() => {
  "use strict";
  const D = JSON.parse(document.getElementById("catalogue-data").textContent);
  const $ = (id) => document.getElementById(id);
  const esc = (s) => String(s == null ? "" : s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const fmt = (n) => Number(n).toLocaleString("en-IN");
  const day = (iso) => new Date(String(iso).slice(0, 10) + "T00:00:00Z").toLocaleDateString("en-GB", { day: "numeric", month: "short", year: "numeric", timeZone: "UTC" });
  const still = () => matchMedia("(prefers-reduced-motion: reduce)").matches;
  const plural = (n, one, many) => `${fmt(n)} ${n === 1 ? one : many}`;

  const COLS = D.columns, PTS = D.patients, FOLLOW = D.patient.index;
  const HOLD = COLS.length * PTS.length;
  const CAT = Object.fromEntries(D.categories.map((c) => [c.id, c.label]));
  const MODS = D.modules;
  const modOf = (i) => MODS.find((m) => i >= m.start && i < m.start + m.count);
  const BRIEF = D.briefings;
  const RULES = D.rules;

  const state = { plate: 0, comp: "a", job: D.jobs[0].id, model: (D.models.find((m) => m.id === "claude-opus-5-5") || D.models[0]).id, brief: "policy" };
  const JOB = () => D.jobs.find((j) => j.id === state.job);
  const TECH = (x) => D.techniques[x === "a" ? "ours" : x === "c" ? "base" : `${state.model}|${state.brief}`];
  const RUN = (x) => TECH(x).jobs[state.job][0];
  const MODEL = () => D.models.find((m) => m.id === state.model);
  const briefLabel = () => (BRIEF.find((b) => b.id === state.brief) || {}).label || "";

  /* ------------------------------------------------------------ what a run comes to */
  const values = (r) => r.cols.length * (r.named ? r.patients.length : r.rows);
  const held = (r) => Object.values(r.rules).filter((v) => v[0] === "pass").length;
  const applicable = (r) => Object.values(r.rules).filter((v) => v[0] !== "not_applicable").length;
  const named = (r) => { const e = (r.audit || []).find((e) => e.event === "extraction"); return e && e.subjects ? e.subjects.length : 0; };
  const distinct = (x) => { const t = TECH(x); return (t.bench.distinct || {})[state.job] || 1; };
  const trapOf = (x) => { const t = TECH(x).bench.traps || {}; return t[state.job] || null; };
  const who = (x) => x === "a" ? ["Ours", "the reference"] : x === "c" ? ["Baseline", "every module, every record"] : [MODEL().name, briefLabel()];
  const replays = (x) => x === "b" ? `Run 1 of ${TECH(x).samples} recorded, as the portal replays it` : x === "a" ? "One run: the job's expert field list, nothing sampled" : "One run: every module, every record";
  const totalPages = (x) => Object.values(TECH(x).jobs).reduce((s, runs) => s + (runs[0].pages || 0), 0);

  /* ------------------------------------------------------------ the plates */
  const PLATES = [
    { id: "hospital", short: "Hospital", title: "The hospital", comp: false },
    { id: "request", short: "Request", title: "The request", comp: false },
    { id: "taken", short: "Taken", title: "Taken", comp: true },
    { id: "cost", short: "Cost", title: "The cost", comp: true },
    { id: "declared", short: "Declared", title: "Declared", comp: true },
    { id: "left", short: "As it left", title: "As it left", comp: true },
    { id: "kept", short: "Kept until", title: "Kept until", comp: true },
    { id: "repeated", short: "Repeated", title: "Repeated", comp: true },
    { id: "custody", short: "Custody", title: "Custody", comp: true },
    { id: "index", short: "Index", title: "Index", comp: false },
  ];
  const COVER = { id: "cover", short: "Cover", title: "Catalogue of a run", comp: false };
  const PLATE = () => (state.plate === 0 ? COVER : PLATES[state.plate - 1]);
  const N = PLATES.length + 1;                       // the cover and ten plates

  // Each comparandum plate: the figure, the value shown in the comparanda list, the entry, the object.
  const FIG = {
    taken(x) { const r = RUN(x), bad = r.oos.length > 0, per = r.named ? r.patients.length : r.rows;
      const how = r.named ? `${plural(r.cols.length, "field", "fields")} × ${plural(r.patients.length, "patient", "patients")}` : `${plural(r.cols.length, "field", "fields")} × ${fmt(r.rows)} rows, no record number kept`;
      const oos = bad ? ` · <span class="bad">${fmt(r.oos.length * per)} out of purpose</span>` : "";
      return { n: fmt(values(r)), u: `of ${fmt(HOLD)}`, cap: `values: ${how}${oos}`, v: fmt(values(r)), vbad: bad }; },
    cost(x) { const r = RUN(x), k = kinds(r);
      return { n: fmt(r.pages), u: r.pages === 1 ? "page load" : "page loads", cap: `${plural(k.search, "search", "searches")}, ${plural(k.list, "list page", "list pages")}, ${plural(k.record, "record page", "record pages")}`, v: fmt(r.pages) }; },
    declared(x) { const r = RUN(x), h = held(r), a = applicable(r), b = TECH(x).bench;
      const mean = x === "b" && b.per_task ? ` · mean over ${TECH(x).samples} runs ${Number(b.per_task[state.job]).toFixed(3)}` : "";
      return { n: fmt(h), u: `of ${a} rules held`, bad: h < a, cap: `score ${r.score.toFixed(3)}${mean}`, v: `${h} of ${a}` }; },
    left(x) { const r = RUN(x), e = r.export, bad = e.leaked > 0;
      const cap = e.kind === "tok" ? `record number left as <b>${esc(e.token)}</b>` : e.kind === "raw" ? `<span class="bad">identifiers left as they were read</span>` : "no identifier left";
      return { n: fmt(e.leaked), u: e.leaked === 1 ? "raw identifier" : "raw identifiers", bad, cap, v: e.kind === "tok" ? "token" : e.kind === "raw" ? `${fmt(e.leaked)} raw` : "none", vbad: bad }; },
    kept(x) { const r = RUN(x), j = JOB(), over = r.rules["SL-01"] && r.rules["SL-01"][0] === "fail";
      if (!r.erase) return { n: "Never", u: "", bad: true, cls: "mid", cap: `<span class="bad">no retention declared; nothing schedules its erasure</span>`, v: "never", vbad: true };
      return { n: day(r.erase), u: "", bad: over, cls: "long", cap: `${plural(r.retention, "day", "days")}, of the ${fmt(j.ceiling)} the purpose allows`, v: day(r.erase), vbad: over }; },
    repeated(x) { const n = distinct(x), s = TECH(x).samples;
      return { n: fmt(n), u: n === 1 ? "decision" : "decisions", cap: x === "b" ? `in ${s} recorded runs of this job` : "one run; nothing is sampled", v: x === "b" ? `${n} in ${s}` : `${n}` }; },
    custody(x) { const r = RUN(x), n = named(r);
      return { n: fmt(n), u: n === 1 ? "patient named" : "patients named", cap: `in the audit log, as keyed tokens · chain ${D.meta.chain_intact ? "verified" : "broken"}`, v: fmt(n) }; },
  };

  function kinds(r) {
    const k = { search: 0, list: 0, record: 0 };
    for (const v of r.visits || []) k[v[0]] = (k[v[0]] || 0) + 1;
    return k;
  }

  /* ------------------------------------------------------------ the right page */
  function figureHTML(f) {
    return `<p class="fig ${f.cls || ""} ${f.bad ? "bad" : ""}"><span class="n">${esc(f.n)}</span>${f.u ? `<span class="u">${esc(f.u)}</span>` : ""}</p>
      <p class="figcap">${f.cap}</p>`;
  }

  function comparandaHTML(p) {
    return `<ul class="comp" aria-label="Comparanda">${["a", "b", "c"].map((x) => {
      const f = FIG[p.id](x), [w, sub] = who(x);
      return `<li><button type="button" data-comp="${x}" aria-pressed="${x === state.comp}"><span class="l">${x}</span>
        <span class="who">${esc(w)}<small>${esc(sub)}</small></span><span class="v ${f.vbad || f.bad ? "bad" : ""}">${esc(f.v)}</span></button></li>`;
    }).join("")}</ul>`;
  }

  const dl = (rows) => `<dl class="rec-dl">${rows.filter(Boolean).map(([k, v, cls]) => `<dt>${esc(k)}</dt><dd class="${cls || ""}">${v}</dd>`).join("")}</dl>`;

  function entryRows(p, x) {
    const j = JOB();
    if (p.id === "hospital") {
      const counts = D.categories.map((c) => [c.label, COLS.filter((k) => k.cat === c.id).length]).filter((c) => c[1]);
      return [
        ["Modules", `${MODS.length} found in ${D.meta.found} page loads`],
        ["Categories", counts.map(([l, n]) => `${n} ${esc(l.toLowerCase())}`).join(" · ")],
        ["Connection", D.meta.tls ? "TLS, observed by the browser" : "not encrypted"],
        ["Account", `${esc(D.meta.account)} <small>service account</small>`],
        ["Authorisation", esc(D.meta.authorisation)],
        ["Recorded", day(D.meta.generated)],
      ];
    }
    if (p.id === "request") {
      const not = D.categories.filter((c) => !j.allowed.includes(c.id)).map((c) => c.label.toLowerCase());
      return [
        ["Purpose", esc(j.purpose_label)],
        ["Allows", esc(j.allowed.map((c) => CAT[c].toLowerCase()).join(", "))],
        ["Not for it", esc(not.join(", ") || "nothing")],
        ["May keep", `up to ${fmt(j.ceiling)} days`],
        ["Patients", j.single ? "one, bound by the harness at run time" : "every patient"],
        j.trap ? ["Trap", esc(j.trap)] : null,
      ];
    }
    const r = RUN(x), t = TECH(x), b = t.bench;
    if (p.id === "taken") {
      const trap = trapOf(x);
      return [
        ["Fields read", `${r.cols.length} of ${COLS.length}`],
        ["The job needs", `${r.hit} of ${r.needed} obtained${r.missed.length ? ` <small>not read: ${esc(r.missed.map((i) => COLS[i].label).join(", "))}</small>` : ""}`],
        ["Out of purpose", r.oos.length ? `<span class="bad">${esc(r.oos.map((i) => COLS[i].label).join(", "))}</span>` : "none"],
        ["Patients", r.named ? `${r.patients.length} of ${PTS.length}` : `${fmt(r.rows)} rows, no record number kept`],
        j.trap && trap ? ["Trap", trap[0] === trap[1] ? `held in ${trap[0]} of ${trap[1]} ${trap[1] === 1 ? "run" : "runs"}` : `<span class="bad">taken in ${trap[1] - trap[0]} of ${trap[1]} ${trap[1] === 1 ? "run" : "runs"}</span>`] : null,
      ];
    }
    if (p.id === "cost") {
      const k = kinds(r);
      return [
        ["Searches", fmt(k.search)], ["List pages", fmt(k.list)], ["Record pages", fmt(k.record)],
        ["All four jobs", `${fmt(totalPages(x))} page loads${x === "b" ? " <small>this run</small>" : ""}`],
        x === "b" && b.page_loads != null ? ["Over 5 runs", `${fmt(b.page_loads)} page loads a run <small>mean, all four jobs</small>`] : null,
        ["Before any job", `${D.meta.found} page loads to find the modules, shared`],
      ];
    }
    if (p.id === "declared") {
      return [["The rules", `<div class="rules">${RULES.map((rule) => {
        const v = r.rules[rule.id] || ["not_applicable"], ok = v[0] === "pass";
        return `<span>${esc(rule.id)}</span><span>${esc(rule.title)}</span><span class="${ok ? "" : v[0] === "fail" ? "bad" : ""}">${ok ? "held" : v[0] === "fail" ? "broken" : "n/a"}</span>`;
      }).join("")}</div>`]];
    }
    if (p.id === "left") {
      const e = r.export, quasi = r.cols.some((i) => COLS[i].cat === "quasi_identifier" && COLS[i].field !== "sex");
      return [
        ["Record number", e.kind === "tok" ? `<b>${esc(e.token)}</b> <small>keyed token</small>` : e.kind === "raw" ? `<span class="bad">${esc(D.patient.mrn)} raw</span> <small>masked here</small>` : "not exported"],
        quasi ? ["Date of birth, PIN", e.generalised ? "coarsened: the year, three digits" : `<span class="bad">as read</span>`] : null,
        ["Messages", `${fmt(e.messages)} HL7 v2 · ${fmt(e.resources)} FHIR resources`],
        ["About others", plural(r.hl7_others || 0, "message", "messages")],
      ];
    }
    if (p.id === "kept") {
      const purge = (r.audit || []).find((e) => e.event === "purge"), s = r.sidecar || {};
      return [
        ["Retention", r.retention ? `${plural(r.retention, "day", "days")} <small>allowed ${fmt(JOB().ceiling)}</small>` : `<span class="bad">not declared</span>`],
        ["Erased by", r.mechanism ? esc(r.mechanism) : `<span class="bad">nothing</span>`],
        ["The key", s.key_holder ? `held apart by ${esc(s.key_holder)}, erased with the export` : "none: nothing was pseudonymised"],
        ["Erased", purge ? `${esc(purge.note.split(":")[0].replace(/^erased /, ""))} on ${day(purge.at)}` : `<span class="bad">never</span>`],
      ];
    }
    if (p.id === "repeated") {
      const range = (b.range || {})[state.job];
      return [
        x === "b" ? ["Same as run 1", `${b.stable} of ${b.repeats} repeats <small>all four jobs</small>`] : ["Runs", "one a job"],
        ["Every rule held", `${b.runs_clean} of ${b.runs} runs`],
        range ? ["Score, this job", range[0] === range[1] ? range[0].toFixed(3) : `${range[0].toFixed(3)} to ${range[1].toFixed(3)}`] : null,
        b.coverage != null ? ["Needed fields", `${Math.round(b.coverage * 100)}% obtained, all runs`] : null,
      ];
    }
    if (p.id === "custody") {
      const ex = (r.audit || []).find((e) => e.event === "extraction") || {};
      return [
        ["Events", esc((r.audit || []).map((e) => e.event).join(", "))],
        ["Account", esc(ex.account || "")],
        ["Authorisation", esc(ex.authorisation || "")],
        ["Scoped", ex.scoped ? "every fetch filtered to one patient" : "no"],
        ["Log kept", `${D.meta.log_days} days, apart from the export`],
      ];
    }
    return [];
  }

  function rightHTML() {
    const p = PLATE(), x = state.comp;
    if (p.id === "cover") return coverHTML();
    if (p.id === "index") return colophonHTML();
    let fig;
    if (p.id === "hospital") fig = { n: fmt(HOLD), u: "values", cap: `${PTS.length} patients × ${COLS.length} fields` };
    else if (p.id === "request") { const j = JOB(); fig = { n: fmt(j.needed.length), u: "fields needed", cap: `of the ${COLS.length} it holds, ${j.single ? "for one patient" : "for every patient"}` }; }
    else fig = FIG[p.id](x);
    const prov = p.comp ? replays(x) : p.id === "hospital" ? `Synthetic hospital: ${D.meta.records} records a module, seed ${D.meta.seed}` : `Purpose policy: ${esc(JOB().purpose_label.toLowerCase())}`;
    return `<header class="eh"><span class="no">${state.plate}</span><h2>${esc(p.title)}</h2></header>
      ${figureHTML(fig)}
      ${p.comp ? comparandaHTML(p) : ""}
      ${dl(entryRows(p, x))}
      <p class="prov">${prov}</p>`;
  }

  function coverHTML() {
    return `<header class="eh cover"><h2>Catalogue<br>of a run</h2></header>
      <p class="figcap">${esc(JOB().name)} · recorded ${day(D.meta.generated)}</p>
      <ol class="contents" aria-label="Contents">${PLATES.map((p, i) => `<li><button type="button" data-plate="${i + 1}"><b>${i + 1}</b><span>${esc(p.title)}</span></button></li>`).join("")}</ol>
      <p class="prov">Space opens the catalogue</p>`;
  }

  function fanHTML() {        // the comparanda as a fan of colour stocks, each with what it took for this job
    const angles = { c: -36, b: -18, a: 0 };
    return `<div class="obj fan" role="img" aria-label="${esc(["a", "b", "c"].map((x) => `${who(x)[0]}: ${FIG.taken(x).n} of ${fmt(HOLD)} values`).join("; "))}">${["c", "b", "a"].map((x, k) => {
      const [w, sub] = who(x), f = FIG.taken(x);
      return `<div class="blade ${x}" style="--r:${angles[x]}deg;--k:${k}"><span class="bd ${x}">${x}</span>
        <span class="nm">${esc(w)}${x === "c" ? "" : `<small>${esc(sub)}</small>`}</span>
        <span class="tally"><span class="num">${esc(f.n)}</span><span class="of">of ${fmt(HOLD)} values taken</span></span></div>`;
    }).join("")}<span class="rivet" aria-hidden="true"></span></div>`;
  }

  function colophonHTML() {
    const rec = D.meta.recorded || {};
    return `<header class="eh"><span class="no">${state.plate}</span><h2>Index</h2></header>
      ${dl([
        ["Typeface", "Archivo, by Omnibus-Type <small>SIL Open Font License</small>"],
        ["Recorded", `${day(D.meta.generated)}, the run the portal replays`],
        ["Hospital", `synthetic, ${D.meta.records} records a module, seed ${D.meta.seed}; served over TLS, signed in as ${esc(D.meta.account)}`],
        ["Models", D.models.map((m) => `${esc(m.name)}${rec[m.id] ? ` <small>${esc(rec[m.id])}</small>` : ""}`).join("<br>")],
        ["Computed by", "the project's own code: the rules engine, the export and its audit, the retention record, the audit log"],
        ["Privacy", "no raw identifier on these pages; the builder checks every value and refuses to write"],
      ])}
      <p class="prov">Computed from the run of ${day(D.meta.generated)}</p>`;
  }

  /* ------------------------------------------------------------ the plate (left page) */
  function inventoryHTML(r) {
    const job = JOB(), need = new Set(job.needed.map((n) => n.col));
    const on = r ? new Set(r.cols) : null, oos = r ? new Set(r.oos) : new Set();
    const read = r ? new Set(r.named ? r.patients : []) : null;
    const fcls = (i) => !on ? "f" : oos.has(i) ? "f oos" : on.has(i) ? "f" : need.has(i) ? "f off miss" : "f off";
    const mods = MODS.map((m) => `<section class="mod"><h3>${esc(m.title)}</h3><p class="flds">${COLS.slice(m.start, m.start + m.count).map((c, k) =>
      `<span class="${fcls(m.start + k)}" data-col="${m.start + k}" title="${esc(CAT[c.cat])}">${esc(c.label)}</span>`).join("")}</p></section>`).join("");
    const pts = PTS.map((mrn, i) => `<li class="${read && !read.has(i) ? "off" : ""} ${i === FOLLOW ? "me" : ""}" data-pt="${i}">${esc(mrn)}</li>`).join("");
    const note = r && !r.named ? `<p class="note">${fmt(r.rows)} rows read without a record number: no patient can be named</p>` : "";
    return `<div class="obj inv"><div class="mods">${mods}</div><div class="pts"><h3 class="ttl">Patients</h3><ol>${pts}</ol>${note}</div></div>`;
  }

  function reInk(r) {      // the same inventory, re-inked in place for another comparandum
    const job = JOB(), need = new Set(job.needed.map((n) => n.col)), on = new Set(r.cols), oos = new Set(r.oos);
    const read = new Set(r.named ? r.patients : []);
    document.querySelectorAll("#plate .f").forEach((el) => {
      const i = +el.dataset.col;
      el.className = oos.has(i) ? "f oos" : on.has(i) ? "f" : need.has(i) ? "f off miss" : "f off";
    });
    document.querySelectorAll("#plate .pts li").forEach((el) => {
      const i = +el.dataset.pt;
      el.classList.toggle("off", !read.has(i));
    });
    const pts = document.querySelector("#plate .pts");
    const old = pts.querySelector(".note");
    if (old) old.remove();
    if (!r.named) pts.insertAdjacentHTML("beforeend", `<p class="note">${fmt(r.rows)} rows read without a record number: no patient can be named</p>`);
  }

  function slipHTML() {
    const j = JOB();
    return `<div class="obj slip"><p class="ask">${esc(j.description)}</p>
      <dl class="need">${j.needed.map((n) => `<dt>${esc(COLS[n.col].label)}<small>${esc(modOf(n.col).short)}</small></dt><dd>${esc(n.why || "")}</dd>`).join("")}</dl>
      ${j.trap ? `<p class="trap"><b>Trap</b><span>${esc(j.trap)}</span></p>` : ""}</div>`;
  }

  function logHTML(r) {
    const lines = (r.visits || []).map((v, i) => {
      const [w, mod, n] = v, d = w === "search" ? "search" : w === "list" ? `page ${n}` : `row ${n + 1}`;
      const cls = w === "search" ? "sr" : w === "list" ? "pg" : "";
      return `<li><span class="k">${String(i + 1).padStart(3, "0")}</span><span class="m">${esc(mod)}</span><span class="w ${cls}">${esc(d)}</span></li>`;
    }).join("");
    return `<div class="obj fill"><h3 class="ttl">Page loads, in order</h3><ol class="log">${lines}</ol></div>`;
  }
  function fitLog() {      // the log fills at most four columns: its line height gives way, never its size
    const ol = document.querySelector("#plate .log");
    if (!ol || matchMedia("(max-width: 860px)").matches) return;
    const n = ol.children.length, rows = Math.max(1, Math.ceil(n / 4));
    const fs = parseFloat(getComputedStyle(ol).fontSize);
    const lh = Math.max(fs * 1.18, Math.min(fs * 1.5, ol.clientHeight / rows - 0.5));
    ol.style.setProperty("--lh", `${lh.toFixed(2)}px`);
  }

  const CLAIMS = [
    ["lawful-basis reference", "Lawful basis"], ["transport encryption", "Transport"], ["encryption at rest", "Encryption at rest"],
    ["access control", "Access control"], ["pseudonymisation on export", "Pseudonymisation"], ["deletion mechanism", "Deletion"],
    ["privacy notice", "Privacy notice"], ["machine-readable notice", "Notice, machine-readable"], ["audit log", "Audit log"],
    ["accountable party", "Accountable party"], ["record of processing", "Record of processing"],
  ];
  function formHTML(r) {
    const by = Object.fromEntries((r.claims || []).map((c) => [c.control, c]));
    const reg = (key) => { const v = D.register[key]; return key === "lawful-basis reference" ? (v || {})[JOB().purpose] : v; };
    const row = (label, value, cls, backing) => `<div class="r"><span class="c">${esc(label)}</span><span class="d ${cls || ""}">${value}</span><span class="b">${backing || ""}</span></div>`;
    const head = [
      `<div class="r rh"><span class="c h">Control</span><span class="d h">Declared</span><span class="b h">Backed by the register</span></div>`,
      row("Purpose", r.specified ? esc(JOB().purpose_label) : "not specified", r.specified ? "" : "nil"),
      row("Retention", r.retention ? esc(plural(r.retention, "day", "days")) : "not declared", r.retention ? "" : "nil"),
      row("Onward use", r.onward.length ? esc(r.onward.join(", ")) : "none", r.onward.length ? "no" : ""),
    ];
    const rest = CLAIMS.map(([key, label]) => {
      const c = by[key];
      if (!c) return row(label, "not declared", "nil");
      const v = c.declared === "True" ? "yes" : c.declared.split(/\s+--\s+|\s+/)[0];
      if (!c.ok) return row(label, esc(v), "", `<span class="no">nothing</span><small>${esc(c.note)}</small>`);
      const g = reg(key) || {};
      return row(label, esc(v), "", `<span class="${c.basis === "demonstrated" ? "dem" : "att"}">${esc(g.id || "")}</span><small>${esc(c.basis)}</small>`);
    });
    return `<div class="obj doc"><h3 class="ttl">Manifest, as declared</h3><div class="form">${head.join("")}${rest.join("")}</div></div>`;
  }

  function hl7HTML(r) {
    const seg = (s) => {
      const parts = s.split("|"), name = parts[0];
      const body = parts.map((f, i) => {
        if (i === 0) return `<b>${esc(f)}</b>`;
        const cls = /PSN-[0-9a-f]+/.test(f) ? "id" : /•|\*{3,}/.test(f) ? "raw" : "";
        return cls ? `<span class="${cls}">${esc(f)}</span>` : esc(f);
      }).join(`<span class="p">|</span>`);
      return `<span class="seg-l ${name === "MSH" ? "msh" : ""}">${body}</span>`;
    };
    const mine = (r.hl7 || []).length;
    const msgs = (r.hl7 || []).map((m) => `<p class="msg">${m.map(seg).join("")}</p>`).join("");
    const none = !mine ? `<p class="more">Nothing about this patient was exported.</p>` : "";
    return `<div class="obj"><h3 class="ttl">HL7 v2, about ${esc(D.patient.mrn)}</h3><div class="msgs">${msgs}${none}<p class="more tail"></p></div></div>`;
  }
  function fitMsgs() {    // as many whole messages as the plate holds; the rest are counted, never cut
    const plate = $("plate"), box = plate.querySelector(".msgs");
    if (!box) return;
    const r = RUN(state.comp), mine = (r.hl7 || []).length, msgs = [...box.querySelectorAll(".msg")], tail = box.querySelector(".tail");
    const say = (shown) => {
      const parts = [];
      if (mine > shown) parts.push(`${plural(mine - shown, "more message", "more messages")} about this patient`);
      if (r.hl7_others) parts.push(`${plural(r.hl7_others, "message", "messages")} about others`);
      tail.textContent = parts.length ? `and ${parts.join("; ")}` : "";
      tail.hidden = !parts.length;
    };
    let shown = msgs.length;
    say(shown);
    if (matchMedia("(max-width: 860px)").matches) return;
    while (shown > 1 && plate.scrollHeight > plate.clientHeight + 1) { msgs[--shown].remove(); say(shown); }
  }

  function fileHTML(r) {
    const s = r.sidecar;
    if (!s) return `<div class="obj file"><p class="after bad">No export written, so no retention record.</p></div>`;
    const v = (x) => x == null || x === "" ? null : x;
    const rows = [
      ["run_id", s.run_id], ["purpose", s.purpose], ["retention_days", v(s.retention_days)], ["written_at", s.written_at && s.written_at.slice(0, 16).replace("T", " ")],
      ["delete_after", v(s.delete_after) && s.delete_after.slice(0, 16).replace("T", " ")], ["files", (s.files || []).join("\n")],
      ["deletion_mechanism", v(s.deletion_mechanism)], ["key_file", v(s.key_file)], ["key_holder", v(s.key_holder)],
    ];
    const bad = new Set(["retention_days", "delete_after", "deletion_mechanism"]);
    const purge = (r.audit || []).find((e) => e.event === "purge");
    const after = purge ? `<p class="after">purge · ${esc(purge.at.slice(0, 16))} · ${esc(purge.note.split(":")[0])}</p>`
      : `<p class="after bad">No purge: nothing schedules this export's erasure.</p>`;
    return `<div class="obj file"><h3 class="ttl fn">${esc(s.run_id)}.retention.json</h3>
      <dl class="kv">${rows.map(([k, val]) => `<dt>${k}</dt><dd class="${val == null && bad.has(k) ? "bad" : ""}">${val == null ? "null" : esc(val).replace(/\n/g, "<br>")}</dd>`).join("")}</dl>${after}</div>`;
  }

  function runsHTML(x) {
    const runs = TECH(x).jobs[state.job], first = runs[0];
    const cell = (r) => ({
      f: r.cols.length, n: `${r.hit} of ${r.needed}`, o: r.oos.length ? r.oos.map((i) => COLS[i].label).join(", ") : "none",
      k: r.retention ? `${r.retention} d` : "never", e: r.export.kind === "tok" ? "token" : r.export.kind === "raw" ? "raw" : "none", s: r.score.toFixed(3),
    });
    const a = cell(first);
    const rows = runs.map((r, i) => {
      const c = cell(r);
      const td = (k, bad) => `<td class="${i && c[k] === a[k] ? "same" : ""} ${bad ? "bad" : ""}">${esc(c[k])}</td>`;
      return `<tr><td>${i + 1}</td>${td("f")}${td("n")}${td("o", r.oos.length)}${td("k", !r.retention)}${td("e", r.export.kind === "raw")}${td("s")}</tr>`;
    }).join("");
    const once = runs.length === 1 ? `<p class="once">${x === "a" ? "Ours is not sampled: the same job gives the same list every time." : "The baseline is not sampled: it takes everything every time."}</p>` : "";
    return `<div class="obj doc"><h3 class="ttl">Every recorded run of this job</h3><table class="runs"><thead><tr><th>Run</th><th>Fields</th><th>Needed</th><th>Out of purpose</th><th>Kept</th><th>Left as</th><th>Score</th></tr></thead><tbody>${rows}</tbody></table>${once}</div>`;
  }

  function chainHTML(r) {
    const evs = r.audit || [];
    const short = (h) => (h || "").slice(0, 12);
    const gap = (n, what) => `<div class="ev gap"><p>${esc(plural(n, `line ${what}`, `lines ${what}`))}</p></div>`;
    const cards = evs.map((e, k) => {
      const before = k === 0 ? (e.seq ? gap(e.seq, "earlier in the log") : "")
        : (e.seq - evs[k - 1].seq > 1 ? gap(e.seq - evs[k - 1].seq - 1, "from other runs") : "");
      const rows = [];
      if (e.event === "extraction") {
        const f = e.fields || {}, n = Object.values(f).reduce((s, v) => s + v.length, 0);
        rows.push(["fields", `${n} across ${Object.keys(f).length} module${Object.keys(f).length === 1 ? "" : "s"}`]);
        rows.push(["records", fmt(e.records || 0)]);
      } else if (e.event === "export") rows.push(["note", e.note.split(";")[0]]);
      else rows.push(["note", e.note.split(":")[0]]);
      if (e.subjects) rows.push(["patients", e.subjects.length > 2 ? `${e.subjects.slice(0, 2).join(", ")} and ${e.subjects.length - 2} more` : e.subjects.join(", ")]);
      if (e.event === "extraction") rows.push(["scoped", e.scoped ? "yes" : "no"]);
      rows.push(["prev", short(e.prev_sha256) || "(first line)"]);
      return `${before}<div class="ev"><h4>${esc(e.event)}<span>${esc(e.at.slice(0, 16))}</span></h4>
        <dl class="kv">${rows.map(([k, v]) => `<dt>${k}</dt><dd>${esc(v)}</dd>`).join("")}<dt>this line</dt><dd class="link"><b>${esc(short(e.sha256))}</b></dd></dl></div>`;
    }).join("");
    const missing = !evs.some((e) => e.event === "purge") ? `<div class="ev missing"><h4>no purge</h4><p class="more">Nothing will erase this export.</p></div>` : "";
    return `<div class="obj chain"><h3 class="ttl">Audit log, this run's lines</h3>${cards}${missing}</div>`;
  }

  function listHTML() {
    const plates = PLATES.filter((p) => p.comp);
    const rows = plates.map((p) => {
      const n = PLATES.indexOf(p) + 1;
      return `<tr data-plate="${n}"><td class="n">${n}</td><td>${esc(p.title)}</td>${["a", "b", "c"].map((x) => { const f = FIG[p.id](x); return `<td class="v ${f.vbad || f.bad ? "bad" : ""}">${esc(f.v)}</td>`; }).join("")}</tr>`;
    }).join("");
    return `<div class="obj doc"><h3 class="ttl">${esc(JOB().name)}</h3><table class="lop"><thead><tr><th></th><th>Plate</th><th><span class="bd a">a</span>Ours</th><th><span class="bd b">b</span>${esc(MODEL().name)}</th><th><span class="bd c">c</span>Baseline</th></tr></thead><tbody>${rows}</tbody></table></div>`;
  }

  function leftHTML() {
    const p = PLATE(), x = state.comp;
    if (p.id === "cover") return fanHTML();
    if (p.id === "hospital") return inventoryHTML(null);
    if (p.id === "request") return slipHTML();
    if (p.id === "index") return listHTML();
    const r = RUN(x);
    return { taken: () => inventoryHTML(r), cost: () => logHTML(r), declared: () => formHTML(r), left: () => hl7HTML(r),
             kept: () => fileHTML(r), repeated: () => runsHTML(x), custody: () => chainHTML(r) }[p.id]();
  }

  const CAPTIONS = {
    hospital: ["Inventory", "the portal's five modules, the fields each holds, its patients"],
    request: ["The job", "what it asks for, and why each field is needed"],
    taken: ["The extract", "the fields and patients this run read"],
    cost: ["The browser's log", "one line per page load"],
    declared: ["The manifest", "what the run declared, checked against the hospital's register"],
    left: ["The export", "HL7 v2 messages about the followed patient, as they left"],
    kept: ["The retention record", "written beside the export"],
    repeated: ["The runs", "every recorded run of this job, against the first"],
    custody: ["The audit log", "this run's lines; each holds the hash of the line before"],
    index: ["Index", "the comparanda for this job, and how the catalogue was made"],
    cover: ["The comparanda", "ours, an AI model and the baseline, each on its own stock, with the values each took for this job"],
  };
  const KEYS = {
    taken: `<i>ink</i> read · <i class="r">red</i> out of purpose · <i>dashed</i> needed, not read`,
    declared: `<i>solid</i> demonstrated · <i>dashed</i> attested · <i class="r">struck</i> not backed`,
    left: `<i>bold</i> token · <i class="r">red</i> raw, masked here`,
  };
  function captionHTML() {
    const p = PLATE(), [a, b] = CAPTIONS[p.id];
    const no = p.comp ? `${state.plate}<span class="cl">${state.comp}</span>` : `${state.plate}`;
    return `<span><b>${p.id === "cover" ? "Frontispiece" : `Plate ${no}`}</b>${esc(a)}: ${esc(b)}</span>${KEYS[p.id] ? `<span class="lg">${KEYS[p.id]}</span>` : ""}`;
  }

  /* ------------------------------------------------------------ chrome: pickers, index */
  function chrome() {
    $("rec").textContent = `recorded ${day(D.meta.generated)}`;
    $("job").innerHTML = D.jobs.map((j) => `<option value="${esc(j.id)}">${esc(j.name)}${j.trap ? " (trap)" : ""}</option>`).join("");
    $("model").innerHTML = D.models.map((m) => `<option value="${esc(m.id)}">${esc(m.name)}</option>`).join("");
    $("brief").innerHTML = BRIEF.map((b) => `<button type="button" role="radio" data-brief="${b.id}">${esc(b.label.replace(/^told /, "").replace(/^task \+ register$/, "task + register"))}</button>`).join("");
    $("index").innerHTML = PLATES.map((p, i) => `<button type="button" data-plate="${i + 1}"><b>${i + 1}</b><span>${esc(p.short)}</span></button>`).join("");
  }
  function sync() {
    $("job").value = state.job;
    $("model").value = state.model;
    document.querySelectorAll("#brief button").forEach((b) => b.setAttribute("aria-checked", String(b.dataset.brief === state.brief)));
    document.querySelectorAll("#index button").forEach((b) => {
      const cur = +b.dataset.plate === state.plate;
      b.toggleAttribute("aria-current", false);
      if (cur) b.setAttribute("aria-current", "step");
      const abc = b.querySelector(".abc");
      if (abc) abc.remove();
      if (cur && PLATE().comp) b.insertAdjacentHTML("beforeend", `<span class="abc">${state.comp}</span>`);
    });
    const end = state.plate === PLATES.length;
    $("next").querySelector("span").textContent = end ? "Again" : state.plate === 0 ? "Open" : "Next";
    document.body.dataset.comp = state.plate === 0 ? "cover" : PLATE().comp ? state.comp : "none";
    // the leaves already turned lie to the left of the spread, the ones to come to the right
    $("vol").style.setProperty("--tl", `${state.plate * 2}px`);
    $("vol").style.setProperty("--tr", `${(N - 1 - state.plate) * 2}px`);
    markIndex();
    history.replaceState(null, "", `#${state.plate}${PLATE().comp ? state.comp : ""}`);
  }
  function markIndex() {          // one rule travels along the index to the plate that is open
    const nav = $("index"), b = nav.querySelector('[aria-current="step"]');
    let m = nav.querySelector(".ixm");
    if (!m) { m = document.createElement("i"); m.className = "ixm"; m.setAttribute("aria-hidden", "true"); nav.append(m); }
    if (!b) { m.style.opacity = "0"; return; }
    m.style.opacity = "1";
    slideTo(m, b.offsetLeft, b.offsetWidth);
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
  function markComp(from, tint, wait = 0) {  // the chosen comparandum's stock, sliding from the last one chosen once the new figure is set
    const ul = document.querySelector("#right .comp");
    if (!ul) return;
    const b = ul.querySelector('[aria-pressed="true"]');
    let m = ul.querySelector(".cm");
    if (!m) { m = document.createElement("li"); m.className = "cm"; m.setAttribute("aria-hidden", "true"); ul.prepend(m); }
    if (!b) return;
    const y = b.getBoundingClientRect().top - ul.getBoundingClientRect().top;
    m.style.height = `${b.offsetHeight}px`;
    m.style.transform = `translateY(${y}px)`;
    m.dataset.y = String(y);
    if (from != null && from !== y) anim(m, [{ transform: `translateY(${from}px)`, backgroundColor: tint }, { transform: `translateY(${y}px)`, backgroundColor: getComputedStyle(m).backgroundColor }], { delay: wait, duration: 520 });
  }

  /* ------------------------------------------------------------ motion: each step plays; a second press lands it */
  const EASE = "cubic-bezier(.16, 1, .3, 1)";
  const easeOut = (t) => 1 - Math.pow(1 - t, 3);
  const tweens = new Set();
  let until = 0;
  const now = () => performance.now();
  const busy = () => now() < until;
  const hold = (ms) => { until = Math.max(until, now() + ms); };
  const css = (name) => getComputedStyle(document.body).getPropertyValue(name).trim();
  function rgba(hex, a) {
    const h = hex.replace("#", ""), n = parseInt(h.length === 3 ? h.replace(/./g, "$&$&") : h, 16);
    return `rgba(${(n >> 16) & 255}, ${(n >> 8) & 255}, ${n & 255}, ${a})`;
  }
  function anim(el, frames, o = {}) {      // holds its first frame until its delay is up, then lands on the page's own style
    if (!el || still()) return null;
    const opt = { duration: 420, easing: EASE, fill: "backwards", ...o };
    hold((opt.delay || 0) + opt.duration);
    return el.animate(frames, opt);
  }
  const rise = (el, delay, duration = 380, by = ".35em") => anim(el, [{ opacity: 0, transform: `translateY(${by})` }, { opacity: 1, transform: "none" }], { delay, duration });
  const fade = (el, delay, duration = 340) => anim(el, [{ opacity: 0 }, { opacity: 1 }], { delay, duration, easing: "ease-out" });
  const print = (el, delay, duration = 260) => anim(el, [{ clipPath: "inset(0 100% 0 0)" }, { clipPath: "inset(0 0 0 0)" }], { delay, duration, easing: "cubic-bezier(.35, .6, .4, 1)" });
  const flash = (el, delay, colour) => anim(el, [{ backgroundColor: colour }, { backgroundColor: "rgba(0, 0, 0, 0)" }], { delay, duration: 1100, easing: "ease-out" });
  const gap = (n, total, most) => (n > 1 ? Math.min(most, total / (n - 1)) : 0);   // a stagger that sets n marks within total ms
  function tween(ms, delay, step) {        // a figure kept in step with the marks; lands on its last frame
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
  function land() {                        // whatever is playing arrives at its last frame now
    for (const tw of [...tweens]) tw.finish();
    for (const a of document.getAnimations()) {
      try { if (a.effect && a.effect.getComputedTiming().endTime !== Infinity) a.finish(); } catch (e) { /* an animation that cannot finish is left to run */ }
    }
    until = 0;
  }

  /* the figure, counted as the plate's marks are set */
  const numeric = (s) => /^[\d,]+$/.test(String(s).trim());
  const value = (s) => Number(String(s).replace(/,/g, ""));
  const figN = () => document.querySelector("#right .fig .n");
  function countBy(marks) {                // [[ms, adds], ...] in order: the figure appears with the first mark and counts each as it is set
    const n = figN();
    if (!n || !numeric(n.textContent) || !marks.length) return null;
    const end = n.textContent, t0 = marks[0][0], t1 = marks[marks.length - 1][0] + 60;
    anim(n, [{ opacity: 0 }, { opacity: 1 }], { delay: t0, duration: 240, easing: "ease-out" });
    tween(Math.max(1, t1 - t0), t0, (f) => {
      if (f >= 1) { n.textContent = end; return; }
      const at = t0 + f * (t1 - t0);
      let sum = 0;
      for (const [t, k] of marks) if (t <= at) sum += k;
      n.textContent = fmt(sum);
    });
    return { t0, t1 };
  }
  const inOut = (t) => (t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2);
  function atRoll(y) { let lo = 0, hi = 1; for (let i = 0; i < 22; i++) { const m = (lo + hi) / 2; if (inOut(m) < y) lo = m; else hi = m; } return lo; }
  function refigure(was, delay, ms) {      // the figure goes from the last comparandum's value to this one's
    const n = figN();
    if (!n) return;
    const fig = n.closest(".fig"), u = fig.querySelector(".u"), no = $("right").querySelector(".eh .no");
    const is = { text: n.textContent, u: u ? u.textContent : null, bad: fig.classList.contains("bad") };
    if (!was) { anim(n, [{ opacity: 0, transform: "translateY(14%)" }, { opacity: 1, transform: "none" }], { delay, duration: 560 }); return; }
    const pin = (on) => {                  // until the new figure is set, the page wears the old stock's ink
      [[n, was.ink], [u, was.unit], [no, was.no]].forEach(([el, c]) => { if (el) el.style.color = on && c ? c : ""; });
    };
    if (!numeric(was.text) || !numeric(is.text) || was.bad !== is.bad) {
      // a breach is never counted into: the old figure stands until the roller is half way, then the new one is set whole
      tween(ms, delay, (f) => {
        const late = f >= 0.5, s = late ? is : was;
        n.textContent = s.text;
        if (u && s.u != null) u.textContent = s.u;
        fig.classList.toggle("bad", s.bad);
        pin(!late);
      });
      anim(n, [{ opacity: 0, transform: "translateY(14%)" }, { opacity: 1, transform: "none" }], { delay: delay + ms / 2, duration: 460, fill: "none" });
      return;
    }
    const a = value(was.text), b = value(is.text);
    tween(ms, delay, (f) => { n.textContent = f >= 1 ? is.text : fmt(Math.round(a + (b - a) * inOut(f))); pin(f < 0.5); });
  }

  /* each plate's object, set the way the run made it: d is when it starts, k how fast, o.right whether the entry is in play */
  const q = (sel) => document.querySelector(`#plate ${sel}`);
  const qa = (sel) => [...document.querySelectorAll(`#plate ${sel}`)];
  const PLAY = {
    cover(d, k) {                          // the three stocks lie stacked on their rivet, ours on top, then fan open; each shows what it took once it is at its angle
      fade(q(".fan"), d, 360);
      qa(".blade").forEach((b) => {
        const r = getComputedStyle(b).getPropertyValue("--r").trim() || "0deg", deg = Math.abs(parseFloat(r)) || 0, dur = 1250 * k;
        if (deg) anim(b, [{ transform: "rotate(0deg)" }, { transform: `rotate(${r})` }], { delay: d + 260, duration: dur, easing: "cubic-bezier(.16, 1, .3, 1)" });
        const at = d + 260 + (deg ? dur * 0.55 : 120);
        b.querySelectorAll(".num, .of, .nm").forEach((x) => fade(x, at, 420));
      });
    },
    hospital(d, k, o) {                    // the inventory sets in, module by module; each field adds its column of patients
      const fl = qa(".f"), g = gap(fl.length, 780 * k, 26), marks = [];
      qa(".mod").forEach((m) => fade(m.querySelector("h3"), d + fl.indexOf(m.querySelector(".f")) * g, 320));
      fl.forEach((f, i) => { const at = d + 60 + i * g; rise(f, at, 380, ".3em"); marks.push([at, PTS.length]); });
      const pl = qa(".pts li"), pg = gap(pl.length, 560 * k, 28);
      fade(q(".pts .ttl"), d + 140);
      pl.forEach((li, i) => rise(li, d + 240 + i * pg, 340, ".3em"));
      return o.right ? countBy(marks) : null;
    },
    request(d, k, o) {                     // the job, then each needed field with its reason
      rise(q(".ask"), d, 560, ".3em");
      const dt = qa(".need dt"), g = gap(dt.length, 820 * k, 120), marks = [];
      dt.forEach((t, i) => { const at = d + 320 * k + i * g; rise(t, at, 400, ".3em"); fade(t.nextElementSibling, at + 100, 420); marks.push([at, 1]); });
      rise(q(".trap"), d + 320 * k + dt.length * g + 120, 480, ".3em");
      return o.right ? countBy(marks) : null;
    },
    taken(d, k, o) {                       // the inventory in grey, then what the run read inks in, in the order it read it
      const r = RUN(state.comp), per = r.named ? r.patients.length : r.rows, ghost = css("--ghost");
      const fl = qa(".f"), g0 = gap(fl.length, 360 * k, 10);
      qa(".mod h3").forEach((h, i) => fade(h, d + i * 50, 300));
      fl.forEach((f, i) => fade(f, d + i * g0, 260));
      const t1 = d + 440 * k, g = gap(r.cols.length, 1050 * k, 85), marks = [];
      r.cols.forEach((c, i) => {
        const el = q(`.f[data-col="${c}"]`);
        if (!el) return;
        const at = t1 + i * g, cs = getComputedStyle(el);
        anim(el, [{ color: ghost }, { color: cs.color }], { delay: at, duration: 440, easing: "ease-out" });
        if (el.classList.contains("oos")) anim(el, [{ textDecorationColor: "rgba(0, 0, 0, 0)" }, { textDecorationColor: cs.textDecorationColor }], { delay: at + 260, duration: 340, easing: "ease-out" });
        marks.push([at, per]);
      });
      const pl = qa(".pts li"), pg0 = gap(pl.length, 320 * k, 12);
      fade(q(".pts .ttl"), d + 60);
      pl.forEach((li, i) => fade(li, d + 80 + i * pg0, 260));
      const on = pl.filter((li) => !li.classList.contains("off")), t2 = t1 + Math.max(0, r.cols.length - 1) * g * 0.4, pg = gap(on.length, 640 * k, 45);
      on.forEach((li, i) => anim(li, [{ color: ghost }, { color: getComputedStyle(li).color }], { delay: t2 + i * pg, duration: 400, easing: "ease-out" }));
      fade(q(".pts .note"), t1 + 320);
      return o.right ? countBy(marks) : null;
    },
    cost(d, k, o) {                        // the browser's log prints, a line a page load
      fade(q(".ttl"), d, 300);
      const li = qa(".log li"), g = gap(li.length, 1550 * k, 80), marks = [];
      li.forEach((l, i) => { const at = d + 140 + i * g; print(l, at, 230); marks.push([at, 1]); });
      return o.right ? countBy(marks) : null;
    },
    declared(d, k, o) {                    // the manifest sets in, then each backing is drawn under its control
      const rows = qa(".form > .r"), g = gap(rows.length, 580 * k, 46);
      rows.forEach((row, i) => [...row.children].forEach((c) => rise(c, d + i * g, 340, ".25em")));
      const ink = qa(".form .b .dem, .form .b .att, .form .b .no"), t1 = d + rows.length * g + 160, g2 = gap(ink.length, 820 * k, 90);
      ink.forEach((s, i) => {
        const end = getComputedStyle(s).backgroundSize;
        anim(s, [{ backgroundSize: end.replace(/^\S+/, "0%") }, { backgroundSize: end }], { delay: t1 + i * g2, duration: 440, easing: "cubic-bezier(.65, 0, .25, 1)" });
      });
      if (!o.right) return null;
      const vs = [...document.querySelectorAll("#right .rules span:nth-child(3n)")], g3 = gap(vs.length, 760 * k, 115), t3 = d + 220 * k, marks = [];
      vs.forEach((v, i) => { const at = t3 + i * g3; rise(v, at, 340, ".25em"); if (v.textContent === "held") marks.push([at, 1]); });
      return countBy(marks);
    },
    left(d, k) {                           // the messages as they left, segment by segment; a token where the record number was
      fade(q(".ttl"), d, 300);
      const ls = qa(".seg-l"), g = gap(ls.length, 1050 * k, 100), tone = rgba(css("--deep"), 0.32), ink = css("--ink"), red = css("--red");
      ls.forEach((l, i) => {
        const at = d + 120 + i * g;
        print(l, at, 360);
        l.querySelectorAll(".id").forEach((s) => flash(s, at + 280, tone));
        l.querySelectorAll(".raw").forEach((s) => anim(s, [{ color: ink }, { color: red }], { delay: at + 320, duration: 520, easing: "ease-out" }));
      });
      qa(".more").forEach((m) => fade(m, d + 160 + ls.length * g, 420));
    },
    kept(d, k) {                           // the retention record writes itself out, then the purge (or its absence)
      rise(q(".ttl"), d, 380, ".25em");
      const dt = qa(".kv dt"), g = gap(dt.length, 780 * k, 85);
      dt.forEach((t, i) => { print(t, d + 140 + i * g, 240); print(t.nextElementSibling, d + 200 + i * g, 340); });
      anim(q(".after"), [{ opacity: 0, transform: "translateY(.5em)" }, { opacity: 1, transform: "none" }], { delay: d + 300 + dt.length * g, duration: 600 });
    },
    repeated(d, k, o) {                    // run after run; what matches run 1 settles to grey, each new decision is counted
      fade(q(".ttl"), d, 300);
      fade(q(".runs thead"), d + 60, 320);
      const tr = qa(".runs tbody tr"), g = gap(tr.length, 1050 * k, 200), runs = TECH(state.comp).jobs[state.job], seen = new Set(), marks = [];
      const ink = css("--ink"), ghost = css("--ghost");
      tr.forEach((row, i) => {
        const at = d + 160 + i * g;
        [...row.children].forEach((td, j) => rise(td, at + j * 24, 380, ".3em"));
        row.querySelectorAll("td.same").forEach((td) => anim(td, [{ color: ink }, { color: ink, offset: .3 }, { color: ghost }], { delay: at + 220, duration: 900, easing: "ease-in-out" }));
        const key = runs[i] ? runs[i].decision : i;
        if (!seen.has(key)) { seen.add(key); marks.push([at, 1]); }
      });
      fade(q(".once"), d + 220 + tr.length * g, 420);
      return o.right ? countBy(marks) : null;
    },
    custody(d, k, o) {                     // the run's lines, each holding the hash of the line before it
      fade(q(".chain > .ttl"), d, 300);
      const ev = qa(".chain > .ev"), g = gap(ev.length, 1400 * k, 300), tone = rgba(css("--deep"), 0.3);
      let named = null;
      ev.forEach((e, i) => {
        const at = d + 140 + i * g, h = e.querySelector("h4");
        rise(e, at, 480, ".45em");
        const link = e.querySelector(".link b");
        if (link) flash(link, at + 340, tone);
        const prev = [...e.querySelectorAll("dt")].find((t) => t.textContent === "prev");
        if (prev && prev.nextElementSibling.textContent !== "(first line)") flash(prev.nextElementSibling, at + 200, tone);
        if (named == null && h && /^extraction/.test(h.textContent)) named = at;
      });
      if (!o.right || named == null) return null;
      return countBy([[named + 220, value(figN() ? figN().textContent : "0") || 0]]);
    },
    index(d, k) {
      fade(q(".ttl"), d, 300);
      fade(q(".lop thead"), d + 60, 320);
      qa(".lop tbody tr").forEach((tr, i) => [...tr.children].forEach((td, j) => rise(td, d + 160 + i * 85 * k + j * 60, 360, ".25em")));
    },
  };
  function playEntry(d, t) {               // the catalogue entry sets in beside its plate; t: when the plate's marks set the figure, if they do
    const R = $("right"), p = PLATE(), n = figN();
    rise(R.querySelector(".eh"), d, 560, ".3em");
    if (p.id === "cover") R.querySelectorAll(".contents li").forEach((li, i) => rise(li, d + 380 + i * 55, 400, ".3em"));
    else if (n && !t) anim(n, [{ opacity: 0, transform: "translateY(14%)" }, { opacity: 1, transform: "none" }], { delay: d + 140, duration: 620 });
    const t0 = t ? t.t0 : d + 160, t1 = t ? t.t1 + 80 : d + 300;
    fade(R.querySelector(".fig .u"), t0, 420);
    fade(R.querySelector(".figcap"), t1, 480);
    R.querySelectorAll(".comp li:not(.cm)").forEach((li, i) => rise(li, d + 320 + i * 85, 400, ".25em"));
    R.querySelectorAll(".comp .v").forEach((v, i) => fade(v, t1 + i * 70, 380));
    fade(R.querySelector(".comp .cm"), d + 560, 420);
    R.querySelectorAll(".rec-dl > dt").forEach((dt, i) => { fade(dt, d + 420 + i * 55, 360); fade(dt.nextElementSibling, d + 450 + i * 55, 360); });
    fade(R.querySelector(".prov"), d + 760, 520);
  }
  function play(left, right) {             // delays in ms; null leaves that page as it stands
    if (still()) return;
    const t = left != null ? PLAY[PLATE().id](left, 1, { right: right != null }) : null;
    if (right != null) playEntry(right, t || null);
  }

  /* turning a leaf: the page lifts off the spread and comes down on the other side */
  const TURN = 880;
  function keep(el) {                      // a still copy of a page as it stands, printed on its own stock
    const c = el.cloneNode(true), cs = getComputedStyle(document.body);
    c.removeAttribute("id"); c.removeAttribute("aria-live");
    c.querySelectorAll("[id]").forEach((n) => n.removeAttribute("id"));
    c.classList.add("still");
    for (const v of ["--tint", "--deep"]) c.style.setProperty(v, cs.getPropertyValue(v));
    return c;
  }
  function turnLeaf(dir, draw) {
    if (still() || matchMedia("(max-width: 860px)").matches) return false;
    const vol = $("vol"), L = $("left"), R = $("right"), vb = vol.getBoundingClientRect();
    const box = (el) => { const b = el.getBoundingClientRect(); return [b.left - vb.left, b.top - vb.top, b.width, b.height]; };
    const oldL = keep(L), oldR = keep(R), bl = box(L), br = box(R);
    draw();
    const newL = keep(L), newR = keep(R), fwd = dir > 0;
    if (fwd) { const p = newL.querySelector(".plate"); if (p) [...p.children].forEach((c) => { c.style.visibility = "hidden"; }); }   // the plate's object is set once the page is down
    const place = (o, b) => Object.assign(o.style, { left: `${b[0]}px`, top: `${b[1]}px`, width: `${b[2]}px`, height: `${b[3]}px` });
    const sheet = (b, page, cls) => {
      const o = document.createElement("div");
      o.className = `ov ${cls}`; o.setAttribute("aria-hidden", "true");
      place(o, b); o.append(page);
      const s = document.createElement("i"); s.className = "shade"; o.append(s);
      vol.append(o);
      return o;
    };
    const under = sheet(fwd ? bl : br, fwd ? oldL : oldR, "under");
    const cast = document.createElement("i");
    cast.className = `cast ${fwd ? "r" : "l"}`; cast.setAttribute("aria-hidden", "true"); place(cast, fwd ? br : bl); vol.append(cast);
    const front = sheet(fwd ? br : bl, fwd ? oldR : oldL, `front ${fwd ? "r" : "l"}`);
    const back = sheet(fwd ? bl : br, fwd ? newL : newR, `back ${fwd ? "l" : "r"}`);
    front.style.transformOrigin = fwd ? "0 50%" : "100% 50%";
    back.style.transformOrigin = fwd ? "100% 50%" : "0 50%";
    const half = TURN / 2, s = fwd ? -1 : 1;
    front.animate([{ transform: "rotateY(0deg)" }, { transform: `rotateY(${s * 90}deg)` }], { duration: half, easing: "cubic-bezier(.45, .05, .85, .55)", fill: "forwards" });
    front.querySelector(".shade").animate([{ opacity: 0, backgroundPosition: "100% 0" }, { opacity: 1, backgroundPosition: "0% 0" }], { duration: half, easing: "ease-in", fill: "forwards" });
    front.querySelector(".page").animate([{ opacity: 1 }, { opacity: 1, offset: 0.84 }, { opacity: 0 }], { duration: half, easing: "linear", fill: "forwards" });
    cast.animate([{ opacity: 0 }, { opacity: 1, offset: 0.5 }, { opacity: 0 }], { duration: half * 1.2, easing: "ease-in-out", fill: "forwards" });
    under.querySelector(".shade").animate([{ opacity: 0 }, { opacity: 0.32 }], { delay: half, duration: half, easing: "ease-in", fill: "both" });
    back.querySelector(".shade").animate([{ opacity: 1, backgroundPosition: "0% 0" }, { opacity: 0, backgroundPosition: "100% 0" }], { delay: half, duration: half, easing: "ease-out", fill: "both" });
    back.querySelector(".page").animate([{ opacity: 0 }, { opacity: 1, offset: 0.16 }, { opacity: 1 }], { delay: half, duration: half, easing: "linear", fill: "both" });
    const down = back.animate([{ transform: `rotateY(${-s * 90}deg)` }, { transform: "rotateY(0deg)" }], { delay: half, duration: half, easing: "cubic-bezier(.15, .45, .3, 1)", fill: "both" });
    hold(TURN);
    const done = () => { under.remove(); front.remove(); back.remove(); cast.remove(); };
    down.finished.then(done, done);
    return true;
  }

  /* a comparandum's stock rolled across the plate: the last one's ink ahead of the roller, the new one's behind it */
  const ROLL = 760;
  function rollStock(oldTint, oldHTML, oldH) {
    const plate = $("plate"), w = document.createElement("div"), roll = document.createElement("i");
    w.className = "wash"; roll.className = "roller";
    w.setAttribute("aria-hidden", "true"); roll.setAttribute("aria-hidden", "true");
    const kids = [...plate.children];
    let ghost = null;
    if (oldHTML != null) {
      ghost = document.createElement("div");
      ghost.className = "ghost"; ghost.setAttribute("aria-hidden", "true"); ghost.innerHTML = oldHTML;
      plate.append(ghost);
    }
    plate.prepend(w, roll);
    plate.style.backgroundColor = oldTint;
    const W = plate.clientWidth, newH = plate.offsetHeight, geo = ghost ? kids.map((c) => [c, c.offsetLeft, c.offsetWidth]) : [];
    if (oldH && Math.abs(oldH - newH) > 1) anim(plate, [{ height: `${oldH}px` }, { height: `${newH}px` }], { duration: ROLL, easing: "cubic-bezier(.65, 0, .35, 1)" });
    tween(ROLL, 0, (f) => {
      if (f >= 1) {
        w.remove(); roll.remove(); if (ghost) ghost.remove();
        plate.style.backgroundColor = "";
        for (const [c] of geo) c.style.clipPath = "";
        return;
      }
      const x = W * inOut(f);
      w.style.clipPath = `inset(0 ${(W - x).toFixed(1)}px 0 0)`;
      roll.style.transform = `translateX(${x.toFixed(1)}px)`;
      roll.style.opacity = String(f > 0.85 ? ((1 - f) / 0.15) * 0.32 : 0.32);
      if (ghost) ghost.style.clipPath = `inset(0 0 0 ${x.toFixed(1)}px)`;
      for (const [c, L, cw] of geo) c.style.clipPath = `inset(0 ${Math.max(0, L + cw - x).toFixed(1)}px 0 0)`;
    });
  }
  function flipTo() {
    const p = PLATE(), R = $("right"), plate = $("plate");
    const oldTint = getComputedStyle(plate).backgroundColor, oldN = figN(), oldFig = oldN && oldN.closest(".fig");
    const oldU = oldFig && oldFig.querySelector(".u"), oldNo = R.querySelector(".eh .no");
    const was = oldN ? { text: oldN.textContent, u: oldU ? oldU.textContent : null, bad: oldFig.classList.contains("bad"),
                         ink: getComputedStyle(oldN).color, unit: oldU ? getComputedStyle(oldU).color : null, no: oldNo ? getComputedStyle(oldNo).color : null } : null;
    const cm = R.querySelector(".comp .cm"), mFrom = cm && cm.dataset.y != null ? +cm.dataset.y : null;
    const inPlace = p.id === "taken" && plate.querySelector(".inv");
    const before = inPlace ? [...plate.querySelectorAll(".f, .pts li")].map((el) => { const c = getComputedStyle(el); return [el, c.color, c.textDecorationColor]; }) : null;
    const oldHTML = inPlace ? null : [...plate.children].map((c) => c.outerHTML).join("");
    const oldH = plate.offsetHeight;
    if (inPlace) reInk(RUN(state.comp)); else plate.innerHTML = leftHTML();
    $("cap").innerHTML = captionHTML();
    R.innerHTML = rightHTML();
    fit(); fitLog(); fitMsgs();
    sync();
    markComp(mFrom, oldTint, ROLL / 2);
    if (still()) return;
    rollStock(oldTint, oldHTML, oldH);
    if (inPlace) {                         // the same inventory: each field re-inks as the roller passes it
      const pb = plate.getBoundingClientRect();
      for (const [el, c, dc] of before) {
        const cs = getComputedStyle(el);
        if (cs.color === c && cs.textDecorationColor === dc) continue;
        const x = Math.min(1, Math.max(0, (el.getBoundingClientRect().left - pb.left) / pb.width));
        anim(el, [{ color: c, textDecorationColor: dc }, { color: cs.color, textDecorationColor: cs.textDecorationColor }], { delay: ROLL * atRoll(x), duration: 360, easing: "ease-out" });
      }
      fade(plate.querySelector(".pts .note"), ROLL * 0.7);
    }
    refigure(was, 0, ROLL);
    fade(R.querySelector(".figcap"), 180, 440);
    R.querySelectorAll(".rec-dl > dd").forEach((dd, i) => fade(dd, 160 + i * 45, 380));
    fade(R.querySelector(".prov"), 320, 420);
  }

  /* ------------------------------------------------------------ render */
  function fit() {
    const fig = document.querySelector("#right .fig"), n = fig && fig.querySelector(".n");
    if (!n) return;
    n.style.fontSize = "";
    let size = parseFloat(getComputedStyle(n).fontSize), k = 0;
    while (fig.scrollWidth > fig.clientWidth + 1 && k++ < 10) { size *= 0.9; n.style.fontSize = `${size}px`; }
  }
  function draw() {
    $("left").classList.toggle("fit", !["cover", "cost"].includes(PLATE().id));
    $("plate").innerHTML = leftHTML();
    $("cap").innerHTML = captionHTML();
    $("right").innerHTML = rightHTML();
    fit(); fitLog(); fitMsgs();
    sync();
    markComp();
  }
  function render(kind, dir = 1) {         // "turn": a new plate or job; "flip": another comparandum; "open": the first view; "now": no motion
    land();
    if (kind === "flip") { flipTo(); return; }
    if (kind === "turn") {
      if (turnLeaf(dir, draw)) { if (dir > 0) play(TURN - 60, 150); else play(170, null); return; }
      draw();
      if (!still()) {
        const v = $("vol");
        v.classList.remove("turning-in"); void v.offsetWidth; v.classList.add("turning-in");
        v.addEventListener("animationend", () => v.classList.remove("turning-in"), { once: true });
        play(240, 60);
      }
      return;
    }
    draw();
    if (kind === "open") play(260, 60);
  }

  /* ------------------------------------------------------------ moving through the catalogue */
  const COMP = ["a", "b", "c"];
  function go(plate, comp = "a", dir) {
    plate = ((plate % N) + N) % N;
    const from = state.plate;
    state.plate = plate;
    state.comp = plate && PLATES[plate - 1].comp ? comp : "a";
    render(plate !== from ? "turn" : "flip", dir || (plate > from ? 1 : -1));
  }
  function flip(comp) { if (!PLATE().comp || comp === state.comp) return; state.comp = comp; render("flip"); }
  function next() {
    if (busy()) { land(); return; }        // a second press lands the step that is playing
    const p = PLATE(), i = COMP.indexOf(state.comp);
    if (p.comp && i < 2) flip(COMP[i + 1]); else go(state.plate + 1, "a", 1);
  }
  function prev() {
    const p = PLATE(), i = COMP.indexOf(state.comp);
    if (p.comp && i > 0) flip(COMP[i - 1]);
    else { const q = (state.plate - 1 + N) % N; go(q, q && PLATES[q - 1].comp ? "c" : "a", -1); }
  }
  const cycle = (list, cur, d) => list[(list.indexOf(cur) + d + list.length) % list.length];
  function setJob(id) { state.job = id; render("turn", 1); }
  function setModel(id) { state.model = id; render(PLATE().comp && state.comp === "b" ? "flip" : "now"); }
  function setBrief(id) { state.brief = id; render(PLATE().comp && state.comp === "b" ? "flip" : "now"); }

  document.addEventListener("click", (e) => {
    const t = e.target.closest("[data-comp],[data-plate],[data-brief]");
    if (!t || t.closest(".ov")) return;
    if (t.dataset.comp) flip(t.dataset.comp);
    else if (t.dataset.plate) go(+t.dataset.plate, PLATES[+t.dataset.plate - 1].comp ? state.comp : "a");
    else if (t.dataset.brief) setBrief(t.dataset.brief);
  });
  $("next").addEventListener("click", next);
  $("prev").addEventListener("click", prev);
  $("job").addEventListener("change", (e) => setJob(e.target.value));
  $("model").addEventListener("change", (e) => setModel(e.target.value));

  document.addEventListener("keydown", (e) => {
    if (e.ctrlKey || e.metaKey || e.altKey) return;
    const tag = (e.target.tagName || "").toLowerCase();
    if (tag === "select" && !["Escape"].includes(e.key)) return;
    const k = e.key;
    let done = true;
    if (k === " " || k === "PageDown") (e.shiftKey ? prev : next)();
    else if (k === "PageUp" || k === "Backspace") prev();
    else if (k === "ArrowRight") go(state.plate + 1, "a", 1);
    else if (k === "ArrowLeft") go(state.plate - 1, "a", -1);
    else if (k === "ArrowDown") { if (PLATE().comp) flip(cycle(COMP, state.comp, 1)); }
    else if (k === "ArrowUp") { if (PLATE().comp) flip(cycle(COMP, state.comp, -1)); }
    else if (k === "Home") go(0, "a", -1);
    else if (k === "End") go(PLATES.length, "a", 1);
    else if (/^[abc]$/i.test(k)) flip(k.toLowerCase());
    else if (/^[0-9]$/.test(k)) { const n = k === "0" ? 10 : +k; if (n <= PLATES.length) go(n, PLATES[n - 1].comp ? state.comp : "a"); }
    else if (k === "j" || k === "J") setJob(cycle(D.jobs.map((j) => j.id), state.job, e.shiftKey ? -1 : 1));
    else if (k === "m" || k === "M") setModel(cycle(D.models.map((m) => m.id), state.model, e.shiftKey ? -1 : 1));
    else if (k === "t" || k === "T") setBrief(cycle(BRIEF.map((b) => b.id), state.brief, e.shiftKey ? -1 : 1));
    else done = false;
    if (done) e.preventDefault();
  });

  let resizeT = 0;
  addEventListener("resize", () => { clearTimeout(resizeT); resizeT = setTimeout(() => { land(); fit(); fitLog(); fitMsgs(); markComp(); markIndex(); }, 120); });

  // A plate in the address (#3b) opens there, and a link to another plate turns to it.
  const fromHash = () => {
    const m = location.hash.match(/^#(\d{1,2})([abc]?)$/);
    if (!m || +m[1] > PLATES.length) return null;
    return [+m[1], +m[1] && PLATES[+m[1] - 1].comp && m[2] ? m[2] : "a"];
  };
  const start = fromHash();
  if (start) [state.plate, state.comp] = start;
  addEventListener("hashchange", () => {
    const to = fromHash();
    if (to && (to[0] !== state.plate || to[1] !== state.comp)) go(to[0], to[1]);
  });
  chrome();
  let opened = false;
  const open = () => { if (opened) return; opened = true; render("open"); };
  (document.fonts ? document.fonts.ready : Promise.resolve()).then(open);
  setTimeout(open, 1200);
})();
