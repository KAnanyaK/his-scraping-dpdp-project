"""The Portal v3 (docs/review/portal-v3.html): the recorded run, catalogued.

Pinned here: the builder refuses a page that would carry a raw identifier; every
figure on a plate traces to the shared record, and the record to the recorded run
-- the page loads are the portal's recorded visits, every replayed run scores
exactly what the benchmark reported for it (mean and range, per job), the audit
entries form an unbroken hash chain, the retention record's erase date is the
one the run declared; and the committed page carries its data and its font, and
no link to the Report.
"""

from __future__ import annotations

import hashlib
import json
import re

import pytest

from tools import build_portal_app as v1
from tools import build_portal_v3 as v3
from tools.page_kit import REVIEW_DIR

PAGE = REVIEW_DIR / "portal-v3.html"


def _data(html: str) -> dict:
    return json.loads(re.search(r'<script type="application/json" id="catalogue-data">(.*?)</script>', html, re.S).group(1))


@pytest.fixture(scope="module")
def built():
    data, secrets = v3.payload()
    return data, secrets, v3.render(data)


def test_the_page_refuses_a_raw_identifier(built):
    data, secrets, html = built
    v1.check(html, secrets)
    with pytest.raises(v1.PortalLeak):
        v1.check(html + next(iter(secrets)), secrets)
    assert all(re.fullmatch(r"MRN\*+\d{2}", m) for m in data["patients"])
    assert "•" in data["patient"]["name"]
    # the followed patient's record shows its identifiers masked
    cols = data["columns"]
    for c, v in zip(cols, data["patient"]["values"]):
        if c["field"] in ("mrn", "subject_mrn") and v:
            assert re.fullmatch(r"MRN\*+\d{2}", v)


def test_the_hospital_is_the_catalogue(built):
    from data_synthetic.catalogue import FIELD_CATALOGUE
    data, _, _ = built
    assert len(data["columns"]) == sum(len(f) for f in FIELD_CATALOGUE.values())
    assert sum(m["count"] for m in data["modules"]) == len(data["columns"])
    assert len(data["patients"]) == data["meta"]["records"] == data["patient"]["of"]
    for job in data["jobs"]:
        assert job["needed"] and all(n["why"] for n in job["needed"]), job["id"]


def test_every_plate_traces_to_the_recorded_run(built):
    data, _, _ = built
    parts = v1._parts()
    by_name = {t["name"]: v1._tech_id(t["name"])[0] for t in parts["portal"]["techniques"]}
    visits: dict[tuple[str, str], int] = {}
    for v in parts["portal"]["visits"]:
        if v["who"] in by_name and v.get("task") and v.get("sample", 0) == 0:
            key = (by_name[v["who"]], v["task"])
            visits[key] = visits.get(key, 0) + 1
    bench = {v1._tech_id(r["technique"])[0]: r for r in parts["rules"]["portal"]}
    rule_ids = {r["id"] for r in data["rules"]}
    for tid, t in data["techniques"].items():
        for job, runs in t["jobs"].items():
            first = runs[0]
            assert first["pages"] == visits.get((tid, job), 0) == len(first["visits"]), (tid, job)
            assert len(runs) == t["samples"]
            scores = [r["score"] for r in runs]
            b = bench[tid]
            # every replayed run scores what the benchmark reported: its mean and its range, per job
            assert abs(sum(scores) / len(scores) - b["per_task"][job]) < 0.0015, (tid, job)
            lo, hi = b["per_task_range"][job]
            assert abs(min(scores) - lo) < 0.0015 and abs(max(scores) - hi) < 0.0015, (tid, job)
            for r in runs:
                assert set(r["oos"]) <= set(r["cols"])
                assert set(r["rules"]) == rule_ids
                assert r["hit"] <= r["needed"]
    ours, base = data["techniques"]["ours"]["jobs"], data["techniques"]["base"]["jobs"]
    for job in data["jobs"]:
        o, b = ours[job["id"]][0], base[job["id"]][0]
        assert all(v[0] == "pass" for v in o["rules"].values()), job["id"]
        assert not any(v[0] == "pass" for v in b["rules"].values()), job["id"]
        assert o["export"]["leaked"] == 0 and o["export"]["kind"] == "tok" and o["erase"]
        assert b["export"]["kind"] == "raw" and b["erase"] is None
        assert not o["oos"] and o["hit"] == o["needed"]
        if job["single"]:
            assert o["patients"] == [data["patient"]["index"]]


def test_the_custody_record_is_the_real_chain(built):
    data, _, _ = built
    assert data["meta"]["chain_intact"]
    for tid, t in data["techniques"].items():
        for job, runs in t["jobs"].items():
            r = runs[0]
            events = [e["event"] for e in r["audit"]]
            assert events[:2] == ["extraction", "export"], (tid, job)
            # each line holds the hash of the line before: within a run, export follows extraction directly
            assert r["audit"][1]["prev_sha256"] == r["audit"][0]["sha256"]
            if r["erase"]:
                assert events[-1] == "purge" and r["audit"][-1]["at"].startswith(r["erase"])
                assert r["sidecar"]["delete_after"].startswith(r["erase"])
            else:
                assert "purge" not in events and r["sidecar"]["delete_after"] is None


def test_the_committed_page_carries_its_data_and_font():
    assert PAGE.exists(), "build it with python tools/build_portal_v3.py"
    html = PAGE.read_text(encoding="utf-8")
    assert "data:font/woff2;base64," in html
    assert "report.html" not in html
    data = _data(html)
    for key in ("columns", "modules", "jobs", "techniques", "patient", "rules", "register"):
        assert data.get(key), key
