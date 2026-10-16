"""The Portal v5 (docs/review/portal-v5.html): one patient's record, and what each technique did with it.

Pinned here: the builder refuses a page that would carry a raw identifier, and
the record shows every identifier, contact detail and quasi-identifier only
masked; the copy that left the hospital is the export's own transform of this
patient's rows -- a keyed token where the record number was and a birth year
where the date was when the run pseudonymised, the value as read (masked here)
when it did not; a copy is destroyed exactly when its run declared a retention
and the purge ran on that date; and the committed page carries its data and its
font, and no link to the Report.
"""

from __future__ import annotations

import json
import re

import pytest

from tools import build_portal_app as v1
from tools import build_portal_v5 as v5
from tools.page_kit import REVIEW_DIR

PAGE = REVIEW_DIR / "portal-v5.html"


def _data(html: str) -> dict:
    return json.loads(re.search(r'<script type="application/json" id="record-data">(.*?)</script>', html, re.S).group(1))


@pytest.fixture(scope="module")
def built():
    data, secrets = v5.payload()
    return data, secrets, v5.render(data)


def test_the_page_refuses_a_raw_identifier(built):
    data, secrets, html = built
    v1.check(html, secrets)
    with pytest.raises(v1.PortalLeak):
        v1.check(html + next(iter(secrets)), secrets)
    for c, v in zip(data["columns"], data["patient"]["values"]):
        if c["field"] in ("mrn", "subject_mrn") and v:
            assert re.fullmatch(r"MRN\*+\d{2}", v)
        if c["field"] in ("full_name", "phone", "email", "street_address", "date_of_birth", "pincode") and v:
            assert "•" in v, c["field"]


def test_the_copy_is_the_exports_own_transform(built):
    data, _, _ = built
    cols = data["columns"]
    mrn = [str(i) for i, c in enumerate(cols) if c["field"] == "mrn"]
    for tid, t in data["techniques"].items():
        for job, runs in t["jobs"].items():
            r = runs[0]
            copy = dict(r["copy"], fields={str(k): v for k, v in r["copy"]["fields"].items()})
            if not copy["found"]:
                continue
            assert set(map(int, copy["fields"])) <= set(r["cols"]), (tid, job)
            for i in mrn:
                f = copy["fields"].get(i)
                if f is None:
                    continue
                if copy["pseudonymised"]:
                    assert f["how"] == "token" and f["value"].startswith("PSN-"), (tid, job)
                else:
                    assert f["how"] == "raw" and re.fullmatch(r"MRN\*+\d{2}", f["value"]), (tid, job)
    ours = data["techniques"]["ours"]["jobs"]["patient-summary"][0]["copy"]
    ours = dict(ours, fields={str(k): v for k, v in ours["fields"].items()})
    dob = next(str(i) for i, c in enumerate(cols) if c["field"] == "date_of_birth")
    assert ours["pseudonymised"] and ours["fields"][dob]["how"] == "generalised" and re.fullmatch(r"\d{4}", ours["fields"][dob]["value"])
    base = data["techniques"]["base"]["jobs"]["patient-summary"][0]["copy"]
    assert not base["pseudonymised"] and len(base["fields"]) == len(cols)


def test_a_copy_is_destroyed_on_its_date_or_never(built):
    data, _, _ = built
    for tid, t in data["techniques"].items():
        for job, runs in t["jobs"].items():
            r = runs[0]
            purge = [e for e in r["audit"] if e["event"] == "purge"]
            if r["erase"]:
                assert purge and purge[0]["at"].startswith(r["erase"]), (tid, job)
            else:
                assert not purge, (tid, job)


def test_the_committed_page_carries_its_data_and_font():
    assert PAGE.exists(), "build it with python tools/build_portal_v5.py"
    html = PAGE.read_text(encoding="utf-8")
    assert "data:font/woff2;base64," in html
    assert "report.html" not in html
    data = _data(html)
    for key in ("columns", "modules", "jobs", "techniques", "patient"):
        assert data.get(key), key
