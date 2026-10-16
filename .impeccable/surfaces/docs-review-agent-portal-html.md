---
version: 1
slug: "docs-review-agent-portal-html"
primary_target: "docs/review/agent-portal.html"
related_targets: ["tools/agent_portal/agent.html","tools/agent_portal/agent.css","tools/agent_portal/agent.js","tools/build_agent_portal.py"]
---

# HIS Staff Assistant portal (docs/review/agent-portal.html)

Scope: a new standalone surface for Review-III (26.10.2026). It is the staff-guidance assistant (`src/agent/`) as its own portal. Mode: **Operate**.

Audience and job:
- The review panel follows a presenter on the presenting laptop (1366x768); later, examiners use it alone.
- Inside the fiction, the users are hospital staff: reception, nurse and administrator.
- The job: ask the assistant for an HIS task in plain words (the live walkthrough), or play one pre-run tour per role.
- Beside the conversation, the page shows how the request moves through the assistant:
  - understood (which task, from which words);
  - the DPDP check for this role, before any detail is asked;
  - the details collected, each one shape-checked;
  - the steps placed on the HIS screens the crawler found;
  - the answer.
- A replica of the HIS screen lights the module, column and button each step uses.

Constraints (user, 2026-10-16):
- Commands and instructions only assist with HIS tasks: the engine's 31 functions, plus help, cancel and "what changed". Anything else is turned away politely, with the role's tasks offered instead.
- Named "HIS Staff Assistant". It is rule-based with no AI model; one quiet technical note says so.
- The engine is the Python agent's own. The builder takes its tables, the step placements and the navigation map from `src/agent/` and `docs/benchmark_results/navigation-map.json`. On open, the page's port replays every recorded Python conversation; on any mismatch, typing is switched off and the tours run from the recorded transcripts.
- No patient value anywhere: inputs are the registry's own examples, and the replica's rows are blank placeholders.
- Offline single file, with Atkinson Hyperlegible Next embedded (OFL, user-approved 2026-10-16).
- 13px floor; keyboard path; reduced motion lands every state; clean at 1280/1366/1440/1920/390.
- Elegant and professional (the standing bar); no vendor names; no link to the Report.

## Direction contract

THESIS: Every request is a route through the hospital's own screens.
- The assistant is the enquiry desk.
- The DPDP check is the staff-only door.
- The HIS modules are colour-coded departments.
- The answer is a set of signs that lead to the exact screen and button.

It refuses the chatbot with a side panel, and the node-graph "AI pipeline".

OWN-WORLD: Hospital wayfinding signage.
- Ground: a pale cool corridor wall.
- Signs: navy panels with white Atkinson Hyperlegible Next.
- Departments: five colours, each shown as a square pictogram tile: Registration blue, Clinical green, Orders violet, Billing amber, Audit slate.
- State colours: no-entry red only for a refusal; clear green only for a passed check.
- Pictograms: one family, drawn and stroked, never glyphs. Arrows are drawn too.
- Sign corners 6px.
- No decorative gradient, no glass, no side stripes. A shadow appears only where a sign stands off the wall.

Raises:
- Split-flap: stage signs hold fixed positions, and only their state changes.
- Event catalog: directory and map are one space; each step's tag jumps to its spot on the replica.
- Ticket wallet: nothing disappears; refused or cancelled requests stay on the desk, stamped.
- Monochrome product: every instruction is paired with the screen that proves where it happens.
- Star atlas: one fixed ramp of emphasis for stage states (waiting, passing, passed, stopped).

STORY:
- The visitor puts on a staff badge and asks in their own words, or plays that badge's tour.
- They watch the route light up:
  - understood, with the words it matched on;
  - the staff-only door, three rules checked for this badge before any detail is asked;
  - the details, each shape-checked;
  - the department;
  - the destination screen, with its column and button lit.
- They come away believing three things: it helps only with HIS work, it refuses outside the role with the rule cited, and it never guesses a screen.

FIRST VIEWPORT (1366x768):
- A navy sign band across the top holds the information pictogram, "HIS Staff Assistant", the three staff badges, "Tour", and the live state.
- Below it, two columns.
- Left (about 42%), the enquiry desk:
  - a welcome sign with the badge's common tasks;
  - the conversation;
  - the input bar, focused on load.
- Right (about 58%), the route:
  - a fixed row of five stage signs joined by drawn arrows (Enquiry, Staff only, Details, Department, Screen);
  - under it, the active stage's board;
  - under that, the replica HIS screen.

FORM: Hospital Wayfinding.
- Third on our grounded list, ordered: Surgical Safety Checklist, clinical algorithm card, hospital wayfinding, SBAR handover, lab requisition, illustrated instruction manual, token display.
- Assigned by the roll, seed key 0e7fd19e. Code-led, since no image generation is available.
- Signature interaction: a request walks the route. Stage signs light as the engine decides, the door's rules tick one by one, and the route line is drawn to the department. The replica then lights the step's column and button. Clicking a step on the desk moves the replica to it.
- Motion: state changes take 160-240ms, and a full route takes about 1.2s. Space or Enter lands it. Nothing moves at rest.

FINISH: unreviewed and undocumented is unfinished; this build ends with the finish review, the verdict, DESIGN.md, and every shipping raster carrying its provenance. (The design record for this surface is `DESIGN-agent-portal.md` with `.impeccable/design-agent-portal.json`; `DESIGN.md` stays the Report's.)
