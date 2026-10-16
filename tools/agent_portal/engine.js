/* The HIS Staff Assistant's engine, in the page. It mirrors agent/session.py line for line (the same
   recogniser, the same gate before any detail is asked, the same slots and shape checks, the same
   wording), and it does not ask to be trusted: on open it replays every recorded Python conversation
   and compares each reply character for character. On any difference typing is switched off and
   only the recorded conversations play. Rule-based: there is no model in it. */
const Engine = (() => {
  "use strict";
  const D = JSON.parse(document.getElementById("agent-data").textContent);
  const F = Object.fromEntries(D.functions.map((f) => [f.id, f]));
  const R = Object.fromEntries(D.roles.map((r) => [r.id, r]));

  const STOP = new Set(D.stopwords);
  const SPEC = Object.fromEntries(Object.entries(D.tokens).map(([k, v]) => [k, new Set(v)]));
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
    const scored = D.order.map((id) => [req.filter((w) => SPEC[id].has(w) || [...SPEC[id]].some((s) => near(w, s))).length
      + D.phraseWeight * D.phrases[id].filter((p) => said.includes(` ${p} `)).length, id]);
    const best = Math.max(...scored.map((s) => s[0]));
    if (best === 0) return [];
    return scored.filter((s) => s[0] === best).map((s) => s[1]);
  }
  // Which of the words typed the task was recognised by (for the route's first sign; not part of the decision).
  function matched(text, id) {
    const hits = new Set();
    for (const w of words(text)) {
      if (STOP.has(w)) continue;
      const s = stem(w);
      if (SPEC[id].has(s) || [...SPEC[id]].some((t) => near(s, t))) hits.add(w);
    }
    const said = ` ${norm(text)} `;
    const phrases = D.phrases[id].filter((p) => said.includes(` ${p} `));
    return { words: [...hits], phrases };
  }
  const fits = (slot, answer) => slot.pattern === null || new RegExp(`^(?:${slot.pattern})$`, "i").test(answer.trim());
  function foundIn(slot, text) {
    if (slot.find === null) return null;
    const m = text.match(new RegExp(slot.find, "i"));
    return m ? m[0] : null;
  }
  function renderGuidance(role, id, inputs) {
    const f = F[id], p = D.purposes[f.purpose];
    const lines = [`How to ${f.label} -- for ${role}`, ""];
    if (f.withheld) lines.push(D.texts.withheldHead, "");
    f.steps.forEach((s, i) => {
      lines.push(`  ${i + 1}. ${s.text.replace(/\{(\w+)\}/g, (m, k) => (k in inputs ? inputs[k] : m))}`);
      lines.push(`     [${s.layer} / ${s.artefact}${s.where ? " / " + s.where : ""}]`);
      if (s.caution) lines.push(`     note: ${s.caution}`);
    });
    lines.push("", `  purpose      : ${f.purpose} (${p.note})`, `  data touched : ${f.touched}`,
      `  retain       : no longer than ${p.days} days for this purpose`);
    if (D.screensAsOf) lines.push(`  screens      : as found on ${D.screensAsOf}`);
    return lines.join("\n");
  }
  class Session {
    constructor(role) { this.role = role; this.reset(); }
    reset() { this.state = "idle"; this.options = []; this.spec = null; this.inputs = {}; this.request = ""; this.prefilled = []; this.misfits = {}; }
    respond(text) {
      text = text.trim();
      const cmd = norm(text);
      if (D.commands.help.includes(cmd)) return this.help();
      if (D.commands.changes.includes(cmd)) return { kind: "changes", fn: null, text: R[this.role].changes };
      if (D.commands.cancel.includes(cmd)) {
        if (this.state === "idle") return { kind: "cancelled", fn: null, text: D.texts.nothing };
        this.reset();
        return { kind: "cancelled", fn: null, text: D.texts.cancelled };
      }
      if (this.state === "choosing") return this.choose(text);
      if (this.state === "collecting") return this.collect(text);
      return this.start(text);
    }
    start(text) {
      let m = recognise(text);
      if (!m.length) return { kind: "unrecognised", fn: null, text: R[this.role].unrecognised };
      this.request = text;
      if (m.length > 1) {
        const mine = m.filter((id) => R[this.role].gate[id].allowed);
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
      const gate = R[this.role].gate[id];
      if (!gate.allowed) { this.reset(); return { kind: "declined", fn: id, text: R[this.role].decline[id] }; }
      this.spec = id; this.inputs = {}; this.prefilled = []; this.misfits = {};
      for (const s of F[id].inputs) { const v = foundIn(s, this.request); if (v !== null && fits(s, v)) { this.inputs[s.name] = v; this.prefilled.push(s.name); } }
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
      if (!fits(slot, text)) { this.misfits[slot.name] = (this.misfits[slot.name] || 0) + 1; return { kind: "ask_input", fn: this.spec, text: `${D.texts.misfit}\n${slot.prompt} (e.g. ${slot.example})` }; }
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
      return { kind: "help", fn: null, text: R[this.role].help };
    }
    finish() {
      const id = this.spec, text = renderGuidance(this.role, id, this.inputs);
      // What the finished request was given, kept for the route (never part of a reply).
      this.last = { fn: id, inputs: { ...this.inputs }, prefilled: [...this.prefilled], misfits: { ...this.misfits } };
      this.reset();
      return { kind: "guidance", fn: id, text };
    }
  }

  /* ---------------------------------------------------- the self-check against the Python transcripts */
  let mismatch = null;
  for (const v of D.vectors) {
    const s = new Session(v.role);
    for (let i = 0; i < v.turns.length && !mismatch; i++) {
      const got = s.respond(v.turns[i]), want = v.replies[i];
      if (got.text !== want.text || got.kind !== want.kind) mismatch = { v, i, got, want };
    }
    if (mismatch) break;
  }
  if (mismatch) console.warn("HIS Staff Assistant: the page's engine differs from the Python assistant", mismatch);

  return { D, F, R, Session, recognise, matched, live: !mismatch, checked: D.vectors.length };
})();
