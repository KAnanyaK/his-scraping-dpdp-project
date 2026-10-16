/* The staff assistant, live. The engine below mirrors agent/session.py line for line and is
   checked on load against every recorded Python conversation; typing switches off on a mismatch. */
(() => {
  const { D, $, esc, cap, dash, icon, fig } = R;
  const A = D.assistant;
  if (!A) return;
  const F = Object.fromEntries(A.functions.map((f) => [f.id, f]));
  const RO = Object.fromEntries(A.roles.map((r) => [r.id, r]));

  /* ------------------------------------------------------------ the engine (mirrors agent/session.py) */
  const STOP = new Set(A.stopwords);
  const SPEC = Object.fromEntries(Object.entries(A.tokens).map(([k, v]) => [k, new Set(v)]));
  const words = (t) => t.toLowerCase().match(/[a-z0-9]+/g) || [];
  const norm = (t) => words(t).join(" ");
  const stem = (w) => {
    if (w.length > 5 && w.endsWith("ing")) return w.slice(0, -3);
    if (w.length > 4 && w.endsWith("ed")) return w.slice(0, -2);
    if (w.length > 4 && w.endsWith("ies")) return w.slice(0, -3) + "y";
    if (w.length > 3 && w.endsWith("s") && !w.endsWith("ss")) return w.slice(0, -1);
    return w;
  };
  const near = (a, b) => {
    if (a === b) return true;
    if (Math.min(a.length, b.length) < 5 || Math.abs(a.length - b.length) > 1) return false;
    if (a.length === b.length) { let d = 0; for (let i = 0; i < a.length; i++) if (a[i] !== b[i]) d++; return d === 1; }
    const [s, l] = a.length < b.length ? [a, b] : [b, a];
    let i = 0;
    while (i < s.length && s[i] === l[i]) i++;
    return s.slice(i) === l.slice(i + 1);
  };
  const tokens = (t) => new Set(words(t).filter((w) => !STOP.has(w)).map(stem));
  function recognise(text) {
    const req = [...tokens(text)];
    if (!req.length) return [];
    const said = ` ${norm(text)} `;
    const scored = A.order.map((id) => [req.filter((w) => SPEC[id].has(w) || [...SPEC[id]].some((s) => near(w, s))).length
      + A.phraseWeight * A.phrases[id].filter((p) => said.includes(` ${p} `)).length, id]);
    const best = Math.max(...scored.map((s) => s[0]));
    if (best === 0) return [];
    return scored.filter((s) => s[0] === best).map((s) => s[1]);
  }
  const fits = (slot, answer) => slot.pattern === null || new RegExp(`^(?:${slot.pattern})$`, "i").test(answer.trim());
  function foundIn(slot, text) {
    if (slot.find === null) return null;
    const m = text.match(new RegExp(slot.find, "i"));
    return m ? m[0] : null;
  }
  function renderGuidance(role, id, inputs) {
    const f = F[id], p = A.purposes[f.purpose];
    const lines = [`How to ${f.label} -- for ${role}`, ""];
    if (f.withheld) lines.push(A.texts.withheldHead, "");
    f.steps.forEach((s, i) => {
      lines.push(`  ${i + 1}. ${s.text.replace(/\{(\w+)\}/g, (m, k) => (k in inputs ? inputs[k] : m))}`);
      lines.push(`     [${s.layer} / ${s.artefact}${s.where ? " / " + s.where : ""}]`);
      if (s.caution) lines.push(`     note: ${s.caution}`);
    });
    lines.push("", `  purpose      : ${f.purpose} (${p.note})`, `  data touched : ${f.touched}`,
      `  retain       : no longer than ${p.days} days for this purpose`);
    if (A.screensAsOf) lines.push(`  screens      : as found on ${A.screensAsOf}`);
    return lines.join("\n");
  }
  class Session {
    constructor(role) { this.role = role; this.reset(); }
    reset() { this.state = "idle"; this.options = []; this.spec = null; this.inputs = {}; this.request = ""; }
    respond(text) {
      text = text.trim();
      const cmd = norm(text);
      if (A.commands.help.includes(cmd)) return this.help();
      if (A.commands.changes.includes(cmd)) return { kind: "changes", fn: null, text: RO[this.role].changes };
      if (A.commands.cancel.includes(cmd)) {
        if (this.state === "idle") return { kind: "cancelled", fn: null, text: A.texts.nothing };
        this.reset();
        return { kind: "cancelled", fn: null, text: A.texts.cancelled };
      }
      if (this.state === "choosing") return this.choose(text);
      if (this.state === "collecting") return this.collect(text);
      return this.start(text);
    }
    start(text) {
      let m = recognise(text);
      if (!m.length) return { kind: "unrecognised", fn: null, text: RO[this.role].unrecognised };
      this.request = text;
      if (m.length > 1) {
        const mine = m.filter((id) => RO[this.role].gate[id].allowed);
        if (mine.length === 1) return this.begin(mine[0]);
        m = mine.length ? mine : m;
        this.options = m; this.state = "choosing";
        return { kind: "ask_choose", fn: null, text: ["I can help with a few things that sound like that -- which one?", ...m.map((id, i) => `  ${i + 1}. ${F[id].label}`)].join("\n") };
      }
      return this.begin(m[0]);
    }
    chooseAgain() {
      return { kind: "ask_choose", fn: null, text: ["Sorry -- pick one by number:", ...this.options.map((id, i) => `  ${i + 1}. ${F[id].label}`)].join("\n") };
    }
    choose(text) {
      let chosen = null;
      if (/^[0-9]+$/.test(text) && +text >= 1 && +text <= this.options.length) chosen = this.options[+text - 1];
      else {
        const low = text.toLowerCase();
        chosen = this.options.find((id) => low === id || low === F[id].label.toLowerCase()) || null;
        if (!chosen) { const n = recognise(text).filter((id) => this.options.includes(id)); if (n.length === 1) chosen = n[0]; }
      }
      if (!chosen) return this.chooseAgain();
      this.options = [];
      return this.begin(chosen);
    }
    begin(id) {
      const gate = RO[this.role].gate[id];
      if (!gate.allowed) { this.reset(); return { kind: "declined", fn: id, text: RO[this.role].decline[id] }; }
      this.spec = id; this.inputs = {};
      for (const s of F[id].inputs) { const v = foundIn(s, this.request); if (v !== null && fits(s, v)) this.inputs[s.name] = v; }
      const taken = Object.entries(this.inputs);
      if (taken.length === F[id].inputs.length) return this.finish();
      this.state = "collecting";
      let pre = `Sure -- to ${F[id].label} I need a couple of details.`;
      if (taken.length) pre += "\n(From your message: " + taken.map(([k, v]) => `${k} ${v}`).join(", ") + ".)";
      return this.askNext(pre);
    }
    pending() { return F[this.spec].inputs.find((s) => !(s.name in this.inputs)); }
    collect(text) {
      const slot = this.pending();
      if (!text) return { kind: "ask_input", fn: this.spec, text: `${slot.prompt} (e.g. ${slot.example})` };
      if (!fits(slot, text)) return { kind: "ask_input", fn: this.spec, text: `${A.texts.misfit}\n${slot.prompt} (e.g. ${slot.example})` };
      this.inputs[slot.name] = text;
      if (Object.keys(this.inputs).length === F[this.spec].inputs.length) return this.finish();
      return this.askNext();
    }
    askNext(preface) {
      const slot = this.pending();
      const t = `${slot.prompt} (e.g. ${slot.example})`;
      return { kind: "ask_input", fn: this.spec, text: preface ? `${preface}\n${t}` : t };
    }
    help() {
      if (this.state === "collecting") {
        const slot = this.pending();
        return { kind: "ask_input", fn: this.spec, text: `(Say "cancel" to stop.) To ${F[this.spec].label} I still need this:\n${slot.prompt} (e.g. ${slot.example})` };
      }
      if (this.state === "choosing") return this.chooseAgain();
      return { kind: "help", fn: null, text: RO[this.role].help };
    }
    finish() {
      const id = this.spec, text = renderGuidance(this.role, id, this.inputs);
      this.reset();
      return { kind: "guidance", fn: id, text };
    }
  }

  /* ------------------------------------------------------------ self-check against the Python transcripts */
  let mismatch = null;
  for (const v of A.vectors) {
    const s = new Session(v.role);
    for (let i = 0; i < v.turns.length && !mismatch; i++) {
      const got = s.respond(v.turns[i]), want = v.replies[i];
      if (got.text !== want.text || got.kind !== want.kind) mismatch = { v, i, got, want };
    }
    if (mismatch) break;
  }
  const LIVE = !mismatch;
  if (mismatch) console.warn("assistant self-check mismatch", mismatch);
  document.body.dataset.assistant = LIVE ? "live" : "replay";

  /* ------------------------------------------------------------ the figure */
  fig("fig-assistant", {
    title: "Ask it as reception, a nurse or an administrator",
    body: `<div class="roles" id="aroles" role="group" aria-label="Working as"></div>`
      + `<div class="amain"><div class="tasks" id="atasks" aria-label="Common tasks"></div>`
      + `<section class="chat" aria-label="Conversation"><div class="bar"><span class="cw">Conversation<small id="awho"></small></span><span class="acts"><button type="button" class="btn ghost" id="aplay">${icon("play")} Watch a demo</button><button type="button" class="btn ghost" id="areset">${icon("replay")} Start over</button></span></div>`
      + `<div class="clog" id="alog" aria-live="polite"></div>`
      + `<form class="compose" id="acompose" autocomplete="off"><label class="sr-only" for="ainput">What do you need to do?</label><input id="ainput" placeholder="Type what you need to do"><button type="submit" class="btn" id="asend">Send ${icon("arrow")}</button></form>`
      + `<div class="hint">Enter to send · <b>help</b> lists your tasks · <b>cancel</b> stops</div></section></div>`
      + `<details class="more tech"><summary>How each answer is checked</summary><p class="selftest">${LIVE ? `<span class="yes">${icon("check")}</span> Identical to the Python assistant on all ${A.vectors.length} recorded conversations, checked when this page opened.` : `<span class="no">${icon("x")}</span> Typing is off: this copy differs from the Python assistant.`} </p>`
      + `<h4 style="margin:14px 0 6px">What each role may see</h4><div class="tbl"><table class="bt" id="ascope"></table></div>`
      + `<h4 style="margin:18px 0 6px">Who may be walked through what <span class="muted" style="font-weight:400">· click a cell to play it</span></h4><div class="tbl"><table class="bt mx" id="amatrix"></table></div></details>`,
    caption: `Rules, not a language model: it cannot invent a step.`,
  });

  /* ------------------------------------------------------------ state and replies */
  let role = "reception", session = new Session(role), history = [], busy = false, epoch = 0;
  const wait = (ms) => new Promise((r) => setTimeout(r, ms));
  const mine = (r) => A.functions.filter((f) => RO[r].gate[f.id].allowed);
  function replayed(turns) {
    const v = A.vectors.concat(A.scenes).find((c) => c.role === role && turns.every((t, i) => c.turns[i] === t));
    return v ? v.replies[turns.length - 1] : { kind: "unrecognised", fn: null, text: "(Typing is off on this copy: choose a task from the list.)" };
  }
  function respond(text) {
    history.push(text);
    const r = LIVE ? session.respond(text) : replayed(history);
    if (LIVE && r.kind === "ask_input" && session.state === "collecting") return { ...r, progress: [Object.keys(session.inputs).length + 1, F[session.spec].inputs.length] };
    return r;
  }
  function howHTML(id, label) {
    const f = F[id], g = RO[role].gate[id], p = A.purposes[f.purpose];
    let stopped = false;
    const checks = g.checks.map((c) => {
      const st = stopped ? "skip" : (c.ok ? "ok" : "no");
      if (!c.ok) stopped = true;
      return `<div class="check"><span class="mark ${st}">${st === "ok" ? icon("check") : st === "no" ? icon("x") : "·"}</span><div><div><span class="rid">${esc(c.rule)}</span>${esc(cap(c.name))}</div><div class="cd">${esc(c.detail)}${st === "skip" ? " · not reached" : ""}</div></div></div>`;
    }).join("");
    const pages = [...new Set(f.steps.map((s) => s.page).filter(Boolean))];
    const facts = [["Purpose", esc(`${f.purpose.replace(/_/g, " ")}: ${dash(p.note)}`)], ["Data touched", esc(f.touched.replace(/_/g, " "))], ["Records", esc(f.artefacts.join(" · "))], ...(pages.length ? [["Screens", pages.map((u) => `<code>${esc(u)}</code>`).join(" ")]] : [])];
    return `<details class="how"><summary>${icon("chev")}${esc(label)}</summary><div class="inner">${checks}<dl class="hfacts">${facts.map(([k, v]) => `<dt>${k}</dt><dd>${v}</dd>`).join("")}</dl></div></details>`;
  }
  const loc = (w) => { if (!w) return ""; const p = w.split(", "), s = p.length > 1 && /page$/.test(p[p.length - 1]) ? p[p.length - 1] : ""; return `<div class="loc">${icon("grid")}<span>${esc(p[0])}${s ? " · " + esc(s) : ""}</span></div>`; };
  function guidanceHTML(r) {
    const lines = r.text.split("\n"), f = F[r.fn] || { steps: [], label: "", purpose: "" };
    let i = 2, n = 0, h = "";
    const withheld = lines[2] === A.texts.withheldHead;
    if (withheld) i = 4;
    while (i < lines.length && lines[i] !== "") {
      const m = lines[i].match(/^  (\d+)\. (.*)$/);
      if (m) {
        const st = f.steps[n] || {};
        let note = "";
        if (/^\s+\[(.*)\]$/.test(lines[i + 1] || "")) i++;
        const c = (lines[i + 1] || "").match(/^\s+note: (.*)$/);
        if (c) { note = `<div class="warnline">${icon("flag")}<span>${esc(dash(c[1]))}</span></div>`; i++; }
        h += `<li><span class="no">${m[1]}</span><div><div>${esc(dash(m[2]))}</div>${loc(st.where)}${note}</div></li>`;
        n++;
      }
      i++;
    }
    const p = A.purposes[f.purpose] || {};
    return `<div class="ans"><div class="ah"><span class="ai">${icon("check")}</span><div><div class="at">${esc(cap(f.label))}</div><div class="as">Steps for ${esc(cap(role))}</div></div></div>`
      + (withheld ? `<div class="withheld">${icon("alert")}<span>${esc(dash(A.texts.withheldHead.trim()))}</span></div>` : "")
      + `<ol class="gsteps">${h}</ol><div class="afoot"><span class="okline">${icon("shield")} Part of your work as ${esc(role)}: ${esc(p.plain || "")}.</span><div class="row2"><span>Keep these details no longer than ${p.days} days.</span>${A.screensAsOf ? `<span>Screens as found on ${esc(A.screensAsOf)}</span>` : ""}</div></div>`
      + howHTML(r.fn, "How this was checked") + `</div>`;
  }
  function declinedHTML(r) {
    const lines = r.text.split("\n"), f = F[r.fn], at = lines.findIndex((l) => /^\s+\[/.test(l));
    return `<div class="ans no"><div class="ah"><span class="ai">${icon("ban")}</span><div><div class="at">${esc(cap(f.label))}</div><div class="as">Not part of ${esc(role)}'s work</div></div></div>`
      + `<div class="body"><p style="margin:0">${esc(dash(lines[0]))}</p>${lines.slice(at + 1).map((l) => l.trim()).filter(Boolean).map((l) => `<div class="handoff">${icon("arrow")}<span>${esc(dash(l))}</span></div>`).join("")}<div class="nothing">No patient details were asked for.</div></div>`
      + howHTML(r.fn, "Why not") + `</div>`;
  }
  function listHTML(r) {
    let h = "", opts = [];
    const flush = () => { if (opts.length) { h += `<div class="choices">${opts.join("")}</div>`; opts = []; } };
    for (const l of r.text.split("\n")) {
      const m = l.match(/^\s+(?:(\d+)\.|-) (.*)$/);
      if (m) { opts.push(`<button class="opt opt-say" data-say="${esc(m[1] || m[2])}">${esc(cap(m[2]))}</button>`); continue; }
      flush();
      const g = l.match(/^\s+(.*):$/);
      if (g) h += `<div class="grp">${esc(g[1])}</div>`;
      else if (l.trim()) h += `<p class="${/^Say "cancel"/.test(l) ? "soft" : ""}">${esc(dash(l))}</p>`;
    }
    flush();
    return h;
  }
  function askHTML(r) {
    const lines = r.text.split("\n"), last = lines.pop(), ex = last.match(/^(.*) \(e\.g\. (.*)\)$/);
    return lines.map((l) => l === A.texts.misfit ? `<p class="misfit">${icon("alert")}<span>${esc(l)}</span></p>` : `<p class="soft">${esc(dash(l))}</p>`).join("")
      + `<p class="askline">${esc(ex ? ex[1] : last)}</p><div class="qrow">${r.progress ? `<span class="prog2">Detail ${r.progress[0]} of ${r.progress[1]}</span>` : ""}${ex ? `<button class="opt opt-say" data-say="${esc(ex[2])}">Use example: <b>${esc(ex[2])}</b></button>` : ""}</div>`;
  }
  function botHTML(r) {
    if (r.kind === "guidance") return guidanceHTML(r);
    if (r.kind === "declined") return declinedHTML(r);
    if (r.kind === "ask_choose" || r.kind === "unrecognised" || r.kind === "help") return listHTML(r);
    if (r.kind === "ask_input") return askHTML(r);
    if (r.kind === "changes") { const lines = r.text.split("\n"), items = lines.slice(1).filter((l) => l.trim()); return `<p>${esc(dash(lines[0]))}</p>${items.length ? `<ul class="bul">${items.map((l) => `<li>${esc(dash(l.replace(/^\s+- /, "").trim()))}</li>`).join("")}</ul>` : ""}`; }
    return `<p>${esc(dash(r.text))}</p>`;
  }
  function add(kind, html) {
    const div = document.createElement("div");
    div.className = `msg ${kind}`;
    div.innerHTML = `<span class="sr-only">${kind === "you" ? "You said:" : "Assistant:"}</span>${html}`;
    $("alog").appendChild(div);
    div.querySelectorAll(".opt-say, [data-example]").forEach((b) => b.addEventListener("click", () => { if (!busy) say(b.dataset.say || b.dataset.example); }));
    const log = $("alog");
    log.scrollTop = kind === "bot" && div.offsetHeight > log.clientHeight * 0.6 ? div.offsetTop - 12 : log.scrollHeight;
    return div;
  }
  function say(text) {
    const was = busy;
    busy = true;
    add("you", esc(text || "(nothing)"));
    const r = respond(text);
    add("bot", botHTML(r));
    if (r.fn) $("atasks").querySelectorAll(".task").forEach((b) => b.setAttribute("aria-current", String(b.dataset.f === r.fn)));
    busy = was;
  }
  function welcome() {
    const ex = mine(role).slice(0, 3).map((f) => f.synonyms[0] || f.label), groups = [];
    A.functions.forEach((f) => { if (!RO[role].gate[f.id].allowed && !groups.includes(f.group)) groups.push(f.group); });
    const whole = groups.filter((g) => A.functions.filter((f) => f.group === g).every((f) => !RO[role].gate[f.id].allowed));
    add("bot", `<p>What do you need to do? Describe it in your own words, or choose a task from the list.</p><p class="soft">You'll get the steps for ${esc(role)}, or be told who can do it instead.</p>`
      + `<div class="examples">${ex.map((e) => `<button class="opt" data-example="${esc(e)}">${esc(cap(e))}</button>`).join("")}</div>`
      + (whole.length ? `<p class="soft" style="margin-top:8px">Not part of ${esc(role)}'s work: ${whole.map((g) => esc(g.toLowerCase())).join(", ")}. Ask anyway and I'll say who can.</p>` : ""));
  }
  function setRole(r) {
    epoch++; role = r; session = new Session(role); history = [];
    $("alog").innerHTML = "";
    $("awho").textContent = `as ${cap(role)}`;
    $("aroles").innerHTML = A.roles.map((x) => `<button class="role" aria-pressed="${x.id === role}" data-r="${x.id}"><span class="rn">${esc(cap(x.id))}</span><span class="rc">${mine(x.id).length} tasks</span><span class="rt">${esc(x.title)}</span></button>`).join("");
    $("aroles").querySelectorAll(".role").forEach((b) => b.addEventListener("click", () => { if (!busy && b.dataset.r !== role) setRole(b.dataset.r); }));
    const gs = [];
    mine(role).forEach((f) => { let g = gs.find((x) => x.name === f.group); if (!g) gs.push(g = { name: f.group, fns: [] }); g.fns.push(f); });
    $("atasks").innerHTML = gs.map((g) => `<h4>${esc(g.name)}</h4><ul>${g.fns.map((f) => `<li><button class="task" data-f="${f.id}"><span>${esc(cap(f.label))}</span>${icon("arrow")}</button></li>`).join("")}</ul>`).join("");
    $("atasks").querySelectorAll(".task").forEach((b) => b.addEventListener("click", () => { if (busy) return; session.reset(); history = []; say(F[b.dataset.f].label); }));
    welcome();
  }
  async function type(text) { const box = $("ainput"); box.value = ""; for (const ch of text) { box.value += ch; await wait(22); } await wait(250); box.value = ""; }
  async function autoplay(turns) {
    const me = epoch;
    busy = true; lock(true);
    for (const t of turns) { if (me !== epoch) break; await type(t); busy = false; say(t); busy = true; await wait(700); }
    busy = false; lock(false);
  }
  function lock(on) { ["ainput", "asend", "aplay", "areset"].forEach((id) => { $(id).disabled = on || (!LIVE && (id === "ainput" || id === "asend")); }); document.body.classList.toggle("busy", on); }
  $("aplay").addEventListener("click", async () => { if (busy) return; for (const s of A.scenes) { setRole(s.role); await autoplay(s.turns); await wait(1400); } });
  $("acompose").addEventListener("submit", (e) => { e.preventDefault(); if (busy || !LIVE) return; const t = $("ainput").value; $("ainput").value = ""; say(t); });
  $("areset").addEventListener("click", () => { if (!busy) setRole(role); });
  if (!LIVE) { const n = document.createElement("div"); n.className = "offline"; n.textContent = "Typing is off on this copy. Choose a task from the list to see a recorded answer."; $("alog").before(n); }

  $("ascope").innerHTML = `<thead><tr><th>Role</th><th>Purposes</th><th>May see</th></tr></thead><tbody>`
    + A.roles.map((r) => `<tr><td>${esc(cap(r.id))}</td><td class="muted">${esc(r.purposes.map((p) => p.replace(/_/g, " ")).join(", "))}</td><td><span class="cats">${r.may_touch.map((c) => `<span class="cat ${esc(c)}">${esc(c.replace(/_/g, " "))}</span>`).join("")}</span></td></tr>`).join("") + `</tbody>`;
  $("amatrix").innerHTML = `<thead><tr><th>Task</th><th>Purpose</th>${A.roles.map((r) => `<th>${esc(cap(r.id))}</th>`).join("")}</tr></thead><tbody>`
    + A.functions.map((f) => `<tr><td>${esc(cap(f.label))}</td><td class="muted">${esc(f.purpose.replace(/_/g, " "))}</td>${A.roles.map((r) => { const g = r.gate[f.id]; return `<td><button class="cell ${g.allowed ? "ok" : "no"}" data-r="${r.id}" data-f="${f.id}" title="${esc(g.reason)}" aria-label="${esc(cap(r.id))}: ${esc(f.label)}: ${g.allowed ? "allowed" : "declined, " + esc(g.rule)}">${g.allowed ? icon("check") : esc(g.rule)}</button></td>`; }).join("")}</tr>`).join("") + `</tbody>`;
  $("amatrix").querySelectorAll(".cell").forEach((b) => b.addEventListener("click", () => {
    if (busy) return;
    const f = F[b.dataset.f];
    setRole(b.dataset.r);
    $("fig-assistant").scrollIntoView({ behavior: R.still ? "auto" : "smooth", block: "start" });
    autoplay([f.label, ...(RO[b.dataset.r].gate[f.id].allowed ? f.inputs.map((i) => i.example) : [])]);
  }));
  setRole(role); lock(false);
})();
