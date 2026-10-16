/* The Redacted Record (Portal v5): one patient's record, every value under a bar.
   Leaf 1, the record: choosing who read it lifts exactly the bars that run read.
   Leaf 2, the copy that left the hospital: each value as the export carried it; turn to the erase date and it empties.
   Leaf 3, the access slip: every reading of this record, as the patient would be told.
   Keys: Space next (through the readers, then the next leaf), Shift+Space back, arrows a leaf, a b c a reader,
   E the erase date, J job, M model, T what the model was told. Every value is the recorded one, masked where it identifies. */
(() => {
  "use strict";
  const D = JSON.parse(document.getElementById("record-data").textContent);
  const $ = (id) => document.getElementById(id);
  const esc = (s) => String(s == null ? "" : s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const fmt = (n) => Number(n).toLocaleString("en-IN");
  const day = (iso) => new Date(String(iso).slice(0, 10) + "T00:00:00Z").toLocaleDateString("en-GB", { day: "numeric", month: "short", year: "numeric", timeZone: "UTC" });
  const still = () => matchMedia("(prefers-reduced-motion: reduce)").matches;
  const plural = (n, one, many) => `${fmt(n)} ${n === 1 ? one : many}`;
  const purged = (ev) => { const m = ev && ev.note.match(/erased (\d+) file\(s\) after (\d+) d/); return m ? `${m[1]} files, after ${m[2]} days` : ""; };
  const shown = (v) => (v == null ? "" : String(v).replace(/^(\d{4}-\d{2}-\d{2})T(\d{2}:\d{2}):\d{2}$/, "$1 $2"));

  const COLS = D.columns, MODS = D.modules, FOLLOW = D.patient.index, PTS = D.patients.length;
  const VALUES = D.patient.values, BRIEF = D.briefings;
  const LEAVES = [["The record", 1], ["The copy", 2], ["The slip", 3]];

  const state = { leaf: 1, reader: null, erased: false, job: D.jobs[0].id, model: (D.models.find((m) => m.id === "claude-opus-5-5") || D.models[0]).id, brief: "policy" };
  const JOB = () => D.jobs.find((j) => j.id === state.job);
  const TECH = (x) => D.techniques[x === "a" ? "ours" : x === "c" ? "base" : `${state.model}|${state.brief}`];
  const RUN = (x, job = state.job) => TECH(x).jobs[job][0];
  const MODEL = () => D.models.find((m) => m.id === state.model);
  const briefLabel = () => (BRIEF.find((b) => b.id === state.brief) || {}).label || "";
  const NAME = { a: () => ["Ours", "the reference"], b: () => [MODEL().name, briefLabel()], c: () => ["Baseline", "every module, every record"] };

  // did this run read this patient's record, and which of its lines
  const recordNo = (c) => {
    const xs = COLS.map((k, i) => (k.field === "mrn" || k.field === "subject_mrn" ? c.fields[String(i)] : null)).filter(Boolean);
    return xs.find((f) => f.how === "token") || xs[0] || null;
  };
  const readsPatient = (r) => (r.named ? r.patients.includes(FOLLOW) : r.rows > 0);
  const linesRead = (r) => (readsPatient(r) ? new Set(r.cols) : new Set());
  const others = (r) => (r.named ? r.patients.filter((p) => p !== FOLLOW).length : Math.max(0, r.rows - 1));

  /* ------------------------------------------------------------ leaf 1: the record */
  function recordHTML() {
    const r = state.reader ? RUN(state.reader) : null, job = JOB();
    const read = r ? linesRead(r) : new Set(), oos = r ? new Set(r.oos) : new Set(), need = new Set(job.needed.map((n) => n.col));
    let k = 0;
    const line = (i) => {
      const v = shown(VALUES[i]), cls = ["ln"];
      if (read.has(i)) cls.push("read");
      if (read.has(i) && oos.has(i)) cls.push("oos");
      if (!read.has(i) && need.has(i)) cls.push("miss");
      return `<div class="${cls.join(" ")}" data-col="${i}"><span class="lb">${esc(COLS[i].label)}</span><span class="v ${v ? "" : "empty"}" style="--i:${k++}"><span class="t">${esc(v)}</span></span></div>`;
    };
    const mod = (m) => `<section class="mod"><h3>${esc(m.title)}</h3>${[...Array(m.count).keys()].map((q) => line(m.start + q)).join("")}</section>`;
    return `<header class="lh"><span class="lh-t">Patient record</span><span class="lh-r">the hospital portal<br>recorded ${day(D.meta.generated)}</span></header>
      <p class="whom"><b>${esc(D.patient.mrn)}</b><span>${esc(D.patient.name)}</span><span>${plural(COLS.length, "line", "lines")}, five modules</span></p>
      <div class="mods"><div class="mcol">${MODS.slice(0, 2).map(mod).join("")}</div><div class="mcol">${MODS.slice(2).map(mod).join("")}</div></div>`;
  }
  /* ------------------------------------------------------------ leaf 2: the copy that left */
  function copyHTML() {
    const x = state.reader || "a", r = RUN(x), c = r.copy || { found: false, fields: {} }, e = r.export;
    const purge = (r.audit || []).find((ev) => ev.event === "purge");
    const head = `<header class="lh"><span class="lh-t">The copy that left</span><span class="lh-r">exported ${day(D.meta.generated)}<br>${fmt(e.messages)} HL7 v2 messages, ${fmt(e.resources)} FHIR resources</span></header>`;
    const rn = recordNo(c);
    const whom = `<p class="whom"><b>${rn ? esc(rn.value) : c.found ? "no record number" : "not exported"}</b><span>${rn ? (rn.how === "token" ? "a keyed token stands where the record number was" : rn.how === "raw" ? "the record number as it was read, masked here" : "") : c.found ? "this patient's rows left without one" : ""}</span></p>`;
    let body;
    if (!c.found) {
      body = `<p class="note">${r.named === false && r.rows ? "The rows left without a record number: this patient cannot be found in the copy." : "Nothing about this patient left in this copy."}</p>`;
    } else {
      const oos = new Set(r.oos);
      let k = 0;
      const line = (i) => {
        const f = c.fields[String(i)];
        if (!f) return `<div class="ln gone"><span class="lb">${esc(COLS[i].label)}</span><span class="v" style="--i:${k++}"><span class="t"></span></span></div>`;
        const how = f.how === "token" ? "tok" : f.how === "raw" ? "raw" : f.how === "generalised" ? "gen" : "";
        const tag = f.how === "token" ? "token" : f.how === "raw" ? "raw" : f.how === "generalised" ? "coarsened" : "";
        return `<div class="ln ${oos.has(i) ? "oos" : ""}"><span class="lb">${esc(COLS[i].label)}</span><span class="v ${how}" style="--i:${k++}"><span class="t">${esc(shown(f.value))}</span>${tag ? `<span class="how ${how}">${tag}</span>` : ""}</span></div>`;
      };
      const mod = (m) => `<section class="mod"><h3>${esc(m.title)}</h3>${[...Array(m.count).keys()].map((q) => line(m.start + q)).join("")}</section>`;
      body = `<div class="mods"><div class="mcol">${MODS.slice(0, 2).map(mod).join("")}</div><div class="mcol">${MODS.slice(2).map(mod).join("")}</div></div>`;
    }
    const stamp = r.erase
      ? (state.erased ? `<div class="stamp">Destroyed ${esc(day(r.erase))}<small>${esc(purged(purge))}</small></div>`
                      : `<div class="stamp">Destroy after<small>${esc(day(r.erase))}</small></div>`)
      : `<div class="stamp never">No destruction date<small>kept indefinitely</small></div>`;
    return head + whom + body + stamp;
  }

  /* ------------------------------------------------------------ leaf 3: the access slip */
  function slipRows() {
    const rows = [];
    for (const x of ["a", "b", "c"]) for (const j of D.jobs) {
      const r = RUN(x, j.id);
      if (!readsPatient(r)) continue;
      rows.push({ x, job: j, r });
    }
    return rows;
  }
  function slipHTML() {
    const rows = slipRows();
    const body = rows.map(({ x, job, r }) => {
      const [w, sub] = NAME[x](), e = r.export;
      const left = e.kind === "tok" ? `<span class="tk"><span>${esc(e.token.slice(0, 8))}</span><wbr><span>${esc(e.token.slice(8))}</span></span>` : e.kind === "raw" ? `<span class="rw">raw</span>` : `<span class="dim">nothing</span>`;
      return `<tr class="${x === state.reader ? "cur" : ""}" data-r="${x}"><td>${esc(w)}${x === "b" ? `<span class="dim"> · ${esc(sub.replace(/^told /, ""))}</span>` : ""}</td><td>${esc(job.name)}<span class="show-s"> · ${plural(r.cols.length, "line", "lines")}</span></td>
        <td class="hide-s">${plural(r.cols.length, "line", "lines")}</td><td>${left}</td><td class="d ${r.erase ? "" : "never"}">${r.erase ? esc(day(r.erase)) : "never"}</td></tr>`;
    }).join("");
    return `<header class="slip-h"><span class="lh-t">Record access slip</span><span class="lh-r">${esc(D.patient.mrn)}<br>read on ${day(D.meta.generated)}</span></header>
      <table class="slip"><thead><tr><th>Read by</th><th>For</th><th class="hide-s">Lines</th><th>Left as</th><th>Destroy after</th></tr></thead><tbody>${body}</tbody></table>`;
  }

  /* ------------------------------------------------------------ the reading card */
  const facts = (rows) => `<dl class="facts">${rows.filter(Boolean).map(([k, v]) => `<dt>${esc(k)}</dt><dd>${v}</dd>`).join("")}</dl>`;
  function cardHTML() {
    const job = JOB();
    if (state.leaf === 3) {
      const rows = slipRows(), never = rows.filter((x) => !x.r.erase).length, raw = rows.filter((x) => x.r.export.kind === "raw").length;
      return `<p class="who">This record<small>${esc(D.patient.mrn)}, by ours, ${esc(MODEL().name)} and the baseline</small></p>
        <p class="big"><span class="n">${fmt(rows.length)}</span><span class="u">${rows.length === 1 ? "reading" : "readings"}</span></p>
        ${facts([["Destroyed on a date", fmt(rows.length - never)], ["Never destroyed", never ? `<span class="bad">${fmt(never)}</span>` : "0"],
                 ["Left raw", raw ? `<span class="bad">${fmt(raw)}</span>` : "0"]])}
        <p class="prov">The answer to the patient's right of access, from the run's own record.</p>`;
    }
    if (!state.reader) {
      return `<p class="who">No reader chosen<small>choose a tab on the folder</small></p>
        <p class="big"><span class="n">0</span><span class="u">of ${COLS.length} lines read</span></p>
        ${facts([["The job", esc(job.name)], ["Purpose", esc(job.purpose_label)], ["It needs", plural(job.needed.length, "line", "lines")]])}
        ${keyHTML()}`;
    }
    const x = state.reader, [w, sub] = NAME[x](), r = RUN(x), t = TECH(x);
    if (state.leaf === 2) {
      const c = r.copy || { fields: {} };
      const rn = recordNo(c);
      const dob = c.fields[String(COLS.findIndex((k) => k.field === "date_of_birth"))];
      const purge = (r.audit || []).find((ev) => ev.event === "purge"), s = r.sidecar || {};
      return `<p class="who">${esc(w)}<small>${esc(sub)}</small></p>
        <p class="big ${r.erase ? "" : "bad"}"><span class="n mid">${r.erase ? esc(day(r.erase)) : "Never"}</span></p>
        <p class="u">${r.erase ? `the copy is destroyed${state.erased ? "" : " on this date"}` : "nothing schedules its destruction"}</p>
        ${facts([["Record number", rn ? (rn.how === "token" ? "a keyed token" : `<span class="bad">raw</span>`) : c.found ? "left without one" : "not exported"],
                 dob ? ["Date of birth", dob.how === "generalised" ? "the year only" : `<span class="bad">as read</span>`] : null,
                 ["Retention", r.retention ? `${plural(r.retention, "day", "days")}, of ${fmt(job.ceiling)} allowed` : `<span class="bad">not declared</span>`],
                 ["The key", s.key_holder ? `held apart by ${esc(s.key_holder)}` : "none"],
                 purge ? [state.erased ? "Destroyed" : "Destroys", esc(purged(purge))] : null])}
        <p class="prov">${r.erase ? (state.erased ? "Turned to the erase date: the copy is gone." : "E turns to the erase date.") : "E turns to the erase date: nothing changes."}</p>`;
    }
    const n = linesRead(r).size, oth = others(r), trap = (t.bench.traps || {})[state.job];
    return `<p class="who">${esc(w)}<small>${esc(sub)}${t.sampled ? ` · run 1 of ${t.samples}` : ""}</small></p>
      <p class="big"><span class="n">${fmt(n)}</span><span class="u">of ${COLS.length} lines read</span></p>
      ${facts([["This patient", readsPatient(r) ? (r.named ? "read" : "read, without a record number") : "not read"],
               ["Other patients", oth ? `<span class="${job.single ? "bad" : ""}">${plural(oth, "record", "records")} read too</span>` : "none"],
               ["Outside the purpose", r.oos.length ? `<span class="bad">${esc(r.oos.map((i) => COLS[i].label).join(", "))}</span>` : "none"],
               ["Needed, still covered", r.missed.length ? esc(r.missed.map((i) => COLS[i].label).join(", ")) : "none"],
               ["Page loads", fmt(r.pages)],
               job.trap && trap ? ["Trap", trap[0] === trap[1] ? `held in ${trap[0]} of ${trap[1]} ${trap[1] === 1 ? "run" : "runs"}` : `<span class="bad">taken in ${trap[1] - trap[0]} of ${trap[1]} ${trap[1] === 1 ? "run" : "runs"}</span>`] : null])}
      ${keyHTML()}`;
  }
  const keyHTML = () => `<div class="key-l"><span><i></i>covered: not read</span><span><i class="oos"></i>read, outside the purpose</span><span><i class="miss"></i>needed, still covered</span></div>`;

  /* ------------------------------------------------------------ chrome */
  function chrome() {
    $("job").innerHTML = D.jobs.map((j) => `<option value="${esc(j.id)}">${esc(j.name)}${j.trap ? " (trap)" : ""}</option>`).join("");
    $("model").innerHTML = D.models.map((m) => `<option value="${esc(m.id)}">${esc(m.name)}</option>`).join("");
    $("brief").innerHTML = BRIEF.map((b) => `<button type="button" role="radio" data-brief="${b.id}">${esc(b.label.replace(/^told /, ""))}</button>`).join("");
    $("leaves").innerHTML = LEAVES.map(([name, n]) => `<button type="button" data-leaf="${n}"><b>${n}</b><span>${esc(name)}</span></button>`).join("") + `<i class="lvm" aria-hidden="true"></i>`;
    $("stack").innerHTML = Array.from({ length: PTS - 1 }, (_, k) => `<i style="--k:${k}"></i>`).join("");
    $("tabs").innerHTML = ["a", "b", "c"].map((x) => `<button class="tab" type="button" data-reader="${x}" aria-pressed="false"></button>`).join("");
  }
  function fan(show = true) {              // the other records read too fan out behind the folder (red when the job is about one patient)
    const r = state.reader ? RUN(state.reader) : null;
    const out = show && state.leaf === 1 && r ? others(r) : 0, breach = JOB().single;
    document.querySelectorAll("#stack i").forEach((el, k) => { el.classList.toggle("out", k < out); el.classList.toggle("brk", k < out && breach); });
  }
  function sync(fanNow = true) {
    $("job").value = state.job;
    $("model").value = state.model;
    document.body.dataset.leaf = String(state.leaf);
    document.querySelectorAll("#brief button").forEach((b) => b.setAttribute("aria-checked", String(b.dataset.brief === state.brief)));
    document.querySelectorAll("#leaves button").forEach((b) => { b.removeAttribute("aria-current"); if (+b.dataset.leaf === state.leaf) b.setAttribute("aria-current", "page"); });
    document.querySelectorAll("#tabs .tab").forEach((t) => {          // the tabs stay; the chosen one comes forward
      const x = t.dataset.reader, [w, sub] = NAME[x](), html = `<b>${x}</b>${esc(w)}${x === "b" ? `<small>${esc(sub)}</small>` : ""}`;
      if (t.innerHTML !== html) t.innerHTML = html;
      t.setAttribute("aria-pressed", String(x === state.reader));
    });
    if (fanNow) fan();
    const last = beats().length - 1 === beatIndex() && state.leaf === 3;
    $("next").querySelector("span").textContent = last ? "Again" : "Next";
    const lb = document.querySelector('#leaves button[aria-current="page"]'), lm = document.querySelector("#leaves .lvm");
    if (lb && lm) slideTo(lm, lb.offsetLeft, lb.offsetWidth);
    history.replaceState(null, "", `#${state.leaf}${state.reader || ""}${state.erased ? "e" : ""}`);
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

  /* ------------------------------------------------------------ motion: each step plays; a second press lands it */
  const EASE = "cubic-bezier(.16, 1, .3, 1)";
  const tweens = new Set();
  let until = 0;
  const now = () => performance.now();
  const busy = () => now() < until;
  const hold = (ms) => { until = Math.max(until, now() + ms); };
  function anim(el, frames, o = {}) {      // holds its first frame until its delay is up, then lands on the page's own style
    if (!el || still()) return null;
    const opt = { duration: 420, easing: EASE, fill: "backwards", ...o };
    hold((opt.delay || 0) + opt.duration);
    return el.animate(frames, opt);
  }
  const rise = (el, delay, duration = 400, by = ".3em") => anim(el, [{ opacity: 0, transform: `translateY(${by})` }, { opacity: 1, transform: "none" }], { delay, duration });
  const fade = (el, delay, duration = 340) => anim(el, [{ opacity: 0 }, { opacity: 1 }], { delay, duration, easing: "ease-out" });
  const print = (el, delay, duration = 180) => anim(el, [{ opacity: 0, transform: "translateY(1px)" }, { opacity: 1, transform: "none" }], { delay, duration, easing: "ease-out" });   // written whole
  const flash = (el, delay, colour, duration = 1100) => anim(el, [{ backgroundColor: colour }, { backgroundColor: "rgba(0, 0, 0, 0)" }], { delay, duration, easing: "ease-out" });
  const gap = (n, total, most) => (n > 1 ? Math.min(most, total / (n - 1)) : 0);
  const numeric = (s) => /^[\d,]+$/.test(String(s).trim());
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
  const idx = (v) => +v.style.getPropertyValue("--i") || 0;
  const LIFTED = (i) => i * 18 + 220;      // a bar is half wiped off its value: the CSS wipe (ease-in) runs .36s from i x 18ms
  const STAMP_INK = "rgba(51, 71, 154, .22)";

  /* the record: which lines this reader's run read */
  function lines(x) {
    const r = x ? RUN(x) : null, job = JOB();
    return { read: r ? linesRead(r) : new Set(), oos: r ? new Set(r.oos) : new Set(), need: new Set(job.needed.map((n) => n.col)) };
  }
  function relift(x = state.reader) {      // the same sheet: bars lift or settle in place for another reader
    const { read, oos, need } = lines(x);
    document.querySelectorAll("#sheet .ln").forEach((el) => {
      const i = +el.dataset.col;
      el.classList.toggle("read", read.has(i));
      el.classList.toggle("oos", read.has(i) && oos.has(i));
      el.classList.toggle("miss", !read.has(i) && need.has(i));
    });
  }
  function layDown(d) {                    // every value covered: a bar laid over each, module by module
    const vs = [...document.querySelectorAll("#sheet .v")];
    document.querySelectorAll("#sheet .mod h3").forEach((h) => fade(h, d + idx(h.parentElement.querySelector(".v")) * 22, 320));
    document.querySelectorAll("#sheet .lb").forEach((l) => fade(l, d + idx(l.nextElementSibling) * 22, 320));
    vs.forEach((v) => anim(v, [{ clipPath: "inset(0 100% 0 0)" }, { clipPath: "inset(0 0 0 0)" }], { delay: d + 60 + idx(v) * 22, duration: 360, easing: "cubic-bezier(.65, 0, .35, 1)", pseudoElement: "::after" }));
    return d + 60 + vs.length * 22 + 360;
  }
  function liftPlay(before, d = 0) {       // bars wipe off down the page; the card counts each line as it is uncovered. Returns when the wave is done
    const ln = [...document.querySelectorAll("#sheet .ln")];
    const ev = ln.map((l) => [d + LIFTED(idx(l.querySelector(".v"))) + 80, before.has(+l.dataset.col) ? 1 : 0, l.classList.contains("read") ? 1 : 0]);   // a line counts once it is off
    const T = Math.max(d, ...ev.map((e) => e[0])) + 220;
    const n = document.querySelector("#card .big .n");
    if (n && numeric(n.textContent)) {
      const end = n.textContent;
      tween(T, 0, (f) => {
        if (f >= 1) { n.textContent = end; return; }
        const at = f * T;
        n.textContent = fmt(ev.reduce((s, [t, a, b]) => s + (at >= t ? b : a), 0));
      });
    }
    // the red pencil goes under a value read outside the purpose once its bar is off
    ln.filter((l) => l.classList.contains("oos") && !before.has(+l.dataset.col)).forEach((l) => {
      const v = l.querySelector(".v");
      anim(v.querySelector(".t"), [{ backgroundSize: "0% .55em" }, { backgroundSize: "100% .55em" }], { delay: d + idx(v) * 18 + 380, duration: 480, easing: "cubic-bezier(.5, 0, .3, 1)" });
    });
    return T;
  }
  function stampIn(st, delay) {            // the stamp comes down, and the sheet takes it. Returns when it is down
    if (!st) return delay;
    anim(st, [{ opacity: 0, transform: "rotate(-5deg) scale(1.08)" }, { opacity: 1, transform: "rotate(-5deg) scale(1)" }], { delay, duration: 260, easing: "cubic-bezier(.2, .7, .3, 1)" });
    anim($("sheet"), [{ transform: "none" }, { transform: "scale(.996)", offset: 0.5 }, { transform: "none" }], { delay: delay + 160, duration: 220, easing: "ease-out" });
    return delay + 260;
  }

  /* each leaf, set the way it was made */
  function recordIn(d) {                   // returns when the figure appears and when the lift is done
    const sh = $("sheet");
    rise(sh.querySelector(".lh"), d, 440);
    fade(sh.querySelector(".whom"), d + 120, 420);
    fan(false);
    if (!state.reader) { layDown(d + 180); return null; }
    relift(null);                          // laid down first, then this run's bars come off
    const t = layDown(d + 180), maxI = Math.max(0, ...[...sh.querySelectorAll(".v")].map(idx)), T = t + LIFTED(maxI) + 220;
    tween(t, 0, (f) => { if (f >= 1) { relift(); liftPlay(new Set()); } });
    tween(T, 0, (f) => { if (f >= 1) fan(); });
    return { figAt: t, T };
  }
  function copyIn(d) {                     // returns when the stamp is down
    const sh = $("sheet");
    rise(sh.querySelector(".lh"), d, 440);
    fade(sh.querySelector(".whom"), d + 120, 420);
    const ln = [...sh.querySelectorAll(".ln")], g = gap(ln.length, 900, 26);
    ln.forEach((l, i) => {
      const at = d + 200 + i * g;
      fade(l, at, 320);
      l.querySelectorAll(".v.tok .t").forEach((t) => flash(t, at + 200, STAMP_INK));
      if (l.classList.contains("oos")) { const t = l.querySelector(".v .t"); if (t) anim(t, [{ backgroundSize: "0% .55em" }, { backgroundSize: "100% .55em" }], { delay: at + 260, duration: 480 }); }
    });
    fade(sh.querySelector(".note"), d + 260, 480);
    return stampIn(sh.querySelector(".stamp"), d + 260 + ln.length * g + 120);
  }
  function slipIn(d) {                     // returns when the count starts and when it is done
    const sh = $("sheet");
    rise(sh.querySelector(".slip-h"), d, 440);
    fade(sh.querySelector(".slip thead"), d + 120, 360);
    const rows = [...sh.querySelectorAll(".slip tbody tr")], g = gap(rows.length, 1100, 150), marks = [];
    rows.forEach((tr, i) => {
      const at = d + 240 + i * g;
      [...tr.children].forEach((td, j) => print(td, td.classList.contains("d") ? at + 260 : at + j * 50));   // the date in stamp ink, printed like the rest
      marks.push(at + 150);                // a reading counts once its row is written
    });
    const n = document.querySelector("#card .big .n");
    if (!n || !numeric(n.textContent) || !marks.length) return null;
    const end = n.textContent, T = marks[marks.length - 1] + 60;
    tween(T, 0, (f) => { n.textContent = f >= 1 ? end : fmt(marks.filter((m) => m <= f * T).length); });
    return { figAt: marks[0], T };
  }
  function cardIn(d, o = {}) {             // the reading card: who first; the figure when its marks set it; a breakdown or verdict when its fact is down
    const c = $("card"), big = c.querySelector(".big");
    fade(c.querySelector(".who"), d, 380);
    if (big && o.counted) { fade(big.querySelector(".n"), o.figAt != null ? o.figAt : d, 300); fade(big.querySelector(".u"), d + 60, 380); }
    else if (big) rise(big, o.bigAt != null ? o.bigAt : d + 120, 520, ".2em");
    fade(c.querySelector(":scope > .u"), o.bigAt != null ? o.bigAt + 120 : d + 200, 380);
    const f0 = o.factsAt != null ? o.factsAt : d + 240;
    c.querySelectorAll(".facts dt").forEach((dt, i) => { fade(dt, f0 + i * 60, 340); fade(dt.nextElementSibling, f0 + 30 + i * 60, 340); });
    fade(c.querySelector(".key-l"), d + 520, 420);
    fade(c.querySelector(".prov"), o.bigAt != null ? o.bigAt + 240 : o.factsAt != null ? o.factsAt + 200 : d + 600, 420);
  }
  function patchCard(when) {               // only what changed on the card is rewritten, each part when its fact is down
    const c = $("card"), tmp = document.createElement("div");
    tmp.innerHTML = cardHTML();
    const a = [...c.children], b = [...tmp.children];
    const show = (el) => { const t = when(el); if (t != null) fade(el, t, 340); };
    if (a.length !== b.length || a.some((el, i) => el.tagName !== b[i].tagName || el.className !== b[i].className)) {
      c.replaceChildren(...b); [...c.children].forEach(show); return;
    }
    a.forEach((el, i) => {
      const nu = b[i];
      if (el.outerHTML === nu.outerHTML) return;
      if (el.matches("dl.facts") && el.children.length === nu.children.length) {
        [...nu.children].forEach((y, k) => { const x = el.children[k]; if (x.outerHTML !== y.outerHTML) { const z = y.cloneNode(true); x.replaceWith(z); show(z); } });
        return;
      }
      el.replaceWith(nu); show(nu);
    });
  }
  function play(d) {
    if (still()) return;
    if (state.leaf === 1) { const r = recordIn(d); cardIn(d + 100, { counted: true, figAt: r ? r.figAt : undefined, factsAt: r ? r.T : undefined }); }
    else if (state.leaf === 2) { const S = copyIn(d); cardIn(d + 100, { bigAt: S, factsAt: S }); }
    else { const s = slipIn(d); cardIn(d + 100, { counted: true, figAt: s ? s.figAt : undefined, factsAt: s ? s.T : undefined }); }
  }

  /* turning a leaf: the top sheet is lifted and put aside to the left; going back, it is laid on again, whole */
  const SLIDE = 600;
  function keepSheet() {
    const c = $("sheet").cloneNode(true);
    c.removeAttribute("id"); c.removeAttribute("aria-live");
    c.querySelectorAll("[id]").forEach((n) => n.removeAttribute("id"));
    c.classList.add("still");
    return c;
  }
  function slideLeaf(dir, drawFn) {
    if (still() || matchMedia("(max-width: 860px)").matches) return false;
    const desk = $("desk"), db = desk.getBoundingClientRect(), sb = $("sheet").getBoundingClientRect();
    const old = keepSheet();
    drawFn();
    const sheet = (page, cls) => {
      const o = document.createElement("div");
      o.className = `aside ${cls}`; o.setAttribute("aria-hidden", "true");
      Object.assign(o.style, { left: `${sb.left - db.left}px`, top: `${sb.top - db.top}px`, width: `${sb.width}px`, height: `${sb.height}px` });
      o.append(page); desk.append(o);
      return o;
    };
    const flat = "0 1px 1px rgba(0, 0, 0, .14)", lifted = "0 12px 22px -12px rgba(0, 0, 0, .45)";
    const away = "translate(-104%, 1.5%) rotate(-2deg)", up = "translate(-1%, .2%) rotate(-.4deg)";
    const parts = [];
    let last;
    if (dir > 0) {                         // opaque all the way; it fades only once it has cleared the folder
      const o = sheet(old, "");
      parts.push(o);
      last = o.animate([{ transform: "none", boxShadow: flat }, { transform: up, boxShadow: lifted, offset: 0.2 }, { transform: away, boxShadow: lifted, opacity: 1, offset: 0.9 }, { transform: away, boxShadow: lifted, opacity: 0 }], { duration: SLIDE, easing: "cubic-bezier(.42, 0, .58, 1)", fill: "forwards" });
    } else {                               // the landed sheet is laid back on; nothing underneath replays
      const under = sheet(old, "under"), o = sheet(keepSheet(), "");
      parts.push(under, o);
      last = o.animate([{ transform: away, boxShadow: lifted, opacity: 0 }, { transform: away, boxShadow: lifted, opacity: 1, offset: 0.1 }, { transform: up, boxShadow: lifted, offset: 0.8 }, { transform: "none", boxShadow: flat }], { duration: SLIDE, easing: "cubic-bezier(.42, 0, .58, 1)", fill: "both" });
    }
    hold(SLIDE);
    const done = () => parts.forEach((p) => p.remove());
    last.finished.then(done, done);
    return true;
  }

  /* ------------------------------------------------------------ render */
  function drawSheet() {
    const sheet = $("sheet");
    const gone = state.leaf === 2 && state.erased && !!RUN(state.reader || "a").erase;   // only a copy with an erase date empties
    sheet.className = `sheet ${state.leaf === 2 ? "copy" : ""} ${gone ? "erased" : ""}`;
    sheet.innerHTML = state.leaf === 1 ? recordHTML() : state.leaf === 2 ? copyHTML() : slipHTML();
  }
  function draw() {
    drawSheet();
    $("card").innerHTML = cardHTML();
    sync();
  }
  // "turn" a leaf; "lift" the record for another reader or job; "reset" the same leaf for another copy or slip; "erase"; "open"; "now"
  function render(kind, dir = 1) {
    land();
    if (kind === "lift" && state.leaf === 1 && $("sheet").querySelector(".ln")) {
      const before = new Set([...document.querySelectorAll("#sheet .ln.read")].map((l) => +l.dataset.col));
      relift();
      if (still()) { $("card").innerHTML = cardHTML(); sync(); return; }
      sync(false);
      const maxI = Math.max(0, ...[...document.querySelectorAll("#sheet .v")].map(idx)), T = LIFTED(maxI) + 220;
      patchCard((el) => (el.matches(".big") ? null : el.closest(".facts") ? T : 0));   // the breakdown waits for the wave
      liftPlay(before);                    // counts on the patched figure
      tween(T, 0, (f) => { if (f >= 1) fan(); });
      return;
    }
    if (kind === "erase" && state.leaf === 2) {
      const sheet = $("sheet"), r = RUN(state.reader || "a"), st = sheet.querySelector(".stamp");
      sheet.classList.toggle("erased", state.erased && !!r.erase);   // the copy's lines go out one by one (CSS, staggered down the sheet); a copy never destroyed stays
      let at = 0;
      if (st && r.erase) {
        st.outerHTML = copyHTML().match(/<div class="stamp[\s\S]*<\/div>$/)[0];
        if (state.erased) at = stampIn(sheet.querySelector(".stamp"), 0); else fade(sheet.querySelector(".stamp"), 0, 360);
      }
      sync();
      if (still()) { $("card").innerHTML = cardHTML(); return; }
      patchCard(() => at);
      hold(state.erased && r.erase ? 1700 : 400);
      return;
    }
    if (kind === "reset") {
      drawSheet(); sync();
      if (still()) { $("card").innerHTML = cardHTML(); return; }
      if (state.leaf === 2) { const S = copyIn(0); patchCard((el) => (el.matches(".who") ? 0 : S)); }
      else { document.querySelectorAll('#sheet tr[data-r="b"]').forEach((tr, i) => fade(tr, 60 + i * 70, 320)); patchCard(() => 200); }
      return;
    }
    if (kind === "turn") {
      if (slideLeaf(dir, draw)) {
        if (dir > 0) play(120);
        else if (!still()) fade($("card"), SLIDE * 0.6, 320);
        return;
      }
      draw();
      if (!still()) {
        const s = $("sheet");
        s.classList.remove("turn-in"); void s.offsetWidth; s.classList.add("turn-in");
        s.addEventListener("animationend", () => s.classList.remove("turn-in"), { once: true });
        play(120);
      }
      return;
    }
    draw();
    if (kind === "open") play(200);
  }

  /* ------------------------------------------------------------ the presenter's path */
  function beats(leaf = state.leaf) {
    if (leaf === 1) return [[null, false], ["a", false], ["b", false], ["c", false]];
    if (leaf === 2) return [["a", false], ["a", true], ["b", false], ["b", true], ["c", false], ["c", true]];
    return [[state.reader, false]];
  }
  const beatIndex = () => Math.max(0, beats().findIndex(([x, e]) => x === state.reader && e === state.erased));
  function setBeat(leaf, i, dir = 1) {
    const b = beats(leaf)[i], turn = leaf !== state.leaf, readerChange = b[0] !== state.reader, eraseChange = b[1] !== state.erased;
    state.leaf = leaf; state.reader = b[0]; state.erased = b[1];
    render(turn ? "turn" : readerChange ? (leaf === 1 ? "lift" : leaf === 2 ? "reset" : "now") : eraseChange ? "erase" : "now", dir);
  }
  function next() {
    if (busy()) { land(); return; }        // a second press lands the step that is playing
    const i = beatIndex(), last = beats().length - 1;
    if (i < last) setBeat(state.leaf, i + 1);
    else if (state.leaf < 3) setBeat(state.leaf + 1, 0);
    else setBeat(1, 0, -1);
  }
  function prev() {
    const i = beatIndex();
    if (i > 0) setBeat(state.leaf, i - 1, -1);
    else if (state.leaf > 1) setBeat(state.leaf - 1, beats(state.leaf - 1).length - 1, -1);
  }
  function leaf(n) {
    if (n === state.leaf || n < 1 || n > 3) return;
    const dir = n > state.leaf ? 1 : -1;
    state.leaf = n;
    if (n === 2 && !state.reader) state.reader = "a";
    state.erased = false;
    render("turn", dir);
  }
  function reader(x) {
    if (x === state.reader) return;
    state.reader = x; state.erased = false;
    render(state.leaf === 1 ? "lift" : state.leaf === 2 ? "reset" : "now");
  }
  function respec(aboutB) {                // the run changed, not the leaf: the job (aboutB false), or the model or briefing behind reader b
    if (state.leaf === 1) render(!aboutB || state.reader === "b" ? "lift" : "now");
    else if (state.leaf === 2) render(!aboutB || state.reader === "b" ? "reset" : "now");
    else render(aboutB ? "reset" : "now");
  }
  function erase() { if (state.leaf !== 2) return; if (!state.reader) state.reader = "a"; state.erased = !state.erased; render("erase"); }
  const cycle = (list, cur, d) => list[(list.indexOf(cur) + d + list.length) % list.length];

  document.addEventListener("click", (e) => {
    const t = e.target.closest("[data-reader],[data-leaf],[data-brief]");
    if (!t || t.closest(".aside")) return;
    if (t.dataset.reader) reader(t.dataset.reader);
    else if (t.dataset.leaf) leaf(+t.dataset.leaf);
    else if (t.dataset.brief) { state.brief = t.dataset.brief; respec(true); }
  });
  $("job").addEventListener("change", (e) => { state.job = e.target.value; state.erased = false; respec(false); });
  $("model").addEventListener("change", (e) => { state.model = e.target.value; respec(true); });
  $("next").addEventListener("click", next);
  $("prev").addEventListener("click", prev);
  document.addEventListener("keydown", (e) => {
    if (e.ctrlKey || e.metaKey || e.altKey) return;
    if ((e.target.tagName || "").toLowerCase() === "select") return;
    const k = e.key;
    let done = true;
    if (k === " " || k === "PageDown") (e.shiftKey ? prev : next)();
    else if (k === "PageUp" || k === "Backspace") prev();
    else if (k === "ArrowRight") leaf(state.leaf + 1);
    else if (k === "ArrowLeft") leaf(state.leaf - 1);
    else if (k === "Home") { state.reader = null; state.erased = false; const d = state.leaf > 1 ? -1 : 1; state.leaf = 1; render("turn", d); }
    else if (k === "End") leaf(3);
    else if (/^[1-3]$/.test(k)) leaf(+k);
    else if (/^[abc]$/i.test(k)) reader(k.toLowerCase());
    else if (k === "e" || k === "E") erase();
    else if (k === "j" || k === "J") { state.job = cycle(D.jobs.map((j) => j.id), state.job, e.shiftKey ? -1 : 1); state.erased = false; respec(false); }
    else if (k === "m" || k === "M") { state.model = cycle(D.models.map((m) => m.id), state.model, e.shiftKey ? -1 : 1); respec(true); }
    else if (k === "t" || k === "T") { state.brief = cycle(BRIEF.map((b) => b.id), state.brief, e.shiftKey ? -1 : 1); respec(true); }
    else done = false;
    if (done) e.preventDefault();
  });
  let rt = 0;
  addEventListener("resize", () => { clearTimeout(rt); rt = setTimeout(() => { land(); sync(); }, 120); });

  const m = location.hash.match(/^#([1-3])([abc]?)(e?)$/);
  if (m) { state.leaf = +m[1]; state.reader = m[2] || (state.leaf === 2 ? "a" : null); state.erased = !!m[3] && state.leaf === 2; }
  chrome();
  let opened = false;
  const open = () => { if (opened) return; opened = true; render("open"); };
  (document.fonts ? document.fonts.ready : Promise.resolve()).then(open);
  setTimeout(open, 1200);
})();
