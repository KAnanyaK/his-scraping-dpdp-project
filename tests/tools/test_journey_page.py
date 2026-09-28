"""The journey of one entry: every stage run for real, every column's fate, nothing it must not show.

Built from a synthetic export written in a temp directory, so it needs neither
the public sample nor a browser.
"""

from __future__ import annotations

import csv
import json
import re

import pytest

import tools.build_journey_page as page_builder
from data_synthetic.export import write_export
from trace_journey import STAGES, journey, print_journey

RECORDS = 6


def _export(tmp_path, *, synthetic: bool = True):
    directory = write_export(tmp_path / "export", records_per_layer=RECORDS, seed=11)
    if not synthetic:
        (directory / "manifest.json").unlink()
        (directory / "PROVENANCE.md").write_text(
            "# Provenance\n\nTest export. De-identification: none applied (identifiable).\n", encoding="utf-8")
    return directory


def _first_row(directory):
    with (directory / "patient_administration.csv").open(encoding="utf-8") as fh:
        return next(csv.DictReader(fh))


@pytest.fixture(scope="module")
def synthetic(tmp_path_factory):
    tmp = tmp_path_factory.mktemp("journey")
    directory = _export(tmp)
    return directory, journey(directory, enforce_handling=False)


def test_the_journey_runs_every_stage_for_every_technique(synthetic):
    _, data = synthetic
    assert [s["id"] for s in data["stages"]] == [s for s, _ in STAGES]
    assert [e["layer"] for e in data["entries"]][:1] == ["patient_administration"]
    assert data["tasks"] and all(t["runs"] for t in data["tasks"])
    for task in data["tasks"]:
        kinds = [r["kind"] for r in task["runs"]]
        assert kinds[0] == "ours" and kinds[-1] == "baseline"
        ours, base = task["runs"][0], task["runs"][-1]
        assert ours["score"] > base["score"]
        assert ours["export"]["leaked"] == 0 and base["export"]["leaked"] > 0
        assert ours["retain"]["erase_after"] and ours["retain"]["erased"]        # the purge ran and erased
        assert not base["retain"]["erase_after"] and not base["retain"]["erased"]  # nothing to schedule
        assert [e["event"] for e in ours["log"]] == ["extraction", "export", "purge"]
        assert {v["purpose"] for v in ours["purposes"]} == set(data["purposes"])
        assert sum(v["declared"] for v in ours["purposes"]) == 1


def test_every_column_has_a_fate_at_every_stage(synthetic):
    _, data = synthetic
    for task in data["tasks"]:
        for run in task["runs"]:
            for entry in data["entries"]:
                for col in entry["columns"]:
                    fate = data["fates"][f"{task['id']}|{run['kind']}|{col['id']}"]
                    assert len(fate) == len(STAGES)
                    assert fate[0]["s"] == "ok"
    # The record number: read, taken by ours, exported as its pseudonym, erased on the day.
    mrn_col = next(c for c in data["entries"][0]["columns"] if c["field"] == "mrn")
    fate = data["fates"][f"{data['tasks'][0]['id']}|ours|{mrn_col['id']}"]
    assert data["meta"]["token"] in fate[3]["t"]
    assert fate[6]["t"].startswith("erased on")


def test_no_raw_identifier_leaves_the_journey_and_the_patient_is_its_pseudonym(synthetic):
    directory, data = synthetic
    row = _first_row(directory)
    blob = json.dumps(data, ensure_ascii=False)
    for field in ("mrn", "full_name", "phone", "email", "street_address"):
        assert row[field] not in blob, field
    assert data["meta"]["token"].startswith("PSN-")
    assert data["meta"]["values_shown"] is True


def test_a_real_export_shows_shape_only(tmp_path):
    directory = _export(tmp_path, synthetic=False)
    data = journey(directory, enforce_handling=False)
    assert data["meta"]["values_shown"] is False
    shown = [c["raw"] for c in data["entries"][0]["columns"] if c["raw"]]
    assert shown and all(v.startswith("‹") or v == "▒▒" for v in shown)


def test_a_real_export_page_is_refused_where_git_would_commit_it(tmp_path, monkeypatch):
    directory = _export(tmp_path, synthetic=False)
    monkeypatch.setattr(page_builder, "git_ignores", lambda path: False)
    with pytest.raises(page_builder.PageLeak):
        page_builder.build(directory, out=tmp_path / "journey.html", enforce_handling=False)


def test_the_page_carries_the_journey_and_the_terminal_prints_it(synthetic, tmp_path, capsys):
    directory, data = synthetic
    out = tmp_path / "journey.html"
    page_builder.build(directory, out=out, enforce_handling=False)
    html = out.read_text(encoding="utf-8")
    embedded = json.loads(re.search(r'<script id="data" type="application/json">(.*?)</script>', html, re.S)
                          .group(1).replace("<\\/", "</"))
    assert embedded["meta"]["token"] == data["meta"]["token"]
    assert _first_row(directory)["mrn"] not in html
    print_journey(data, data["tasks"][0]["id"])
    printed = capsys.readouterr().out
    assert "7 RETAIN" in printed and data["meta"]["token"] in printed
    assert _first_row(directory)["mrn"] not in printed
