"""Photograph the screens the thesis shows, into docs/thesis/figures/.

    python tools/capture_thesis_figures.py        # needs Chromium (python -m playwright install chromium)

Two kinds of picture. The portal fixture is started on synthetic data and two
of its pages are captured as the service account sees them. The presentation
pages (the Report and the HIS Staff Assistant) are opened
from docs/review/, stepped to a telling state with their own keys, and
captured. Every picture is of synthetic data; none shows a real patient.
Rebuild after tools/build_review_pages.py.
"""

from __future__ import annotations

import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "src"), str(ROOT)]

REVIEW = ROOT / "docs" / "review"
OUT = ROOT / "docs" / "thesis" / "figures"
VIEWPORT = {"width": 1366, "height": 860}

# picture -> (page, keys pressed in order, milliseconds to wait after each, element to capture or None)
PAGES = {
    "report-forest.png": ("report.html", [], 2500, "#fig-forest"),
    "agent-portal.png": ("agent-portal.html", ["t", "Space", "Space", "Space", "Space"], 2200, None),
}


def capture_portal(browser) -> list[Path]:
    from extraction.adapters.mock_his import MockHISDataSource
    from tools.mock_portal.serve import BackgroundPortal

    written = []
    with BackgroundPortal(MockHISDataSource(records_per_layer=20, seed=42)) as portal:
        ctx = browser.new_context(viewport={"width": 1100, "height": 640}, device_scale_factor=2,
                                  ignore_https_errors=True)
        page = ctx.new_page()
        page.goto(portal.url + "/login")
        page.fill("input[name=username]", portal.username)
        page.fill("input[name=password]", portal.password)
        page.click("button[type=submit], input[type=submit]")
        page.goto(portal.url + "/m/registration/")
        page.wait_for_load_state("load")
        target = OUT / "portal-list.png"
        page.screenshot(path=str(target))
        written.append(target)
        # The record page shown is the first adult's: the synthetic population includes children,
        # whose contact fields would read as a child's own.
        import re
        links = page.locator("tbody tr a")
        for i in range(links.count()):
            page.goto(portal.url + "/m/registration/")
            page.locator("tbody tr a").nth(i).click()
            page.wait_for_load_state("load")
            born = re.search(r"\b(19\d\d|20\d\d)-\d\d-\d\d\b", page.inner_text("body"))
            if born and int(born.group(1)) <= 2000:
                break
        target = OUT / "portal-record.png"
        page.screenshot(path=str(target))
        written.append(target)
        ctx.close()
    return written


def capture_pages(browser) -> list[Path]:
    written = []
    for name, (html, keys, wait, element) in PAGES.items():
        path = REVIEW / html
        if not path.exists():
            print(f"  {html} not built -- skipped {name}")
            continue
        ctx = browser.new_context(viewport=VIEWPORT, device_scale_factor=2, color_scheme="light")
        page = ctx.new_page()
        page.goto(path.resolve().as_uri())
        page.wait_for_load_state("load")
        page.wait_for_timeout(1500)
        # A page may focus its text box on load; keys are meant for the page, not the box.
        page.evaluate("document.activeElement && document.activeElement.blur()")
        for key in keys:
            page.keyboard.press(key)
            page.wait_for_timeout(wait)
        if not keys:
            page.wait_for_timeout(wait)
        target = OUT / name
        if element and page.locator(element).count():
            page.locator(element).scroll_into_view_if_needed()
            page.wait_for_timeout(wait)
            page.locator(element).screenshot(path=str(target))
        else:
            page.screenshot(path=str(target))
        written.append(target)
        ctx.close()
    return written


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        written = capture_portal(browser) + capture_pages(browser)
        browser.close()
    for path in written:
        print(f"  wrote {path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
