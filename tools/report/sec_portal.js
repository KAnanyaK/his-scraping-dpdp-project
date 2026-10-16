/* The setting: a real browser signs in to the fixture portal, finds its modules, and each
   technique's jobs are run through it, every page load captured and checked against the meter. */
(() => {
  const { D, $, esc, num, f2, f3, pct, human, icon, kindColor, wait, fig, replay, seg } = R;
  const P = D.portal;
  if (!P) return;
  const M = P.meta, T = Object.fromEntries(P.techniques.map((t) => [t.name, t]));
  const ours = P.techniques.find((t) => t.kind === "ours"), base = P.techniques.find((t) => t.kind === "baseline");
  const LAYER = { patient_administration: "Patient administration", clinical_ehr: "Clinical / EHR", ancillary_departmental: "Ancillary / departmental", administrative_financial: "Administrative / financial", infrastructure_integration: "Infrastructure / audit" };
  const LCOL = { patient_administration: "var(--l0)", clinical_ehr: "var(--l1)", ancillary_departmental: "var(--l2)", administrative_financial: "var(--l3)", infrastructure_integration: "var(--l4)" };
  const shortName = (n) => T[n] && T[n].kind === "ours" ? "ours (reference)" : T[n] && T[n].kind === "baseline" ? "baseline (take all)" : n.replace(/^ai model: /, "");
  R.portal = { ours, base, M, modules: P.modules };

  /* ------------------------------------------------------------ Figure: the sign-in */
  const disc = P.visits.filter((v) => v.who === "discover");
  const label = (v) => v.kind === "login" ? "/login" : v.kind === "login-submit" ? "/login" : v.kind === "home" ? "/" : v.kind === "list" ? `/m/${v.module}/${v.n > 1 ? "?page=" + v.n : ""}` : v.kind === "detail" ? `/m/${v.module}/record/${v.n}` : v.kind === "search" ? `/m/${v.module}/?q=${v.q}` : (v.path || v.kind);
  fig("fig-signin", {
    title: "Sign-in: a username and a password, nothing else",
    controls: `<button class="btn ghost" id="replay1">${icon("replay")} Replay</button>`,
    body: `<div class="stage"><div class="browser"><div class="chrome"><span class="dots3"><i></i><i></i><i></i></span><span class="addr" id="addr"></span></div><div class="view" id="view"></div><div class="status"><div class="sbar"><i id="sfill"></i></div><span id="discnote"></span></div></div>`
      + `<dl class="facts">`
      + `<div><dt>${icon("lock")} Transport</dt><dd>${M.tls ? esc(M.transport_note || "TLS, observed by the browser") : "not encrypted"}</dd></div>`
      + `<div><dt>${icon("grid")} The portal serves</dt><dd>${P.modules.length} modules · ${num(M.records)} records each · ${M.page_size} a page</dd></div>`
      + `<div><dt>${icon("ban")} No API, no hooks</dt><dd>HTML tables, Next links, a search box</dd></div>`
      + `<div><dt>${icon("file")} robots.txt</dt><dd><span class="mono robots">${esc(M.robots).split("\n").join(" · ")}</span>${M.authorisation ? `<div class="robots">entered under the hospital's authorisation ${esc(M.authorisation)}, logged with every run</div>` : ""}</dd></div>`
      + `</dl></div>`,
  });
  const note = (i) => { $("discnote").textContent = i ? `page load ${i} of ${disc.length}` : `${disc.length} page loads to sign in and look around`; $("sfill").style.transform = `scaleX(${i / disc.length})`; };
  let run1 = 0;
  const lock = () => `<span class="lock">${M.tls ? icon("lock") : ""}</span>`;
  async function signIn() {
    const me = ++run1, alive = () => me === run1;
    note(0);
    $("addr").innerHTML = `${lock()}https://127.0.0.1/login`;
    $("view").innerHTML = `<div class="login"><div class="t">Hospital portal</div><div class="f" id="u"></div><div class="f" id="p"></div><div class="b" id="b">Sign in</div></div>`;
    await wait(500);
    const put = async (id, text) => { $(id).classList.add("on", "caret"); for (const ch of text) { if (!alive()) return; $(id).textContent += ch; await wait(70); } $(id).classList.remove("on", "caret"); };
    await put("u", M.account); if (!alive()) return;
    await put("p", "••••••••"); if (!alive()) return;
    $("b").classList.add("press"); await wait(160); $("b").classList.remove("press");
    for (let i = 0; i < disc.length; i++) {
      if (!alive()) return;
      const l = label(disc[i]);
      $("addr").innerHTML = `${lock()}https://127.0.0.1${esc(l)}`;
      if (i === 2) $("view").innerHTML = `<div style="text-align:center"><div style="font-size:1.8rem;color:var(--held)">${icon("shield")}</div><div style="font-weight:600;margin-top:6px">Signed in as ${esc(M.account)}</div><div class="muted">reading the home page</div></div>`;
      if (i > 2) $("view").innerHTML = `<div style="text-align:center"><div class="mono" style="font-size:1rem;font-weight:600">${esc(l)}</div><div class="muted" style="margin-top:6px">${disc[i].kind === "detail" ? "a record page: which fields live here?" : "a list page: which columns?"}</div></div>`;
      note(i + 1);
      await wait(i < 3 ? 420 : 260);
    }
    if (!alive()) return;
    $("discnote").textContent = `${disc.length} page loads · nothing named in advance`;
    $("view").innerHTML = `<div class="found"><div class="fh2">${P.modules.length} modules found</div>`
      + P.modules.map((m, i) => `<div class="frow" style="animation-delay:${i * 70}ms"><span class="sw" style="--c:${LCOL[m.layer] || "var(--ink-3)"}"></span><span class="ft2">${esc(m.title)}</span><span class="fl">${esc(LAYER[m.layer] || "not inferred")}</span></div>`).join("") + `</div>`;
  }
  $("replay1").addEventListener("click", signIn);
  let started = false;
  new IntersectionObserver((es, io) => { if (!started && es.some((e) => e.isIntersecting)) { started = true; io.disconnect(); signIn(); } }, { threshold: 0.4 }).observe($("fig-signin"));

  /* ------------------------------------------------------------ Figure: discovery as a flow diagram */
  (() => {
    let hide = true;
    function paint() {
      const mods = P.modules.map((m) => {
        const fields = Object.entries(m.evidence).map(([f, layers]) => `<span class="fld${layers.length === 1 ? " unique" : ""}${m.detail_only.includes(f) ? " detail" : ""}" title="${esc(f)}: on ${layers.map((l) => LAYER[l]).join(", ")}">${esc(f)}</span>`).join("");
        return `<div class="mod" style="--c:${LCOL[m.layer] || "var(--ink-3)"}"><div><div class="mt">${esc(m.title)}</div><div class="ml"><span class="sw"></span>${esc(LAYER[m.layer] || "not inferred")}${hide ? "" : ` · <span class="mono">${esc(m.path)}</span>`}</div></div><div class="fields">${fields}</div><div class="mc">${Math.round(m.confidence * 100)}%<small>${m.pages} pages · ${m.records} records</small></div></div>`;
      }).join("");
      const login = disc.filter((v) => v.kind === "login" || v.kind === "login-submit").length;
      R.fig("fig-modules", {
        title: "Each module's layer, read from its fields",
        controls: `<div id="urlseg"></div>`,
        body: `<div class="flow"><div class="flow-in"><div class="fbox"><div class="fb-h">${login}</div><div class="fb-l">page loads to sign in</div></div><div class="fbox"><div class="fb-h">${disc.length}</div><div class="fb-l">page loads in all</div></div><div class="fbox"><div class="fb-h">${P.modules.length}</div><div class="fb-l">modules found, none named</div></div></div>`
          + `<div class="arrow-v" aria-hidden="true"><svg viewBox="0 0 42 100" preserveAspectRatio="none"><path d="M4 50H36M30 44l6 6-6 6" fill="none" stroke="currentColor" stroke-width="1.5" vector-effect="non-scaling-stroke"/></svg></div>`
          + `<div class="mods">${mods}</div></div>`,
        caption: `Tinted: decides the layer · plain: on several layers · dashed: record page only.`,
      });
      R.seg("urlseg", [["hide", "Addresses hidden"], ["show", "shown"]], hide ? "hide" : "show", (v) => { hide = v === "hide"; paint(); });
    }
    paint();
  })();

  /* ------------------------------------------------------------ Figure: the crawl */
  (() => {
    const agents = P.techniques.filter((t) => t.kind === "agent");
    const headAgent = P.headline.find((n) => T[n] && T[n].kind === "agent") || (agents[0] && agents[0].name);
    let speed = 12, timer = null, played = false, agent = headAgent, task = "";
    R.fig("fig-crawl", {
      title: "Every page each technique loaded",
      controls: `<button class="btn" id="play">${icon("play")} Play</button><select id="ctask" aria-label="Job"><option value="">all four jobs</option>${P.tasks.map((t) => `<option value="${esc(t.id)}">${esc(human(t.id))}${t.single ? " · one patient" : ""}${t.trap ? " (trap)" : ""}</option>`).join("")}</select><select id="cagent" aria-label="AI model">${agents.map((a) => `<option value="${esc(a.name)}"${a.name === headAgent ? " selected" : ""}>${esc(shortName(a.name))}</option>`).join("")}</select><div id="speedseg"></div>`,
      body: `<div class="keys" style="margin-bottom:14px"><span><b style="border-radius:1px 1px 5px 5px"></b>list page</span><span><b style="border-radius:50%"></b>search</span><span><b></b>record page</span><span>darker: loaded more often</span></div><div class="lanes" id="lanes"></div>`,
      caption: `<span id="harness"></span>`,
    });
    R.seg("speedseg", [["30", "slow"], ["12", "normal"], ["3", "fast"]], "12", (v) => { speed = Number(v); });
    const lanes = () => [ours.name, agent, base.name].filter((n) => n && T[n]);
    const LANE = { ours: "Ours (reference)", baseline: "Baseline (take all)" };
    const sqId = (li, v) => `q-${li}-${v.module}-${v.kind}-${v.kind === "search" ? 0 : v.n}`;
    function paintLanes() {
      $("lanes").innerHTML = lanes().map((name, li) => {
        const t = T[name];
        const rows = P.modules.map((m) => `<div class="srow"><span class="sl" title="${esc(m.path)}">${esc(m.slug)}</span><div class="sq">${Array.from({ length: m.pages || 1 }, (_, i) => `<b class="lst" id="q-${li}-${m.slug}-list-${i + 1}"></b>`).join("")}<b class="srch" id="q-${li}-${m.slug}-search-0"></b><b class="sep"></b>${Array.from({ length: m.records || 0 }, (_, i) => `<b id="q-${li}-${m.slug}-detail-${i}"></b>`).join("")}</div></div>`).join("");
        const total = P.visits.filter((v) => v.who === name && (!task || v.task === task)).length;
        return `<div class="lane" style="--c:${kindColor(t.kind, name)}"><div class="ln"><span class="sw"></span>${esc(LANE[t.kind] || shortName(name))}</div><div class="count tnum" id="c-${li}">0</div><div class="cl">of ${num(total)} page loads${t.kind === "agent" && t.repeats > 1 ? ` · the first of its ${t.repeats} samples` : ""}</div><div class="prog"><i id="p-${li}"></i></div><div class="site">${rows}</div><div class="done" id="d-${li}"></div></div>`;
      }).join("");
      const h = P.visits.filter((v) => v.who === "harness").length;
      $("harness").innerHTML = `One square per page of the portal. + ${h} harness loads, outside the meter.`;
    }
    function stop() { if (timer) { clearInterval(timer); timer = null; } $("play").disabled = false; }
    function play() {
      stop(); paintLanes(); played = true;
      const names = lanes(), qs = names.map((n) => P.visits.filter((v) => v.who === n && (!task || v.task === task)));
      const heat = {}, counts = names.map(() => 0);
      let tick = 0;
      $("play").disabled = true; $("play").innerHTML = `${icon("play")} Playing`;
      const step = speed <= 3 ? 4 : 1;
      timer = setInterval(() => {
        let live = false;
        for (let s = 0; s < step; s++) {
          names.forEach((_, li) => {
            const q = qs[li], v = q[tick];
            if (!v) return;
            live = true; counts[li]++;
            $("c-" + li).textContent = num(counts[li]);
            $("p-" + li).style.width = (100 * counts[li] / q.length) + "%";
            $("lanes").children[li].querySelectorAll("b.now").forEach((b) => b.classList.remove("now"));
            if (["list", "detail", "search"].includes(v.kind)) {
              const el = document.getElementById(sqId(li, v));
              if (el) { heat[el.id] = (heat[el.id] || 0) + 1; el.classList.remove("h1", "h2", "h3"); el.classList.add(heat[el.id] >= 6 ? "h3" : heat[el.id] >= 2 ? "h2" : "h1", "now"); }
            }
            if (tick + 1 === q.length) {
              const t = T[names[li]];
              $("lanes").children[li].querySelectorAll("b.now").forEach((b) => b.classList.remove("now"));
              $("d-" + li).innerHTML = `${icon("check")} <b>${num(counts[li])}</b> loads${t.record_excess ? ` · <b>${t.record_excess >= 10 ? num(Math.round(t.record_excess)) : f2(t.record_excess)}×</b> the patient's own records read` : ""}`;
            }
          });
          tick++;
        }
        if (!live) { stop(); $("play").innerHTML = `${icon("replay")} Again`; }
      }, speed);
    }
    $("play").addEventListener("click", play);
    $("ctask").addEventListener("change", (e) => { task = e.target.value; stop(); $("play").innerHTML = `${icon("play")} Play`; paintLanes(); });
    $("cagent").addEventListener("change", (e) => { agent = e.target.value; stop(); $("play").innerHTML = `${icon("play")} Play`; paintLanes(); });
    paintLanes();
    // It plays itself once, the first time it comes into view.
    new IntersectionObserver((es, io) => { if (!played && es.some((e) => e.isIntersecting)) { io.disconnect(); if (!R.still) setTimeout(play, 300); } }, { threshold: 0.35 }).observe($("fig-crawl"));
  })();

  /* ------------------------------------------------------------ Table: the portal run */
  (() => {
    const rows = [...P.headline.map((n) => T[n]).filter(Boolean), ...P.techniques.filter((t) => !P.headline.includes(t.name))];
    const head = new Set(P.headline);
    const tr = (t) => `<tr><td><span class="who"><span class="sw" style="--c:${kindColor(t.kind, t.name)}"></span>${esc(shortName(t.name))}</span></td><td class="n">${f3(t.score)}</td><td class="n">${num(t.pages)}</td><td class="n">${pct(t.coverage)}</td><td class="n">${f2(t.excess)}</td><td class="n">${f2(t.record_excess)}</td><td class="n">${esc(t.traps)}</td></tr>`;
    R.fig("tab-portal", {
      title: "The portal run, every technique",
      body: `<div class="tbl"><table class="bt"><thead><tr><th>Technique</th><th class="n">Score</th><th class="n">Page loads</th><th class="n">Expert fields</th><th class="n">Fields ÷ needed</th><th class="n">× own records</th><th class="n">Traps held</th></tr></thead><tbody>`
        + rows.filter((t) => head.has(t.name)).map(tr).join("")
        + `<tr class="grp"><td colspan="7">The other briefings</td></tr>` + rows.filter((t) => !head.has(t.name)).map(tr).join("")
        + `</tbody></table></div>`,
      caption: `Four jobs, through the portal. × own records: records read per record of the patient the job is about.`,
    });
  })();
})();
