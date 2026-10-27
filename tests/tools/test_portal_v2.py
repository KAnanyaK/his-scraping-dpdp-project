"""The Portal v2 (docs/review/portal-v2.html): the recorded run as a live data flow.

Pinned here: the builder refuses a page that would carry a raw identifier; the
hospital matrix is the catalogue (every field, every patient); each lane replays
one recorded run end to end -- its page loads are the recorded visits for that
job, the values it reads are its patients by its fields, and the rule verdicts
are the project's own rule engine on that run (ours holds all seven on every
job, the baseline none); and the committed page carries its data and its font.
"""

from __future__ import annotations

import json
import re

import pytest

from tools import build_portal_v2 as v2
from tools import build_portal_app as v1
from tools.page_kit import REVIEW_DIR

PAGE = REVIEW_DIR / "portal-v2.html"


def _data(html: str) -> dict:
    return json.loads(re.search(r'<script type="application/json" id="flow-data">(.*?)</script>', html, re.S).group(1))


@pytest.fixture(scope="module")
def built():
    data, secrets = v2.payload()
    return data, secrets, v2.render(data)


def test_the_page_refuses_a_raw_identifier(built):
    data, secrets, html = built
    v1.check(html, secrets)
    with pytest.raises(v1.PortalLeak):
        v1.check(html + next(iter(secrets)), secrets)
    assert re.fullmatch(r"MRN\*+\d{2}", data["patient"]["mrn"])
    assert "•" in data["patient"]["name"]


def test_the_hospital_is_the_catalogue(built):
    from data_synthetic.catalogue import FIELD_CATALOGUE
    data, _, _ = built
    assert len(data["columns"]) == sum(len(f) for f in FIELD_CATALOGUE.values())
    assert sum(m["count"] for m in data["modules"]) == len(data["columns"])
    assert data["patient"]["of"] == data["meta"]["records"]


def test_each_lane_replays_one_recorded_run(built):
    data, _, _ = built
    parts = v1._parts()["portal"]
    by_name = {t["name"]: v1._tech_id(t["name"])[0] for t in parts["techniques"]}
    visits: dict[tuple[str, str], int] = {}
    for v in parts["visits"]:
        if v["who"] in by_name and v.get("task"):
            key = (by_name[v["who"]], v["task"])
            visits[key] = visits.get(key, 0) + 1
    for tid, lane in data["lanes"].items():
        for job, j in lane["jobs"].items():
            assert j["pages"] == visits.get((tid, job), 0), (tid, job)
            assert set(j["oos"]) <= set(j["cols"])
            assert set(j["rules"]) == set(data["rule_ids"])
    ours, base = data["lanes"]["ours"]["jobs"], data["lanes"]["base"]["jobs"]
    for job in data["jobs"]:
        assert all(v[0] == "pass" for v in ours[job["id"]]["rules"].values()), job["id"]
        assert not any(v[0] == "pass" for v in base[job["id"]]["rules"].values()), job["id"]
        assert ours[job["id"]]["export"]["leaked"] == 0 and ours[job["id"]]["erase"]
        assert base[job["id"]]["erase"] is None and len(base[job["id"]]["rows"]) == data["patient"]["of"]
        if job["single"]:
            assert ours[job["id"]]["patients"] == [data["patient"]["index"]]
    # the stages between the rules and the export: ours pseudonymises and shapes every job, the baseline never pseudonymises
    for job in data["jobs"]:
        o, b = ours[job["id"]], base[job["id"]]
        assert o["pseud"]["on"] and o["pseud"]["generalised"] and not b["pseud"]["on"]
        assert o["shape"]["hl7"] > 0 and b["shape"]["hl7"] >= o["shape"]["hl7"]
    # every model can take every briefing on lane B
    for m in data["models"]:
        for b in ("unaided", "informed", "policy"):
            assert f"{m}|{b}" in data["lanes"]


def test_the_working_is_the_benchmarks_own_arithmetic(built):
    """The working panel shows each run's figures as the benchmark computes them.

    Each lane's run is scored with the record axis the harness fills in, so its score lies inside the benchmark's
    range for that job (and equals it for ours and the baseline, which do not sample); the score is the mean of
    the seven rule scores the panel sums; the per-job behaviour averages to the benchmark's behaviour score; and
    coverage and excess are the meter's.
    """

    data, _, _ = built
    bench = {v1._tech_id(r["technique"])[0]: r for r in v1._parts()["rules"]["portal"]}
    for tid, lane in data["lanes"].items():
        b = bench[tid]
        for job, j in lane["jobs"].items():
            lo, hi = b["per_task_range"].get(job, [b["per_task"][job]] * 2)
            assert lo - 1e-9 <= j["score"] <= hi + 1e-9, (tid, job, j["score"], lo, hi)
            if not lane["model"]:
                assert j["score"] == b["per_task"][job], (tid, job)
            scores = [j["rules"][r][1] for r in data["rule_ids"] if j["rules"][r][0] != "not_applicable"]
            assert abs(sum(scores) / len(scores) - j["score"]) <= 0.0015, (tid, job)
            assert set(j["why"]) == set(data["rule_ids"])
            c = j["cost"]
            assert c["matched"] == j["hit"] and c["needed"] == j["needed"]
            assert c["coverage"] == round(c["matched"] / c["needed"], 3) and c["excess"] == round(c["distinct"] / c["needed"], 3)
        behaviour = sum(j["behaviour"] for j in lane["jobs"].values()) / len(lane["jobs"])
        assert abs(behaviour - b["behaviour_score"]) <= 0.0015, (tid, behaviour, b["behaviour_score"])
        # an interval only where runs were sampled, as the report prints one
        assert bool(lane["wilson"]) == bool(lane["model"] and lane["traps"])


def test_the_trial_run_timed_the_runs_the_lanes_replay(built):
    """The timing under the lanes is of the same runs: each trial run made the page loads the recorded run made."""

    data, _, _ = built
    if not v2.TRIAL.exists():
        pytest.skip("no timed trial yet: python scripts/time_portal_trial.py")
    assert data["trial"] and data["trial"]["crawl"]["ms"] > 0
    for tid, lane in data["lanes"].items():
        for job, j in lane["jobs"].items():
            t = j["time"]
            assert t and t["access_ms"] > 0 and t["process_ms"] > 0, (tid, job)
            assert t["pages"] == j["pages"], (tid, job, t["pages"], j["pages"])


def test_the_committed_page_carries_its_data_and_font():
    assert PAGE.exists(), "build it with python tools/build_portal_v2.py"
    html = PAGE.read_text(encoding="utf-8")
    assert "data:font/woff2;base64," in html
    data = _data(html)
    for key in ("columns", "modules", "jobs", "lanes", "patient", "rule_ids"):
        assert data.get(key), key
