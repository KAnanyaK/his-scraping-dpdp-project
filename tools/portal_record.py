"""The recorded run as one data block, for the quiet Portals (v3 onwards).

    from tools.portal_record import record
    data, secrets = record()

Versions 1 and 2 each compute what they draw; versions 3, 4 and 5 share this.
Everything here is the recorded run replayed by the project's own code on the
same synthetic source the portal served (20 records a module, seed 42):

* the hospital: the five modules the crawler found, the 34 catalogue fields
  with their DPDP categories, the 20 patients (record numbers masked), and the
  one patient the single-patient jobs are about, with every value of their
  record as a page may show it (identifiers masked, quasi-identifiers coarsened);
* the four jobs: purpose, the categories it allows, its retention ceiling, the
  trap, and the expert field list with each field's reason;
* every technique (ours, 12 model x briefing runs, the baseline) on every job,
  for every recorded sample: what it read, how the seven rules judge it, what
  its manifest declared and whether the register backs each claim (and how:
  demonstrated or attested), what the export made of it, and when it is erased;
* for the replayed run (sample 0, as the portal replays): the page loads the
  browser made, the HL7 v2 messages about the followed patient as they left
  (masked), the retention record, and the run's audit entries -- extraction,
  export and purge -- written by the real code to a temporary log with the
  clock set to the recorded run date, so a rebuild does not churn them;
* the five-run figures the benchmark reports for each technique.

``secrets`` is every raw identifier, contact detail and quasi-identifier of
any record, in each shape a page or an export can give it; a builder passes
it to ``tools.build_portal_app.check`` and refuses to write a page carrying one.
"""

from __future__ import annotations

import contextlib
import hashlib
import json
import re
import sys
import tempfile
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path
from typing import Any, Iterator

