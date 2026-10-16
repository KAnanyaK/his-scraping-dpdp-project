/* One record followed: a line of a public synthetic export through the seven pipeline stages,
   each column's fate at each stage, for each technique. */
(() => {
  const { D, $, esc, num, f2, human, icon, kindColor, wait, fig, seg } = R;
  const J = D.journey;
  if (!J) return;
  const M = J.meta;
  const KC = (k) => kindColor(k === "ours" ? "ours" : k === "baseline" ? "baseline" : "agent", k);
  const whose = (r) => r.kind === "ours" ? "Ours" : `${r.label}'s`;
  const cols = J.entries.flatMap((e) => e.columns.map((c) => ({ ...c, file: e.file, layer: e.layer })));
  const colById = Object.fromEntries(cols.map((c) => [c.id, c]));
  let TASK = (J.tasks.find((t) => t.trap) || J.tasks[0]).id, LENS = "ours", STAGE = 0, SHOWALL = false, FMT = "hl7";
  let FOLLOW = (cols.find((c) => c.field === "mrn") || cols[0]).id;
  const task = () => J.tasks.find((t) => t.id === TASK);
  const run = () => task().runs.find((r) => r.kind === LENS) || task().runs[0];
  const fate = () => J.fates[`${TASK}|${LENS}|${FOLLOW}`] || [];
  const reg = J.entries[0];

  fig("fig-journey", {
    title: `One line of <span class="mono">${esc(reg.file)}</span>, seven stages`,
    controls: `<button class="btn" id="walk">${icon("play")} Walk the journey</button>`,
    body: `<div class="jctl"><div class="row"><span class="ctl-lab">Job</span><div id="jtask"></div><span id="jbadge"></span></div>`
      + `<div class="row"><span class="ctl-lab">Technique</span><div id="jlens"></div></div>`
      + `<div class="row"><span class="ctl-lab">Follow</span><select id="jfollow" aria-label="Column to follow"></select></div></div>`
      + `<div class="jrail" id="jrail" role="tablist" aria-label="Pipeline stages"></div><div class="jpane" id="jpane"></div>`,
    caption: `${M.values_shown ? "Public synthetic data" : "A real export, structure only"}; identifiers masked. Each dot: the followed column at that stage.`,
  });

  function paintControls() {
    seg("jtask", J.tasks.map((t) => [t.id, `${esc(human(t.id))}${t.trap ? " " + icon("alert") : ""}`]), TASK, (v) => { TASK = v; paintAll(); });
    const t = task();
    $("jbadge").innerHTML = `<span class="flag plain">${esc(human(t.purpose))}</span>` + (t.trap ? ` <span class="flag" title="${esc(t.trap)}">${icon("alert")} trap: ${esc(t.trap)}</span>` : "");
    seg("jlens", M.techniques.map((k) => [k.kind, `<span class="sw" style="--c:${KC(k.kind)}"></span>${esc(k.label)}`]), LENS, (v) => { LENS = v; paintAll(); });
    $("jfollow").innerHTML = J.entries.map((e) => `<optgroup label="${esc(e.file)}">` + e.columns.map((c) => `<option value="${esc(c.id)}"${c.id === FOLLOW ? " selected" : ""}>${esc(c.h)}${c.field ? " → " + esc(c.field) : ""}</option>`).join("") + `</optgroup>`).join("");
  }
  $("jfollow").addEventListener("change", (e) => { FOLLOW = e.target.value; paintAll(); });
  const setFollow = (id) => { FOLLOW = id; paintAll(); };

  function paintRail() {
    const f = fate();
    $("jrail").innerHTML = J.stages.map((s, i) => {
      const x = f[i] || { s: "none", t: "" };
      return `<button class="jst" role="tab" data-i="${i}" aria-selected="${i === STAGE}"><span class="jn"><span class="n">${i + 1}</span>${esc(s.label)}</span><span class="jf s-${esc(x.s)}"><i></i><span>${esc(x.t || "–")}</span></span></button>`;
    }).join("");
    $("jrail").querySelectorAll(".jst").forEach((b) => b.addEventListener("click", () => { stopWalk(); STAGE = +b.dataset.i; paintRail(); paintStage(); }));
  }

  /* ------------------------------------------------------------ the seven stage views */
  function colFlow(e) {
    const read = e.columns.filter((c) => c.status === "in").length;
    const flow = e.columns.map((c) => `<button class="cc${c.status === "in" ? " in" : ""}${c.id === FOLLOW ? " on" : ""}" data-c="${esc(c.id)}" title="${c.status === "in" ? "read as " + esc(c.field) : "never read"}">${esc(c.h)}</button>`).join("");
    const f = e.columns.find((c) => c.id === FOLLOW);
    const fol = f ? `<span class="muted">Following</span> <b class="mono">${esc(f.h)}</b> <span class="mono">${esc(f.raw) || '<span class="hid">empty</span>'}</span> ${f.status === "in" ? `<span class="tag in">read as ${esc(f.field)}</span>` : `<span class="tag">never read: ${f.status === "blank" ? "dropped by the column map" : "not understood"}</span>`}`
      : `<span class="muted">${read} of ${e.columns.length} columns read; the rest never leave the file. Click one to follow it.</span>`;
    return { read, html: `<div class="colflow">${flow}</div><div class="fol">${fol}</div>` };
  }
  function entryTable(e, first) {
    return (first ? `<thead><tr><th>Column</th><th>Value</th><th></th><th>Field</th><th>Category</th><th>Held as</th></tr></thead>` : "") + `<tbody><tr class="grp"><td colspan="6">${esc(e.file)} → ${esc(J.layer_labels[e.layer])}${e.confidence ? ` · ${Math.round(e.confidence * 100)}% of the columns it keeps are catalogue fields` : ""}</td></tr>`
      + e.columns.filter((c) => SHOWALL || c.status === "in" || c.id === FOLLOW).map((c) => `<tr class="${c.status === "in" ? "" : "out"}${c.id === FOLLOW ? " on" : ""}" data-c="${esc(c.id)}"><td class="mono">${esc(c.h)}</td><td class="mono">${esc(c.raw) || '<span class="hid">empty</span>'}</td>`
        + (c.status === "in" ? `<td>→</td><td class="mono">${esc(c.field)}</td><td><span class="cat ${esc(c.cat)}">${esc(human(c.cat))}</span></td><td class="mono">${esc(c.held)}</td>` : `<td></td><td colspan="3"><span class="tag">${c.status === "blank" ? "dropped by the column map: never read" : "not a catalogue field: dropped"}</span></td>`) + `</tr>`).join("") + `</tbody>`;
  }
  function rulesCell(rules) {
    const bad = rules.filter((q) => q.status === "fail" || q.status === "partial");
    const tip = (q) => `${esc(q.title)}${q.finding ? ": " + esc(q.finding) : ""}`;
    if (!bad.length) return `<span class="rsum" title="${rules.map(tip).join(" · ")}">${icon("check")} ${rules.length} of ${rules.length} held</span>`;
    return `<div>${bad.map((q) => `<span class="rule ${esc(q.status)}" title="${tip(q)}">${esc(q.id)}</span>`).join("")}</div><div class="muted" style="font-size:.76rem;margin-top:2px">${rules.length - bad.length} of ${rules.length} held</div>`;
  }
  function hilite(s) {
    return esc(s).replace(/PSN-[0-9a-f]{12}/g, (t) => `<span class="tok">${t}</span>`)
      .replace(/[^\s|^"~\\&;:,{}\[\]]{0,2}•+[^\s|^"~\\&;:,{}\[\]]{0,2}/g, (t) => `<span class="raw">${t}</span>`)
      .replace(/(▒▒|‹[a-z_]+›)/g, (t) => `<span class="hid">${t}</span>`);
  }
  const [gy, gm, gd] = M.generated.split("-").map(Number), today = Date.UTC(gy, gm - 1, gd);
  let days = 0, timer = null;
  const VIEWS = [
    () => {   // 1 dataset
      const e0 = J.entries[0], e1 = J.entries[1], a = colFlow(e0), b = e1 ? colFlow(e1) : null;
      return `<h3>The gate, checked before a single row is read</h3><div class="gatebar">${J.gate.checks.map((c) => `<div class="gate${c.ok ? "" : " no"}">${icon(c.ok ? "check" : "x")}<b>${esc(c.name)}</b><span>${esc(c.detail)}</span></div>`).join("")}</div>`
        + `<div class="entry2"><div><h3><span class="mono">${esc(e0.file)}</span>, line ${e0.line}<small>${a.read} of ${e0.columns.length} columns read · one of ${num(e0.rows)} rows</small></h3>${a.html}</div>`
        + (b ? `<div><h3>Same patient, <span class="mono">${esc(e1.file)}</span>, line ${e1.line}<small>${b.read} of ${e1.columns.length} columns read · first diagnosis</small></h3>${b.html}</div>` : "") + `</div>`;
    },
    () => {   // 2 understand
      const followed = colById[FOLLOW], max = Math.max(...J.footprint.map((f) => f.rows), 1);
      return `<div style="display:flex;justify-content:space-between;align-items:center;gap:12px;flex-wrap:wrap;margin-bottom:8px"><h3 style="margin:0">Column by column</h3><div id="jall"></div></div>`
        + `<div class="tbl"><table class="bt ent">${J.entries.map((e, i) => entryTable(e, !i)).join("")}</table></div>`
        + `<div class="split2" style="margin-top:20px"><div><h3>This patient across the export <span class="muted" style="font-weight:400">· ${num(J.footprint.reduce((a, f) => a + f.rows, 0))} rows in ${J.footprint.length} files</span></h3>`
        + [...J.footprint].sort((a, b) => b.rows - a.rows).map((f) => `<div class="barrow"><span class="mono" style="font-size:.78rem">${esc(f.file)}</span><div class="track"><i style="width:${100 * Math.log10(1 + f.rows) / Math.log10(1 + max)}%;background:var(--l${Math.max(0, Object.keys(J.layer_labels).indexOf(f.layer))})"></i></div><span class="tnum" style="text-align:right">${num(f.rows)}</span></div>`).join("")
        + `</div><div><h3>As the adapter holds it <span class="muted" style="font-weight:400">· first record per layer</span></h3>`
        + J.samples.map((s) => `<div style="margin-bottom:10px"><div class="muted" style="font-size:.78rem;margin-bottom:4px">${esc(J.layer_labels[s.layer])}</div><dl class="kvl">${s.fields.map((f) => { const on = followed && followed.field === f.field && followed.layer === s.layer; return `<dt class="${on ? "on" : ""}">${esc(f.field)}</dt><dd class="${on ? "on" : ""}">${esc(f.value) || '<span class="hid">–</span>'}</dd>`; }).join("")}</dl></div>`).join("") + `</div></div>`;
    },
    () => {   // 3 extract
      const t = task(), followed = colById[FOLLOW];
      return `<h3>${esc(t.description)} <span class="muted" style="font-weight:400">· needs ${t.needs.map((n) => `<span class="mono">${esc(n.field)}</span>`).join(", ")} · ${num(t.own)} of this patient's records</span></h3>`
        + `<div class="tbl"><table class="bt"><thead><tr><th>Technique</th><th class="n">Score</th><th class="n">Records read</th><th>Fields taken</th><th>Rules</th></tr></thead><tbody>`
        + t.runs.map((r) => {
          const x = r.record_excess;
          const chips = r.fields.map((f) => `<span class="chip ${!f.allowed ? "oos" : f.needed ? "need" : "extra"}${followed && followed.field === f.field && followed.layer === f.layer ? " on" : ""}" title="${esc(J.layer_labels[f.layer])} · ${esc(human(f.cat))}">${esc(f.field)}</span>`).join(" ");
          return `<tr data-k="${esc(r.kind)}" style="cursor:pointer${r.kind === LENS ? ";background:var(--teal-wash)" : ""}"><td><span class="who"><span class="sw" style="--c:${KC(r.kind)}"></span><b>${esc(r.label)}</b></span></td><td class="n">${f2(r.score)}</td><td class="n">${num(r.records)}<div class="muted">${x ? (x > 1.05 ? `<span class="no">${x >= 10 ? num(Math.round(x)) : f2(x)}× own</span>` : "≤ 1× own") : ""}</div></td><td><div style="display:flex;flex-wrap:wrap;gap:3px">${chips}</div></td><td>${rulesCell(r.rules)}</td></tr>`;
        }).join("") + `</tbody></table></div>`;
    },
    () => {   // 4 normalise
      const r = run(), ex = r.export, items = ex[FMT];
      return `<div style="display:flex;justify-content:space-between;gap:12px;flex-wrap:wrap;align-items:center;margin-bottom:10px"><h3 style="margin:0"><span class="who"><span class="sw" style="--c:${KC(r.kind)}"></span>${esc(r.label)}: ${num(ex.counts.hl7_messages)} HL7 v2 messages, ${num(ex.counts.fhir_resources)} FHIR resources</span></h3><div id="jfmt"></div></div>`
        + `<div class="pseudo">The patient <span class="rawid">${esc(M.mrn_shown)}</span> →${r.manifest.pseudonymised ? ` <span class="token">${esc(M.token)}</span><span class="muted">keyed, one-way: the raw number never leaves</span>` : ` <span class="rawid">exported as it is</span><span class="muted">no pseudonymisation declared</span>`}</div>`
        + `<div class="auditline ${ex.leaked ? "no" : "ok"}">${icon(ex.leaked ? "x" : "shield")} Export audit: ${esc(ex.audit)}</div>`
        + `<pre class="code">${items.length ? items.map((it) => `<span class="hid">── ${esc(J.layer_labels[it.layer] || it.layer)} ──</span>\n${hilite(it.text)}`).join("\n\n") : '<span class="hid">nothing exported</span>'}</pre>`;
    },
    () => {   // 5 purpose
      const r = run();
      return `<h3><span class="who"><span class="sw" style="--c:${KC(r.kind)}"></span>${esc(whose(r))} pull, judged under every purpose</span> <span class="muted" style="font-weight:400">· the records, manifest and rules unchanged; only the purpose moves</span></h3>`
        + r.purposes.map((v) => `<div class="barrow"><span>${esc(human(v.purpose))}${v.declared ? ' <span class="flag plain">declared</span>' : ""}</span><div><div class="track"><i style="width:${100 * v.score}%;background:${v.score >= 0.999 ? "var(--held)" : v.score >= 0.85 ? "var(--caution)" : "var(--harm)"}"></i></div><div class="muted" style="font-size:.78rem;margin-top:3px">${esc(v.verdict)}</div></div><span class="tnum" style="text-align:right;font-family:var(--fig)">${v.score.toFixed(2)}</span></div>`).join("");
    },
    () => {   // 6 assist
      const r = run(), followed = colById[FOLLOW];
      return `<h3>Who the assistant may walk through what <span class="who" style="margin-left:6px"><span class="sw" style="--c:${KC(r.kind)}"></span>${esc(r.label)} took</span> <span class="muted" style="font-weight:400">· a role sees a field only if its purposes and its standards both allow the category</span></h3>`
        + `<div class="tbl"><table class="bt"><thead><tr><th>Field</th><th>Category</th>${J.roles.map((q) => `<th style="text-align:center;text-transform:capitalize" title="${esc(q.description)}">${esc(q.id)}</th>`).join("")}</tr></thead><tbody>`
        + r.fields.map((f) => `<tr${followed && followed.field === f.field && followed.layer === f.layer ? ' style="background:var(--teal-wash)"' : ""}><td class="mono">${esc(f.field)}</td><td><span class="cat ${esc(f.cat)}">${esc(human(f.cat))}</span></td>${J.roles.map((q) => { const ok = q.allowed.includes(f.cat); return `<td style="text-align:center" class="${ok ? "yes" : "no"}">${icon(ok ? "check" : "x")}</td>`; }).join("")}</tr>`).join("") + `</tbody></table></div>`;
    },
    () => {   // 7 retain
      const r = run(), rt = r.retain, max = Math.max(60, (rt.days || 0) + 30);
      days = Math.min(days, max);
      const when = new Date(today + days * 86400000).toISOString().slice(0, 10), gone = rt.erase_after && when >= rt.erase_after;
      return `<div class="timebar"><button class="btn" id="jret">${icon(timer ? "pause" : "play")} ${timer ? "Pause" : "Play"}</button><input type="range" id="jdays" min="0" max="${max}" value="${days}" aria-label="Days from today"><div class="day">${days === 0 ? "Today" : `+${days} days`}<small>${when}</small></div></div>`
        + `<div class="split2"><div><h3>The audit log <span class="muted" style="font-weight:400">· written by the harness, not the technique</span></h3><div class="log">`
        + r.log.map((e) => `<div class="ev${e.event === "purge" && !gone ? " later" : ""}"><span>${esc(e.at)}</span><span class="e">${esc(e.event)}</span><span>${esc(e.note || `${num(e.records)} records; ${Object.entries(e.fields).map(([, fs]) => fs.join(", ")).join("; ")}`)}</span></div>`).join("")
        + (rt.erase_after ? "" : `<div class="ev"><span>never</span><span class="e no">purge</span><span class="no">no retention declared: nothing can schedule the erasure</span></div>`)
        + `</div></div><div><h3><span class="who"><span class="sw" style="--c:${KC(r.kind)}"></span>${esc(whose(r))} export</span> <span class="muted" style="font-weight:400">· ${rt.days ? `kept ${rt.days} d of the ${rt.ceiling} d allowed · erase on or after ${esc(rt.erase_after)}` : "no retention declared"}</span></h3>`
        + Object.entries(rt.files).map(([n, size]) => `<div class="file${gone ? " gone" : ""}"><span>${esc(n)}</span><span>${gone ? "erased" : num(size) + " B"}</span></div>`).join("") + `</div></div>`;
    },
  ];
  function paintStage() {
    $("jpane").innerHTML = VIEWS[STAGE]();
    const p = $("jpane");
    p.querySelectorAll("[data-c]").forEach((x) => x.addEventListener("click", () => setFollow(x.dataset.c)));
    p.querySelectorAll("tr[data-k]").forEach((x) => x.addEventListener("click", () => { LENS = x.dataset.k; paintAll(); }));
    if ($("jall")) seg("jall", [["read", "Columns read"], ["all", "All columns"]], SHOWALL ? "all" : "read", (v) => { SHOWALL = v === "all"; paintStage(); });
    if ($("jfmt")) seg("jfmt", [["hl7", "HL7 v2"], ["fhir", "FHIR"]], FMT, (v) => { FMT = v; paintStage(); });
    if ($("jdays")) {
      $("jdays").addEventListener("input", (e) => { stopTime(); days = +e.target.value; paintStage(); });
      $("jret").addEventListener("click", () => {
        if (timer) { stopTime(); paintStage(); return; }
        if (days >= +$("jdays").max) days = 0;
        timer = setInterval(() => {
          if (STAGE !== 6 || !$("jdays")) { stopTime(); return; }
          days = Math.min(days + 3, +$("jdays").max);
          if (days >= +$("jdays").max) stopTime();
          paintStage();
        }, 30);
        paintStage();
      });
    }
  }
  function stopTime() { if (timer) { clearInterval(timer); timer = null; } }
  function paintAll() { stopTime(); paintControls(); paintRail(); paintStage(); }

  let walking = null;
  function stopWalk() { if (walking) { clearInterval(walking); walking = null; $("walk").innerHTML = `${icon("play")} Walk the journey`; } }
  $("walk").addEventListener("click", () => {
    if (walking) { stopWalk(); return; }
    STAGE = 0; paintRail(); paintStage();
    $("walk").innerHTML = `${icon("pause")} Stop`;
    walking = setInterval(() => {
      if (STAGE + 1 >= J.stages.length) { clearInterval(walking); walking = null; $("walk").innerHTML = `${icon("replay")} Walk again`; return; }
      STAGE += 1; stopTime(); paintRail(); paintStage();
    }, R.still ? 600 : 2600);
  });
  paintAll();
})();
