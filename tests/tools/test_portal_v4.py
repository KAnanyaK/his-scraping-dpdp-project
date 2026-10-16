"""The Portal v4 (docs/review/portal-v4.html): each technique specified as a component datasheet.

Pinned here: the builder refuses a page that would carry a raw identifier; the
absolute maximum ratings are the purpose policy's own limits; every
characteristic's MIN / TYP / MAX is the spread of the runs it summarises, and a
row is marked exceeded exactly when a run goes past a rating; the device
comparison's repeat counts are the benchmark's for a model and five identical
runs for ours and the baseline; the typical curves are the committed scale run;
and the committed page carries its data and its fonts, and no link to the Report.
"""

from __future__ import annotations

import json
import re
import statistics

import pytest

from tools import build_portal_app as v1
from tools import build_portal_v4 as v4
from tools.page_kit import REVIEW_DIR

PAGE = REVIEW_DIR / "portal-v4.html"


def _data(html: str) -> dict:
    return json.loads(re.search(r'<script type="application/json" id="datasheet-data">(.*?)</script>', html, re.S).group(1))


@pytest.fixture(scope="module")
def built():
    data, secrets = v4.payload()
    return data, secrets, v4.render(data)


def test_the_page_refuses_a_raw_identifier(built):
    data, secrets, html = built
    v1.check(html, secrets)
    with pytest.raises(v1.PortalLeak):
        v1.check(html + next(iter(secrets)), secrets)


def test_the_ratings_are_the_purpose_policy(built):
    from compliance.policy import PURPOSE_POLICY
    data, _, _ = built
    for job in data["jobs"]:
        scope = next(s for p, s in PURPOSE_POLICY.items() if p.value == job["purpose"])
        ratings = {r["id"]: r for r in data["sheets"]["ours"]["spec"][job["id"]]["ratings"]}
        assert ratings["retention"]["max"] == scope.max_retention_days and ratings["retention"]["rule"] == "SL-01"
        assert ratings["oos"]["max"] == 0 and ratings["onward"]["max"] == 0
        assert ("raw" in ratings) == scope.requires_pseudonymised_identifiers
        assert ("others" in ratings) == job["single"]


def test_every_characteristic_is_the_spread_of_its_runs(built):
    data, _, _ = built
    subject = data["patient"]["index"]
    for tid, t in data["techniques"].items():
        assert len(next(iter(t["jobs"].values()))) == 5, tid          # five runs, recorded or run here
        for job in data["jobs"]:
            runs = t["jobs"][job["id"]]
            chars = {c["id"]: c for c in data["sheets"][tid]["spec"][job["id"]]["chars"]}
            fields = sorted(len(r["cols"]) for r in runs)
            assert chars["fields"]["spread"] == [fields[0], fields[2], fields[-1]], (tid, job["id"])
            assert abs(chars["score"]["spread"][1] - statistics.mean(r["score"] for r in runs)) < 0.0015
            oos_over = max(len(r["oos"]) for r in runs) > 0
            assert chars["oos"]["over"] == oos_over, (tid, job["id"])
            ret_over = any(r["retention"] is None or r["retention"] > job["ceiling"] for r in runs)
            assert chars["retention"]["over"] == ret_over, (tid, job["id"])
            assert chars["pages"]["spread"][1] == runs[0]["pages"]
            if job["single"]:
                others = max(len([p for p in r["patients"] if p != subject]) for r in runs)
                assert chars["others"]["over"] == (others > 0)
    # the reference is inside every rating on every job, and its runs agree: MIN = TYP = MAX
    for job in data["jobs"]:
        for c in data["sheets"]["ours"]["spec"][job["id"]]["chars"]:
            assert not c["over"], (job["id"], c["id"])
            if c["spread"][0] is not None:
                assert c["spread"][0] == c["spread"][1] == c["spread"][2], (job["id"], c["id"])


def test_the_comparison_matches_the_benchmark(built):
    data, _, _ = built
    for tid, sheet in data["sheets"].items():
        t, row = data["techniques"][tid], sheet["row"]
        if t["sampled"]:
            assert row["stable"] == [t["bench"]["stable"], t["bench"]["repeats"]], tid
            assert sheet["stability"]["distinct"] == t["bench"]["distinct"], tid
        else:
            assert row["stable"] == [16, 16], tid                       # five identical runs on four jobs
        assert row["coverage"] == t["bench"]["coverage"] and row["pages"] == t["bench"]["page_loads"]


def test_the_curves_are_the_scale_run(built):
    data, _, _ = built
    committed = json.loads(v4.SCALE.read_text(encoding="utf-8"))["rows"]
    assert data["scale"] == committed
    assert all(r["ours"]["page_loads"] < r["baseline"]["page_loads"] for r in committed)


def test_the_committed_page_carries_its_data_and_fonts():
    assert PAGE.exists(), "build it with python tools/build_portal_v4.py"
    html = PAGE.read_text(encoding="utf-8")
    assert html.count("data:font/woff2;base64,") == 5
    assert "report.html" not in html
    data = _data(html)
    for key in ("columns", "jobs", "techniques", "sheets", "sweeps", "scale", "register"):
        assert data.get(key), key
