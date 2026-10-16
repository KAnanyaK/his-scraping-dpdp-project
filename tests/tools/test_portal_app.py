"""The Portal (docs/review/portal-v1.html): the recorded run as a metro map.

Pinned here: the builder refuses a page that would carry a raw identifier; the
map's export readings are computed on the very source the portal served, so they
agree with the parts (ours exports no raw identifier, the baseline exports every
one); each line's page loads are the recorded ones; and the committed Portal
carries what the map, the briefing switch and the patient's ticket need.
"""

from __future__ import annotations

import json
import re

import pytest

from tools import build_portal_app as app
from tools.page_kit import REVIEW_DIR

PORTAL = REVIEW_DIR / "portal-v1.html"


def _data(html: str) -> dict:
    return json.loads(re.search(r'<script type="application/json" id="plant-data">(.*?)</script>', html, re.S).group(1))


@pytest.fixture(scope="module")
def built():
    data, secrets = app.payload()
    return data, secrets, app.render(data)


def test_the_portal_refuses_a_raw_identifier(built):
    data, secrets, html = built
    app.check(html, secrets)                                   # the real page passes
    leaked = next(iter(secrets))
    with pytest.raises(app.PortalLeak):
        app.check(html + leaked, secrets)
    # the one patient the ticket follows is masked
    assert re.fullmatch(r"MRN\*+\d{2}", data["patient"]["mrn"])
    assert "•" in data["patient"]["name"]


def test_the_export_stage_runs_on_the_portals_own_source(built):
    data, _, _ = built
    ours, base = data["export"]["ours"], data["export"]["base"]
    assert ours["leaked"] == 0 and ours["pseudonymised"] and ours["retention"]
    assert base["leaked"] == base["identifiers"] > 0 and not base["pseudonymised"] and base["retention"] is None
    # the one-patient job reads one patient for ours, every patient for the baseline
    assert ours["patients"] == [data["patient"]["index"]]
    assert len(base["patients"]) == data["meta"]["records"]
    # every technique the portal run scored has a pull and an export here
    ids = {t["id"] for t in data["techniques"]}
    assert ids == set(data["ledger"]) == set(data["export"])


def test_each_line_carries_its_recorded_page_loads(built):
    data, _, _ = built
    by = {t["id"]: t for t in data["techniques"]}
    assert by["ours"]["traced"] == by["ours"]["pages"]
    assert by["base"]["traced"] == by["base"]["pages"]
    # a model's first recorded sample is the one drawn; its loads are a real sample's
    assert all(0 < t["traced"] for t in data["techniques"])
    # every model can take every briefing on line B
    models = {t["model"] for t in data["techniques"] if t["model"]}
    for m in models:
        for b in ("unaided", "informed", "policy"):
            assert f"{m}|{b}" in by


def test_the_committed_portal_carries_the_map():
    assert PORTAL.exists(), "build it with python tools/build_portal_app.py"
    data = _data(PORTAL.read_text(encoding="utf-8"))
    for key in ("techniques", "ledger", "export", "patient", "rule_ids", "tasks"):
        assert data.get(key), key
    assert data["export"]["ours"]["leaked"] == 0 < data["export"]["base"]["leaked"]
