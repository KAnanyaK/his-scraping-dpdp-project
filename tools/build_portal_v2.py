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
# The timed trial run (scripts/time_portal_trial.py): wall-clock to access and to process each job's records.
TRIAL = ROOT / "docs" / "benchmark_results" / "portal-trial-timing.json"
# The tokens a page shows are made with fixed display keys (one per technique, as each export has its own),
# so a rebuild does not churn them.
# An export made by the pipeline still gets a fresh random secret (interop.normalise).
DISPLAY_KEY = "portal-display-key"
SHORT = {"patient_administration": "Registration", "clinical_ehr": "Clinical", "ancillary_departmental": "Orders",
         "administrative_financial": "Billing", "infrastructure_integration": "Audit"}


def _flow(portal: dict, rules_part: dict) -> tuple[dict, set[str]]:
    """Per technique and job: what the run read, the rules' verdicts, the export, the erasure."""

    from compliance.access_report import mask
    from compliance.benchmark import _split_scores as split_scores, bind_subject, necessary_records
    from compliance.checkers import run_all
    from compliance.models import RecordScope
    from compliance.stats import wilson
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

    necessary = {t.task_id: necessary_records(t, source) for t in tasks}
    lanes: dict[str, dict] = {}
    for technique in default_techniques(tasks, source):
        tid, model, briefing = v1._tech_id(technique.name)
        b = bench.get(tid, {})
        traps = b.get("trap_matrix", {})
        lane = {"id": tid, "model": model, "briefing": briefing, "jobs": {},
                "samples": b.get("repeats", 1), "mean": b.get("per_task", {}), "range": b.get("per_task_range", {}),
                "traps": traps, "decisions": b.get("distinct_decisions", {}),
                # the report prints a 95% Wilson interval beside a model's counts; ours and the baseline do not sample
                "wilson": {job: [round(x, 2) for x in wilson(*hr)] for job, hr in traps.items() if model and hr and hr[1]}}
        for task in tasks:
            metered = MeteredSource(source)
            out = technique.extract(metered, task)
            # As the benchmark harness does: a single-patient run's manifest gets the records the meter saw
            # against the patient's own, so DM-01 scores the record axis on evidence and this run's score is
            # the one the benchmark gives it.
            if necessary[task.task_id] is not None:
                out.run.scope = RecordScope(records_pulled=metered.records, records_necessary=necessary[task.task_id])
            cost = metered.cost({(lf.layer.value, f) for lf in task.needed for f in lf.fields}, 0.0,
                                records_necessary=necessary[task.task_id])
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
            # the report's behaviour score is a mean over every run a technique made of the job
            splits = [split_scores(report, out.run)]
            for k in range(1, lane["samples"] if model else 1):
                technique.sample = k
                again = MeteredSource(source)
                o2 = technique.extract(again, task)
                if necessary[task.task_id] is not None:
                    o2.run.scope = RecordScope(records_pulled=again.records, records_necessary=necessary[task.task_id])
                splits.append(split_scores(run_all(o2.run, o2.records), o2.run))
            if model:
                technique.sample = 0
            behaviour, paperwork = (sum(s[i] for s in splits) / len(splits) for i in (0, 1))
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
                "why": _why(out.run, out.records, report),
                "score": round(report.compliance_score, 3),
                "behaviour": round(behaviour, 3), "paperwork": round(paperwork, 3),
                # the cost profile the report prints: what the meter saw at the adapter boundary
                "cost": {"distinct": cost.distinct_fields, "needed": cost.needed_fields, "matched": cost.matched_fields,
                         "coverage": cost.coverage, "excess": cost.excess_ratio, "records": cost.records,
                         "rec_needed": cost.records_necessary, "rec_excess": cost.record_excess},
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


def _why(run, records, report) -> dict[str, str]:
    """Each rule's score as the rule computes it (compliance/rules/), in figures a presenter can read out.

    Field names and counts only: no value of any record is quoted.
    """

    from compliance.models import FieldCategory
    from compliance.policy import PURPOSE_POLICY, policy_for

    by = {r.rule_id: r for r in report.results}
    pol = policy_for(run.purpose)
    taken = set().union(*(r.field_categories for r in records)) if records else set()
    outside = set(FieldCategory) - pol.allowed_categories
    excess = taken - pol.allowed_categories
    out: dict[str, str] = {}

    cat = 1.0 - len(excess) / len(outside) if outside else 1.0
    dm = f"categories outside the purpose taken: {len(excess)} of {len(outside)}, so 1 - {len(excess)}/{len(outside)} = {cat:.2f}"
    if run.scope is not None:
        p, n = run.scope.records_pulled, run.scope.records_necessary
        rec = 1.0 if p <= max(n, 0) or p == 0 else n / p
        dm += f"; records read {p} where the patient's own are {n}, so {min(p, n)}/{p} = {rec:.2f}; DM-01 is the lower of the two"
    out["DM-01"] = dm + f" = {by['DM-01'].score:.3f}"

    lb = run.lawful_basis
    out["LB-01"] = ("no lawful basis declared = 0" if lb is None else
                    f"basis '{lb.type.value}' declared without its reference = 0.5" if not lb.reference else
                    f"basis '{lb.type.value}' declared with its reference = 1")

    ceiling = pol.max_retention_days
    days = ("no retention declared, -0.5" if run.retention_days is None else
            f"retention {run.retention_days} d over the {ceiling} d ceiling, -0.5" if run.retention_days > ceiling else
            f"retention {run.retention_days} d within the {ceiling} d ceiling")
    out["SL-01"] = f"1, {days}; {'a deletion route declared' if run.deletion_mechanism else 'no deletion route, -0.5'} = {by['SL-01'].score:g}"

    s = run.security
    checks = [s.transport_encrypted, s.at_rest_encrypted, s.access_controlled]
    names = ["TLS", "encrypted at rest", "access control"]
    if pol.requires_pseudonymised_identifiers and FieldCategory.DIRECT_IDENTIFIER in taken:
        checks.append(s.identifiers_pseudonymised)
        names.append("identifiers pseudonymised")
    held = [n for n, ok in zip(names, checks) if ok]
    out["SS-01"] = f"{len(held)} of {len(checks)} safeguards ({', '.join(held) or 'none'}) = {by['SS-01'].score:.2f}"

    if not run.purpose_specified or run.purpose not in PURPOSE_POLICY:
        out["PL-01"] = "no specific purpose declared = 0"
    elif run.secondary_uses:
        out["PL-01"] = f"{len(run.secondary_uses)} onward use(s) beyond the purpose = {by['PL-01'].score:g}"
    else:
        out["PL-01"] = "confined to the one declared purpose = 1"

    nt = run.notice
    out["NT-01"] = ("no privacy notice recorded = 0" if nt is None else
                    "a notice that covers the purpose = 1" if nt.covers_purpose else "a notice not covering the purpose = 0.5")

    g = run.governance
    ac = [g.audit_log_enabled, g.accountable_party is not None, g.processing_record_kept]
    out["AC-01"] = f"{sum(ac)} of 3 controls (audit log, accountable party, record of processing) = {by['AC-01'].score:.2f}"
    return out


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
    # The timed trial run, when there is one: each lane's job carries how long it took on this machine.
    trial = json.loads(TRIAL.read_text(encoding="utf-8")) if TRIAL.exists() else None
    if trial:
        for tid, lane in flow["lanes"].items():
            for job, j in lane["jobs"].items():
                j["time"] = trial["runs"].get(tid, {}).get(job)
    data = {
        "built": date.today().isoformat(),
        "trial": {k: trial[k] for k in ("generated", "machine", "crawl", "portal")} if trial else None,
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
