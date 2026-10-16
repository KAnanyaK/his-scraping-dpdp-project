/* The Portal's kit: the data, a few DOM and SVG helpers, number formats, the tooltip. */
const PT = (() => {
  const D = JSON.parse(document.getElementById("plant-data").textContent);
  const $ = (id) => document.getElementById(id);
  const esc = (s) => String(s == null ? "" : s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const NS = "http://www.w3.org/2000/svg";
  const svg = (tag, attrs = {}, parent = null) => {
    const el = document.createElementNS(NS, tag);
    for (const [k, v] of Object.entries(attrs)) if (v !== null && v !== undefined) el.setAttribute(k, v);
    if (parent) parent.appendChild(el);
    return el;
  };
  const num = (n) => n == null ? "—" : Number(n).toLocaleString("en-IN");
  const f3 = (n) => n == null ? "—" : Number(n).toFixed(3);
  const clamp = (v, a, b) => Math.max(a, Math.min(b, v));
  const shortDate = (iso) => iso ? new Date(iso + "T00:00:00Z").toLocaleDateString("en-GB", { day: "numeric", month: "short", timeZone: "UTC" }) : "—";
  const CAT = { direct_identifier: "Identifier", quasi_identifier: "Quasi-identifier", contact: "Contact", clinical: "Clinical", financial: "Financial", administrative: "Administrative" };
  const CATS = Object.keys(CAT);
  const catOf = (layer, field) => (D.categories[layer] || {})[field] || null;
  /* A model's id as people say it: "claude-opus-5-5" -> "Opus 5.5", "gemini-3.1-flash-lite" -> "Gemini 3.1 Flash-Lite". */
  const modelName = (id) => {
    if (!id) return "";
    const m = String(id).match(/^claude-([a-z]+)-(\d+)-(\d+)$/);
    if (m) return `${m[1][0].toUpperCase()}${m[1].slice(1)} ${m[2]}.${m[3]}`;
    const g = String(id).match(/^gemini-([\d.]+)-(.+)$/);
    if (g) return `Gemini ${g[1]} ${g[2].split("-").map((w) => w[0].toUpperCase() + w.slice(1)).join("-")}`;
    return id;
  };
  const still = () => document.documentElement.classList.contains("still") || matchMedia("(prefers-reduced-motion: reduce)").matches;
  const tip = $("tip");
  function tipOn(e, text) { if (!text) return; tip.textContent = text; tip.hidden = false; const r = tip.getBoundingClientRect(); tip.style.left = clamp(e.clientX + 12, 4, innerWidth - r.width - 4) + "px"; tip.style.top = clamp(e.clientY + 14, 4, innerHeight - r.height - 4) + "px"; }
  function tipOff() { tip.hidden = true; }
  return { D, $, esc, svg, num, f3, shortDate, CAT, CATS, catOf, still, tipOn, tipOff, modelName };
})();
