---
version: 1
slug: "docs-review-portal-v2-html"
primary_target: "docs/review/portal-v2.html"
related_targets: ["tools/portal_v2/portal.html", "tools/portal_v2/portal.css", "tools/portal_v2/flow.js", "tools/build_portal_v2.py"]
---

## Scope

`docs/review/portal-v2.html`, **Portal version 2**: the recorded pipeline run as a live data flow, presented at Review-III (26.10.2026) on a projected laptop. Mode: Experience. Built by `tools/build_portal_v2.py` from `tools/portal_v2/`; one offline file with Inter (OFL) embedded. Version 1 (the metro line map, `docs/review/portal.html`) stays as it is beside it.

Asked for on 2026-10-11 after the user rejected v1's look ("there has to be a different way to showcase our pipeline ... the front end isn't flashy at all ... take inspiration from the front end of other well developed products that share a similar demo"). The user chose **Live Flow** from three directions (Live Flow, Run Console, The Record) and approved embedding Inter. Kept from v1 (user): the race, the briefing switch, the one-patient story, presenter stepping, real recorded numbers, no link to the Report.

Constraints: numbers from artefacts only; no raw identifier on screen (the builder audits with v1's audit); no vendor names; no new dependency (canvas, SVG, CSS); 1366x768 projected; keyboard paths; reduced motion keeps every state.

## Direction contract

THESIS: The pipeline as a live data stream. The hospital is drawn as what it holds (20 patients by 34 fields, 680 values, each coloured by its DPDP data category); for one job at a time, every value a technique reads becomes a particle of light that flies into its lane and travels on through the rules, the export and the erasure. Over-collection, a trap taken, identifiers leaving raw and data never erased happen in the stream, where the panel can see them.

OWN-WORLD: Night ground (#070a12) with light that means something. Inter throughout, product chrome in the Linear / Vercel register: hairline borders, glass lanes, a status pill, metric labels over tabular numerals. Three lane accents (teal ours, pink the AI model, orange the baseline), six category colours for the particles, breach red as a halo, tokens as white diamonds, a yellow gate and spotlight for "here".

STORY: Ready, the hospital dim. The gate lights and its four checks tick. A beam sweeps the hospital and the crawler finds five modules. Then the race: ours lifts a handful of values from one patient's row and is through; the model a little more; the baseline drains the hospital row by row while its counters climb. Rule lamps light at Score, identifiers become tokens (or leave raw) at Export, and at Erase ours dissolves while the baseline's 680 values sit there, kept indefinitely.

FIRST VIEWPORT: Product bar (brand, status, model picker, briefing), a job bar (four jobs, the trap job flagged, the purpose with its allowed categories as the colour key), the hospital matrix with the one patient's row outlined and their card below, the gate, three lanes with their metrics, the transport with the white Next key.

FORM: Live Flow, chosen by the user from three. No concept roll ran (no seed key): the three directions were dealt by hand in a question round, each with a sketch; inspiration named in the round: Stripe / Segment data-flow hero animations, Datadog live tail and sensitive-data scanning, Linear's product chrome, GitHub Actions / Vercel run status.

FINISH: unreviewed and undocumented is unfinished; this build ends with a finish review, its fixes, and a design record of its own (DESIGN.md stays the Report's; DESIGN-portal.md is v1's).
