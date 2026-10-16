---
version: 1
slug: "docs-review-report-html"
primary_target: "docs/review/report.html"
related_targets: ["tools/report/report.html"]
---

## Scope

`docs/review/report.html` (the Report; renamed from portal.html 2026-10-11), rebuilt from scratch (2026-10-11, user: "completely scrap the portal and rebuild from scratch"). Mode: Read, presented live at Review-III (26.10.2026) on a laptop or projector with a presenter clicking; readable offline afterwards. Replaces the six-tab iframe portal with one scrolling report. Content, data and live pieces are kept (sign-in and crawl replay, rules vs AI, journey, patient rights, assistant with its self-check, HIS update); every number still comes from the parts' data blocks; no raw identifier; opens offline by double-click.

## Direction contract

THESIS: The benchmark is a trial and the portal is its evidence report: techniques are arms, ours is the reference, and each finding is a numbered figure with its caption. It refuses the dashboard-of-tabs with KPI cards and the dark "AI vs rules" neon page.

OWN-WORLD: White journal page, ink #121417, one house teal #00737a for figure numbers, rules, links and the reference arm; models keep their own muted hues, baseline amber, harm red #c0392b. Booktabs tables (heavy top and bottom rule, hairline under the header), forest plots (square marker, interval whisker, dashed reference line), a flow diagram with the only boxes on the page, a tinted key-points panel. Bahnschrift for figure labels and numbers, Segoe UI Variable for text.

STORY: The room sees the headline result at once, then follows the trial order: setting, primary outcome (traps), secondary outcomes, adverse events (planted text, breach), one record followed, patients' rights, sensitivity to an HIS update, and the assistant in use. They leave believing the score alone hides what the AI models do.

FIRST VIEWPORT: Left contents rail; masthead line, title, authors and the four key points in a teal-tinted panel; Figure 1, the forest plot of every technique told the policy, starts above the fold with its briefing switch. Signature interaction: switching the briefing slides every marker to its new estimate while ours holds the reference line. Presenter keys step figure to figure, each snapping to the screen.

FORM: The Evidence Report, my own top-ranked candidate (1 of 7), taken as the pick card; seed c17e3be5.

FINISH: unreviewed and undocumented is unfinished; this build ends with the finish review, the verdict, DESIGN.md, and every shipping raster carrying its provenance

## Unresolved

- The deck's demo captures (`tools/capture_demo_pages.py`) photograph the old parts; they follow the report once it ships.
