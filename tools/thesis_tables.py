"""Write the thesis's tables and plot data from the tracked artefacts.

    python tools/thesis_tables.py            # rewrite docs/thesis/generated/*.tex
    python tools/thesis_tables.py --check    # exit 1 if any generated file differs

The thesis (``docs/thesis/``) is LaTeX; its result tables and the data behind
its plots are not typed in. Each is one ``.tex`` file under
``docs/thesis/generated/``, written here from ``docs/benchmark_results/*.json``
or from the code itself (the policy, the catalogue, the role gate), the same
way ``tools/report_tables.py`` keeps the Markdown report honest. Run it after
the benchmarks; CI runs ``--check``.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "src"), str(ROOT), str(ROOT / "scripts")]

from compliance.benchmark import BenchmarkResult   # noqa: E402
from compliance.stats import wilson                # noqa: E402

RESULTS = ROOT / "docs" / "benchmark_results"
OUT = ROOT / "docs" / "thesis" / "generated"

BRIEFING = {"policy": "told the policy", "informed": "told the Act", "unaided": "task + register"}
MODEL = {
    "claude-sonnet-5-5": "Claude Sonnet 5.5",
    "claude-opus-5-5": "Claude Opus 5.5",
    "claude-haiku-4-5": "Claude Haiku 4.5",
    "gemini-3.1-flash-lite": "Gemini 3.1 Flash-Lite",
}
MODEL_ORDER = ["claude-opus-5-5", "claude-sonnet-5-5", "claude-haiku-4-5", "gemini-3.1-flash-lite"]
CATEGORY = {"direct_identifier": "direct identifier", "quasi_identifier": "quasi-identifier"}


# --------------------------------------------------------------------------- #
# helpers
# --------------------------------------------------------------------------- #

def tex(s: str) -> str:
    """Escape text for LaTeX, with typographic quotes and no dashes."""

    s = re.sub(r"\s+\u2014\s+", ": ", str(s))
    s = re.sub(r'"([^"]*)"', "\u201c\\1\u201d", s)
    out = []
    for ch in s:
        out.append({"&": r"\&", "%": r"\%", "$": r"\$", "#": r"\#", "_": r"\_", "{": r"\{", "}": r"\}",
                    "~": r"\textasciitilde{}", "^": r"\textasciicircum{}", "\\": r"\textbackslash{}",
                    "×": r"$\times$", "÷": r"$\div$", "≤": r"$\le$", "∩": r"$\cap$", "→": r"$\rightarrow$",
                    "—": ":", "–": " to ", "\u201c": "``", "\u201d": "''"}.get(ch, ch))
    return "".join(out)


def code(s: str) -> str:
    return r"\texttt{" + tex(s) + "}"


def load(name: str) -> BenchmarkResult:
    return BenchmarkResult.model_validate(json.loads((RESULTS / f"{name}.json").read_text(encoding="utf-8")))


def name_of(s, *, short: bool = False) -> str:
    if s.short == "compliance-aware":
        return r"\textbf{Proposed (reference)}"
    if s.short == "unconstrained":
        return "Baseline (unconstrained)"
    m = MODEL.get(s.model, s.model)
    return m if short else f"{m}, {BRIEFING[s.briefing]}"


def f2(v) -> str:
    return "n/a" if v is None else f"{v:.2f}"


def f3(v) -> str:
    return "n/a" if v is None else f"{v:.3f}"


def rx(v) -> str:
    return "n/a" if v is None else (f"{v:.1f}" if v >= 10 else f"{v:.2f}")


def ci(k: int, n: int) -> str:
    lo, hi = wilson(k, n)
    return f"{lo:.2f}--{hi:.2f}"


def table(spec: str, head: list[str], rows: list[list[str]], *, caption: str, label: str,
          note: str = "", size: str = r"\small", env: str = "tabularx", width: str = r"\textwidth",
          place: str = "htbp") -> str:
    """A booktabs table in a float, caption above, an optional note below."""

    lines = [rf"\begin{{table}}[{place}]", r"\centering", size, rf"\caption{{{caption}}}", rf"\label{{{label}}}"]
    open_ = rf"\begin{{tabularx}}{{{width}}}{{{spec}}}" if env == "tabularx" else rf"\begin{{tabular}}{{{spec}}}"
    lines += [open_, r"\toprule", " & ".join(head) + r" \\", r"\midrule"]
    lines += [" & ".join(r) + r" \\" for r in rows]
    lines += [r"\bottomrule", rf"\end{{{env}}}"]
    if note:
        lines += [r"\par\smallskip", r"\begin{minipage}{0.97\textwidth}\footnotesize " + note + r"\end{minipage}"]
    lines += [r"\end{table}"]
    return "\n".join(lines) + "\n"


def longtable(spec: str, head: list[str], rows: list[list[str]], *, caption: str, label: str,
              size: str = r"\small") -> str:
    lines = [r"\begingroup" + size, rf"\begin{{longtable}}{{{spec}}}",
             rf"\caption{{{caption}}}\label{{{label}}}\\", r"\toprule", " & ".join(head) + r" \\", r"\midrule",
             r"\endfirsthead", r"\toprule", " & ".join(head) + r" \\", r"\midrule", r"\endhead",
             r"\midrule\multicolumn{" + str(len(head)) + r"}{r}{\footnotesize\itshape continued on the next page}\\",
             r"\endfoot", r"\bottomrule", r"\endlastfoot"]
    lines += [" & ".join(r) + r" \\" for r in rows]
    lines += [r"\end{longtable}", r"\endgroup"]
    return "\n".join(lines) + "\n"


def longtable_x(spec: str, head: list[str], rows: list[list[str]], *, caption: str, label: str,
                size: str = r"\small") -> str:
    """A table that may break across pages and fills the text width (xltabular)."""

    lines = [r"\begingroup" + size, rf"\begin{{xltabular}}{{\textwidth}}{{{spec}}}",
             rf"\caption{{{caption}}}\label{{{label}}}\\", r"\toprule", " & ".join(head) + r" \\", r"\midrule",
             r"\endfirsthead", r"\toprule", " & ".join(head) + r" \\", r"\midrule", r"\endhead",
             r"\midrule\multicolumn{" + str(len(head)) + r"}{r}{\footnotesize\itshape continued on the next page}\\",
             r"\endfoot", r"\bottomrule", r"\endlastfoot"]
    lines += [" & ".join(r) + r" \\ \addlinespace" for r in rows]
    lines += [r"\end{xltabular}", r"\endgroup"]
    return "\n".join(lines) + "\n"


# --------------------------------------------------------------------------- #
# setup tables
# --------------------------------------------------------------------------- #

def tab_tasks() -> str:
    r = load("benchmark")
    portal = set(load("benchmark-portal").task_ids)
    rows = []
    for t in r.task_details:
        needs = "; ".join(tex(n.replace(" @ ", " (").replace("_", " ") + ")") for n in t.needs)
        trap = tex(t.trap) if t.trap else "none"
        where = "all three" if t.task_id in portal else "in memory"
        rows.append([code(t.task_id), tex(t.purpose.replace("_", " ")), needs, trap, where])
    return table(r"L{2.4cm}L{1.6cm}YL{2.9cm}L{1.2cm}",
                 ["Task", "Purpose", "Minimum necessary fields (layer)", "What the wording invites", "Sources"],
                 rows, caption="The eight extraction tasks and the expert field list each one executes",
                 label="tab:tasks", size=r"\footnotesize",
                 note="The last four are trap tasks: the purpose and the needed fields are lawful, and only the "
                      "wording asks for more. ``All three'' means the task also runs on the portal and on the "
                      "public export; the in-memory workload runs all eight. Fields needed are counted as distinct "
                      "(layer, field) pairs: 41 for the eight in-memory tasks. On the portal and the export the ward "
                      "census asks for the ward and the encounter time only, so the four-task workload there needs 21.")


def tab_models() -> str:
    r = load("benchmark")
    rows = []
    for m in MODEL_ORDER:
        runs = [s for s in r.scores if s.model == m]
        if not runs:
            continue
        access = "Gemini API, free tier" if m.startswith("gemini") else "command-line client, subscription sign-in"
        rows.append([tex(MODEL[m]) + r"\newline{\scriptsize " + code(m) + "}", access,
                     ", ".join(BRIEFING[s.briefing] for s in sorted(
                         runs, key=lambda s: ["unaided", "informed", "policy"].index(s.briefing))),
                     str(runs[0].repeats)])
    return table(r"L{3.4cm}L{3.4cm}YC{1.2cm}",
                 ["Model", "Access path", "Briefings recorded", "Runs per task"], rows,
                 caption="The publicly available AI models compared", label="tab:models", size=r"\footnotesize")


def tab_policy() -> str:
    from compliance.policy import PURPOSE_POLICY
    rows = []
    for purpose, pol in PURPOSE_POLICY.items():
        cats = ", ".join(sorted(CATEGORY.get(c.value, c.value) for c in pol.allowed_categories))
        rows.append([code(purpose.value), tex(cats), f"{pol.max_retention_days} days",
                     "yes" if pol.requires_pseudonymised_identifiers else "no"])
    return table(r"L{3.3cm}YC{1.7cm}C{1.9cm}",
                 ["Purpose", "Categories necessary for it", "Retention ceiling", "Pseudonymise on export"],
                 rows, caption="The purpose policy read by DM-01, SL-01 and SS-01", label="tab:policy")


def tab_catalogue() -> str:
    from data_synthetic.catalogue import FIELD_CATALOGUE
    rows = []
    for layer, fields in FIELD_CATALOGUE.items():
        for i, (name, cat) in enumerate(fields.items()):
            rows.append([tex(layer.value.replace("_", " ")) if i == 0 else "", code(name),
                         tex(CATEGORY.get(cat.value, cat.value))])
    return longtable("lll", ["HIS layer", "Field", "DPDP category"], rows,
                     caption="The field catalogue: every field, its layer and its category", label="tab:catalogue")


def tab_roles() -> str:
    from compliance.roles import ROLE_POLICY
    rows = []
    for role, pol in ROLE_POLICY.items():
        rows.append([tex(role.value), tex(", ".join(sorted(p.value.replace("_", " ") for p in pol.purposes))),
                     tex(", ".join(sorted(pol.artefacts))),
                     tex(", ".join(sorted(CATEGORY.get(c.value, c.value) for c in pol.allowed_categories())))])
    return table(r"L{1.8cm}L{2.3cm}YL{3.0cm}",
                 ["Role", "Purposes", "Artefacts handled", "Derived scope"], rows,
                 caption=r"Role scopes derived as purposes $\cap$ artefacts", label="tab:roles",
                 size=r"\footnotesize")


def tab_functions() -> str:
    from agent.functions import REGISTRY
    from compliance.roles import StaffRole
    rows = []
    for spec in REGISTRY:
        who = [r.value for r in StaffRole if spec.permitted_for(r)] or ["no role"]
        rows.append([tex(spec.label), tex(spec.purpose.value.replace("_", " ")),
                     tex(", ".join(i.name.replace("_", " ") for i in spec.inputs) or "none"), tex(", ".join(who))])
    return longtable(r"L{3.9cm}L{2.3cm}L{3.5cm}L{2.5cm}",
                     ["Function", "Purpose", "Details asked for", "Permitted for"], rows,
                     caption="The staff assistant's functions and who the gate lets use them",
                     label="tab:functions", size=r"\footnotesize")


def tab_mapping() -> str:
    text = (ROOT / "docs" / "compliance" / "dpdp-provision-map.md").read_text(encoding="utf-8")
    section = text.split("## Section mapping", 1)[1].split("\n## ", 1)[0]
    lines = [l for l in section.splitlines() if l.startswith("|")]
    # The last column of the source table is the team's verification note; the report keeps the first four.
    head = [tex(c.strip().strip("*")) for c in lines[0].strip("|").split("|")][:4]
    rows = []
    for l in lines[2:]:
        cells = [c.strip() for c in l.strip("|").split("|")][:4]
        rows.append([tex(re.sub(r"[`*]", "", c).replace("✔", "").strip()) for c in cells])
    spec = r"L{1.1cm}L{1.9cm}L{5.0cm}Y"
    return longtable_x(spec, head, rows, caption="Rules mapped to the sections of the Act relied on",
                     label="tab:mapping", size=r"\footnotesize")


# --------------------------------------------------------------------------- #
# result tables
# --------------------------------------------------------------------------- #

def tab_headline() -> str:
    r = load("benchmark")
    trap_ids = r.trap_task_ids()
    rows = []
    for s, flagged in r.by_model():
        per = r"\newline{\scriptsize (" + "\\,$\\cdot$\\," .join(
            str(s.trap_matrix[t][0]) for t in trap_ids if t in s.trap_matrix) + ")}"
        stable = f"{s.stable_runs}/{s.repeat_runs}" + (f" [{ci(s.stable_runs, s.repeat_runs)}]"
                                                      if s.model else "")
        rows.append([name_of(s, short=True), f3(s.mean_compliance_score), f2(s.behaviour_score),
                     f"{s.traps_resisted}/{s.traps}{per}", f2(s.cost.coverage), f2(s.cost.excess_ratio),
                     rx(s.cost.record_excess), stable])
    return table(r"YC{0.9cm}C{0.8cm}C{1.9cm}C{1.2cm}C{0.9cm}C{1.0cm}C{1.9cm}",
                 ["Technique", "Score", "Beh.", "Trap runs held", r"Agree\-ment", "Excess", "Record excess",
                  r"Same decision [95\% CI]"], rows,
                 caption="Headline comparison in memory: each AI model told the purpose policy",
                 label="tab:headline", size=r"\footnotesize",
                 note="Eight tasks, five runs each, every run scored. Trap runs are counted per trap task (claim "
                      "reconciliation, desk registration, ward summary for a registry, consultant file; five runs "
                      "each, shown in brackets). Agreement is the share of the expert field list obtained; excess "
                      "is distinct fields taken over fields needed; record excess is records read over the "
                      "patient's own on single-patient tasks. The interval is Wilson's, treating runs as "
                      "independent; runs share a task and a model, so the interval is indicative only. The proposed technique and "
                      "the baseline do not sample, so their repeats carry no interval.")


def tab_traps() -> str:
    """Trap runs held per trap task, every technique and briefing (in memory)."""

    r = load("benchmark")
    ids = r.trap_task_ids()
    labels = {"claim-reconciliation": "Claim recon.", "desk-registration": "Desk reg.",
              "ward-summary-registry": "Registry copy", "consultant-file": "Consultant file"}
    rows = []
    for s in r.scores:
        cells = [f"{s.trap_matrix[t][0]}/{s.trap_matrix[t][1]}" if t in s.trap_matrix else "n/a" for t in ids]
        rows.append([name_of(s), *cells, f"{s.traps_resisted}/{s.traps}"])
    return table(r"Y" + "C{1.55cm}" * (len(ids) + 1),
                 ["Technique", *[labels.get(t, code(t)) for t in ids], "Total"], rows,
                 caption="Trap runs held per trap task, every technique and briefing (in memory)",
                 label="tab:traps", size=r"\footnotesize",
                 note="Each cell counts the runs, out of five, that took no category outside the purpose, declared no "
                      "onward use and declared a retention within the purpose's ceiling. The four tasks invite, in "
                      "order: the diagnosis for billing, an insurance number at the registration desk, a copy for a "
                      "research registry, and a year's retention for care.")


def tab_rules() -> str:
    r = load("benchmark")
    rows = []
    for s in r.scores:
        cells = [f2(s.per_rule_mean.get(k)) for k in r.rule_ids]
        rows.append([name_of(s), f3(s.mean_compliance_score), tex(s.rules_passed), *cells])
    return table(r"YC{0.9cm}C{0.8cm}" + "C{0.72cm}" * len(r.rule_ids),
                 ["Technique", "Score", "Passed", *r.rule_ids], rows,
                 caption="Compliance per rule, in memory, every technique and briefing",
                 label="tab:rules", size=r"\footnotesize",
                 note="Each cell is the mean over all of a technique's runs (forty for a model, eight tasks by five "
                      "runs). ``Passed'' counts rules met in the worst run.")


def _cost_rows(name: str, *, portal: bool) -> list[list[str]]:
    rows = []
    for s in load(name).scores:
        c = s.cost
        stable = f"{s.stable_runs}/{s.repeat_runs}" if s.repeat_runs else "one run"
        row = [name_of(s), f3(s.mean_compliance_score), f3(s.substantiated_score), f"{s.traps_resisted}/{s.traps}",
               f2(c.coverage), f2(c.excess_ratio), rx(c.record_excess)]
        row += [str(c.page_loads)] if portal else [f"{c.distinct_fields}/{c.needed_fields}"]
        rows.append(row + [stable])
    return rows


def tab_cost_memory() -> str:
    return table(r"YC{0.8cm}C{0.8cm}C{0.8cm}C{0.95cm}C{0.8cm}C{0.8cm}C{0.9cm}C{0.8cm}",
                 ["Technique", "Score", "Subst.", "Traps", r"Agree\-ment", "Excess", "Rec. exc.", "Fields",
                  "Stable"], _cost_rows("benchmark", portal=False),
                 caption="Cost, substantiation, traps and repeatability in memory", label="tab:cost-memory",
                 size=r"\scriptsize",
                 note="``Subst.'' is the score after removing any declaration the capability register cannot "
                      "back. ``Fields'' is distinct (layer, field) pairs taken over pairs needed, as a mean per run "
                      "rounded to whole fields; excess is computed exactly over all runs, so the two can differ "
                      "in the second decimal. ``Stable'' counts "
                      "repeats that reproduced the first run's decision: the same fields and the same manifest "
                      "structure.")


def tab_cost_portal() -> str:
    return table(r"YC{0.8cm}C{0.8cm}C{0.8cm}C{0.95cm}C{0.8cm}C{0.8cm}C{0.9cm}C{0.8cm}",
                 ["Technique", "Score", "Subst.", "Traps", r"Agree\-ment", "Excess", "Rec. exc.", "Page loads",
                  "Stable"], _cost_rows("benchmark-portal", portal=True),
                 caption="The same comparison on the login-gated portal, scraped by a real browser",
                 label="tab:cost-portal", size=r"\scriptsize",
                 note="Four tasks (one trap), 20 records per module, ten rows to a page. The proposed technique and the baseline run "
                      "once; each model's five recorded decisions (its field lists and manifests) are replayed through the same browser "
                      "adapter: the models never saw the portal. Page loads are counted by the browser; for a model they "
                      "are a mean per run, rounded.")


def tab_public() -> str:
    r = load("benchmark-public")
    rows = []
    for s, _ in r.by_model():
        rows.append([name_of(s, short=True), f3(s.mean_compliance_score), f2(s.cost.coverage),
                     f2(s.cost.excess_ratio), rx(s.cost.record_excess) + r"$\times$",
                     f"{s.traps_resisted}/{s.traps}"])
    note = ""
    if r.coverage_needed:
        note = (f"Coverage ceiling measured from the export: {r.coverage_reachable} of the {r.coverage_needed} "
                f"fields the tasks need can be obtained; {r.coverage_needed - r.coverage_in_source} are absent "
                f"from the export and {r.coverage_in_source - r.coverage_reachable} are absent from the records "
                f"of the patient a single-patient task is about. Models are shown told the policy. A records ratio below one "
                f"means the request returned fewer rows than the patient has across the needed layers: in this export a "
                f"layer is stacked from several files, and a request for particular fields returns rows only from the "
                f"files that carry them.")
    return table(r"YC{1.0cm}C{1.3cm}C{1.0cm}C{2.0cm}C{1.2cm}",
                 ["Technique", "Score", r"Agree\-ment", "Excess", "Records read / own", "Trap held"], rows,
                 caption="The four-task workload on a public export we did not generate", label="tab:public",
                 note=note)


def tab_injection() -> str:
    data = json.loads((RESULTS / "injection.json").read_text(encoding="utf-8"))
    ids = [t["task_id"] for t in data["tasks"]]
    rows = []
    for r in data["rows"]:
        if r["short"] == "compliance-aware":
            name = r"\textbf{Proposed (reference)}"
        elif r["short"] == "unconstrained":
            name = "Baseline (unconstrained)"
        else:
            name = f"{MODEL.get(r['model'], r['model'])}, {BRIEFING.get(r['briefing'], r['briefing'])}"
        cells = []
        for t in ids:
            c = r["per_task"][t]
            gave = [k for k in ("category", "onward", "retention", "scope") if c[k]]
            cells.append(f"{c['held']}/{c['runs']}" + (" (" + ", ".join(f"{k[0]}{c[k]}" for k in gave) + ")"
                                                        if gave else ""))
        rows.append([name, f"{r['held']}/{r['runs']}", *cells])
    labels = {"injected-billing": "Billing note", "injected-onward": "Onward use", "injected-scope": "Every patient"}
    return table(r"YC{0.9cm}" + "C{2.1cm}" * len(ids),
                 ["Technique", "Held", *[labels.get(t, code(t)) for t in ids]], rows,
                 caption="Instructions planted in the request: runs that held the purpose", label="tab:injection",
                 size=r"\scriptsize",
                 note="Brackets count the runs that broke the purpose on each axis: c, a category outside the "
                      "purpose; o, a declared onward use; r, retention above the ceiling; s, other patients' "
                      "records read (observed by the meter). One unaided Gemini sample was not returned by the "
                      "free tier, so that row is scored on four runs per task.")


def tab_scale() -> str:
    data = json.loads((RESULTS / "scale.json").read_text(encoding="utf-8"))
    rows = []
    for r in data["rows"]:
        o, b = r["ours"], r["baseline"]
        rows.append([str(r["records"]), str(o["page_loads"]), str(b["page_loads"]),
                     f"{b['page_loads'] / o['page_loads']:.1f}" + r"$\times$", f3(o["score"]), f3(b["score"]),
                     f"{b['record_excess'] or 0:.0f}" + r"$\times$"])
    return table("C{1.6cm}C{1.5cm}C{1.7cm}C{1.1cm}C{1.4cm}C{1.6cm}C{2.2cm}",
                 ["Records per module", "Proposed: page loads", "Baseline: page loads", "Ratio", "Proposed: score",
                  "Baseline: score", "Baseline: records read / needed"], rows,
                 caption="Cost as the portal grows (four-task workload)", label="tab:scale", env="tabular",
                 size=r"\footnotesize")


def tab_ablation() -> str:
    data = json.loads((RESULTS / "ablation.json").read_text(encoding="utf-8"))
    rows = []
    for r in data["rows"]:
        lost = ", ".join(f"{k} {v:.2f}" for k, v in r["rules_lost"].items()) or "none"
        ours = r["without"] is None and r["technique"].startswith("compliance")
        name = r"\textbf{Proposed, complete}" if ours else (
            "Baseline (unconstrained)" if r["technique"].startswith("unconstrained")
            else "Proposed " + tex(r["technique"].replace("ours ", "")))
        if r["serves"] and r["serves"].strip("- "):
            name += r"\newline{\tiny " + tex(r["serves"]) + "}"
        rows.append([name, f3(r["score"]), f2(r["excess"]),
                     "n/a" if r["record_excess"] is None else f2(r["record_excess"]), tex(r["traps"]),
                     tex(r["leaked"]), tex(lost)])
    return table(r"L{3.3cm}C{0.8cm}C{0.8cm}C{0.9cm}C{0.7cm}C{1.1cm}Y",
                 ["Variant (principle served)", "Score", "Excess", "Rec. exc.", "Traps", "Leaked", "Rules below 1"],
                 rows, caption="Ablation: our technique with one design choice switched off at a time",
                 label="tab:ablation", size=r"\scriptsize",
                 note="Eight tasks in memory, the same seven rules. ``Leaked'' is the export audit on the patient "
                      "summary: raw identifiers found in the shaped export over identifiers extracted.")


def tab_navmap() -> str:
    d = json.loads((RESULTS / "navigation-map.json").read_text(encoding="utf-8"))
    rows = []
    for m in d["modules"]:
        rows.append([tex(m["title"]), code(m["list_path"]), str(m["page_count"]), str(len(m["columns"])),
                     str(len(m["detail_fields"])), tex(m["inferred_layer"].replace("_", " ")),
                     f"{m['layer_confidence']:.0%}".replace("%", r"\%")])
    return table(r"YL{2.6cm}C{0.8cm}C{1.1cm}C{1.1cm}L{2.5cm}C{1.4cm}",
                 ["Module (portal's name)", "Path", "Pages", "List columns", "Record fields", "Inferred layer",
                  "Confidence"], rows,
                 caption=f"The navigation map the crawler built ({d['page_loads']} page loads after sign-in)",
                 label="tab:navmap", size=r"\footnotesize")


def tab_purpose_matrix() -> str:
    from compare_purposes import BILLING_TASK, CARE_TASK
    from compliance.purpose_matrix import score_across_purposes
    from extraction.adapters.mock_his import MockHISDataSource
    from extraction.techniques.compliant import CompliantExtractionTechnique

    source = MockHISDataSource(records_per_layer=25, seed=42)
    tech = CompliantExtractionTechnique()
    blocks = []
    care = tech.extract(source, CARE_TASK)
    billing = tech.extract(source, BILLING_TASK)
    year = billing.run.model_copy(update={"run_id": "billing-pull--year-retention", "retention_days": 365,
                                          "deletion_mechanism": "purge at end of statutory audit retention"})
    for label, run, recs in (("Care pull, 30 days", care.run, care.records),
                             ("Billing pull, 30 days", billing.run, billing.records),
                             ("Billing pull, 365 days", year, billing.records)):
        m = score_across_purposes(run, recs)
        for i, v in enumerate(m.verdicts):
            blocks.append([label if i == 0 else "", tex(v.purpose.replace("_", " ")),
                           "yes" if v.is_declared_purpose else "no", f3(v.compliance_score),
                           f"{v.rules_passed}/{v.rules_total}",
                           tex(", ".join(v.failed_rules) or "none"), tex(v.verdict().replace("_", " "))])
    rows = []
    for i, b in enumerate(blocks):
        if i and i % 3 == 0:
            rows.append([r"\midrule " + b[0], *b[1:]])
        else:
            rows.append(b)
    return table(r"L{1.9cm}L{1.9cm}C{1.1cm}C{0.9cm}C{0.9cm}L{1.9cm}Y",
                 ["Extraction", "Judged under", "Declared", "Score", "Passed", "Failed", "Why"], rows,
                 caption="One extraction judged under every purpose", label="tab:purpose-matrix",
                 size=r"\footnotesize",
                 note="Each block is one run by our technique with a full manifest; only the purpose it is judged "
                      "under changes. NT-01 fails under every undeclared purpose because the notice named the "
                      "declared one.")


def tab_roles_gate() -> str:
    from show_role_access import REQUESTS
    from compliance.roles import StaffRole, authorise
    rows = []
    for label, purpose, artefacts, categories in REQUESTS:
        cells = [tex(label), tex(purpose.value.replace("_", " "))]
        for role in StaffRole:
            d = authorise(role, purpose, artefacts, categories)
            cells.append("permitted" if d.allowed else r"declined, \textbf{" + d.rule_id + "}")
        rows.append(cells)
    return table(r"YL{2.0cm}" + "C{1.9cm}" * len(list(StaffRole)),
                 ["Request", "Purpose", *[tex(r.value.capitalize()) for r in StaffRole]], rows,
                 caption="One request through all three roles", label="tab:role-gate", size=r"\footnotesize")


def tab_update() -> str:
    v1, v2 = load("benchmark-portal"), load("benchmark-portal-v2")
    b2 = {s.short: s for s in v2.scores}
    rows, same = [], 0
    for s in v1.scores:
        t = b2.get(s.short)
        if t is None:
            continue
        ok = (round(s.mean_compliance_score, 6) == round(t.mean_compliance_score, 6)
              and round(s.cost.coverage, 6) == round(t.cost.coverage, 6)
              and s.traps_resisted == t.traps_resisted and s.cost.distinct_fields == t.cost.distinct_fields)
        same += ok
        if s.briefing in (None, "policy"):
            rows.append([name_of(s, short=True), f3(s.mean_compliance_score), f3(t.mean_compliance_score),
                         f2(s.cost.coverage), f2(t.cost.coverage), str(s.cost.page_loads), str(t.cost.page_loads)])
    return table(r"YC{1.1cm}C{1.1cm}C{1.3cm}C{1.3cm}C{1.0cm}C{1.0cm}",
                 ["Technique", "Score v1", "Score v2", "Agreement v1", "Agreement v2", "Pages v1", "Pages v2"],
                 rows, caption=f"The scraper on the updated HIS: {same} of {len(v1.scores)} technique rows unchanged",
                 label="tab:update", size=r"\footnotesize",
                 note="v1 is the benchmarked portal; v2 a simulated vendor release (modules renamed and moved, "
                      "billing split in two, fields moved to record pages, headers and buttons relabelled). A row "
                      "is unchanged when its score, agreement, traps held and field count are all identical. "
                      "Models are shown told the policy; the count covers all briefings. The models' recorded field lists were replayed "
                      "through the updated adapter: the release was absorbed by the crawler and the alias file, not by the models.")


# --------------------------------------------------------------------------- #
# plots (pgfplots)
# --------------------------------------------------------------------------- #

def fig_traps() -> str:
    """Trap runs held per model under each briefing, out of 20."""

    r = load("benchmark")
    ours = r.reference()
    coords = {b: [] for b in ("unaided", "informed", "policy")}
    for i, m in enumerate(MODEL_ORDER):
        for s in r.scores:
            if s.model == m:
                coords[s.briefing].append(f"({i},{s.traps_resisted})")
    xt = ",".join(tex(MODEL[m]) for m in MODEL_ORDER)
    styles = {"unaided": "fill=white, postaction={pattern=north east lines}", "informed": "fill=black!35",
              "policy": "fill=black!85"}
    lines = [r"\begin{tikzpicture}", r"\begin{axis}[ybar, bar width=10pt, width=0.95\textwidth, height=7cm,",
             r"  ymin=0, ymax=" + str(ours.traps + 6) + r", ylabel={trap runs held (of " + str(ours.traps) + ")},",
             r"  ytick={0,5,...," + str(ours.traps) + r"},",
             r"  xtick={0,...," + str(len(MODEL_ORDER) - 1) + r"}, xticklabels={" + xt + r"},",
             r"  xticklabel style={font=\footnotesize, align=center, text width=2.6cm},",
             r"  legend style={at={(0.5,1.03)}, anchor=south, legend columns=3, font=\small, draw=none,",
             r"    /tikz/every even column/.append style={column sep=0.6cm}},",
             r"  legend image code/.code={\draw[#1] (0cm,-0.13cm) rectangle (0.45cm,0.13cm);},",
             r"  nodes near coords, every node near coord/.append style={font=\scriptsize},",
             r"  enlarge x limits=0.15, ymajorgrids, grid style={black!10}, clip=false]"]
    for b in ("unaided", "informed", "policy"):
        lines.append(rf"\addplot[{styles[b]}, draw=black] coordinates {{{' '.join(coords[b])}}};")
    lines += [r"\legend{task + register, told the Act, told the policy}",
              rf"\draw[dashed, thick] (axis cs:-0.45,{ours.traps_resisted}) -- (axis cs:{len(MODEL_ORDER) - 0.55},"
              rf"{ours.traps_resisted});",
              rf"\node[font=\footnotesize, anchor=south west, fill=white, inner sep=1pt] at "
              rf"(axis cs:-0.45,{ours.traps_resisted + 2.3}) {{proposed: {ours.traps_resisted} of "
              rf"{ours.traps} under every briefing}};",
              r"\end{axis}", r"\end{tikzpicture}"]
    return "\n".join(lines) + "\n"


def fig_coverage() -> str:
    """Agreement against excess, every technique and briefing, in memory."""

    r = load("benchmark")
    marks = {"unaided": "triangle*", "informed": "square*", "policy": "*"}
    lines = [r"\begin{tikzpicture}",
             r"\begin{axis}[width=0.9\textwidth, height=7cm, xlabel={excess ratio (fields taken / fields needed)},",
             r"  ylabel={agreement with the expert field list}, xmin=0.6, xmax=1.6, ymin=0.55, ymax=1.05,",
             r"  grid=both, grid style={black!8}, legend columns=2,",
             r"  legend style={font=\footnotesize, at={(0.5,-0.2)}, anchor=north, draw=none},",
             r"  legend cell align=left]"]
    for b in ("unaided", "informed", "policy"):
        pts = " ".join(f"({s.cost.excess_ratio:.3f},{s.cost.coverage:.3f})" for s in r.scores if s.briefing == b)
        lines.append(rf"\addplot[only marks, mark={marks[b]}, mark size=2.6pt, black!70] coordinates {{{pts}}};")
    ours = r.reference()
    lines.append(rf"\addplot[only marks, mark=star, mark size=5pt, very thick, black] coordinates "
                 rf"{{({ours.cost.excess_ratio:.3f},{ours.cost.coverage:.3f})}};")
    lines += [r"\legend{models: task + register, models: told the Act, models: told the policy, proposed (reference)}",
              r"\draw[dashed, black!40] (axis cs:1,0.55) -- (axis cs:1,1.05);",
              r"\draw[dashed, black!40] (axis cs:0.6,1) -- (axis cs:1.6,1);"]
    b = r.baseline()
    lines += [rf"\node[font=\footnotesize, anchor=north east, align=right, fill=white] at (axis cs:1.59,1.04) "
              rf"{{baseline off the chart:\\ agreement {b.cost.coverage:.2f}, excess {b.cost.excess_ratio:.2f}}};",
              r"\end{axis}", r"\end{tikzpicture}"]
    return "\n".join(lines) + "\n"


def fig_stability() -> str:
    """Repeats that reproduced the first decision, per model and briefing, with Wilson intervals."""

    r = load("benchmark")
    lines = [r"\begin{tikzpicture}",
             r"\begin{axis}[xbar, width=0.5\textwidth, height=9.4cm, xmin=0, xmax=1.05, bar width=6pt,",
             r"  xlabel={share of repeats reproducing the first decision (95\% Wilson interval)},",
             r"  ytick=data, yticklabels from table={\stabdata}{label}, yticklabel style={font=\footnotesize},",
             r"  y dir=reverse, xmajorgrids, grid style={black!10}, enlarge y limits=0.04]"]
    rows = []
    for s in r.scores:
        if not s.repeat_runs:
            continue
        p = s.stable_runs / s.repeat_runs
        lo, hi = wilson(s.stable_runs, s.repeat_runs) if s.model else (p, p)
        rows.append((name_of(s, short=False).replace(r"\textbf{Proposed (reference)}", "Proposed (reference)"),
                     p, p - lo, hi - p))
    data = ["label p lo hi"] + [f"{{{lab}}} {p:.3f} {lo:.3f} {hi:.3f}" for lab, p, lo, hi in rows]
    pre = [r"\pgfplotstableread[col sep=space]{", *data, r"}\stabdata"]
    lines.append(r"\addplot[fill=black!35, draw=black, error bars/.cd, x dir=both, x explicit] "
                 r"table[x=p, y expr=\coordindex, x error minus=lo, x error plus=hi] {\stabdata};")
    lines += [r"\end{axis}", r"\end{tikzpicture}"]
    return "\n".join(pre + lines) + "\n"


def fig_scale() -> str:
    data = json.loads((RESULTS / "scale.json").read_text(encoding="utf-8"))
    ours = " ".join(f"({r['records']},{r['ours']['page_loads']})" for r in data["rows"])
    base = " ".join(f"({r['records']},{r['baseline']['page_loads']})" for r in data["rows"])
    xt = ",".join(str(r["records"]) for r in data["rows"])
    return "\n".join([
        r"\begin{tikzpicture}",
        r"\begin{axis}[width=0.8\textwidth, height=6cm, xlabel={records per portal module},",
        r"  ylabel={page loads, four-task workload}, xmode=log, log basis x=2, ymode=log,",
        r"  xtick={" + xt + r"}, xticklabels={" + xt + r"}, grid=both, grid style={black!8},",
        r"  legend pos=north west, legend style={font=\footnotesize}, legend cell align=left]",
        rf"\addplot[thick, mark=*, black] coordinates {{{ours}}};",
        rf"\addplot[thick, dashed, mark=square*, black!55] coordinates {{{base}}};",
        r"\legend{proposed (reference), baseline}",
        r"\end{axis}", r"\end{tikzpicture}"]) + "\n"


# --------------------------------------------------------------------------- #
# numbers quoted in the prose
# --------------------------------------------------------------------------- #

def _macro(name: str, value) -> str:
    return rf"\newcommand{{\{name}}}{{{value}}}"


def _range(vals, fmt="{:.2f}") -> str:
    lo, hi = min(vals), max(vals)
    return fmt.format(lo) if fmt.format(lo) == fmt.format(hi) else f"{fmt.format(lo)} to {fmt.format(hi)}"


def _pct(v: float) -> str:
    return f"{round(v * 100)}"


def _test_count() -> int:
    import subprocess
    out = subprocess.run([sys.executable, "-m", "pytest", "--collect-only", "-q"], cwd=ROOT,
                         capture_output=True, text=True, encoding="utf-8", errors="replace").stdout
    m = re.search(r"(\d+) tests? collected", out)
    return int(m.group(1)) if m else 0


def numbers() -> str:
    from agent.functions import REGISTRY
    from compliance.roles import StaffRole
    from data_synthetic.catalogue import FIELD_CATALOGUE

    mem, por, pub = load("benchmark"), load("benchmark-portal"), load("benchmark-public")
    v2 = load("benchmark-portal-v2")
    ours_m, base_m = mem.reference(), mem.baseline()
    ours_p, base_p = por.reference(), por.baseline()
    models = [s for s in mem.scores if s.model]
    told = [s for s in models if s.briefing == "policy"]
    untold = [s for s in models if s.briefing in ("unaided", "informed")]
    held_untold, runs_untold = sum(s.traps_resisted for s in untold), sum(s.traps for s in untold)
    claude_told = [s for s in told if s.model.startswith("claude")]
    gem_told = next(s for s in told if s.model.startswith("gemini"))
    lo, hi = wilson(held_untold, runs_untold)
    inj = json.loads((RESULTS / "injection.json").read_text(encoding="utf-8"))
    inj_models = [r for r in inj["rows"] if r["model"]]
    scale = json.loads((RESULTS / "scale.json").read_text(encoding="utf-8"))["rows"]
    ratios = [r["baseline"]["page_loads"] / r["ours"]["page_loads"] for r in scale]
    nav = json.loads((RESULTS / "navigation-map.json").read_text(encoding="utf-8"))
    v2b = {s.short: s for s in v2.scores}
    same = sum(1 for s in por.scores if s.short in v2b
               and round(s.mean_compliance_score, 6) == round(v2b[s.short].mean_compliance_score, 6)
               and round(s.cost.coverage, 6) == round(v2b[s.short].cost.coverage, 6)
               and s.traps_resisted == v2b[s.short].traps_resisted
               and s.cost.distinct_fields == v2b[s.short].cost.distinct_fields)
    told_portal = [s for s in por.scores if s.briefing == "policy"]
    roles = {r.value: sum(1 for f in REGISTRY if f.permitted_for(r)) for r in StaffRole}
    sonnet = next(s for s in told if s.model == "claude-sonnet-5-5")
    out = [
        _macro("NumTests", _test_count()),
        _macro("NumFunctions", len(REGISTRY)),
        _macro("NumFnReception", roles.get("reception", 0)),
        _macro("NumFnNurse", roles.get("nurse", 0)),
        _macro("NumFnAdmin", roles.get("administrator", 0)),
        _macro("NumFields", sum(len(v) for v in FIELD_CATALOGUE.values())),
        _macro("NumModels", len({s.model for s in models})),
        _macro("NumModelRuns", sum(s.runs for s in models)),
        _macro("NumTechniqueRows", len(mem.scores)),
        _macro("NumTasks", len(mem.task_ids)),
        _macro("NumPortalTasks", len(por.task_ids)),
        _macro("NumRepeats", ours_m.repeats),
        # in memory
        _macro("OursScore", f3(ours_m.mean_compliance_score)),
        _macro("BaseScore", f3(base_m.mean_compliance_score)),
        _macro("BaseExcess", f2(base_m.cost.excess_ratio)),
        _macro("BaseRecordExcess", f"{base_m.cost.record_excess:.0f}"),
        _macro("BaseFields", base_m.cost.distinct_fields),
        _macro("NeededFields", ours_m.cost.needed_fields),
        _macro("BaseDM", f2(base_m.per_rule_mean.get("DM-01"))),
        _macro("BaseSS", f2(base_m.per_rule_mean.get("SS-01"))),
        _macro("TrapsHeldUntold", held_untold),
        _macro("TrapRunsUntold", runs_untold),
        _macro("TrapsUntoldCI", f"{lo:.2f} to {hi:.2f}"),
        _macro("TrapsClaudeTold", sum(s.traps_resisted for s in claude_told)),
        _macro("TrapRunsClaudeTold", sum(s.traps for s in claude_told)),
        _macro("TrapsGeminiTold", gem_told.traps_resisted),
        _macro("TrapRunsPerModel", gem_told.traps),
        _macro("AgreeToldRange", _range([s.cost.coverage for s in told])),
        _macro("AgreeToldPctRange", _range([s.cost.coverage * 100 for s in told], "{:.0f}") + r"\,\%"),
        _macro("ExcessToldRange", _range([s.cost.excess_ratio for s in told])),
        _macro("AgreeClaudeToldPctRange", _range([s.cost.coverage * 100 for s in told if s.model.startswith("claude")], "{:.0f}") + r"\,\%"),
        _macro("PortalModelMinPages", min(s.cost.page_loads for s in told_portal)),
        _macro("StableToldRange", _range([s.stable_runs for s in told], "{:d}")),
        _macro("StableMax", max(s.stable_runs for s in models)),
        _macro("StableMin", min(s.stable_runs for s in models)),
        _macro("RepeatRuns", told[0].repeat_runs),
        _macro("ScoreToldRange", _range([s.mean_compliance_score for s in told], "{:.3f}")),
        _macro("ScoreUntoldRange", _range([s.mean_compliance_score for s in untold], "{:.3f}")),
        _macro("SonnetAgreePct", _pct(sonnet.cost.coverage)),
        _macro("SonnetStable", sonnet.stable_runs),
        # portal
        _macro("OursPages", ours_p.cost.page_loads),
        _macro("BasePages", base_p.cost.page_loads),
        _macro("PageRatio", f"{base_p.cost.page_loads / ours_p.cost.page_loads:.1f}"),
        _macro("BasePortalScore", f3(base_p.mean_compliance_score)),
        _macro("BasePortalExcess", f2(base_p.cost.excess_ratio)),
        _macro("BasePortalRecordExcess", f"{base_p.cost.record_excess:.1f}"),
        _macro("ModelPagesToldRange", _range([s.cost.page_loads for s in told_portal], "{:d}")),
        _macro("NavPages", nav["page_loads"]),
        _macro("NavModules", len(nav["modules"])),
        _macro("UpdateSame", same),
        _macro("UpdateRows", len(por.scores)),
        _macro("OursPagesVtwo", v2b["compliance-aware"].cost.page_loads),
        _macro("BasePagesVtwo", v2b["unconstrained"].cost.page_loads),
        # scale, injection, public export
        _macro("ScaleRatioRange", _range(ratios, "{:.1f}")),
        _macro("ScaleMax", scale[-1]["records"]),
        _macro("ScaleBasePagesMax", scale[-1]["baseline"]["page_loads"]),
        _macro("ScaleOursPagesMax", scale[-1]["ours"]["page_loads"]),
        _macro("InjHeldModels", sum(r["held"] for r in inj_models)),
        _macro("InjRunsModels", sum(r["runs"] for r in inj_models)),
        _macro("PublicReachable", pub.coverage_reachable),
        _macro("PublicNeeded", pub.coverage_needed),
        _macro("PublicBaseRecordExcess", f"{pub.baseline().cost.record_excess:.0f}"),
    ]
    return "\n".join(out) + "\n"


OUTPUTS = {
    "numbers": numbers,
    "tab_tasks": tab_tasks, "tab_models": tab_models, "tab_policy": tab_policy, "tab_catalogue": tab_catalogue,
    "tab_roles": tab_roles, "tab_functions": tab_functions, "tab_mapping": tab_mapping,
    "tab_headline": tab_headline, "tab_traps": tab_traps, "tab_rules": tab_rules, "tab_cost_memory": tab_cost_memory,
    "tab_cost_portal": tab_cost_portal, "tab_public": tab_public, "tab_injection": tab_injection,
    "tab_scale": tab_scale, "tab_ablation": tab_ablation, "tab_navmap": tab_navmap,
    "tab_purpose_matrix": tab_purpose_matrix, "tab_role_gate": tab_roles_gate, "tab_update": tab_update,
    "fig_traps": fig_traps, "fig_coverage": fig_coverage, "fig_stability": fig_stability, "fig_scale": fig_scale,
}

HEADER = "% Generated by tools/thesis_tables.py from the tracked artefacts. Do not edit by hand.\n"


def write(check: bool = False) -> list[str]:
    OUT.mkdir(parents=True, exist_ok=True)
    changed = []
    for name, fn in OUTPUTS.items():
        body = HEADER + fn()
        path = OUT / f"{name}.tex"
        old = path.read_text(encoding="utf-8") if path.exists() else None
        if old != body:
            changed.append(path.name)
            if not check:
                path.write_text(body, encoding="utf-8", newline="\n")
    return changed


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    changed = write(check=args.check)
    if args.check:
        print("thesis tables " + ("differ from the artefacts: " + ", ".join(changed) if changed
                                  else "match the artefacts"))
        return 1 if changed else 0
    print("wrote " + (", ".join(changed) or "nothing (already current)"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
