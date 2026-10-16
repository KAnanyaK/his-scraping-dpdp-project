---
version: 1
slug: "docs-review-portal-v4-html"
primary_target: "docs/review/portal-v4.html"
related_targets: ["tools/portal_v4/portal.html","tools/portal_v4/portal.css","tools/portal_v4/datasheet.js","tools/build_portal_v4.py","tools/portal_record.py"]
---

## Scope

`docs/review/portal-v4.html`, **Portal version 4, The Datasheet**: each extraction technique specified the way an electronic component is specified, for the Review-III panel (26.10.2026, projected 1366x768, a School of Electronics Engineering panel that reads datasheets every week) and later offline readers. Mode: Experience. Built by `tools/build_portal_v4.py` from `tools/portal_v4/` and the shared record `tools/portal_record.py`; one offline file with Barlow and Barlow Semi Condensed (OFL, user-approved 2026-10-12) embedded. v1, v2 and v3 stay as they are; v5 (The Redacted Record) follows.

From the direction round of 2026-10-12 (`docs/review/portal-v3-brief.md`): the user was shown The Catalogue, The Datasheet and The Redacted Record and answered "actually do all 3 one by one and label v3, v4 and v5". The Datasheet was the build thread's own top-ranked candidate (the pick card), recommended for this panel.

Audience and job: an engineering panel reads a part's datasheet to know what it does, its limits, how it behaves across conditions and how much it varies; here they read what each technique takes, the purpose limits it must stay within, how it behaves told less or more, and how much it varies from run to run. Constraints: every figure from the recorded run computed by the project's code; no raw identifier (builder audits with v1's `check`); no vendor names; no link to the Report; 13px floor; keyboard path; reduced motion lands every state; no lanes, dots, flows, metro, dark neon, KPI tiles; not a second evidence report.

## Direction contract

THESIS: A technique is a component; specify it. Each technique gets a four-page datasheet: a front page (features, applications, pin configuration of the 34 fields with the ones this part connects, a device comparison table), specifications (absolute maximum ratings = the job's purpose policy, recommended operating conditions = the job's expert field list, characteristics with MIN / TYP / MAX over five runs), typical characteristics (curves), and application information (the manifest as a register map, the export as the package, ordering options = the three briefings, revision history). Ours is the reference design. It refuses the dashboard, the flow diagram and the side-by-side race: comparison lives where a datasheet keeps it, in a device comparison table and in curves.

OWN-WORLD: A well-set component datasheet on a desk: a grey desk surround, one white landscape sheet, near-black ink, hairline table rules with a lightly shaded header row, one engineering blue for the masthead bar, section numbers, the part's own curve and the current row, and red only where a rating is exceeded or a rule breaks. Barlow (a DIN-like engineering grotesk) for text, Barlow Semi Condensed for tables, part numbers and figure labels, tabular figures throughout; uppercase only in table heads, as datasheets set them. Furniture: a document line (part number, document title, revision date), page footers "n of 4", numbered sections, numbered figures and tables with captions, footnotes. Drawings are drawn: the pin diagram and the curves are SVG built from the data. Raised from the round's declined challengers: **Type is the material** (alphabet storm) – the part number and the tables carry the page, no ornament; **Known and attested** (provenance ribbon) – in the register map demonstrated controls carry a solid rule, attested ones a dashed hairline; **Colour is earned** (risograph) – one accent and red, nothing else; **Pages keyed by number** (teletext) – 1-4 jump to a page.

STORY: The reference design connects 7 of 34 pins for a patient summary, stays inside every absolute maximum rating, and its characteristics have MIN = TYP = MAX: the same answer every run. An AI model told the policy connects more pins, sometimes exceeds a rating (the trap job), and its MIN and MAX spread apart across five runs; its typical-characteristics curves show how its behaviour moves with what it was told. The baseline connects every pin, exceeds every rating, and its page loads climb with the hospital's size while the reference's barely move.

FIRST VIEWPORT: A thin viewer strip on the grey desk: three part tabs (Reference design, the AI model with a picker, Baseline), the job, what the model was told, and the four page tabs. The sheet below it: the masthead (part number `compliance-aware` set large in Semi Condensed with a blue bar, the part's title, document line at right); then three columns: 1 Features and 2 Applications; the pin configuration drawing (a package outline with 17 pins a side, the connected pins drawn solid and named in ink, the others grey, out-of-purpose connections red); 3 Device comparison (the reference, four models at the chosen briefing, the baseline; the current part tinted). Footer: document line and "1 of 4".

FORM: The Datasheet; first on our grounded list (the pick card in the round of seed key c8f5e5fe), chosen by the user. Build path: code-led (no image generation). Signature interaction: switching the part or what the model was told re-specifies the sheet in place: the pin diagram re-connects, MIN / TYP / MAX re-set, rows that exceed a rating turn red. **Finish pass, 2026-10-15** (user: "the content and ideology is fine. the layering, textures and quality isn't, refer to v2 for the level of finish and motion"):
- Material:
  - the desk is matte under a lamp: a soft pool of light and a slate fall-off;
  - the datasheet is a stack of sheets: the pages still to read lie beneath the one open, edge on edge, each sheet stepping 5px right and 1px down with its own hairline, so the stack says which page you are on;
  - the sheet has a fine paper tooth and a faint lamp gradient;
  - the masthead band is printed;
  - the chosen part is a white tab that slides along the part bar, and the page rule slides along the page index;
  - the comparison's current row is a blue wash that slides to the part chosen (no side stripe).
- Motion grammar, at v2's level, every move a recorded fact:
  - **paging:** the open sheet lifts over its top edge and away (760ms, in perspective, shading as it rises, casting on the page beneath, gone before it is edge-on); going back, the last sheet comes down again;
  - **each page then reads itself in:**
    - on the front page, the features and applications set in; the pin configuration draws its package outline, then each pin grows out of the package in its number order (1 down the left, 18 up the right), names after; the comparison rows set in with their readings printed;
    - the specifications set row by row, each MIN, TYP and MAX printed in turn, and a reading beyond a rating flashes red after it is printed;
    - the typical curves: grid and axes, the other series, then this part's curve traced;
    - the register map prints row by row and each backing is drawn under its control (solid, dashed, or a red strike);
  - **re-specifying** (another part, job or briefing): a print head runs down the sheet (840ms); above it the new datasheet, below it the last one, so no reading ever sits under the wrong part number; a reading beyond a rating flashes red as the head prints it, and this part's curve is traced once its chart is printed.
- Nothing counts up from zero: a reading is printed, never invented on the way.
- Space while a page plays lands it (as in v2); reduced motion lands every state whole; nothing moves once a step has landed.

FINISH: unreviewed and undocumented is unfinished; this build ends with the finish review, the verdict, DESIGN.md, and every shipping raster carrying its provenance. (The design record for this surface is `DESIGN-portal-v4.md` with `.impeccable/design-portal-v4.json`; `DESIGN.md` stays the Report's.)
