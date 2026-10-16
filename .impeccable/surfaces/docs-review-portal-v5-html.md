---
version: 1
slug: "docs-review-portal-v5-html"
primary_target: "docs/review/portal-v5.html"
related_targets: ["tools/portal_v5/portal.html","tools/portal_v5/portal.css","tools/portal_v5/record.js","tools/build_portal_v5.py","tools/portal_record.py"]
---

## Scope

`docs/review/portal-v5.html`, **Portal version 5, The Redacted Record**: one patient's record, and what each technique did with it, for the Review-III panel (26.10.2026, projected 1366x768) and later offline readers. Mode: Experience. Built by `tools/build_portal_v5.py` from `tools/portal_v5/` and the shared record `tools/portal_record.py`; one offline file with Source Serif 4 (OFL, weight + optical size, user-approved 2026-10-12) embedded. v1-v4 stay as they are.

From the direction round of 2026-10-12 (`docs/review/portal-v3-brief.md`): offered The Catalogue, The Datasheet and The Redacted Record, the user answered "actually do all 3 one by one and label v3, v4 and v5"; on 2026-10-15: "make the v3 bit more catchy and feel and color, then start working on v4 and v5".

Audience and job: the panel sees privacy as what stays covered. One patient (the one the single-patient jobs are about), three readers (ours, an AI model at a briefing, the baseline), four jobs. Constraints: every figure and value from the recorded run computed by the project's code; identifiers, contact details and quasi-identifiers appear only masked (the builder audits with v1's `check`); no vendor names; no link to the Report; 13px floor; keyboard path; reduced motion lands every state; no lanes, dots, flows, metro, dark neon, KPI tiles; not a second evidence report.

## Direction contract

THESIS: Privacy is what stays covered. One patient's record is typeset as a real document in a case folder, every value under a redaction bar; choosing who read it lifts exactly the bars that run read, field by field; the copy that left the hospital is a second leaf, with a token where the record number was, and on its erase date the copy empties; a third leaf is the record's access slip, every reading of this record as the patient would be told. It refuses the dashboard, the pipeline diagram and the race: there is one person on the page.

OWN-WORLD: A records room: a slate desk (#3a4651), a manila case folder (#dfc58c, darker edge) with index tabs on its right edge (one per reader), a white record sheet set in Source Serif 4 with real typographic hierarchy (a letterhead line, the masked record number, module sections in small caps, label and value lines on hairline rules), redaction bars in near-black, red (#b8322a) only for a breach -- a red pencil stroke under a value read outside the purpose, red ink for an identifier that left raw and for a copy never destroyed -- and rubber-stamp ink (#33479a) for the copy's destruction stamp. Behind the sheet, the edges of the other 19 patients' records. No cards, no glow; shadows only where paper or the folder lies on the desk; gradients only as light on a material (the lamp on the desk, the folder, the sheet), never as decoration.

STORY: The record starts covered: 34 lines, nothing read. Ours lifts the 7 lines the patient summary needs and nothing else; the model lifts a few more; the baseline lifts every line, and the 19 records behind it slide out too. On the copy, ours left a token and a birth year, stamped to be destroyed on 10 Nov 2026; turn to that date and the copy empties. The baseline's copy carries the record number and the name as they were read, stamped in red: no destruction date. The access slip lists every reading of this record: who, for what, how much, how it left, when it goes.

FIRST VIEWPORT: A thin top bar on the desk (the title "One patient's record", the job, the model and what it was told). Centre-left: the manila folder, its open sheet with the letterhead line, "MRN*****10" and the patient's masked name, then two columns of module sections with every value under a bar; the stack of other records' edges behind. On the folder's right edge three index tabs: a Ours, b the model, c Baseline. To the right on the desk, the reading card: a large count ("0 of 34 lines read" before a reader is chosen), the reader's facts below. Bottom bar: the three leaves (The record, The copy, The slip) and the Space key.

FORM: The Redacted Record; second on our grounded list (round seed key c8f5e5fe), chosen by the user. Build path: code-led. Signature interaction: choosing a reader lifts the bars over exactly the lines that run read (each bar slides away from its value, staggered down the page), and on the copy, turning to the erase date empties the sheet. **Finish pass, 2026-10-15 (user: "the content and ideology is fine. the layering, textures and quality isn't, refer to v2 for the level of finish and motion"):**

Material:
- the slate desk lies under a warm lamp (a soft pool and a dark fall-off, with fine dust);
- the manila folder has its fibre, its light and a real shadow on the desk; its index tabs are fibred, and the chosen tab comes forward;
- the sheet, the 19 other records and the reading card are grained paper with shadows;
- the redaction bars are marker ink: ragged at the ends, with a slight sheen;
- the destruction stamp is worn rubber-stamp ink (masked), multiplied into the paper;
- a manila marker slides along the leaf index.

Motion grammar, at v2's level, every move a recorded fact:
- **opening the record** lays a bar over every value, module by module;
- **choosing a reader** lifts exactly the bars that run read, in a wave down the page. The card counts each line as its bar comes off, the red pencil is drawn under an out-of-purpose value once its bar is up, and the other records fan out behind the folder;
- **turning a leaf**: the top sheet is lifted and put aside to the left (600ms, opaque, at most 2 degrees), the next lying beneath; going back, the finished sheet is laid on again and nothing replays; a reader, job, model or briefing on the same leaf re-sets in place;
- **the copy** sets in line by line, a token flashes in stamp ink where the record number was, and the destroy-after stamp comes down (the sheet takes the blow);
- **E** stamps "Destroyed" and the copy's lines go out one by one down the sheet;
- **the slip** writes each reading in turn, its date stamped. The card counts the readings as they are written, and its breakdown waits for the count.

Space while a step plays lands it (as in v2). Reduced motion lands every state whole. Nothing moves once a step has landed.

FINISH: unreviewed and undocumented is unfinished; this build ends with the finish review, the verdict, DESIGN.md, and every shipping raster carrying its provenance. (The design record for this surface is `DESIGN-portal-v5.md` with `.impeccable/design-portal-v5.json`; `DESIGN.md` stays the Report's.)
