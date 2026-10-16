"""The Portal, version 4: each technique specified as a component datasheet, ``docs/review/portal-v4.html``.

    python tools/build_portal_v4.py             # from the staged parts in build/review-parts/
    python tools/build_review_pages.py          # builds the parts, the Report and every Portal

A technique is a component, so specify it. Each technique -- ours (the reference
design), an AI model at a briefing, the baseline -- gets a four-page datasheet:
a front page (features, applications, the pin configuration of the 34 fields with
the pins this part connects for the chosen job, a device comparison table),
specifications (absolute maximum ratings = the job's purpose policy, each with
the rule that enforces it; recommended operating conditions = the job's expert
field list; characteristics MIN / TYP / MAX over five runs), typical
characteristics (curves) and application information (the manifest as a register
map, the export as the package, ordering options = the briefings, revision history).

Every figure is the shared record (``tools/portal_record.py``): the recorded run
replayed by the project's own code. A model's five runs are its recorded samples;
ours and the baseline are run here five times, which is how MIN = TYP = MAX is
shown rather than claimed. The page-load curves are the committed scale run
(``docs/benchmark_results/scale.json``). The builder audits its own output with
version 1's audit: no raw identifier, contact detail or quasi-identifier.
"""

from __future__ import annotations

import base64
import json
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for p in (ROOT, ROOT / "src", ROOT / "scripts"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from tools import build_portal_app as v1                                    # noqa: E402
from tools.page_kit import REVIEW_DIR, write                                # noqa: E402
from tools.portal_record import record                                      # noqa: E402

HERE = ROOT / "tools" / "portal_v4"
OUT = REVIEW_DIR / "portal-v4.html"
SHELL = HERE / "portal.html"
CSS = HERE / "portal.css"
SCRIPTS = ["datasheet.js"]
FONTS = {"Barlow": {400: "Barlow-latin-400.woff2", 500: "Barlow-latin-500.woff2", 600: "Barlow-latin-600.woff2"},
         "Barlow Semi Condensed": {400: "BarlowSemiCondensed-latin-400.woff2", 500: "BarlowSemiCondensed-latin-500.woff2"}}
SCALE = ROOT / "docs" / "benchmark_results" / "scale.json"
RUNS = 5


# ------------------------------------------------------------------ the specification of one part on one job

def _spread(values: list, *, mean: bool = False) -> list | None:
    """[MIN, TYP, MAX] over the runs; TYP is the median (the mean for a score, as the benchmark reports it).
    ``None`` (nothing declared) sorts above every number, so a run that declared no retention is the MAX."""

    if not values:
        return None
    nums = [v for v in values if v is not None]
    if not nums:
        return [None, None, None]
    lo = min(nums) if len(nums) == len(values) else min(nums)
    hi = None if len(nums) < len(values) else max(nums)
    if mean:
        typ = round(statistics.mean(nums), 3)
    else:
        ordered = sorted(values, key=lambda v: float("inf") if v is None else v)
        typ = ordered[(len(ordered) - 1) // 2]
    return [lo, typ, hi]


def _ratings(job: dict, policy: dict) -> list[dict]:
    """The job's absolute maximum ratings: the purpose policy's limits, each with the rule that enforces it."""

    not_allowed = [c for c in policy["categories"] if c not in job["allowed"]]
    out = [{"id": "oos", "param": "Fields outside the purpose", "sym": ["N", "oos"], "max": 0, "unit": "fields", "rule": "DM-01",
            "note": "not allowed: " + ", ".join(policy["labels"][c].lower() for c in not_allowed)}]
    if job["single"]:
        out.append({"id": "others", "param": "Other patients' records", "sym": ["N", "other"], "max": 0, "unit": "patients",
                    "rule": "DM-01", "note": "the job is about one patient"})
        out.append({"id": "records", "param": "Records read", "sym": ["R", "read"], "max": job["necessary"], "unit": "records",
                    "rule": "DM-01", "note": "the patient's own, in the modules the job needs"})
    out.append({"id": "retention", "param": "Retention", "sym": ["t", "ret"], "max": job["ceiling"], "unit": "days",
                "rule": "SL-01", "note": "must be declared"})
    if job["pseudonymise"]:
        out.append({"id": "raw", "param": "Raw direct identifiers exported", "sym": ["N", "raw"], "max": 0, "unit": "values",
                    "rule": "SS-01", "note": "the purpose requires pseudonymised identifiers"})
    out.append({"id": "onward", "param": "Onward uses beyond the purpose", "sym": ["N", "onward"], "max": 0, "unit": "uses",
                "rule": "PL-01", "note": ""})
    return out


def _characteristics(runs: list[dict], job: dict, subject: int, ratings: list[dict], distinct: int) -> list[dict]:
    limit = {r["id"]: r["max"] for r in ratings}
    held = [sum(1 for v in r["rules"].values() if v[0] == "pass") for r in runs]
    applicable = max(sum(1 for v in r["rules"].values() if v[0] != "not_applicable") for r in runs)
    rows = [
        ("fields", "Fields read", ["N", "read"], "of 34", [len(r["cols"]) for r in runs]),
        ("needed", "Needed fields obtained", ["C", "need"], "%", [round(100 * r["hit"] / r["needed"]) for r in runs]),
        ("beyond", "Fields beyond the need", ["N", "extra"], "fields", [len(r["cols"]) - r["hit"] for r in runs]),
        ("oos", "Fields outside the purpose", ["N", "oos"], "fields", [len(r["oos"]) for r in runs]),
        ("others", "Other patients named", ["N", "other"], "patients",
         [len([p for p in r["patients"] if p != subject]) for r in runs] if job["single"] else None),
        ("records", "Records read", ["R", "read"], "records",
         [r["scope"][0] if r.get("scope") else None for r in runs] if job["single"] else None),
        ("retention", "Retention declared", ["t", "ret"], "days", [r["retention"] for r in runs]),
        ("onward", "Onward uses", ["N", "onward"], "uses", [len(r["onward"]) for r in runs]),
        ("raw", "Raw identifiers exported", ["N", "raw"], "values", [r["export"]["leaked"] for r in runs]),
        ("held", "Rules held", ["N", "held"], f"of {applicable}", held),
        ("score", "Compliance score", ["S", ""], "", [r["score"] for r in runs]),
    ]
    out = []
    for rid, param, sym, unit, values in rows:
        if values is None:
            continue
        spread = _spread(values, mean=(rid == "score"))
        lim = limit.get(rid, applicable if rid == "held" else None)

        def beyond(v, rid=rid, lim=lim):
            if lim is None:
                return False
            if rid == "held":
                return v is not None and v < lim
            if rid == "retention":                    # None: a run declared no retention
                return v is None or v > lim
            return v is not None and v > lim
        cells = [beyond(v) for v in spread] if spread else [False, False, False]
        over = any(beyond(v) for v in values) if lim is not None else False
        row = {"id": rid, "param": param, "sym": sym, "unit": unit, "spread": spread, "limit": lim, "over": over,
               "cells": cells, "runs": values}
        if rid == "held":
            row["broken"] = sorted({b for r in runs for b in r.get("broken", [])})
        out.append(row)
    out.append({"id": "pages", "param": "Page loads", "sym": ["N", "load"], "unit": "loads", "spread": [None, runs[0]["pages"], None],
                "limit": None, "over": False, "runs": [runs[0]["pages"]], "note": 2})
    out.append({"id": "decisions", "param": "Distinct decisions", "sym": ["N", "dec"], "unit": f"in {len(runs)} runs",
                "spread": [None, distinct, None], "limit": None, "over": False, "runs": [distinct]})
    return out


def _stability(t: dict) -> dict:
    """Over the four jobs: how many repeats gave the first run's decision, and how many decisions per job."""

    stable = repeats = 0
    distinct = {}
    for job, runs in t["jobs"].items():
        keys = [r["decision"] for r in runs]
        distinct[job] = len(set(keys))
        stable += sum(1 for k in keys[1:] if k == keys[0])
        repeats += len(keys) - 1
    return {"stable": stable, "repeats": repeats, "distinct": distinct}


def _comparison_row(t: dict, stab: dict) -> dict:
    b = t["bench"]
    return {"id": t["id"], "kind": t["kind"], "model": t["model"], "briefing": t["briefing"],
            "coverage": b.get("coverage"), "excess": b.get("excess"), "traps": [b.get("traps_held"), b.get("trap_runs")],
            "stable": [stab["stable"], stab["repeats"]], "pages": b.get("page_loads"), "score": b.get("score"),
            "runs_clean": [b.get("runs_clean"), b.get("runs")], "sampled": t["sampled"]}


def _sweep(data: dict, model: str) -> dict:
    """A model's typical characteristics: per job, the five-run mean score and needed-field share at each briefing."""

    out = {}
    for b in ("unaided", "informed", "policy"):
        t = data["techniques"].get(f"{model}|{b}")
        if not t:
            continue
        out[b] = {job: {"score": round(statistics.mean(r["score"] for r in runs), 3),
                        "needed": round(100 * sum(r["hit"] for r in runs) / sum(r["needed"] for r in runs), 1)}
                  for job, runs in t["jobs"].items()}
    return out


def payload() -> tuple[dict, set[str]]:
    from compliance.policy import PURPOSE_POLICY
    data, secrets = record(deterministic_repeats=RUNS)
    labels = {c["id"]: c["label"] for c in data["categories"]}
    policy = {"categories": [c["id"] for c in data["categories"]], "labels": labels}
    for job in data["jobs"]:
        job["pseudonymise"] = next(s.requires_pseudonymised_identifiers for p, s in PURPOSE_POLICY.items() if p.value == job["purpose"])
        scoped = [r["scope"] for t in data["techniques"].values() for r in t["jobs"][job["id"]] if r.get("scope")]
        job["necessary"] = scoped[0][1] if scoped else None
    subject = data["patient"]["index"]

    sheets: dict[str, dict] = {}
    for tid, t in data["techniques"].items():
        stab = _stability(t)
        spec = {}
        for job in data["jobs"]:
            ratings = _ratings(job, policy)
            spec[job["id"]] = {"ratings": ratings,
                               "chars": _characteristics(t["jobs"][job["id"]], job, subject, ratings, stab["distinct"][job["id"]])}
        sheets[tid] = {"spec": spec, "stability": stab, "row": _comparison_row(t, stab)}
    data["sheets"] = sheets
    data["sweeps"] = {m["id"]: _sweep(data, m["id"]) for m in data["models"]}
    data["scale"] = json.loads(SCALE.read_text(encoding="utf-8"))["rows"] if SCALE.exists() else []
    data["runs_here"] = RUNS
    # The page needs the first run's objects and every run's summary; drop what no datasheet page shows.
    for t in data["techniques"].values():
        for runs in t["jobs"].values():
            for r in runs:
                for k in ("hl7", "visits", "audit", "claims_all"):
                    if r is not runs[0] and k in r:
                        r.pop(k, None)
    return data, secrets


def render(data: dict) -> str:
    html = SHELL.read_text(encoding="utf-8")
    faces = []
    for family, weights in FONTS.items():
        for weight, name in weights.items():
            b64 = base64.b64encode((HERE / "fonts" / name).read_bytes()).decode("ascii")
            faces.append(f"@font-face {{ font-family: \"{family}\"; src: url(data:font/woff2;base64,{b64}) format('woff2'); "
                         f"font-weight: {weight}; font-style: normal; font-display: block; }}")
    css = CSS.read_text(encoding="utf-8").replace("/*__FONTS__*/", "\n".join(faces))
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
    print(f"  wrote {out.relative_to(ROOT)}  (the Portal v4, {size:.1f} MB); audit: no raw identifier on the page")
    return 0


if __name__ == "__main__":
    sys.exit(main())