ROOT = Path(__file__).resolve().parents[1]
for p in (ROOT, ROOT / "src", ROOT / "scripts"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from tools import build_portal_app as v1                                    # noqa: E402

# Each technique's export gets its own fixed display key, so a rebuild does not
# churn the tokens and two techniques never show the same token for one patient.
# (An export made by the pipeline still gets a fresh random secret.)
DISPLAY_KEY = "portal-display-key"
SHORT = {"patient_administration": "Registration", "clinical_ehr": "Clinical", "ancillary_departmental": "Orders",
         "administrative_financial": "Billing", "infrastructure_integration": "Audit"}
CATEGORIES = [("direct_identifier", "Identifier"), ("quasi_identifier", "Quasi-identifier"), ("contact", "Contact"),
              ("clinical", "Clinical"), ("financial", "Financial"), ("administrative", "Administrative")]
PURPOSES = {"care_coordination": "Care coordination", "billing_settlement": "Billing settlement",
            "patient_registration": "Patient registration"}
BRIEFINGS = {"unaided": "task + register", "informed": "told the Act", "policy": "told the policy"}
# How a field reads on a page: plain words, not the catalogue's snake case.
LABELS = {
    "mrn": "Record number", "subject_mrn": "Record number", "full_name": "Full name", "phone": "Phone",
    "email": "Email", "street_address": "Address", "date_of_birth": "Date of birth", "sex": "Sex",
    "pincode": "PIN code", "admission_ward": "Ward", "admission_datetime": "Admitted",
    "primary_diagnosis": "Diagnosis", "medication": "Medication", "lab_result": "Lab result", "allergy": "Allergy",
    "encounter_datetime": "Encounter", "attending_clinician": "Clinician", "order_id": "Order",
    "specimen_type": "Specimen", "result_value": "Result", "imaging_modality": "Imaging", "report_text": "Report",
    "invoice_id": "Invoice", "billed_amount": "Amount billed", "insurance_policy_no": "Policy number",
    "payer_name": "Payer", "audit_event_id": "Audit event", "event_timestamp": "Logged at",
    "actor_role": "Actor", "action": "Action", "source_system": "Source system",
}
VISIT = {"search": "search", "list": "list", "detail": "record"}


def model_name(model: str | None) -> str:
    """'claude-opus-5-5' -> 'Opus 5.5'; 'gemini-3.1-flash-lite' -> 'Gemini 3.1 Flash-Lite'."""

    if not model:
        return ""
    m = re.match(r"^claude-([a-z]+)-(\d+)-(\d+)$", model)
    if m:
        return f"{m.group(1).capitalize()} {m.group(2)}.{m.group(3)}"
    g = re.match(r"^gemini-([\d.]+)-(.+)$", model)
    if g:
        return f"Gemini {g.group(1)} " + "-".join(w.capitalize() for w in g.group(2).split("-"))
    return model


# ------------------------------------------------------------------ a clock set to the recorded date

@contextlib.contextmanager
def _clock(at: datetime) -> Iterator[None]:
    """Run the audit and retention code as of ``at`` (the recorded run date), so their stamps are stable."""

    import compliance.audit as audit_mod
    import compliance.retention as retention_mod
    import interop.hl7.messages as hl7_mod

    class _Fixed(datetime):
        @classmethod
        def now(cls, tz=None):                                   # noqa: D401 - the one method the code calls
            return at if tz is None else at.astimezone(tz)

    mods = (audit_mod, retention_mod, hl7_mod)
    saved = [m.datetime for m in mods]
    for m in mods:
        m.datetime = _Fixed
    try:
        yield
    finally:
        for m, d in zip(mods, saved):
            m.datetime = d


# ------------------------------------------------------------------ masking for display

def _masker(secrets: set[str], register: list[str], people: set[str]):
    """Mask a line of export text: record numbers as the project masks them, every other raw value to its first letter."""

    from compliance.access_report import mask
    by_len = sorted(secrets | people, key=len, reverse=True)

    def run(text: str) -> str:
        for mrn in register:
            text = text.replace(mrn, mask(mrn))
        for value in by_len:
            if value in text:
                text = text.replace(value, value[0] + "•" * (len(value) - 1))
        return text
    return run


# ------------------------------------------------------------------ the record

def record(deterministic_repeats: int = 1) -> tuple[dict, set[str]]:
    """``deterministic_repeats``: how many times to run ours and the baseline here (a model's samples are recorded)."""

    from compliance.access_report import mask
    from compliance.audit import AuditLog, fields_by_layer
    from compliance.benchmark import bind_subject, necessary_records
    from compliance.models import RecordScope
    from compliance.capabilities import DEFAULT_REGISTER
    from compliance.checkers import run_all
    from compliance.policy import PURPOSE_POLICY
    from compliance.retention import SIDECAR_SUFFIX, purge_expired
    from data_synthetic.catalogue import FIELD_CATALOGUE
    from extraction.adapters.mock_his import MockHISDataSource
    from extraction.metering import MeteredSource
    from extraction.techniques import default_techniques
    from interop.layers import HISLayer
    from interop.normalise import audit as export_audit, normalise
    from compliance.veracity import verify
    from run_pipeline import TASKS

    parts = v1._parts()
    P, R = parts["portal"], parts["rules"]
    meta = P["meta"]
    records, seed = meta.get("records", v1.RECORDS), meta.get("seed", v1.SEED)
    source = MockHISDataSource(records_per_layer=records, seed=seed)
    cat = {l.value: {f: c.value for f, c in fields.items()} for l, fields in FIELD_CATALOGUE.items()}
    generated = date.fromisoformat(meta.get("generated") or date.today().isoformat())
    recorded_at = datetime.combine(generated, time(9, 0), tzinfo=timezone.utc)

    # ---- the hospital: modules in the order the portal lists them, one column per catalogue field
    order = [m["layer"] for m in P["modules"]]
    titles = {m["layer"]: m["title"] for m in P["modules"]}
    columns, modules = [], []
    for layer in order:
        start = len(columns)
        for f, c in cat[layer].items():
            columns.append({"key": f"{layer}/{f}", "layer": layer, "field": f, "label": LABELS.get(f, f), "cat": c})
        modules.append({"layer": layer, "title": titles[layer], "short": SHORT.get(layer, titles[layer]),
                        "start": start, "count": len(columns) - start})
    col_of = {c["key"]: i for i, c in enumerate(columns)}

    # ---- every value the page must never show, and the people a page must not name
    secrets: set[str] = set()
    people: set[str] = set()
    raw: dict[str, list[dict]] = {}
    for layer in source.layers():
        raw[layer.value] = list(source.fetch(layer))
        for r in raw[layer.value]:
            for f, val in r.items():
                if (cat[layer.value].get(f) in v1.DIRECT and f != "sex") or f == "insurance_policy_no":
                    secrets |= v1._variants(val)
                if f == "attending_clinician" and val:              # a person too; masked like a name
                    people |= {w for w in str(val).split() if len(w) >= 4 and not w.endswith(".")}
    register = [r["mrn"] for r in raw[HISLayer.PATIENT_ADMINISTRATION.value]]
    index = {m: i for i, m in enumerate(register)}
    show = _masker(secrets, register, people)

    tasks = bind_subject(TASKS, source)
    about = index.get(next(t.subject for t in tasks if t.single_subject))
    followed = register[about]

    # the followed patient's record, every field as a page may show it
    values: list[Any] = []
    for c in columns:
        rows = raw.get(c["layer"], [])
        key = "subject_mrn" if c["layer"] == HISLayer.INFRASTRUCTURE_INTEGRATION.value else "mrn"
        mine = [r for r in rows if r.get(key) == followed]
        v = mine[0].get(c["field"]) if mine else None
        shown = v1._mask_value(c["field"], c["cat"], v)
        if isinstance(shown, float):
            shown = f"{shown:,.2f}"
        values.append(None if shown in (None, "") else str(shown))
    per_layer = {l: sum(1 for r in rows if r.get("subject_mrn" if l == HISLayer.INFRASTRUCTURE_INTEGRATION.value else "mrn") == followed)
                 for l, rows in raw.items()}

    # ---- the jobs
    # The portal's jobs carry no reasons; the benchmark's task of the same id gives each needed field its reason.
    from run_benchmark import TASKS as BENCH_TASKS
    reasons = {t.task_id: t for t in BENCH_TASKS}
    jobs = []
    for t in tasks:
        scope = PURPOSE_POLICY[t.purpose]
        why = reasons.get(t.task_id)
        needed = [{"col": col_of[f"{lf.layer.value}/{f}"],
                   "why": (t.rationale or (why.rationale if why else {})).get(f"{lf.layer.value}/{f}", "")}
                  for lf in t.needed for f in lf.fields if f"{lf.layer.value}/{f}" in col_of]
        jobs.append({"id": t.task_id, "name": t.task_id.replace("-", " ").capitalize(), "description": t.description,
                     "purpose": t.purpose.value, "purpose_label": PURPOSES.get(t.purpose.value, t.purpose.value),
                     "single": t.single_subject, "trap": t.trap or "",
                     "trap_why": t.trap_rationale or (why.trap_rationale if why and why.trap == t.trap else ""),
                     "allowed": [c for c, _ in CATEGORIES if c in {x.value for x in scope.allowed_categories}],
                     "ceiling": scope.max_retention_days, "needed": needed})

    # ---- the recorded page loads, per technique and job (the portal replays a model's first sample)
    by_name = {t["name"]: v1._tech_id(t["name"])[0] for t in P["techniques"]}
    short_of = {m["slug"]: m["short"] for m in _portal_modules(P, titles)}
    visits: dict[str, dict[str, list]] = {}
    for v in P["visits"]:
        if v["who"] in by_name and v.get("task") and v.get("sample", 0) == 0:
            line = [VISIT.get(v["kind"], v["kind"]), short_of.get(v.get("module", ""), v.get("module", "")), v.get("n", 0)]
            visits.setdefault(by_name[v["who"]], {}).setdefault(v["task"], []).append(line)
    found = sum(1 for v in P["visits"] if v["who"] == "discover")
    harness = sum(1 for v in P["visits"] if v["who"] == "harness")

    bench = {v1._tech_id(row["technique"])[0]: row for row in R.get("portal", [])}
    necessary = {t.task_id: necessary_records(t, source) for t in tasks}
    observed = {"transport_encrypted": True} if meta.get("tls") else {}

    # ---- every technique, every job, every recorded sample
    techniques: dict[str, dict] = {}
    with tempfile.TemporaryDirectory(prefix="portal-record-") as tmp:
        log = AuditLog(Path(tmp) / "audit.jsonl")
        for technique in default_techniques(tasks, source):
            tid, model, briefing = v1._tech_id(technique.name)
            b = bench.get(tid, {})
            samples = b.get("repeats", 1) if model else max(1, deterministic_repeats)
            entry = {
                "id": tid, "kind": "model" if model else ("ours" if tid == "ours" else "base"),
                "model": model, "model_name": model_name(model), "briefing": briefing,
                "briefing_label": BRIEFINGS.get(briefing or "", ""), "samples": samples, "sampled": bool(model),
                "bench": _five_runs(b), "jobs": {},
            }
            for task in tasks:
                runs = []
                for k in range(samples):
                    if model:
                        technique.sample = k
                    metered = MeteredSource(source)
                    out = technique.extract(metered, task)
                    # As the benchmark harness does: a single-patient run's manifest gets the records the meter
                    # saw against the patient's own, so DM-01 scores the record axis on evidence.
                    if necessary[task.task_id] is not None:
                        out.run.scope = RecordScope(records_pulled=metered.records, records_necessary=necessary[task.task_id])
                    with _clock(recorded_at):
                        shaped = normalise(out, key=f"{DISPLAY_KEY}:{tid}")
                    run = _run(out, shaped, task, col_of, cat, index, verify, DEFAULT_REGISTER, run_all,
                               PURPOSE_POLICY, export_audit, observed, generated)
                    run["decision"] = _decision(out, metered)
                    if k == 0:
                        run["pages"] = len(visits.get(tid, {}).get(task.task_id, []))
                        run["visits"] = visits.get(tid, {}).get(task.task_id, [])
                        run.update(_left(out, shaped, followed, show))
                        run["copy"] = _copy(out, followed, f"{DISPLAY_KEY}:{tid}", col_of, cat, show, metered.subject_scope())
                        run.update(_custody(out, shaped, metered, technique.name, log, Path(tmp), tid, task.task_id,
                                            recorded_at, meta, fields_by_layer, purge_expired, SIDECAR_SUFFIX))
                    runs.append(run)
                entry["jobs"][task.task_id] = runs
            if model:
                technique.sample = 0
            techniques[tid] = entry
        first = [runs[0] for t in techniques.values() for runs in t["jobs"].values()]
        _purge_in_date_order(first, log, purge_expired)
        events = _events(log)
        for r in first:
            r["audit"] = events.get(r.pop("_run_id"), [])
            r.pop("_purge", None)
        chain_ok, _ = log.verify()

    models = []
    for name in P["headline"]:
        _, model, _ = v1._tech_id(name)
        if model and model not in models:
            models.append(model)
    for t in techniques.values():
        if t["model"] and t["model"] not in models:
            models.append(t["model"])

    data = {
        "meta": {"records": records, "seed": seed, "generated": generated.isoformat(),
                 "tls": meta.get("tls"), "account": meta.get("account"), "authorisation": meta.get("authorisation"),
                 "found": found, "harness": harness, "modules_found": len(P.get("modules") or []),
                 "chain_intact": chain_ok, "log_days": _log_days(),
                 "recorded": {i["model"]: i.get("recorded", "") for i in R.get("meta", {}).get("model_info", [])}},
        "rules": [{"id": r["id"], "title": r["title"]} for r in v1._rule_titles() if r["id"] in P["rule_ids"]],
        "categories": [{"id": c, "label": l} for c, l in CATEGORIES],
        "modules": modules, "columns": columns,
        "patients": [mask(m) for m in register],
        "patient": {"index": about, "mrn": mask(followed), "name": v1._mask_value("full_name", None, raw[HISLayer.PATIENT_ADMINISTRATION.value][about]["full_name"]),
                    "of": len(register), "values": values, "rows": per_layer},
        "jobs": jobs,
        "models": [{"id": m, "name": model_name(m)} for m in models],
        "briefings": [{"id": k, "label": v} for k, v in BRIEFINGS.items()],
        "register": _register(DEFAULT_REGISTER),
        "techniques": techniques,
    }
    return data, secrets


def _register(reg) -> dict:
    """Which register control backs each kind of claim a manifest can make (what ``compliance.veracity`` checks against)."""

    def c(control):
        return {"id": control.id, "basis": "demonstrated" if control.demonstrated else "attested"} if control else None
    out = {
        "transport encryption": c(reg.transport_encrypted), "encryption at rest": c(reg.at_rest_encrypted),
        "access control": c(reg.access_controlled), "pseudonymisation on export": c(reg.pseudonymisation),
        "deletion mechanism": c(reg.deletion_mechanism), "privacy notice": c(reg.notice),
        "machine-readable notice": c(reg.notice), "audit log": c(reg.audit_log),
        "accountable party": c(reg.accountable_party), "record of processing": c(reg.processing_record),
    }
    out["lawful-basis reference"] = {p.value: c(ctl) for p, ctl in reg.lawful_bases.items()}
    return out


def _portal_modules(P: dict, titles: dict) -> list[dict]:
    from tools.mock_portal.layouts import LAYOUTS
    return [{"slug": m.slug, "short": SHORT.get(m.layer.value, m.title)} for m in LAYOUTS["v1"].modules]


def _log_days() -> int:
    from compliance.audit import LOG_RETENTION_DAYS
    return LOG_RETENTION_DAYS


def _five_runs(b: dict) -> dict:
    """The figures the portal benchmark reports for a technique, over every run it replayed."""

    if not b:
        return {}
    c = b.get("cost", {})
    return {
        "score": b.get("mean_compliance_score"), "per_task": b.get("per_task", {}), "range": b.get("per_task_range", {}),
        "traps": b.get("trap_matrix", {}), "traps_held": b.get("traps_resisted"), "trap_runs": b.get("traps"),
        "distinct": b.get("distinct_decisions", {}), "stable": b.get("stable_runs"), "repeats": b.get("repeat_runs"),
        "runs": b.get("runs"), "runs_clean": b.get("runs_all_passed"), "coverage": c.get("coverage"),
        "excess": c.get("excess_ratio"), "page_loads": c.get("page_loads"),
        "demonstrated": b.get("demonstrated"), "attested": b.get("attested"),
    }


def _decision(out, metered) -> str:
    """What a run decided, as the benchmark compares repeats: the fields pulled and the manifest's structure."""

    from compliance.benchmark import manifest_structure
    key = [sorted(map(list, metered.pulled)), sorted([k, repr(v)] for k, v in manifest_structure(out.run).items())]
    return hashlib.sha256(json.dumps(key).encode("utf-8")).hexdigest()[:12]


def _run(out, shaped, task, col_of, cat, index, verify, register, run_all, policy, export_audit, observed,
         generated) -> dict:
    """One run of one technique on one job: what it read, the rules' verdicts, its claims, its export, its erasure."""

    read = set()
    rows_n = 0
    for layer_rows in out.rows.values():
        rows_n = max(rows_n, len(layer_rows))
        for r in layer_rows:
            m = r.get("mrn") or r.get("subject_mrn")
            if m in index:
                read.add(index[m])
    keys = sorted({f"{lv}/{f}" for lv, layer_rows in out.rows.items() for r in layer_rows for f in r if f"{lv}/{f}" in col_of},
                  key=lambda k: col_of[k])
    allowed = {c.value for c in policy[task.purpose].allowed_categories}
    needed = {f"{lf.layer.value}/{f}" for lf in task.needed for f in lf.fields}
    report = run_all(out.run, out.records)
    a = export_audit(out, shaped)
    token = ""
    for msgs in shaped.hl7.values():
        seg = next((s for m in msgs for s in m.split("\r") if s.startswith("PID")), "")
        if seg:
            token = (re.search(r"PSN-[0-9a-f]+", seg) or [""])[0] if shaped.pseudonymised else ""
            break
    days = out.run.retention_days
    claims = verify(out.run, register, observed).claims
    lb = out.run.lawful_basis
    return {
        "patients": sorted(read), "named": bool(read), "rows": rows_n,
        "cols": [col_of[k] for k in keys],
        "oos": [col_of[k] for k in keys if cat[k.split("/")[0]].get(k.split("/")[1]) not in allowed],
        "needed": len(needed), "hit": len(needed & set(keys)),
        "missed": sorted(col_of[k] for k in needed - set(keys) if k in col_of),
        "rules": {r.rule_id: [r.status.value, round(r.score, 3)] for r in report.results},
        "score": round(report.compliance_score, 3),
        "claims": [{"control": c.control, "declared": c.declared, "ok": c.substantiated, "basis": c.basis, "note": c.note}
                   for c in claims],
        "specified": out.run.purpose_specified,
        "scope": [out.run.scope.records_pulled, out.run.scope.records_necessary] if out.run.scope else None,
        "broken": sorted(r.rule_id for r in report.results if r.status.value == "fail"),
        "basis": lb.reference.split(" -- ")[0] if lb and lb.reference else "",
        "onward": [u.value if hasattr(u, "value") else str(u) for u in (out.run.secondary_uses or [])],
        "export": {"kind": "raw" if a.leaked > 0 else "tok" if token else "none", "token": token, "leaked": a.leaked,
                   "identifiers": a.identifier_values, "k": a.k, "generalised": a.generalised,
                   "messages": shaped.counts()["hl7_messages"], "resources": shaped.counts()["fhir_resources"]},
        "retention": days, "erase": (generated + timedelta(days=days)).isoformat() if days else None,
        "mechanism": (out.run.deletion_mechanism or "").split(" -- ")[0],
    }


def _copy(out, followed, key, col_of, cat, show, scoped=None) -> dict:
    """The followed patient's fields as the export carried them: each value after the export's own transform
    (``pseudonymise_row`` then ``generalise_row`` when the manifest declares pseudonymisation), and how it left."""

    from compliance.pseudonymise import QUASI_IDENTIFIERS, direct_identifier_fields, generalise_row, pseudonymise_row
    from interop.layers import HISLayer
    pseud = out.run.security.identifiers_pseudonymised
    fields: dict[int, dict] = {}
    found = False
    for layer_value, rows in out.rows.items():
        layer = HISLayer(layer_value)
        # every fetch filtered to this patient (the meter saw it): rows that dropped the record number are still theirs
        mine = [r for r in rows if (r.get("mrn") or r.get("subject_mrn")) == followed
                or (scoped == followed and not (r.get("mrn") or r.get("subject_mrn")))]
        if not mine:
            continue
        found = True
        raw = mine[0]
        row = generalise_row(pseudonymise_row(layer, raw, key=key)) if pseud else raw
        direct = set(direct_identifier_fields(layer))
        for f, v in row.items():
            i = col_of.get(f"{layer_value}/{f}")
            if i is None:
                continue
            c = cat[layer_value].get(f)
            if pseud and f in direct:
                how = "token"
            elif pseud and f in QUASI_IDENTIFIERS and v != raw.get(f):
                how = "generalised"
            elif (c in ("direct_identifier", "contact", "quasi_identifier") and f != "sex") or f == "insurance_policy_no":
                how = "raw"
            else:
                how = "as read"
            if v in (None, ""):
                shown = ""
            elif how == "raw" or f == "attending_clinician":      # masked as the record itself is masked
                shown = str(v1._mask_value(f, c, v))
            else:
                shown = show(f"{v:,.2f}" if isinstance(v, float) else str(v))
            fields[i] = {"value": shown, "how": how}
    return {"found": found, "pseudonymised": bool(pseud), "fields": fields}


def _left(out, shaped, followed, show) -> dict:
    """The HL7 v2 messages about the followed patient, as the export carried them (raw values masked)."""

    mine, others = [], 0
    unnamed = True
    for layer, msgs in shaped.hl7.items():
        rows = out.rows.get(layer, [])
        for i, msg in enumerate(msgs):
            r = rows[i] if i < len(rows) else {}
            who = r.get("mrn") or r.get("subject_mrn")
            if who is not None:
                unnamed = False
            if who == followed or (who is None and i == 0 and len(rows) == 1):
                mine.append([show(seg) for seg in msg.split("\r") if seg])
            else:
                others += 1
    if unnamed and not mine:                  # a run that dropped the record number: its first message stands in
        for layer, msgs in shaped.hl7.items():
            if msgs:
                mine.append([show(seg) for seg in msgs[0].split("\r") if seg])
                others -= 1
                break
    return {"hl7": mine, "hl7_others": max(others, 0), "hl7_unnamed": unnamed}


def _custody(out, shaped, metered, name, log, tmp: Path, tid, job, recorded_at, meta, fields_by_layer,
             purge_expired, suffix) -> dict:
    """The run's audit entries and retention record, written by the real code to a temporary log and folder."""

    here = tmp / re.sub(r"[^a-z0-9]+", "-", f"{tid}-{job}".lower())
    with _clock(recorded_at):
        log.extraction(out.run, technique=name, records=len(out.records), fields=fields_by_layer(metered.pulled),
                       source="hospital portal (fixture)", rows=out.rows, scoped_to=metered.subject_scope(),
                       account=meta.get("account") or "", authorisation=meta.get("authorisation") or "")
        written = shaped.to_files(here, audit=log, key_dir=tmp / "keys")
    sidecar = None
    side = next(iter(here.glob(f"*{suffix}")), None) if here.exists() else None
    if side is not None:
        s = json.loads(side.read_text(encoding="utf-8"))
        s["files"] = [Path(f).name for f in s.get("files", [])]
        s["key_file"] = Path(s["key_file"]).name if s.get("key_file") else ""
        sidecar = s
    due = None
    if sidecar and sidecar.get("delete_after"):
        due = datetime.fromisoformat(sidecar["delete_after"].replace("Z", "+00:00"))
    return {"files": [p.name for p in written], "sidecar": sidecar, "_purge": (due, here, out.run.run_id) if due else None,
            "_run_id": out.run.run_id}


def _purge_in_date_order(runs: list[dict], log, purge_expired) -> None:
    """Every export is written on the run date; each purge then runs on its own erase date, in date order."""

    for due, here, _ in sorted((r["_purge"] for r in runs if r.get("_purge")), key=lambda x: (x[0], x[2])):
        with _clock(due):
            purge_expired(here, now=due, audit=log)


def _events(log) -> dict[str, list[dict]]:
    """The log's lines per run, each with its own hash (what the next line's prev_sha256 holds)."""

    out: dict[str, list[dict]] = {}
    lines = [l for l in log.path.read_text(encoding="utf-8").splitlines() if l.strip()]
    for seq, line in enumerate(lines):
        d = json.loads(line)
        d["seq"] = seq                                                   # its place in the shared log
        d["at"] = d["at"][:19].replace("T", " ")
        d = {k: v for k, v in d.items() if v not in ("", [], {}, None, 0, False) or k in ("event", "scoped")}
        d["sha256"] = hashlib.sha256(line.encode("utf-8")).hexdigest()
        out.setdefault(d["run_id"], []).append(d)
    return out


if __name__ == "__main__":
    data, secrets = record()
    t = data["techniques"]["ours"]["jobs"]["patient-summary"][0]
    print(json.dumps({k: t[k] for k in ("cols", "score", "export", "retention", "erase", "pages")}, indent=1))
    print(json.dumps(t["audit"], indent=1)[:2000])
    print(json.dumps(t["sidecar"], indent=1))
    print(t["hl7"])
    b = data["techniques"]["base"]["jobs"]["patient-summary"][0]
    print(b["hl7"], b["hl7_others"], b["audit"][-1])
    print(len(json.dumps(data)) / 1024, "KB")
