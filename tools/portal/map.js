/* The map: three lines through seven stations, Hospital to Erased, straight and parallel. What sets
   them apart is their stopping pattern: between Acquire and Extract a line calls at one square per
   page load it made, and its train moves on only as its squares fill -- ours runs the express, the
   baseline the all-stations service. A line with no erase date does not stop at Erased: it runs on
   off the map. Each station lights its readings as a line's train reaches it. Every number is the
   recorded one: the extraction stations count all four jobs of the portal run, the export stations
   the patient-summary job. The drawing is laid out once in map units (1030 x 648 at 1366 x 768) and
   scaled to its box, so a larger screen gets a larger map, not a sparser one. */
PT.map = (() => {
  const { D, $, svg, num, f3, CAT, CATS, catOf } = PT;
  const root = $("map");
  const T = Object.fromEntries(D.techniques.map((t) => [t.id, t]));
  const STATIONS = [
    { id: "hospital", name: "Hospital", sub: `${D.patient.of} patients`, tip: "The hospital's system, as the portal serves it" },
    { id: "gate", name: "Gate", sub: "may it read?" },
    { id: "acquire", name: "Acquire", sub: D.modules ? `${D.modules} modules found` : "pages loaded", tip: `Found by the fields on their pages, never named in advance, in ${D.discover} page loads` },
    { id: "extract", name: "Extract", sub: "fields taken" },
    { id: "score", name: "Score", sub: "7 DPDP rules" },
    { id: "export", name: "Export", sub: "the identifier" },
    { id: "erased", name: "Erased", sub: "kept until" },
  ];
  const SPANS = [.125, .13, .26, .145, .17, .17];          // each station's share of the run
  const ZONES = [["Intake", "z1"], ["Extraction · all four jobs", "z2"], ["Export · the patient-summary job", "z3"]];
  const REF = [1030, 648];
  const PITCH = 5.5, SQ = 4.4;                                // one page load's square
  const PAGE_T = 0.02, RUN = 230;                           // seconds per page load; map units per second elsewhere
  const NAMES = { A: "Ours", C: "Baseline" }, SUBS = { A: "the reference", C: "takes everything" };
  let G = null;

  const text = (attrs, s, parent) => { const t = svg("text", attrs, parent); t.textContent = s; return t; };
  const tip = (el, s) => { el.addEventListener("mousemove", (e) => PT.tipOn(e, s)); el.addEventListener("mouseleave", PT.tipOff); };
  const briefWords = (b) => ({ unaided: "task + register", informed: "told the Act", policy: "told the policy" }[b] || "");
  const width = (el, fallback) => { try { return el.getComputedTextLength(); } catch (e) { return fallback; } };

  /* ------------------------------------------------------------ geometry, in map units */
  function layout() {
    const w = root.clientWidth || REF[0], h = root.clientHeight || REF[1];
    const s = Math.max(0.6, Math.min(1.8, Math.min(w / REF[0], h / REF[1])));
    const W = w / s, H = h / s;
    const x = [190];
    const end = W - 140;
    SPANS.forEach((f) => x.push(x[x.length - 1] + f * (end - 190)));
    const top = 122, gap = Math.max(112, Math.min(170, (H - top - 205) / 2));
    return { W, H, s, x, y: [top, top + gap, top + 2 * gap] };
  }

  /* ------------------------------------------------------------ what each line carries */
  function lineData(slot, id) {
    const t = T[id], L = D.ledger[id] || {}, ex = D.export[id] || null;
    const seen = new Map();
    for (const j of D.tasks) for (const [layer, fs] of Object.entries((L[j.id] || {}).fields || {})) for (const f of fs) {
      const key = `${layer}/${f}`;
      if (!seen.has(key)) seen.set(key, catOf(layer, f) || "administrative");
    }
    const passengers = [...seen.values()].sort((a, b) => CATS.indexOf(a) - CATS.indexOf(b));
    const failed = D.rule_ids.filter((r) => t && t.rules[r] != null && t.rules[r] < 1);
    const [held, runs] = (t && t.trap_runs) || [];
    return { slot, id, t, pages: t ? t.traced : 0, passengers, fields: seen.size, coverage: t ? t.coverage : null,
             score: t ? t.score : null, failed, trap: runs ? { held, runs } : null, ex, ends: !!(ex && ex.retention) };
  }

  /* ------------------------------------------------------------ the drawing */
  function build(lines, intro) {
    const g = layout(), X = g.x;
    root.setAttribute("viewBox", `0 0 ${g.W.toFixed(1)} ${g.H.toFixed(1)}`);
    root.innerHTML = "";
    root.classList.toggle("intro", !!intro && !PT.still());
    const defs = svg("defs", {}, root);
    // a fine dot grid under everything, like the printed card of a map; a light streak for moving trains
    const dots = svg("pattern", { id: "dots", width: 14, height: 14, patternUnits: "userSpaceOnUse" }, defs);
    svg("circle", { cx: 7, cy: 7, r: 0.75, class: "dot" }, dots);
    const streak = svg("linearGradient", { id: "streak", x1: 0, x2: 1, y1: 0, y2: 0 }, defs);
    svg("stop", { offset: 0, "stop-color": "#fff", "stop-opacity": 0 }, streak);
    svg("stop", { offset: 1, "stop-color": "#fff", "stop-opacity": 0.8 }, streak);
    const back = svg("g", {}, root), linesG = svg("g", {}, root), stnG = svg("g", {}, root), readG = svg("g", {}, root), trainG = svg("g", {}, root);

    // fare zones: a tint, a band along the top, the zone's number and name
    const edge = [X[0] - 46, (X[1] + X[2]) / 2, (X[4] + X[5]) / 2, g.W];
    ZONES.forEach(([name, z], k) => {
      const w = edge[k + 1] - edge[k];
      svg("rect", { x: edge[k], y: 0, width: w, height: g.H, class: `zone ${z}` }, back);
      svg("rect", { x: edge[k], y: 0, width: w, height: 4, class: `zfill ${z}` }, back);
      svg("rect", { x: edge[k] + 14, y: 17, width: 20, height: 20, rx: 4, class: `zfill ${z}` }, back);
      text({ x: edge[k] + 24, y: 31.5, "text-anchor": "middle", class: "zn" }, String(k + 1), back);
      text({ x: edge[k] + 42, y: 32, class: `zl ${z}` }, name, back);
    });
    svg("rect", { x: edge[0], y: 4, width: g.W - edge[0], height: g.H - 4, fill: "url(#dots)" }, back);

    // stations: a name, what it stands for, a dotted guide down through the lines
    const here = STATIONS.map((s, k) => {
      const mark = svg("rect", { x: X[k], y: 52, width: 0, height: 23, rx: 4, class: "here" }, back);
      const nm = text({ x: X[k], y: 68, "text-anchor": "middle", class: "sname" }, s.name, back);
      const w = width(nm, 60) + 14;
      mark.setAttribute("x", (X[k] - w / 2).toFixed(1)); mark.setAttribute("width", w.toFixed(1));
      return mark;
    });
    STATIONS.forEach((s, k) => {
      const sub = text({ x: X[k], y: 86, "text-anchor": "middle", class: "ssub" }, s.sub, back);
      if (s.tip) tip(sub, s.tip);
      svg("path", { d: `M${X[k]} 98V${g.y[2]}`, class: "guide" }, back);
    });

    // the lines: from each line's roundel to Erased; a line with no erase date runs on, fading off the map
    const L = lines.map((ln, i) => {
      const y = g.y[i], cls = ln.slot.toLowerCase();
      svg("path", { d: `M46 ${y}H${X[6]}`, class: "casing" }, linesG);
      const path = svg("path", { d: `M46 ${y}H${X[6]}`, class: `line ${cls}` }, linesG);
      path.style.setProperty("--len", (X[6] - 46).toFixed(0));
      path.style.animationDelay = `${i * 90}ms`;
      if (!ln.ends) {
        const grad = svg("linearGradient", { id: `run-${cls}`, gradientUnits: "userSpaceOnUse", x1: X[6], y1: 0, x2: g.W - 4, y2: 0 }, defs);
        svg("stop", { offset: 0, "stop-color": `var(--${cls})` }, grad);
        svg("stop", { offset: 1, "stop-color": `var(--${cls})`, "stop-opacity": 0 }, grad);
        svg("path", { d: `M${X[6]} ${y}H${g.W}`, class: "line run", stroke: `url(#run-${cls})` }, linesG);
        svg("path", { d: `M${X[6] + 4} ${y}H${g.W}`, class: "flow" }, linesG);      // what is never erased keeps flowing on
      }
      return { ...ln, y, cls, path, read: [], bottom: y };
    });

    // station discs; a line that runs on does not stop at Erased
    const discs = X.map((xx, k) => L.map((ln, i) => {
      if (k === 6 && !ln.ends) return null;
      const c = svg("circle", { cx: xx, cy: ln.y, r: 7.5, class: "stn" }, stnG);
      c.style.animationDelay = `${300 + k * 70 + i * 30}ms`;
      return c;
    }));
    const pulseG = svg("g", {}, stnG);

    // each line's roundel, its name above the line and what it is below
    L.forEach((ln) => {
      svg("circle", { cx: 30, cy: ln.y, r: 16, class: `roundel ${ln.cls}` }, stnG);
      text({ x: 30, y: ln.y + 5.5, "text-anchor": "middle", class: `rk ${ln.cls}` }, ln.slot, stnG);
      text({ x: 56, y: ln.y - 17, class: "lname" }, ln.slot === "B" ? PT.modelName(ln.t ? ln.t.model : "") : NAMES[ln.slot], back);
      text({ x: 56, y: ln.y + 31, class: "lsub" }, ln.slot === "B" ? briefWords(ln.t && ln.t.briefing) : SUBS[ln.slot], back);
    });

    // readings, per line, per station; hidden until that line's train arrives
    L.forEach((ln) => {
      const y = ln.y, c = ln.cls;
      const keep = (b) => { ln.bottom = Math.max(ln.bottom, b); };

      // Acquire to Extract: the stopping pattern, one square per page load, and the count
      const pl = svg("g", { class: "reading" }, readG);
      const gx = X[2] + 15, cols = Math.max(8, Math.floor((X[3] - X[2] - 30) / PITCH));
      ln.plN = text({ x: gx - 1.5, y: y + 41, class: `pln ${c}` }, num(ln.pages), pl);
      const nw = width(ln.plN, 48);
      ln.plN.textContent = "0";
      text({ x: gx + nw + 6, y: y + 41, class: "plu" }, "page loads", pl);
      ln.sq = [];
      for (let k = 0; k < ln.pages; k++) ln.sq.push(svg("rect", { x: gx + (k % cols) * PITCH, y: y + 52 + Math.floor(k / cols) * PITCH, width: SQ, height: SQ, rx: 0.8, class: `sq ${c}` }, pl));
      const gridB = y + 52 + Math.ceil(ln.pages / cols) * PITCH;
      tip(svg("rect", { x: gx - 4, y: y + 18, width: cols * PITCH + 8, height: gridB - y - 14, fill: "transparent" }, pl), `${num(ln.pages)} page loads across the four jobs: one square each`);
      keep(gridB);
      ln.pl = pl; ln.shown = -1;

      // Extract: the passengers who boarded, one dot per field, in its data category's colour
      const ex = svg("g", { class: "reading" }, readG);
      const px0 = X[3] + 17, pp = 8.5, pcols = Math.max(5, Math.floor((X[4] - X[3] - 30) / pp));
      ln.passengers.forEach((cat, k) => {
        const dot = svg("circle", { cx: px0 + (k % pcols) * pp, cy: y + 26 + Math.floor(k / pcols) * pp, r: 3.3, class: "pax", fill: `var(--c-${cat})` }, ex);
        dot.style.transitionDelay = `${k * 18}ms`;
      });
      const rowsY = y + 26 + (Math.ceil(ln.passengers.length / pcols) - 1) * pp;
      text({ x: px0 - 3.5, y: rowsY + 25, class: "rd" }, `${ln.fields} fields`, ex);
      if (ln.coverage != null) text({ x: px0 - 3.5, y: rowsY + 42, class: "rd2" }, `${Math.round(ln.coverage * 100)}% needed`, ex);
      tip(svg("rect", { x: px0 - 6, y: y + 18, width: pcols * pp + 6, height: rowsY - y, fill: "transparent" }, ex),
          CATS.filter((cat) => ln.passengers.includes(cat)).map((cat) => `${CAT[cat]} ${ln.passengers.filter((x) => x === cat).length}`).join(" · "));
      keep(rowsY + 46);

      // Score: the score, seven rule lamps (lit when held, red when broken), a sign if a rule broke or the trap was taken
      const sc = svg("g", { class: "reading" }, readG);
      text({ x: X[4] + 14, y: y + 41, class: `scv ${c}` }, f3(ln.score), sc);
      D.rule_ids.forEach((r, k) => {
        const bad = ln.failed.includes(r);
        const lamp = svg("circle", { cx: X[4] + 19 + k * 12, cy: y + 57, r: 4.6, class: `lamp ${bad ? "fail" : "held"}` }, sc);
        lamp.style.transitionDelay = `${120 + k * 75}ms`;
        if (bad) lamp.style.animationDelay = `${120 + k * 75}ms`;
        tip(lamp, `${r} ${D.rule_titles[r] || ""}: ${bad ? "broken" : "held"}`);
      });
      const trapT = (D.tasks.find((j) => j.trap) || {}).trap || "";
      if (ln.trap && ln.trap.held < ln.trap.runs) sign(sc, X[4] + 14, y + 82, "Trap taken", `Taken in ${ln.trap.runs - ln.trap.held} of ${ln.trap.runs} run${ln.trap.runs > 1 ? "s" : ""}: ${trapT}`);
      else if (ln.failed.length) sign(sc, X[4] + 14, y + 82, `${ln.failed.length} rule${ln.failed.length > 1 ? "s" : ""} broken`, ln.failed.map((r) => `${r} ${D.rule_titles[r] || ""}`).join(" · "));
      keep(y + 92);

      // Export: the identifier that leaves -- a token, the raw record number, or none
      const xp = svg("g", { class: "reading" }, readG);
      const e = ln.ex;
      const tok = e && (e.pid.match(/PSN-[0-9a-f]+/) || [""])[0];
      const kind = !e ? "none" : e.leaked > 0 ? "raw" : tok ? "tok" : "none";
      const label = kind === "raw" ? D.patient.mrn : kind === "tok" ? tok.slice(0, 10) + "…" : "no id";
      svg("rect", { x: X[5] + 14, y: y + 22, width: 96, height: 24, rx: 12, class: `chip ${kind}` }, xp);
      ln.chipT = text({ x: X[5] + 62, y: y + 38.5, "text-anchor": "middle", class: `chipt ${kind}` }, label, xp);
      ln.chip = { kind, label };
      if (e && e.leaked > 0) sign(xp, X[5] + 14, y + 82, `${e.leaked} raw ids`, `${e.leaked} of ${e.identifiers} raw identifiers appear in the export`);

      // Erased: a terminus with its date, or no stop at all
      const er = svg("g", { class: "reading" }, readG);
      if (ln.ends) {
        svg("rect", { x: X[6] + 26, y: y - 12, width: 108, height: 24, rx: 12, class: "term" }, er);
        text({ x: X[6] + 80, y: y + 4.5, "text-anchor": "middle", class: "termt" }, `Erased ${PT.shortDate(e.erase_after)}`, er);
      } else {
        svg("rect", { x: X[6] + 14, y: y + 22, width: 116, height: 24, rx: 12, class: "nodate" }, er);
        text({ x: X[6] + 72, y: y + 38.5, "text-anchor": "middle", class: "termt" }, "No erase date", er);
      }
      ln.read = [null, null, null, ex, sc, xp, er];
    });

    // the gate's checks, in the intake zone under the last line
    const gate = svg("g", { class: "reading" }, readG), gy = g.y[2] + 60, gx0 = edge[0] + 14;
    text({ x: gx0, y: gy, class: "bh" }, "At the gate", gate);
    const gateRows = [["TLS observed", D.meta.tls ? "TLS was observed on the browser's session" : ""], ["robots.txt read", "robots.txt says Disallow: /; the hospital's authorisation lets it in"],
                      ["Authorised", `Authorisation reference ${D.meta.authorisation || ""}, logged with every run`], ["Signed in", `Service account ${D.meta.account}: a username and a password, nothing else`]];
    const ticks = gateRows.map(([r, t], k) => {
      const yy = gy + 22 + k * 19;
      const tk = svg("path", { d: `M${gx0 + 1} ${yy - 5}l3.6 3.6 6.4-7.4`, class: "tick", opacity: 0 }, gate);
      const tt = text({ x: gx0 + 19, y: yy, class: "bt" }, r, gate);
      if (t) tip(tt, t);
      return tk;
    });

    // the key: one strip along the foot of the map, wrapping if the map is narrow
    keyStrip(svg("g", {}, readG), g);

    // trains: a pill per line carrying its letter
    L.forEach((ln) => {
      ln.trail = svg("rect", { x: 0, y: ln.y - 3.5, width: 0, height: 7, rx: 3.5, fill: "url(#streak)", class: "trail" }, trainG);
      const tr = svg("g", { class: "train" }, trainG);
      svg("rect", { x: -19, y: -12, width: 38, height: 24, rx: 12, class: `tr ${ln.cls}` }, tr);
      text({ x: 0, y: 5, "text-anchor": "middle", class: `tl ${ln.cls}` }, ln.slot, tr);
      ln.train = tr;
    });

    G = { g, L, discs, gate, ticks, here, pulseG };
    L.forEach((ln) => { ln.lit = X.map(() => false); ln.xpOn = false; });
    if (root.classList.contains("intro")) setTimeout(() => root.classList.remove("intro"), 1600);
    return G;
  }
  function keyStrip(key, g) {
    const items = [];
    const item = (draw) => { const it = svg("g", {}, key); draw(it); items.push(it); };
    item((it) => text({ x: 0, y: 0, class: "bh" }, "Key", it));
    item((it) => {
      [0, 1, 2].forEach((c) => [0, 1].forEach((r) => svg("rect", { x: c * PITCH, y: -9 + r * PITCH, width: SQ, height: SQ, rx: 0.8, fill: "var(--ink)" }, it)));
      text({ x: 3 * PITCH + 7, y: 0, class: "bt" }, "one page load each", it);
    });
    CATS.forEach((cat) => item((it) => {
      svg("circle", { cx: 4.6, cy: -4.5, r: 4.6, fill: `var(--c-${cat})` }, it);
      text({ x: 14, y: 0, class: "bt" }, CAT[cat], it);
    }));
    item((it) => {
      svg("circle", { cx: 4.6, cy: -4.5, r: 4.6, class: "lamp held" }, it);
      svg("circle", { cx: 16.6, cy: -4.5, r: 4.6, class: "lamp fail" }, it);
      text({ x: 27, y: 0, class: "bt" }, "rule held, broken", it);
    });
    const gapX = 18, maxX = g.W - 16;
    const rows = [[]];
    let x = 16;
    items.forEach((it, k) => {
      let w = 0;
      try { w = it.getBBox().width; } catch (e) { w = 90; }
      if (x + w > maxX && rows[rows.length - 1].length) { rows.push([]); x = 16; }
      rows[rows.length - 1].push([it, x]);
      x += w + (k === 0 ? 12 : gapX);
    });
    rows.forEach((row, r) => row.forEach(([it, xx]) => it.setAttribute("transform", `translate(${xx.toFixed(1)} ${(g.H - 20 - (rows.length - 1 - r) * 22).toFixed(1)})`)));
    svg("path", { d: `M0 ${(g.H - 42 - (rows.length - 1) * 22).toFixed(1)}H${g.W}`, class: "keyrule" }, key);
  }
  function sign(parent, x, y, label, tipText) {
    const hit = svg("rect", { x, y: y - 10, width: 130, height: 20, fill: "transparent" }, parent);
    if (tipText) tip(hit, tipText);
    svg("circle", { cx: x + 8, cy: y, r: 8.5, class: "sign" }, parent);
    svg("rect", { x: x + 3.2, y: y - 1.7, width: 9.6, height: 3.4, rx: 1, class: "signbar" }, parent);
    text({ x: x + 22, y: y + 4.5, class: "signt" }, label, parent);
  }

  /* ------------------------------------------------------------ the state at a moment
     step: the station the trains are heading for (0..6); p: seconds into that step. Between Acquire
     and Extract a train's time is its page loads; elsewhere every train runs at the same speed. */
  const dest = (ln, k) => (k === 6 && !ln.ends) ? G.g.W + 40 : G.g.x[k];
  function leg(ln, k) {
    if (k <= 0) return 0;
    if (k === 3) return Math.max(0.25, ln.pages * PAGE_T);
    return (dest(ln, k) - G.g.x[k - 1]) / RUN;
  }
  function duration(k) { return k <= 0 || !G ? 0 : Math.max(...G.L.map((ln) => leg(ln, k))) + (k === 1 ? 1.1 : 0.15); }

  /* An arrival: a ring in the line's colour opens out from the station. */
  function pulse(x, y, cls) {
    const c = svg("circle", { cx: x, cy: y, r: 8, class: `pulse ${cls}` }, G.pulseG);
    c.addEventListener("animationend", () => c.remove());
  }
  /* Pseudonymisation, made visible: the record number scrambles into its token. */
  function scramble(el, from, to) {
    const HEX = "0123456789abcdef", n = Math.max(from.length, to.length), t0 = performance.now(), dur = 620;
    const tick = (now) => {
      const f = Math.min(1, (now - t0) / dur), fixed = Math.floor(f * n);
      let s = "";
      for (let k = 0; k < n; k++) s += k < fixed ? (to[k] || "") : (k < to.length ? HEX[(Math.random() * 16) | 0] : "");
      el.textContent = f < 1 ? s : to;
      if (f < 1) requestAnimationFrame(tick);
    };
    requestAnimationFrame(tick);
  }

  function draw(step, p, live) {
    if (!G) return;
    const X = G.g.x;
    G.L.forEach((ln, li) => {
      const f = step <= 0 ? 1 : Math.min(1, p / (leg(ln, step) || 1));
      const x = step <= 0 ? X[0] : X[step - 1] + f * (dest(ln, step) - X[step - 1]);
      ln.train.setAttribute("transform", `translate(${x.toFixed(1)} ${ln.y})`);
      // a light streak behind a moving train, longer the faster it goes
      const moving = live && step > 0 && f < 1;
      const from = step > 0 ? X[step - 1] : X[0], len = moving ? Math.min(step === 3 ? 34 : 70, Math.max(0, x - from - 19)) : 0;
      ln.trail.setAttribute("x", (x - 19 - len).toFixed(1));
      ln.trail.setAttribute("width", len.toFixed(1));
      // the squares fill as the train calls
      const n = step < 3 ? 0 : step > 3 ? ln.pages : Math.round(ln.pages * f);
      if (n !== ln.shown) {
        const [a, b] = ln.shown < 0 ? [0, ln.sq.length] : [Math.min(n, ln.shown), Math.max(n, ln.shown)];
        for (let k = a; k < b; k++) ln.sq[k].classList.toggle("on", k < n);
        ln.shown = n;
        ln.plN.textContent = num(n);
      }
      ln.pl.classList.toggle("on", step >= 3);
      const reached = (k) => step >= k && x >= X[k] - 0.5;
      ln.read.forEach((gr, k) => { if (gr) gr.classList.toggle("on", reached(k)); });
      G.discs.forEach((col, k) => {
        const on = step > 0 && reached(k);
        if (col[li]) col[li].classList.toggle("lit", on);
        if (on && !ln.lit[k] && live && !PT.still() && col[li]) pulse(X[k], ln.y, ln.cls);
        ln.lit[k] = on;
      });
      // at Export, a token is shown being made from the record number
      const xpOn = reached(5);
      if (ln.chip && ln.chip.kind === "tok") {
        if (xpOn && !ln.xpOn && live && !PT.still()) scramble(ln.chipT, D.patient.mrn, ln.chip.label);
        else if (!xpOn) ln.chipT.textContent = ln.chip.label;
      }
      ln.xpOn = xpOn;
    });
    G.here.forEach((m, k) => m.classList.toggle("on", k === step));
    const atGate = step > 1 || (step === 1 && p >= leg(G.L[0], 1));
    G.gate.classList.toggle("on", atGate);
    const tickT = step > 1 ? 99 : p - leg(G.L[0], 1);
    G.ticks.forEach((t, k) => t.setAttribute("opacity", step >= 1 && tickT >= k * 0.22 ? 1 : 0));
  }

  function flash(slot) {
    if (!G || PT.still()) return;
    const ln = G.L.find((l) => l.slot === slot);
    if (!ln) return;
    for (const el of [ln.path, ln.train, ln.pl, ...ln.read.filter(Boolean)]) { el.classList.remove("flash"); void el.getBBox(); el.classList.add("flash"); }
  }

  return { build, draw, duration, lineData, flash, STATIONS, get G() { return G; } };
})();
