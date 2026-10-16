"""The Portal: the recorded pipeline run as a metro map, ``docs/review/portal-v1.html``.

    python tools/build_portal_app.py            # from the staged parts in build/review-parts/
    python tools/build_review_pages.py          # builds the parts, the Report and this

Three straight lines -- ours, an AI model, the baseline -- run through the same
stations, Hospital to Erased. Between Acquire and Extract each calls at one square
per page load and its train moves on only as they fill: ours is the express, the
baseline the all-stations service. A line with no erase date runs off the map.
The presenter steps it station by station; a passenger ticket follows one
patient's record.

Every number replays an artefact. The page loads, scores, rules and traps come
from the parts the demo builders already write and audit
(``build/review-parts/``). Two things no part carries are computed here by the
project's own code on the *same* synthetic source the portal served (20 records
a module, seed 42), so the map shows one hospital: what each technique's pull
holds (fields by category, patients read) and what the pipeline's export stage
makes of it (pseudonymised or raw, the token, the retention and its erase date).

The builder audits its own output, like the others: no raw direct identifier,
contact detail or quasi-identifier of any record may appear anywhere in the
file; the one patient the ticket follows is shown masked.
"""

from __future__ import annotations

import json
import re
import sys
from datetime import date, timedelta
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
for p in (ROOT, ROOT / "src", ROOT / "scripts"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from tools.page_kit import REVIEW_DIR, REPORT, part_data, part_path, write   # noqa: E402

HERE = ROOT / "tools" / "portal"
OUT = REVIEW_DIR / "portal-v1.html"
SHELL = HERE / "portal.html"
CSS = HERE / "portal.css"
SCRIPTS = ["kit.js", "map.js", "main.js"]
PARTS = ("portal", "rules")
RECORDS, SEED = 20, 42
BRIEFINGS = {"task + register": "unaided", "told the Act": "informed", "told the policy": "policy"}
# The tokens a page shows are made with fixed display keys (one per technique, as each export has its own),
# so a rebuild does not churn them.
# An export made by the pipeline still gets a fresh random secret (interop.normalise).
DISPLAY_KEY = "portal-display-key"
DIRECT = ("direct_identifier", "contact", "quasi_identifier")


class PortalLeak(RuntimeError):
    """The built Portal would carry a value it must not show."""


# ------------------------------------------------------------------ the parts

def _parts() -> dict[str, dict]:
    """Each part's data block: the staged part where this machine built one, else the committed Report's."""

    from tools.build_report import report_data
    committed = report_data(REPORT)
    out: dict[str, dict] = {}
    for key in PARTS:
        path = part_path(key)
        data = part_data(path.read_text(encoding="utf-8")) if path.exists() else {}
        out[key] = data or committed.get(key) or {}
        if not out[key]:
            raise SystemExit(f"no data for '{key}': run python tools/build_review_pages.py first")
    return out


def _tech_id(name: str) -> tuple[str, str | None, str | None]:
    """'ai model: claude-opus-5-5 (told the policy)' -> ('claude-opus-5-5|policy', model, briefing)."""

    if "(ours)" in name:
        return "ours", None, None
    if "baseline" in name:
        return "base", None, None
    m = re.match(r"ai model: (\S+) \((.+)\)$", name)
    if not m:
        raise ValueError(f"unexpected technique name {name!r}")
    model, briefing = m.group(1), BRIEFINGS[m.group(2)]
    return f"{model}|{briefing}", model, briefing


# ------------------------------------------------------------------ masking

def _mask_value(field: str, cat: str | None, value: Any) -> Any:
    """What the replica shows for one cell: identifiers and contact details masked, quasi-identifiers coarsened."""

    from compliance.access_report import mask
    if value is None or value == "":
        return value
    v = str(value)
    if field in ("mrn", "subject_mrn"):
        return mask(v)
    if field == "attending_clinician":            # a person too, and a surname can be a patient's
        return " ".join(w if w.endswith(".") else w[0] + "•" * 3 for w in v.split())
    if field == "full_name":
        return " ".join(w[0] + "•" * 4 for w in v.split())
    if field == "phone":
        return v[:4] + "•" * 6 + v[-2:]
    if field == "email":
        return v[0] + "•" * 5 + "@••••"
    if field == "street_address":
        return "•" * 8
    if field == "date_of_birth":
        return v[:4] + "-••-••"
    if field == "pincode":
        return v[:3] + "•••"
    if field == "insurance_policy_no":
        return mask(v)
    if cat in ("direct_identifier", "contact"):
        return "•" * 6
    return value


def _variants(value: Any) -> set[str]:
    """The shapes a raw value can take on a page or in an export: whole, its words, its digits."""

    if value in (None, ""):
        return set()
    v = str(value)
    out = {v} if len(v) >= 4 else set()
    out |= {w for w in re.split(r"[\s,./@^]+", v) if len(w) >= 4 and not w.isdigit()}
    digits = re.sub(r"\D", "", v)
    if len(digits) >= 6:
        out.add(digits)
    return out


# ------------------------------------------------------------------ the plant, computed on the portal's own source

def _plant(portal: dict) -> dict:
    """The replica's records, and what stages 4-5 make of every technique's pull, on the portal's source."""

    from compliance.access_report import mask
    from compliance.benchmark import bind_subject
    from compliance.purpose_matrix import score_across_purposes
    from data_synthetic.catalogue import FIELD_CATALOGUE
    from extraction.adapters.mock_his import MockHISDataSource
    from extraction.metering import MeteredSource
    from extraction.techniques import default_techniques
    from interop.layers import HISLayer
    from interop.normalise import audit, normalise
    from run_pipeline import TASKS
    from tools.mock_portal import MODULE_BLURBS
    from tools.mock_portal.layouts import LAYOUTS, V2_FIELD_ALIASES

    meta = portal["meta"]
    records, seed = meta.get("records", RECORDS), meta.get("seed", SEED)
    source = MockHISDataSource(records_per_layer=records, seed=seed)
    cat = {l.value: {f: c.value for f, c in fields.items()} for l, fields in FIELD_CATALOGUE.items()}

    # Every value the page must never show: identifiers, contact details, quasi-identifiers (bar sex).
    secrets: set[str] = set()
    rows: dict[str, list[dict]] = {}
    for layer in source.layers():
        raw = list(source.fetch(layer))
        shown = []
        for r in raw:
            shown.append({f: _mask_value(f, cat[layer.value].get(f), v) for f, v in r.items()})
            for f, v in r.items():
                if (cat[layer.value].get(f) in DIRECT and f != "sex") or f == "insurance_policy_no":
                    secrets |= _variants(v)
        rows[layer.value] = shown
    register = [r["mrn"] for r in source.fetch(HISLayer.PATIENT_ADMINISTRATION, fields=["mrn"])]
    index = {m: i for i, m in enumerate(register)}

    layouts = {}
    for name, lay in LAYOUTS.items():
        layouts[name] = {
            "prefix": lay.prefix, "record": lay.record_segment, "labels": dict(lay.labels),
            "modules": [{"slug": m.slug, "title": m.title, "layer": m.layer.value, "blurb": MODULE_BLURBS.get(m.layer, ""),
                         "columns": list(m.list_columns), "record_fields": list(m.record_fields) if m.record_fields else None,
                         "list_actions": list(m.list_actions), "record_actions": list(m.record_actions)}
                        for m in lay.modules if rows.get(m.layer.value)],
        }
    layouts["v2"]["aliases"] = dict(V2_FIELD_ALIASES)

    # Each technique's pull of each job (the first recorded sample, as the portal replays), and the export of each.
    tasks = bind_subject(TASKS, source)
    generated = date.fromisoformat(meta.get("generated") or date.today().isoformat())
    ledger: dict[str, dict] = {}
    export: dict[str, dict] = {}
    for technique in default_techniques(tasks, source):
        tid = _tech_id(technique.name)[0]
        ledger[tid] = {}
        for task in tasks:
            out = technique.extract(MeteredSource(source), task)
            read = set()
            for layer_rows in out.rows.values():
                for r in layer_rows:
                    m = r.get("mrn") or r.get("subject_mrn")
                    if m in index:
                        read.add(index[m])
            fields = {lv: sorted({f for r in layer_rows for f in r}) for lv, layer_rows in out.rows.items() if layer_rows}
            ledger[tid][task.task_id] = {
                "records": len(out.records), "patients": sorted(read),
                "fields": fields, "retention": out.run.retention_days,
                "onward": [u.value if hasattr(u, "value") else str(u) for u in (out.run.secondary_uses or [])],
            }
            if task.task_id != "patient-summary":
                continue
            shaped = normalise(out, key=f"{DISPLAY_KEY}:{tid}")      # each export its own key, as in the pipeline
            a = audit(out, shaped)
            matrix = score_across_purposes(out.run, out.records)
            pid = ""
            msgs = shaped.hl7.get(HISLayer.PATIENT_ADMINISTRATION.value) or []
            if msgs:
                pid = next((seg for seg in msgs[0].split("\r") if seg.startswith("PID")), "")
                # Every raw value, in any of the shapes an export gives it (a name's words, a date's digits), masked.
                for value in sorted(secrets, key=len, reverse=True):
                    if value in pid:
                        pid = pid.replace(value, value[0] + "•" * (len(value) - 1))
            days = out.run.retention_days
            export[tid] = {
                "counts": shaped.counts(), "pseudonymised": shaped.pseudonymised,
                "leaked": a.leaked, "identifiers": a.identifier_values, "k": a.k, "generalised": a.generalised,
                "audit": a.one_line(), "pid": pid, "records": len(out.records),
                "patients": sorted(read),
                "categories": sorted({cat[lv].get(f) for lv, fs in fields.items() for f in fs if cat[lv].get(f)}),
                "purposes": [{"purpose": v.purpose, "declared": v.is_declared_purpose, "score": round(v.compliance_score, 3),
                              "verdict": v.verdict(), "oos": v.out_of_scope_categories, "limit": v.retention_limit_days}
                             for v in matrix.verdicts],
                "retention": days, "erase_after": (generated + timedelta(days=days)).isoformat() if days else None,
                "mechanism": out.run.deletion_mechanism or "",
            }
    return {"rows": rows, "layouts": layouts, "categories": cat, "ledger": ledger, "export": export,
            "about": index.get(next(t.subject for t in tasks if t.single_subject)),
            "needed": {t.task_id: [f"{lf.layer.value}/{f}" for lf in t.needed for f in lf.fields] for t in TASKS},
            "secrets": secrets}


# ------------------------------------------------------------------ the payload

def payload() -> tuple[dict, set[str]]:
    parts = _parts()
    P, R = parts["portal"], parts["rules"]
    plant = _plant(P)
    secrets = plant.pop("secrets")

    cost = {row["technique"]: row for row in R.get("portal", [])}
    traced: dict[str, int] = {}
    techniques = []
    by_name = {t["name"]: _tech_id(t["name"])[0] for t in P["techniques"]}
    for v in P["visits"]:
        who = v["who"] if v["who"] in ("discover", "harness") else by_name[v["who"]]
        traced[who] = traced.get(who, 0) + 1
    for t in P["techniques"]:
        tid, model, briefing = _tech_id(t["name"])
        c = cost.get(t["name"], {})
        techniques.append({
            "id": tid, "name": t["name"], "kind": t["kind"], "model": model, "briefing": briefing,
            "score": t["score"], "pages": t["pages"], "traced": traced.get(tid, 0), "repeats": t["repeats"],
            "coverage": t["coverage"], "excess": t["excess"], "rules": t["rules"], "per_task": t["per_task"],
            "trap_runs": [c.get("traps_resisted"), c.get("traps")],
        })
    rows = plant["rows"]["patient_administration"]
    about = plant["about"]
    data = {
        "built": date.today().isoformat(),
        "meta": {k: P["meta"].get(k) for k in ("records", "generated", "tls", "account", "authorisation")},
        "tasks": P["tasks"], "needed": plant["needed"], "rule_ids": P["rule_ids"],
        "rule_titles": {r["id"]: r["title"] for r in _rule_titles()},
        "techniques": techniques, "headline": [by_name[n] for n in P["headline"] if n in by_name],
        "discover": traced.get("discover", 0), "harness": traced.get("harness", 0), "modules": len(P.get("modules") or []),
        "categories": plant["categories"], "ledger": plant["ledger"], "export": plant["export"],
        "purposes": _purposes(),
        "patient": {"index": about, "mrn": rows[about]["mrn"], "name": rows[about]["full_name"], "of": len(rows)},
    }
    return data, secrets


def _rule_titles() -> list[dict]:
    from compliance.rules import ALL_RULES
    return [{"id": r.rule_id, "title": r.title} for r in ALL_RULES]


def _purposes() -> dict:
    from compliance.policy import PURPOSE_POLICY
    return {purpose.value: {"allowed": sorted(c.value for c in scope.allowed_categories), "ceiling": scope.max_retention_days}
            for purpose, scope in PURPOSE_POLICY.items()}


# ------------------------------------------------------------------ render and audit

def render(data: dict) -> str:
    html = SHELL.read_text(encoding="utf-8")
    html = html.replace("/*__CSS__*/", CSS.read_text(encoding="utf-8"))
    html = html.replace("/*__JS__*/", "\n".join((HERE / name).read_text(encoding="utf-8") for name in SCRIPTS))
    # No "<" survives inside the data element, so nothing in a value can end the script early.
    blob = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c")
    return html.replace("/*__DATA__*/null", blob)


def check(html: str, secrets: set[str]) -> None:
    """Refuse a page that carries any raw identifier, contact detail or quasi-identifier of a record."""

    found = sorted(s for s in secrets if s in html)
    if found:
        raise PortalLeak(f"{len(found)} raw value(s) would reach the Portal, e.g. {found[0][:3]}...")


def build(out: Path = OUT) -> Path:
    data, secrets = payload()
    html = render(data)
    check(html, secrets)
    return write(out, html)


def main() -> int:
    out = build()
    size = out.stat().st_size / 1024 / 1024
    print(f"  wrote {out.relative_to(ROOT)}  (the Portal, {size:.1f} MB); audit: no raw identifier on the page")
    return 0


if __name__ == "__main__":
    sys.exit(main())
