"""The Report: the benchmark as one evidence report, ``docs/review/report.html``.

Rebuilt 2026-10-11 (user: "completely scrap the portal and rebuild from scratch"):
the six demos stop being tabs of separate pages and become one scrolling report
in trial-report order -- the headline result, the setting, the primary and
secondary outcomes, adverse events, one record followed, patients' rights,
sensitivity to an HIS update, and the staff assistant -- with numbered figures
and a contents rail.

The report reads nothing of its own. Each demo builder still writes its part
into ``build/review-parts/`` and audits it (no record number, the trace equals
the meter); the report takes each part's data block as it is, so every number
on it comes from the same artefacts and the same audits. The template is a few
small files under ``tools/report/`` -- the shell, one stylesheet, the kit and
one script per data source -- inlined here into a single file that opens
offline by double-click.
"""

from __future__ import annotations

import json
import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.page_kit import REPORT, TABS, write                    # noqa: E402

HERE = ROOT / "tools" / "report"
SHELL = HERE / "report.html"
CSS = HERE / "report.css"
# Order matters: the kit first, then one script per data source, then the start.
SCRIPTS = ["kit.js", "sec_rules.js", "sec_portal.js", "sec_journey.js", "sec_rights.js", "sec_update.js",
           "sec_assistant.js", "main.js"]
KEYS = [k for k, _ in TABS]                                         # portal, rules, journey, rights, assistant, update
_DATA = re.compile(r'<script id="data" type="application/json">(.*?)</script>', re.S)


def render(data: dict) -> str:
    """The report with its stylesheet, scripts and data inlined."""

    html = SHELL.read_text(encoding="utf-8")
    html = html.replace("/*__CSS__*/", CSS.read_text(encoding="utf-8"))
    html = html.replace("/*__JS__*/", "\n".join((HERE / s).read_text(encoding="utf-8") for s in SCRIPTS))
    # No "<" survives inside the data element, so nothing in a value can end the script early.
    payload = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c")
    return html.replace("/*__DATA__*/null", payload)


def report_data(portal: Path = REPORT) -> dict:
    """The data a built report carries, by section key ({} when there is none or it predates the report)."""

    if not portal.exists():
        return {}
    m = _DATA.search(portal.read_text(encoding="utf-8"))
    if not m:
        return {}
    try:
        data = json.loads(m.group(1))
    except json.JSONDecodeError:
        return {}
    return {k: v for k, v in data.items() if k in KEYS}


def build(sections: dict[str, dict], out: Path = REPORT) -> Path:
    """Write the report from each section's data block; sections absent are simply left out."""

    data = {k: sections[k] for k in KEYS if k in sections}
    data["built"] = date.today().isoformat()
    return write(out, render(data))
