"""Shared by the demo builders: one look, one data block per demo.

Every demo is built as its own self-contained page (``tools/*_page.html`` with
``tools/page_base.css`` and ``tools/page_base.js`` inlined) and written as a
*part* into a git-ignored staging folder; each builder audits its own part. The
published file, ``docs/review/report.html``, is the Report (the evidence report
``tools/build_report.py``), which carries each part's data block and draws its
own figures from it. Until 2026-10-11 the portal was a shell with one tab per
part; ``parts_in`` still reads that older format, so a part this machine cannot
rebuild can be carried over from a portal built before the report.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE_CSS = ROOT / "tools" / "page_base.css"
BASE_JS = ROOT / "tools" / "page_base.js"
REVIEW_DIR = ROOT / "docs" / "review"
PARTS_DIR = ROOT / "build" / "review-parts"            # git-ignored staging
REPORT = REVIEW_DIR / "report.html"          # the Report (renamed from portal.html 2026-10-11)
LEGACY_PORTAL = REVIEW_DIR / "portal.html"   # the tabbed portal it replaced; that name now belongs to the Portal deliverable

# The demos the report is built from, by key (labels were the old shell's tab names).
# Cut to six on 2026-10-09 (user: "too many tabs"): the overview, the Synthea walkthrough and
# the aggregate hospital register left the portal; their builders still run on their own.
TABS = [
    ("portal", "Portal run"),
    ("rules", "Rules vs AI"),
    ("journey", "Journey"),
    ("rights", "Patient rights"),
    ("assistant", "Assistant"),
    ("update", "HIS update"),
]


def part_path(key: str) -> Path:
    return PARTS_DIR / f"{key}.html"


def render(template: Path, data: dict | None, *, current: str = "", out: Path | None = None) -> str:
    """The template with the base stylesheet, the base script and the data block filled in."""

    html = template.read_text(encoding="utf-8")
    html = html.replace("/*__BASE__*/", BASE_CSS.read_text(encoding="utf-8"))
    html = html.replace("/*__KIT__*/", BASE_JS.read_text(encoding="utf-8"))
    html = html.replace("<!--__NAV__-->", "")             # the portal's tab bar is the navigation
    if data is not None:
        payload = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
        html = html.replace("/*__DATA__*/null", payload)
    return html


def write(out: Path, html: str) -> Path:
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")
    return out


_PARTS = re.compile(r'<script id="parts" type="application/json">(.*?)</script>', re.S)
# The bridge the old shell appended to each part; stripped when a part is carried over.
_BRIDGE_START = "<style>.tools,.sitenav{display:none!important}</style>"


def parts_in(portal: Path = LEGACY_PORTAL) -> dict[str, str]:
    """The parts a portal built before 2026-10-11 (the tabbed shell) carries, without the shell's
    bridge -- for carrying over a demo this machine cannot rebuild. {} for the report."""

    if not portal.exists():
        return {}
    m = _PARTS.search(portal.read_text(encoding="utf-8"))
    if not m:
        return {}
    parts = json.loads(m.group(1))["parts"]
    return {k: v.split(_BRIDGE_START)[0] for k, v in parts.items()}


def part_data(html: str) -> dict:
    """The data block of one part, as its builder embedded it."""

    m = re.search(r'<script id="data" type="application/json">(.*?)</script>', html, re.S)
    return json.loads(m.group(1).replace("<\\/", "</")) if m else {}
