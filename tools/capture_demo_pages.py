"""Photograph the demo pages in their most telling state, for the review deck.

    python tools/capture_demo_pages.py        # writes docs/review/img/*.png (needs Chromium)

Each picture is one figure of the Report (``docs/review/report.html``),
opened in headless Chromium at a projector-like size, brought into view, left to
finish what it plays (the crawl), and captured.
The deck (``tools/build_review_deck.py``) places these on its demonstration
slide, so the pictures are there even if the room's browser is not. Rebuild
after ``tools/build_review_pages.py``.
"""

from __future__ import annotations

import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
REVIEW = ROOT / "docs" / "review"
OUT = REVIEW / "img"
VIEWPORT = {"width": 1366, "height": 900}

# name -> (figure id in the report, seconds to let it play before the capture)
SHOTS = {
    "portal-crawl": ("fig-crawl", 9),
    "rules-vs-ai": ("fig-forest", 2),
    # Review-III deck (tools/build_review3_deck.py)
    "r3-traps": ("fig-traps", 2),
    "r3-injection": ("fig-injection", 2),
    "r3-coverage": ("fig-coverage", 2),
    "r3-stability": ("fig-stability", 2),
    "r3-modules": ("fig-modules", 2),
    "r3-retention": ("fig-retention", 2),
    "r3-breach": ("fig-breach", 2),
    "r3-release": ("fig-release", 2),
    "r3-scraper": ("fig-scraper", 2),
    "r3-assistant": ("fig-assistant", 4),
}


def capture() -> list[Path]:
    sys.path.insert(0, str(ROOT))
    from tools.page_kit import REPORT

    OUT.mkdir(parents=True, exist_ok=True)
    written = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        for name, (fig, settle) in SHOTS.items():
            page = browser.new_page(viewport=VIEWPORT, device_scale_factor=2, color_scheme="light")
            page.goto(REPORT.resolve().as_uri())
            page.wait_for_load_state("load")
            el = page.locator(f"#{fig}")
            if not el.count():
                print(f"  {name}: the report has no #{fig} -- skipped")
                continue
            el.scroll_into_view_if_needed()
            page.wait_for_timeout(int(settle * 1000))
            target = OUT / f"{name}.png"
            el.screenshot(path=str(target))
            written.append(target)
            page.close()
        browser.close()
    return written


def main() -> int:
    for path in capture():
        print(f"  wrote {path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
