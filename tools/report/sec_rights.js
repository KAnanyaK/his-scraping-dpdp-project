/* Patients' rights: an access request answered from the audit log, a leaked export assessed,
   and the notices to the Board and to each patient. Masked record numbers, never a value. */
(() => {
  const { D, $, esc, human, dash, icon, fig, seg, replay } = R;
  const G = D.rights;
  if (!G) return;
  const M = G.meta, B = G.breach;
  const KC = (k) => (k === "ours" ? "var(--teal)" : "var(--ctrl)");

  /* ------------------------------------------------------------ Figure: a patient asks */
  (() => {
    let pick = G.people.findIndex((p) => !p.about && p.ours.length < p.baseline.length);
    if (pick < 0) pick = 0;
    fig("fig-access", {
      title: "A patient asks what was read about them",
      body: `<div class="ask"><div class="plist"><div class="phead"><span>Patient</span><span>Ours</span><span>Baseline</span></div><div id="plist"></div></div><div class="reply" id="reply"></div></div>`,
      caption: `Field names and categories only; record numbers masked.`,
    });
    function paint() {
      const row = (p, i, lab) => `<button class="prow" data-i="${i}" aria-pressed="${i === pick}"><span class="pid">${lab}</span><span class="pn o">${p.ours.length}</span><span class="pn">${p.baseline.length}</span></button>`;
      const groups = [];
      G.people.forEach((p, i) => { const sig = `${p.about}|${p.ours.length}|${p.baseline.length}`; const g = groups.find((x) => x.sig === sig); if (g) g.m.push(i); else groups.push({ sig, m: [i] }); });
      $("plist").innerHTML = groups.map((g) => {
        const p = G.people[g.m[0]];
        if (g.m.length === 1) return row(p, g.m[0], `${esc(p.id)}${p.about ? "<small>the patient the jobs are about</small>" : ""}`);
        const on = g.m.includes(pick), lead = on ? pick : g.m[0];
        return row(G.people[lead], lead, `${g.m.length} other patients<small>read alike; ${on ? "showing " + esc(G.people[pick].id) : "pick one below"}</small>`)
          + `<details class="pall"${on && pick !== g.m[0] ? " open" : ""}><summary>Each of the ${g.m.length}</summary>${g.m.map((i) => row(G.people[i], i, esc(G.people[i].id))).join("")}</details>`;
      }).join("");
      $("plist").querySelectorAll(".prow").forEach((b) => b.addEventListener("click", () => { pick = +b.dataset.i; paint(); }));
      const p = G.people[pick], groupsA = [];
      [...p.activities].sort((a, b) => (a.kind === b.kind ? 0 : a.kind === "ours" ? -1 : 1)).forEach((a) => {
        const sig = JSON.stringify([a.kind, Object.keys(a.categories).sort(), a.exported, a.pseudonymised]);
        const g = groupsA.find((x) => x.sig === sig);
        if (g) g.tasks.push(a.task); else groupsA.push({ ...a, sig, tasks: [a.task] });
      });
      $("reply").innerHTML = `<h3>Access request · <span class="mono">${esc(p.id)}</span></h3>`
        + `<div class="tally"><div class="o"><div class="big">${p.ours.length} <small>of ${M.tasks}</small></div><div class="lab">runs by ours read their records</div></div><div><div class="big">${p.baseline.length} <small>of ${M.tasks}</small></div><div class="lab">runs by the baseline did</div></div></div>`
        + (p.about ? `<p class="muted" style="margin:0 0 8px">Every job reads this patient: they are the one the jobs are about.</p>` : "")
        + groupsA.map((a) => `<div class="act"><span class="t"><span class="who"><span class="sw" style="--c:${KC(a.kind)}"></span>${a.tasks.length > 1 ? `${a.tasks.length} runs` : esc(human(a.task))}</span><small>${a.kind === "ours" ? "ours" : "baseline"}${a.tasks.length > 1 ? ": " + a.tasks.map(human).map(esc).join(", ") : " · for " + esc(human(a.purpose))}</small></span>`
          + `<span class="cats">${Object.entries(a.categories).map(([c, n]) => `<span class="cat ${esc(c)}" title="${n} field${n > 1 ? "s" : ""}">${esc(human(c))}</span>`).join("")}</span>`
          + `<span class="ex${a.exported ? " yes" : ""}">${a.exported ? `exported${a.pseudonymised ? ", pseudonymised" : ""}${a.erase_after ? ` · erase by ${esc(a.erase_after)}` : ""}` : "not exported"}</span></div>`).join("")
        + `<details class="more" style="margin:12px 0 0"><summary>The reply as written</summary><pre class="txt">${esc(dash(p.summary))}</pre></details>`;
    }
    paint();
  })();

  /* ------------------------------------------------------------ Figure: an export leaks */
  (() => {
    const card = (k, label) => {
      const b = B[k], high = b.severity.startsWith("high");
      return `<div class="lcard ${k === "ours" ? "o" : "b"}"><div class="lw"><span class="sw" style="--c:${KC(k)}"></span>${label}<span class="flag ${high ? "" : "warn"}">${esc(b.severity.split(" -- ")[0])}</span></div>`
        + `<div class="big">${b.patients}</div><div class="unit">patient${b.patients === 1 ? "" : "s"} exposed, of the ${M.patients} in the portal</div>`
        + `<div class="pdots" aria-hidden="true">${Array.from({ length: M.patients }, (_, i) => `<i class="${i < b.patients ? "hit" : ""}" style="--i:${i}"></i>`).join("")}</div>`
        + `<dl><dt>Identifiers</dt><dd class="${b.raw ? "no" : "yes"}">${b.raw ? "raw: names and record numbers as they are" : "keyed tokens; the key was not in the files"}</dd>`
        + `<dt>Categories</dt><dd><span class="cats">${b.categories.map((c) => `<span class="cat ${esc(c)}">${esc(human(c))}</span>`).join("")}</span></dd><dt>Severity</dt><dd>${esc(dash(b.severity))}</dd></dl></div>`;
    };
    fig("fig-breach", {
      title: "An exported summary is lost on a USB drive",
      body: `<div class="leak">${card("ours", "After ours")}${card("baseline", "After the baseline")}</div>`
        + `<div class="late">${icon("alert")}<span>${B.late.line ? `Had the drive been found 31 days later: ${esc(dash(B.late.line))}.` : "Had the drive been found 31 days later, the export would already have passed its erasure date."}</span></div>`,
      caption: `One dot per patient in the portal. The Board's report is due within 72 hours (Rule 7).`,
    });
  })();

  /* ------------------------------------------------------------ Figure: the notices */
  (() => {
    let which = "ours";
    function board(text) {
      const lines = text.split("\n"), rows = [];
      for (const l of lines.slice(1)) { const m = l.match(/^\s{2}(\S[^:]*?)\s*: (.*)$/); if (m) rows.push([m[1], m[2]]); else if (l.trim() && rows.length) rows[rows.length - 1][1] += " " + l.trim(); }
      return `<div class="to">To the Data Protection Board</div><h4>${esc(dash(lines[0]).replace(/ — to the Data Protection Board$/, ""))}</h4><dl>${rows.map(([k, v]) => `<dt>${esc(k)}</dt><dd>${esc(dash(v).replace(/_/g, " "))}</dd>`).join("")}</dl>`;
    }
    function patient(text) {
      const lines = text.split("\n");
      return `<div class="to">To each affected patient · the same letter for each, naming no one</div><h4>${esc(lines[0])}</h4>${lines.slice(1).filter((l) => l.trim()).map((l) => `<p>${esc(dash(l.trim()))}</p>`).join("")}<div class="sign">the hospital's data-protection contact</div>`;
    }
    function paint() {
      fig("fig-notices", {
        title: "The notices, drafted from the audit log",
        controls: `<div id="which"></div>`,
        body: `<div class="letters"><div class="letter">${board(B[which].board)}</div><div class="letter">${patient(B[which].patient)}</div></div>`,
      });
      seg("which", [["ours", "After ours"], ["baseline", "After the baseline"]], which, (v) => { which = v; paint(); });
    }
    paint();
  })();
})();
