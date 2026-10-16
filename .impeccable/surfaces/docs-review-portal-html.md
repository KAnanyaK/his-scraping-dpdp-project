---
version: 1
slug: "docs-review-portal-html"
primary_target: "docs/review/portal.html"
related_targets: ["tools/portal/portal.html"]
---

## Scope

`docs/review/portal.html`, the **Portal**: the recorded pipeline run as a display, presented at Review-III (26.10.2026) on a projected laptop. Mode: Experience. Built by `tools/build_portal_app.py` from `tools/portal/`; one offline file. Not the Report (`docs/review/report.html`); no link between the two.

Redesigned 2026-10-11 after the user's review of the control-room build: "the final portal should have a lot of colors and contrast", "less about functionality and more about visuality", "simple flow of pipeline is enough, the display design should be the focus". Kept (user): the race (ours vs an AI model vs the baseline), the briefing switch, the one-patient story. Cut: the HIS replica window, faceplates, scenario drills, the staff assistant, the alarm list. Presenter steps it (Space plays, arrows move station to station). Every number is the real recorded one.

Constraints: numbers from artefacts only; no raw identifier on screen (the builder audits); no vendor names; no new dependency (SVG, CSS); 1366x768 projected; keyboard paths; reduced motion keeps every state.

## Direction contract

THESIS: The pipeline is a metro map. Three straight lines (ours, an AI model, the baseline) run through the same stations, Hospital to Erased, and what sets them apart is their stopping pattern: between Acquire and Extract each calls at one square per page load, its train moving on only as they fill; ours is the express, the baseline the all-stations service, and a line with no erase date runs off the map. It refuses the dark neon node graph, the grey dashboard and the template look. (Revised 2026-10-11: the first metro build drew page loads as route length, and the user found the baseline's switchbacks "unprofessional and not presentable" and asked for better graphic design, "it shouldn't look like some bootstrap project".)

OWN-WORLD: White map ground, black type, three bold saturated lines (teal ours, magenta model, orange baseline), stations as white discs in black rings joined by interchange links, three fare-zone tints (intake, extraction, export), passengers as dots in the six data-category colours, disruption signs (red disc, white bar) for a broken rule or a trap taken. Line badges, a route strip, and a passenger ticket for the patient.

STORY: The panel watches three trains leave the hospital; ours fills its one short row of squares and is through, the model a little after, while the baseline's block of 440 squares fills square by square and its train crawls. Passengers board at Extract, rule lamps come on at Score, identifiers turn into tokens at Export, and the baseline's line runs on past Erased, off the map.

FIRST VIEWPORT: Full-bleed map: line roundels, the model picker and the briefing switch in a slim navy header; three straight lines across three pale zones with seven named stations; trains waiting at Hospital; the patient's ticket at the right; the route strip with a Space cue at the foot. Signature: Space sends the trains; between Acquire and Extract each line's squares fill as its train calls.

FORM: Metro Line Map, my top-ranked candidate (1 of 7), chosen by the user from the pick card; seed 8685d5a7. Kept from the declined hand: counts arrive as visible events (rolling digits); the numbers are the picture; one axis woken in sequence; one switch re-colours the whole field (the briefing); each station has a window onto what it holds; crisp state changes.

FINISH: unreviewed and undocumented is unfinished; this build ends with the finish review, the verdict, DESIGN.md, and every shipping raster carrying its provenance

## Unresolved

- Whether the deck's demonstration slide (`tools/capture_demo_pages.py`) captures the Portal.
