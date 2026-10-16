/* Sensitivity: a simulated vendor release (layout v2) against the benchmarked portal (v1). */
(() => {
  const { D, $, esc, cap, dash, icon, modelColor, fig, seg } = R;
  const U = D.update;
  if (!U) return;
  const M = U.meta, TK = Object.fromEntries(U.tasks.map((t) => [t.id, t]));
  const screens = U.release.filter((r) => r.old);

  /* ------------------------------------------------------------ Figure: the release */
  (() => {
    const KIND = { renamed: "renamed", split: "split in two", moved: "moved", gone: "gone", same: "unchanged", across: "on every screen" };
    const wire = (n) => n <= 1
      ? `<svg class="wire" viewBox="0 0 64 40" preserveAspectRatio="none" aria-hidden="true"><path d="M4 20H56" stroke="currentColor" stroke-width="1.5" fill="none" vector-effect="non-scaling-stroke"/><path d="M50 15l7 5-7 5" stroke="currentColor" stroke-width="1.5" fill="none" stroke-linejoin="round" vector-effect="non-scaling-stroke"/></svg>`
      : `<svg class="wire" viewBox="0 0 64 96" preserveAspectRatio="none" aria-hidden="true"><path d="M4 48H26M26 48C36 48 36 22 46 22H56M26 48C36 48 36 74 46 74H56" stroke="currentColor" stroke-width="1.5" fill="none" vector-effect="non-scaling-stroke"/><path d="M50 17l7 5-7 5M50 69l7 5-7 5" stroke="currentColor" stroke-width="1.5" fill="none" stroke-linejoin="round" vector-effect="non-scaling-stroke"/></svg>`;
    let sel = Math.max(0, U.release.findIndex((r) => r.kind === "split"));
    function movesFirst(cs) {
      const out = [], by = {};
      cs.forEach((c) => {
        const m = c.text.match(/^(.+?) moved: (.+?) → (.+?)\.$/);
        if (!m) { out.push(c); return; }
        const k = m[2] + "\u0000" + m[3];
        if (!by[k]) { by[k] = { kind: c.kind, cols: [], from: m[2], to: m[3] }; out.push(by[k]); }
        by[k].cols.push(m[1]);
      });
      return out.map((c) => c.cols ? { kind: c.kind, text: `${c.cols.length > 1 ? c.cols.slice(0, -1).join(", ") + " and " + c.cols[c.cols.length - 1] : c.cols[0]} moved: ${c.from} → ${c.to}.` } : c);
    }
    function changeRow(c) {
      let m = c.text.match(/^The "(.+?)" column is now headed "(.+?)"\.$/);
      if (m) return `<div class="ch"><span class="from">${esc(m[1])}</span><span class="ar">→</span><span class="to">${esc(m[2])}</span></div>`;
      m = c.text.match(/^(.+?) moved: (.+?) → (.+?)\.$/);
      if (m) return `<div class="ch"><span class="from">${esc(m[2])}</span><span class="ar">→</span><span class="to">${esc(m[3])}</span><span class="where">the ${esc(m[1])} column${/ and /.test(m[1]) ? "s" : ""}</span></div>`;
      m = c.text.match(/^"(.+?)" is now "(.+?)"(?: \((.+)\)|, on (.+))?\.$/);
      if (m) return `<div class="ch"><span class="from">${esc(m[1])}</span><span class="ar">→</span><span class="to">${esc(m[2])}</span>${m[3] || m[4] ? `<span class="where">${esc(m[3] || m[4])}</span>` : ""}</div>`;
      if (/ is gone| no longer found/.test(c.text)) return `<div class="ch gone">${icon("alert")}<span>${esc(dash(c.text))}</span></div>`;
      return `<div class="ch ${c.kind === "unmapped" ? "warn" : ""}">${esc(dash(c.text))}</div>`;
    }
    function paint() {
      const r = U.release[sel];
      const rows = U.release.map((x, i) => {
        const left = x.old ? `<div class="scr old"><span class="t2">${esc(x.old.title)}</span><span class="p">${esc(x.old.path)}</span></div>` : `<div class="scr old"><span class="t2">Column headings</span><span class="p">wherever they appear</span></div>`;
        const right = x.new.length ? `<div class="news">${x.new.map((s) => `<div class="scr"><span class="t2">${esc(s.title)}</span><span class="p">${esc(s.path)}</span></div>`).join("")}</div>` : `<div class="news"><div class="scr"><span class="t2">Renamed</span><span class="p">same columns, new words</span></div></div>`;
        const n = x.changes.length;
        return `<button class="rrow" data-i="${i}" aria-pressed="${i === sel}">${left}${wire(x.new.length)}${right}<span class="rm"><span class="k">${esc(KIND[x.kind] || x.kind)}</span><span class="n">${n ? `${n} change${n > 1 ? "s" : ""} inside` : "nothing else"}</span></span></button>`;
      }).join("");
      const title = r.old ? (r.new.length ? `${r.old.title} → ${r.new.map((s) => s.title).join(" + ")}` : r.old.title) : "Column headings, on every screen";
      const groups = [["field", "Columns"], ["button", "Buttons"], ["unmapped", "Not recognised: a person decides"]].map(([k, h]) => [h, r.changes.filter((c) => c.kind === k)]).filter(([, cs]) => cs.length);
      fig("fig-release", {
        title: `The release: ${screens.filter((x) => x.kind !== "same").length} of ${screens.length} screens renamed, moved or split`,
        body: `<div class="rel">${rows}</div><div class="clist"><h3>${esc(title)}</h3>${groups.length ? groups.map(([h, cs]) => `<div class="cgroup"><h4>${h}</h4>${movesFirst(cs).map(changeRow).join("")}</div>`).join("") : `<p class="muted">Only the name and address changed; every column and button is where it was.</p>`}</div>`,
        caption: `Pick a row for the changes inside it.`,
      });
      $("fig-release").querySelectorAll(".rrow").forEach((b) => b.addEventListener("click", () => { sel = +b.dataset.i; paint(); }));
    }
    paint();
  })();

  /* ------------------------------------------------------------ Figure: your tasks */
  (() => {
    let confirmed = false, task = (U.tasks.find((t) => t.status === "withheld") || U.tasks[0]).id;
    const statusOf = (t) => (t.status === "withheld" && confirmed ? t.fixed_status : t.status);
    const human = (id) => id.replace(/_/g, " ");
    const where = (w) => { if (!w) return ""; const p = w.split(", "), s = p.length > 1 && /page$/.test(p[p.length - 1]) ? p[p.length - 1] : ""; return `<span class="w">${icon("grid")}${esc(p[0])}${s ? " · " + esc(s) : ""}</span>`; };
    const steps = (list, against) => list.map((s, i) => {
      if (s.withheld) return `<div class="st held"><span class="no">${i + 1}</span><span>${icon("alert")} ${esc(dash(s.withheld))}</span></div>`;
      const o = against && against[i], diff = o && (o.text !== s.text || o.where !== s.where);
      return `<div class="st${diff ? " diff" : ""}"><span class="no">${i + 1}</span><span>${esc(dash(s.text))}</span>${where(s.where)}</div>`;
    }).join("");
    function paint() {
      const items = [...Object.entries(U.proposals.fields).map(([h, f]) => ({ q: "A column it does not know", from: h, to: human(f), why: "the only field to vanish from that screen" })),
        ...Object.entries(U.proposals.buttons).map(([b, a]) => ({ q: "A button it does not know", from: b, to: human(a), why: "the only button of that kind to vanish" }))];
      const placed = U.tasks.filter((t) => statusOf(t) !== "withheld").length, held = U.tasks.length - placed;
      const groups = [];
      U.tasks.forEach((t) => { let g = groups.find((x) => x.name === t.group); if (!g) groups.push(g = { name: t.group, ts: [] }); g.ts.push(t); });
      const t = TK[task], s = statusOf(t), after = t.status === "withheld" && confirmed ? t.fixed : t.after;
      const lab = s === "withheld" ? ["warn", "a step withheld"] : t.status === "withheld" ? ["ok", "placed after confirming"] : s === "unchanged" ? ["plain", "unchanged"] : ["ok", "re-worded for the new screens"];
      fig("fig-tasks", {
        title: `${U.tasks.length} staff tasks on the new screens: ${placed} placed${held ? `, ${held} withheld` : ""}`,
        body: `<div class="props">${items.map((p) => `<div class="prop${confirmed ? " ok" : ""}"><span class="q">${p.q} · ${confirmed ? "confirmed" : "probably"}</span><span class="big2">“${esc(p.from)}”<span class="ar">→</span>${esc(p.to)}</span><span class="why">${esc(p.why)}</span></div>`).join("")}`
          + `<div class="pact">${confirmed ? `<button class="btn ghost" id="undo">Undo</button><span>Confirmed: every withheld step is placed again.</span>` : `<button class="btn" id="confirm">${icon("check")} Confirm both</button><span>A person checks; nothing is assumed.</span>`}</div></div>`
          + `<div class="ttally"><span class="big">${placed} / ${U.tasks.length}</span><span class="muted">tasks placed on the new screens</span><span class="legend"><span><span style="color:var(--held)">${icon("check")}</span>re-worded for the new screens</span><span><span style="color:var(--caution)">${icon("alert")}</span>a step withheld</span></span></div>`
          + `<div class="tgrid">${groups.map((g) => `<div class="tg"><h4>${esc(g.name)}</h4><div class="tiles">${g.ts.map((x) => { const st = statusOf(x); return `<button class="tile ${st === "withheld" ? "withheld" : st === "unchanged" ? "same" : ""}" data-t="${x.id}" aria-pressed="${x.id === task}">${icon(st === "withheld" ? "alert" : "check")}<span>${esc(cap(x.label))}</span></button>`; }).join("")}</div></div>`).join("")}</div>`
          + `<div class="ba"><div><h4>${esc(cap(t.label))}: before the release</h4>${steps(t.before)}</div><div><h4>After it <span class="flag ${lab[0]}" style="margin-left:6px">${lab[1]}</span></h4>${steps(after, t.before)}</div></div>`,
        caption: `Withheld steps wait for a person to confirm the two changes. Green: re-worded.`,
      });
      ($("confirm") || $("undo")).addEventListener("click", () => { confirmed = !confirmed; paint(); });
      $("fig-tasks").querySelectorAll(".tile").forEach((b) => b.addEventListener("click", () => { task = b.dataset.t; paint(); }));
    }
    paint();
  })();

  /* ------------------------------------------------------------ Figure: the scraper on the new screens */
  (() => {
    const S = U.scraper;
    if (!S.available) { fig("fig-scraper", { title: "The scraper on the new screens", body: `<p class="muted">Run <code>python scripts/run_pipeline.py --layout v2</code> to benchmark the updated portal.</p>` }); return; }
    const pick = [...S.rows.filter((r) => r.kind === "ours"), ...S.rows.filter((r) => r.kind === "agent" && r.briefing === "policy"), ...S.rows.filter((r) => r.kind === "baseline")];
    const color = (r) => (r.kind === "ours" ? "var(--teal)" : r.kind === "baseline" ? "var(--ctrl)" : modelColor(r.name));
    const name = (r) => r.kind === "agent" ? r.name.replace(/^ai model: /, "").replace(/ \(told the policy\)$/, "") : r.kind === "ours" ? "ours (reference)" : "baseline (take all)";
    const max = Math.max(...pick.flatMap((r) => r.pages)), w = (v) => `${Math.max(1.5, 100 * v / max).toFixed(1)}%`;
    const pct = (v) => (v * 100).toFixed(0) + "%";
    fig("fig-scraper", {
      title: `The scraper on the new screens: ${M.scraper_same} of ${M.scraper_rows} results unchanged`,
      body: `<div class="tbl"><table class="bt"><thead><tr><th>Technique</th><th class="n">Score</th><th style="width:40%">Page loads, before and after</th><th class="n">Before → after</th></tr></thead><tbody>`
        + pick.map((r) => `<tr><td><span class="who"><span class="sw" style="--c:${color(r)}"></span>${esc(name(r))}</span></td><td class="n">${r.score[1].toFixed(3)} ${r.same ? `<span class="yes">${icon("check")}</span>` : ""}</td><td><div class="pbar" title="${r.pages[0]} before, ${r.pages[1]} after"><i style="width:${w(r.pages[0])};background:${color(r)}"></i><i class="v2" style="width:${w(r.pages[1])};background:${color(r)}"></i></div></td><td class="n">${r.pages[0]} → ${r.pages[1]}</td></tr>`).join("")
        + `</tbody></table></div>`
        + `<details class="more" style="margin:16px 0 0"><summary>All techniques and briefings</summary><div class="tbl"><table class="bt"><thead><tr><th>Technique</th><th class="n">Score</th><th class="n">Coverage</th><th class="n">Traps held</th><th class="n">Page loads</th><th>Same</th></tr></thead><tbody>`
        + S.rows.map((r) => `<tr><td>${esc(r.name)}</td><td class="n">${r.score[0].toFixed(3)} → ${r.score[1].toFixed(3)}</td><td class="n">${pct(r.coverage[0])} → ${pct(r.coverage[1])}</td><td class="n">${esc(r.traps[0])} → ${esc(r.traps[1])}</td><td class="n">${r.pages[0]} → ${r.pages[1]}</td><td class="${r.same ? "yes" : "no"}">${r.same ? "yes" : "no"}</td></tr>`).join("") + `</tbody></table></div></details>`,
      caption: `Only the page loads moved. Solid: before · faint: after.`,
    });
  })();
})();
