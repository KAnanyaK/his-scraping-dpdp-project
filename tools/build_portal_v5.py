"""The Portal, version 5: one patient's record, and what each technique did with it, ``docs/review/portal-v5.html``.

    python tools/build_portal_v5.py             # from the staged parts in build/review-parts/
    python tools/build_review_pages.py          # builds the parts, the Report and every Portal

Privacy is what stays covered. The record of the one patient the single-patient
jobs are about is typeset as a document in a case folder, every value under a
redaction bar; choosing who read it -- ours, an AI model at a briefing, the
baseline -- lifts exactly the bars that run read. A second leaf is the copy that
left the hospital, each value as the export's own transform carried it (a token
where the record number was, a birth year where the date was, or the value as
read); turned to its erase date, the copy empties. A third leaf is the record's
access slip: every reading of this record, as the patient would be told.

The data is the shared record (``tools/portal_record.py``). Identifiers, contact
details and quasi-identifiers appear only masked; the builder audits its own
output with version 1's audit and refuses to write a page carrying a raw value.
"""

from __future__ import annotations

import base64
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for p in (ROOT, ROOT / "src", ROOT / "scripts"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from tools import build_portal_app as v1                                    # noqa: E402
from tools.page_kit import REVIEW_DIR, write                                # noqa: E402
from tools.portal_record import record                                      # noqa: E402

HERE = ROOT / "tools" / "portal_v5"
OUT = REVIEW_DIR / "portal-v5.html"
SHELL = HERE / "portal.html"
CSS = HERE / "portal.css"
SCRIPTS = ["record.js"]
FONT = HERE / "fonts" / "SourceSerif4-latin-opsz.woff2"


def payload() -> tuple[dict, set[str]]:
    data, secrets = record()
    # One patient is on the page: keep each run's summary, its copy of this patient and its custody lines.
    for t in data["techniques"].values():
        for runs in t["jobs"].values():
            for r in runs:
                for k in ("hl7", "visits", "claims"):
                    r.pop(k, None)
    return data, secrets


def render(data: dict) -> str:
    html = SHELL.read_text(encoding="utf-8")
    font = base64.b64encode(FONT.read_bytes()).decode("ascii")
    css = CSS.read_text(encoding="utf-8").replace("/*__FONT__*/", f"url(data:font/woff2;base64,{font}) format('woff2')")
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
    print(f"  wrote {out.relative_to(ROOT)}  (the Portal v5, {size:.1f} MB); audit: no raw identifier on the page")
    return 0


if __name__ == "__main__":
    sys.exit(main())
