"""Build the Report, docs/review/report.html, and the Portal, docs/review/portal-v1.html (v1), portal-v2.html (v2), portal-v3.html (v3), portal-v4.html (v4) and portal-v5.html (v5), in one command.

    python tools/build_review_pages.py                  # every demo that can be built here
    python tools/build_review_pages.py --skip-portal    # no browser on this machine
    python tools/build_review_pages.py --report-only    # re-render the report from the staged parts

Every demo is built as a part into the git-ignored ``build/review-parts/`` (each
builder audits its own), and the parts' data blocks become one self-contained
evidence report (``tools/build_report.py``, since 2026-10-11; before that a shell
with a tab per demo). A part this machine
cannot rebuild -- the portal run and the HIS update need Chromium
(``python -m playwright install chromium``), the journey needs the public
Synthea sample (``python scripts/fetch_public_dataset.py``) -- is carried over
from the report already committed, never dropped. Every part is synthetic or
public-synthetic data, so the portal is committable. The dataset walkthrough
and the hospital-register page left the portal; ``tools/build_dataset_page.py``
and ``tools/build_real_page.py`` still build them on their own.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from tools.page_kit import LEGACY_PORTAL, REPORT, REVIEW_DIR, part_data, part_path, parts_in   # noqa: E402
from tools.build_report import KEYS, build as build_report, report_data       # noqa: E402

SYNTHEA = ROOT / "data" / "public_synthea"
RESULTS = ROOT / "docs" / "benchmark_results"

# The separate pages the portal replaced (2026-10-06). Removed when the portal is built.
RETIRED = [REVIEW_DIR / n for n in ("index.html", "portal-run.html", "dataset-walkthrough.html", "real-data.html",
                                    "journey.html", "assistant.html", "his-update.html", "patient-rights.html")] \
    + [RESULTS / "rules-vs-just-ai.html", RESULTS / "techniques-compared.html"]


def build_parts(*, skip_browser: bool = False) -> dict[str, str]:
    """Every part this machine can build, written to the staging folder; returns {key: html}."""

    built: dict[str, Path] = {}

    def done(key: str) -> None:
        built[key] = part_path(key)
        print(f"  built {key}")

    from tools import build_demo_page
    build_demo_page.main()
    done("rules")

    from tools import build_assistant_page
    build_assistant_page.build()
    done("assistant")

    from tools import build_rights_page
    build_rights_page.build()
    done("rights")

    if skip_browser:
        print("  portal run and HIS update: skipped (no browser) -- carried over")
    else:
        from tools import build_portal_page, build_update_page
        build_portal_page.build()
        done("portal")
        build_update_page.build()
        done("update")

    if (SYNTHEA / "patients.csv").exists():
        from extraction.adapters.dataset_his import load_column_map
        from tools import build_journey_page
        column_map, file_maps = load_column_map(SYNTHEA / "column_map.json")
        build_journey_page.build(SYNTHEA, column_map=column_map, file_maps=file_maps)
        done("journey")
    else:
        print("  journey: no Synthea sample here (scripts/fetch_public_dataset.py) -- carried over")

    return {k: p.read_text(encoding="utf-8") for k, p in built.items()}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--skip-portal", action="store_true", help="no browser here: carry the browser-built demos over")
    parser.add_argument("--report-only", action="store_true", help="rebuild nothing: re-render the report from the staged parts")
    args = parser.parse_args()

    # What the committed report already carries, for a section this machine cannot rebuild.
    previous = report_data(REPORT) or report_data(LEGACY_PORTAL) or {k: part_data(v) for k, v in parts_in(LEGACY_PORTAL).items()}
    if args.report_only:
        parts = {k: part_path(k).read_text(encoding="utf-8") for k in KEYS if part_path(k).exists()}
    else:
        parts = build_parts(skip_browser=args.skip_portal)
    sections = {k: part_data(html) for k, html in parts.items() if k in KEYS}
    for key, data in previous.items():
        if key not in sections and key in KEYS and data:
            sections[key] = data
            print(f"  carried over {key} from the committed report")

    missing = [k for k in KEYS if k not in sections]
    build_report(sections)
    size = REPORT.stat().st_size / 1024 / 1024
    print(f"  wrote {REPORT.relative_to(ROOT)}  (the Report, {len(sections)} of {len(KEYS)} sections, {size:.1f} MB)"
          + (f"; not available: {', '.join(missing)}" if missing else ""))

    for old in RETIRED:
        if old.exists():
            old.unlink()
            print(f"  removed {old.relative_to(ROOT)} (now part of the report)")

    # The Portal replays the same parts (the staged ones, else the Report just written).
    from tools import build_portal_app, build_portal_v2, build_portal_v3, build_portal_v4, build_portal_v5
    build_portal_app.main()            # version 1, the metro line map
    build_portal_v2.main()             # version 2, the live data flow
    build_portal_v3.main()             # version 3, the catalogue
    build_portal_v4.main()             # version 4, the datasheets
    build_portal_v5.main()             # version 5, the redacted record
    return 0


if __name__ == "__main__":
    sys.exit(main())
