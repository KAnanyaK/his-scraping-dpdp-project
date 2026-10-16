"""The Portal, version 3: the recorded run catalogued, ``docs/review/portal-v3.html``.

    python tools/build_portal_v3.py             # from the staged parts in build/review-parts/
    python tools/build_review_pages.py          # builds the parts, the Report and every Portal

A run leaves objects behind, so the page catalogues them. Each view is a spread:
on the left a plate, one real artefact the pipeline made for the chosen job (the
field inventory, the request, the extract, the browser's page-load log, the
manifest checked against the register, the HL7 message as it left, the retention
record, every recorded run, the audit log's lines); on the right its catalogue
entry with one fact set large. Comparanda a / b / c -- ours, an AI model, the
baseline -- flip in place on the same plate.

The data is the shared record (``tools/portal_record.py``): the recorded run
replayed by the project's own code on the source the portal served. The builder
audits its own output with version 1's audit: no raw identifier, contact detail
or quasi-identifier of any record may appear on the page.
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

HERE = ROOT / "tools" / "portal_v3"
OUT = REVIEW_DIR / "portal-v3.html"
SHELL = HERE / "portal.html"
CSS = HERE / "portal.css"
SCRIPTS = ["catalogue.js"]
FONT = HERE / "fonts" / "Archivo-latin-wdth.woff2"


def payload() -> tuple[dict, set[str]]:
    return record()


def render(data: dict) -> str:
    html = SHELL.read_text(encoding="utf-8")
    font = base64.b64encode(FONT.read_bytes()).decode("ascii")
    css = CSS.read_text(encoding="utf-8").replace("/*__FONT__*/", f"url(data:font/woff2;base64,{font}) format('woff2')")
    html = html.replace("/*__CSS__*/", css)
    html = html.replace("/*__JS__*/", "\n".join((HERE / name).read_text(encoding="utf-8") for name in SCRIPTS))
    # No "<" survives inside the data element, so nothing in a value can end the script early.
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
    print(f"  wrote {out.relative_to(ROOT)}  (the Portal v3, {size:.1f} MB); audit: no raw identifier on the page")
    return 0


if __name__ == "__main__":
    sys.exit(main())
