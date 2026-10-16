"""The Portal, version 2: the recorded run as a live data flow, ``docs/review/portal-v2.html``.

    python tools/build_portal_v2.py             # from the staged parts in build/review-parts/
    python tools/build_review_pages.py          # builds the parts, the Report and both Portals

The hospital is drawn as what it holds: 20 patients by 34 fields, 680 values,
each coloured by its DPDP data category. For one job at a time, each technique
-- ours, an AI model, the baseline -- reads cells out of that matrix; every value
it reads becomes a particle that flies into its lane and travels on through the
rules, the export and the erasure. The presenter steps it station by station.

Every number is the recorded one, and every lane replays one run end to end. The
page loads come from the recorded portal visits (the portal replays a model's
first sample). What that run read, how the seven rules judge it, what the export
stage makes of it and when it is erased are computed here by the project's own
code on the same synthetic source the portal served (20 records a module, seed
42). A model's lane also carries the five-sample figures the benchmark reports.

The builder audits its own output with version 1's audit: no raw identifier,
contact detail or quasi-identifier of any record may appear on the page.
"""

from __future__ import annotations

import base64
import json
import re
import sys
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for p in (ROOT, ROOT / "src", ROOT / "scripts"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from tools import build_portal_app as v1                                    # noqa: E402
from tools.page_kit import REVIEW_DIR, write                                # noqa: E402

HERE = ROOT / "tools" / "portal_v2"
OUT = REVIEW_DIR / "portal-v2.html"
SHELL = HERE / "portal.html"
CSS = HERE / "portal.css"
SCRIPTS = ["flow.js"]
FONT = HERE / "fonts" / "Inter-latin-wght.woff2"
# The tokens a page shows are made with fixed display keys (one per technique, as each export has its own),
# so a rebuild does not churn them.
# An export made by the pipeline still gets a fresh random secret (interop.normalise).
DISPLAY_KEY = "portal-display-key"
SHORT = {"patient_administration": "Registration", "clinical_ehr": "Clinical", "ancillary_departmental": "Orders",
         "administrative_financial": "Billing", "infrastructure_integration": "Audit"}


def _flow(portal: dict, rules_part: dict) -> tuple[dict, set[str]]:
    """Per technique and job: what the run read, the rules' verdicts, the export, the erasure."""

    from compliance.access_report import mask
    from compliance.benchmark import bind_subject
    from compliance.checkers import run_all
    from compliance.policy import PURPOSE_POLICY
    from data_synthetic.catalogue import FIELD_CATALOGUE
    from extraction.adapters.mock_his import MockHISDataSource
    from extraction.metering import MeteredSource
    from extraction.techniques import default_techniques
    from interop.layers import HISLayer
    from interop.normalise import audit, normalise
    from run_pipeline import TASKS

    meta = portal["meta"]
    source = MockHISDataSource(records_per_layer=meta.get("records", v1.RECORDS), seed=meta.get("seed", v1.SEED))
    cat = {l.value: {f: c.value for f, c in fields.items()} for l, fields in FIELD_CATALOGUE.items()}

    # the matrix: one column per catalogue field, module by module, in the order the portal lists the modules
    order = [m["layer"] for m in portal["modules"]]
    titles = {m["layer"]: m["title"] for m in portal["modules"]}
    columns, modules = [], []
    for layer in order:
        start = len(columns)
        for f, c in cat[layer].items():
            columns.append({"key": f"{layer}/{f}", "field": f, "cat": c})
        modules.append({"layer": layer, "title": titles[layer], "short": SHORT.get(layer, titles[layer]), "start": start, "count": len(columns) - start})
    col_of = {c["key"]: i for i, c in enumerate(columns)}

    secrets: set[str] = set()
    for layer in source.layers():
        for r in source.fetch(layer):
            for f, val in r.items():
                if (cat[layer.value].get(f) in v1.DIRECT and f != "sex") or f == "insurance_policy_no":
                    secrets |= v1._variants(val)
    register = list(source.fetch(HISLayer.PATIENT_ADMINISTRATION, fields=["mrn", "full_name"]))
    index = {r["mrn"]: i for i, r in enumerate(register)}

    tasks = bind_subject(TASKS, source)
    about = index.get(next(t.subject for t in tasks if t.single_subject))
    generated = date.fromisoformat(meta.get("generated") or date.today().isoformat())
    by_name = {t["name"]: v1._tech_id(t["name"])[0] for t in portal["techniques"]}
    pages: dict[str, dict[str, int]] = {}
    for visit in portal["visits"]:
        if visit["who"] in by_name and visit.get("task"):
            tid = by_name[visit["who"]]
            pages.setdefault(tid, {}).setdefault(visit["task"], 0)
            pages[tid][visit["task"]] += 1
    bench = {v1._tech_id(row["technique"])[0]: row for row in rules_part.get("portal", [])}

    lanes: dict[str, dict] = {}
    for technique in default_techniques(tasks, source):
        tid, model, briefing = v1._tech_id(technique.name)
        b = bench.get(tid, {})
        lane = {"id": tid, "model": model, "briefing": briefing, "jobs": {},
                "samples": b.get("repeats", 1), "mean": b.get("per_task", {}), "range": b.get("per_task_range", {}),
                "traps": b.get("trap_matrix", {}), "decisions": b.get("distinct_decisions", {})}
        for task in tasks:
            out = technique.extract(MeteredSource(source), task)
            read = set()
            for layer_rows in out.rows.values():
                for r in layer_rows:
                    m = r.get("mrn") or r.get("subject_mrn")
                    if m in index:
                        read.add(index[m])
            keys = sorted({f"{lv}/{f}" for lv, layer_rows in out.rows.items() for r in layer_rows for f in r if f"{lv}/{f}" in col_of},
                          key=lambda k: col_of[k])
            allowed = {c.value for c in PURPOSE_POLICY[task.purpose].allowed_categories}
            needed = {f"{lf.layer.value}/{f}" for lf in task.needed for f in lf.fields}
            report = run_all(out.run, out.records)
            shaped = normalise(out, key=f"{DISPLAY_KEY}:{tid}")      # each export its own key, as in the pipeline
            a = audit(out, shaped)
            pid = ""
            for msgs in shaped.hl7.values():
                seg = next((s for m in msgs for s in m.split("\r") if s.startswith("PID")), "")
                if seg:
                    pid = seg
                    break
            token = (re.search(r"PSN-[0-9a-f]+", pid) or [""])[0] if shaped.pseudonymised else ""
            kind = "raw" if a.leaked > 0 else "tok" if token else "none"
            days = out.run.retention_days
            lane["jobs"][task.task_id] = {
                "pages": pages.get(tid, {}).get(task.task_id, 0),
                # rows read: the patients the run can name, or, when it dropped the record number, as many rows as it read
                "patients": sorted(read), "rows": sorted(read) or list(range(min(len(register), max((len(v) for v in out.rows.values()), default=0)))),
                "named": bool(read), "cols": [col_of[k] for k in keys],
                "oos": [col_of[k] for k in keys if cat[k.split("/")[0]].get(k.split("/")[1]) not in allowed],
                "needed": len(needed), "hit": len(needed & set(keys)),
                "rules": {r.rule_id: [r.status.value, round(r.score, 3)] for r in report.results},
                "score": round(report.compliance_score, 3),
                "export": {"kind": kind, "token": token, "leaked": a.leaked, "identifiers": a.identifier_values},
                # the stages between the rules and the export: pseudonymise (and generalise), then shape
                "pseud": {"on": shaped.pseudonymised, "generalised": a.generalised, "k": a.k, "k_rows": a.k_rows},
                "shape": {"hl7": shaped.counts()["hl7_messages"], "fhir": shaped.counts()["fhir_resources"]},
                "retention": days, "erase": (generated + timedelta(days=days)).isoformat() if days else None,
            }
        lanes[tid] = lane

    jobs = [{"id": t.task_id, "purpose": t.purpose.value, "description": t.description, "single": t.single_subject,
             "trap": t.trap or "", "allowed": sorted(c.value for c in PURPOSE_POLICY[t.purpose].allowed_categories),
             "ceiling": PURPOSE_POLICY[t.purpose].max_retention_days}
            for t in tasks]
    patient = {"index": about, "mrn": mask(register[about]["mrn"]), "name": v1._mask_value("full_name", None, register[about]["full_name"]),
               "of": len(register)}
    return {"columns": columns, "modules": modules, "jobs": jobs, "lanes": lanes, "patient": patient}, secrets


def payload() -> tuple[dict, set[str]]:
    parts = v1._parts()
    P, R = parts["portal"], parts["rules"]
    flow, secrets = _flow(P, R)
    traced = {"discover": 0, "harness": 0}
    for visit in P["visits"]:
        if visit["who"] in traced:
            traced[visit["who"]] += 1
    models = []
    for name in P["headline"]:
        tid, model, _ = v1._tech_id(name)
        if model and model not in models:
            models.append(model)
    for lane in flow["lanes"].values():
        if lane["model"] and lane["model"] not in models:
            models.append(lane["model"])
    data = {
        "built": date.today().isoformat(),
        "meta": {k: P["meta"].get(k) for k in ("records", "generated", "tls", "account", "authorisation")},
        "discover": traced["discover"], "harness": traced["harness"],
        "rule_ids": P["rule_ids"], "rule_titles": {r["id"]: r["title"] for r in v1._rule_titles()},
        "models": models, **flow,
    }
    return data, secrets


def render(data: dict) -> str:
    html = SHELL.read_text(encoding="utf-8")
    font = base64.b64encode(FONT.read_bytes()).decode("ascii")
    css = CSS.read_text(encoding="utf-8").replace("/*__FONT__*/", f"url(data:font/woff2;base64,{font}) format('woff2')")
    html = html.replace("/*__CSS__*/", css)
    html = html.replace("/*__JS__*/", "\n".join((HERE / name).read_text(encoding="utf-8") for name in SCRIPTS))
    blob = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c")
    return html.replace("/*__DATA__*/null", blob)


def build(out: Path = OUT) -> Path:
    data, secrets = payload()
    html = render(data)
    v1.check(html, secrets)
    return write(out, html)


def main() -> int:
    out = build()
    size = out.stat().st_size / 1024 / 1024
    print(f"  wrote {out.relative_to(ROOT)}  (the Portal v2, {size:.1f} MB); audit: no raw identifier on the page")
    return 0


if __name__ == "__main__":
    sys.exit(main())
