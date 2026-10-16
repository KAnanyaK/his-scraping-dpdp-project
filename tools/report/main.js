/* The masthead's key points, the colophon, and start-up. */
(() => {
  const { D, $, esc, num, f2, pct, range } = R;
  const Q = R.rules, P = R.portal;
  const dates = [D.rules && D.rules.meta.generated, D.built].filter(Boolean);
  $("mastdate").textContent = `AI models recorded ${D.rules ? D.rules.meta.generated : "–"} · built ${D.built} · synthetic data only`;

  // Key points at the headline briefing (told the policy), whatever the figures below are switched to.
  const kp = [];
  if (Q) {
    const H = "policy", o = Q.mem["compliance-aware"];
    const ms = Q.MODELS.filter((m) => m.briefs[H] && Q.mem[m.briefs[H]]).map((m) => Q.mem[m.briefs[H]]);
    if (ms.length) {
      const held = ms.reduce((x, m) => x + m.traps_resisted, 0), traps = ms.reduce((x, m) => x + m.traps, 0);
      const vs = (a, b) => `<span class="ours">${a}</span><span class="vs">vs</span>${b}`;
      kp.push([vs(`${o.traps_resisted}/${o.traps}`, `${held}/${traps}`), `trap runs held · ours vs AI models told the policy`]);
      kp.push([vs(pct(o.cost.coverage), range(ms.map((m) => m.cost.coverage), pct)), `needed fields obtained`]);
      kp.push([vs(`${o.stable_runs}/${o.repeat_runs}`, `${range(ms.map((m) => m.stable_runs), String)}/${ms[0].repeat_runs}`), `repeats giving the same answer`]);
    }
  }
  if (P) kp.push([`<span class="ours">${num(P.ours.pages)}</span><span class="vs">vs</span>${num(P.base.pages)}`, `portal page loads · ours vs baseline`]);
  $("keypoints").innerHTML = `<h2>Key points</h2>` + kp.map(([v, l]) => `<div class="kp"><div class="kv">${v}</div><div class="kl">${esc(l)}</div></div>`).join("");

  // The colophon: where every number came from.
  const info = D.rules ? (D.rules.meta.model_info || []).map((m) => `${esc(m.model)} (${esc(m.recorded)})`).join(", ") : "";
  $("colophon").innerHTML = `<h2>Methods and provenance</h2><dl>`
    + `<dt>Data</dt><dd>Synthetic records on a login-gated fixture portal, and the public Synthea sample. No real patient data.</dd>`
    + (info ? `<dt>AI models</dt><dd>${info}. Briefed with field names only; replayed from the committed recordings.</dd>` : "")
    + `<dt>Scores</dt><dd>Our executable reading of seven DPDP Act 2023 principles, not a legal opinion.</dd>`
    + `<dt>Numbers</dt><dd>Read from <code>docs/benchmark_results/</code>; each builder audits its output for patients' record numbers. <code>python tools/build_review_pages.py</code></dd>`
    + `<dt>Keys</dt><dd><kbd>→</kbd> <kbd>←</kbd> figure to figure · <kbd>Esc</kbd> stop presenting · A+ for a projector</dd>`
    + `</dl>`;
  R.start();
})();
