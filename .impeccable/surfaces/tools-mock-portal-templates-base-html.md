---
version: 1
slug: "tools-mock-portal-templates-base-html"
primary_target: "tools/mock_portal/templates/base.html"
related_targets: ["tools/mock_portal/templates/home.html","tools/mock_portal/templates/list.html","tools/mock_portal/templates/detail.html","tools/mock_portal/templates/login.html"]
---

# Mock HIS portal (tools/mock_portal/templates)

Scope: every page of the fixture portal (sign-in, home, module list, record). Mode: Operate.

Audience and job: someone watching a real browser crawl the portal on a laptop (`run_pipeline.py --show`), with a presenter at reviews or alone afterwards. The one thing they must catch on a page shown for under a second: **which module**. Second reader: the Tier 2 scraper, which must read exactly what it read before (DOM contract in PRODUCT.md; page loads and committed artefacts unchanged).

Must not feel like: the project's own review pages (rounded cards, soft shadows, system-ui, blue/violet/amber technique colours).

## Direction contract

THESIS: The portal is the grid-control client staff run at a registration counter: module tab strip, dense grid, a status bar that says where you are. It refuses the blue-navbar-plus-bordered-table web portal every hospital ships, where module identity rests on reading a title.

OWN-WORLD: Steel-grey application chrome, a dark title bar, squared 2px corners, 1px bevel-lite borders, Tahoma/Segoe workhorse type, tabular figures, fixed 26px grid rows on white. Five module colours used as code and nowhere else, kept out of the review pages' blue/violet/amber technique families: teal Registration, crimson Clinical, plum Departments, olive Billing, slate Audit, marking the tab, a full-width title band, the favicon, the status chip and the launcher's code cell (row hover tint only; a crawl never hovers). The grid itself stays achromatic.

STORY: The watcher sees colour change as the browser moves between modules, reads "page 3 of 20" ticking in one fixed spot, and understands the crawl's cost as pages going by.

FIRST VIEWPORT: Title bar (portal name, user, sign out); tab strip; module colour band with code and name at 28px; search toolbar and "500 records · page 1 of 20"; the grid filling the rest; status bar pinned bottom with fixed slots: module, view, page, rows, user, load time.

FORM: Front-Office Client, candidate 3 of 7 on the ordered list; seed key 4ee5e18f. Raises: fixed-slot counters (seven-segment); strict cell grid (ASCII); colour as code, total (catalog sleeve); colour confined to the frame (cloud edge); one law per colour (gravity garden). Signature interaction: on each page load the status-bar slots whose value changed flash once in the module tint, so each load is visibly a tick.

FINISH: unreviewed and undocumented is unfinished; this build ends with the finish review, the verdict, DESIGN.md, and every shipping raster carrying its provenance

## Unresolved

None.
