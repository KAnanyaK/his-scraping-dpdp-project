---
version: 1
slug: "docs-review-agent-portal-html"
primary_target: "docs/review/agent-portal.html"
related_targets: ["tools/agent_portal/agent.html","tools/agent_portal/agent.css","tools/agent_portal/agent.js","tools/build_agent_portal.py"]
---

# HIS Staff Assistant portal (docs/review/agent-portal.html)

Scope: a standalone surface for Review-III (28.10.2026). It is the staff-guidance assistant (`src/agent/`) as its own portal. Mode: **Operate**.

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

Constraints (user, 2026-10-16, still binding):
- Commands and instructions only assist with HIS tasks: the engine's 31 functions, plus help, cancel and "what changed". Anything else is turned away politely, with the role's tasks offered instead.
- Named "HIS Staff Assistant". It is rule-based with no AI model; one quiet technical note says so.
- The engine is the Python agent's own. The builder takes its tables, the step placements and the navigation map from `src/agent/` and `docs/benchmark_results/navigation-map.json`. On open, the page's port replays every recorded Python conversation; on any mismatch, typing is switched off and the tours run from the recorded transcripts.
- Reply wording is never changed (it is self-checked); presentation only.
- No patient value anywhere: inputs are the registry's own examples, and the replica's rows are blank.
- Offline single file. 13px floor; keyboard path; reduced motion lands every state; clean at 1280/1366/1440/1920/390.
- Elegant and professional (the standing bar); no vendor names; no link to the Report.

Rework, 2026-10-23 (user: "rework the UI of the agent portal, i feel it could be a bit more elegant and professional, you could take inspiration from portal v2 for theme"). The user pinned the world (Portal v2's dark product console) and chose, in one round: Inter like v2 (replaces Atkinson Hyperlegible Next), the HIS screen as a dark schematic, and the route as a v2-style stepper. The composition (desk + route + board + replica, one tour per badge) is kept from the 2026-10-16 build, so no concept roll was run.

## Direction contract

THESIS: A staff request is a run through the assistant, and only what the run decided gives off light. It refuses the light signage panel and the chatbot-with-a-sidebar.

OWN-WORLD: Portal v2's console. Night ground `#070a12` with two faint radial tints; glass panels at 2.8-5% white with 13%/22% hairlines; Inter (embedded, tabular figures); lit yellow `#ffd84d` only for "here" (the current stop, the button to press, focus); teal for a check passed; breach red only for the staff-only door shut; five department hues, brightened for night; white for the one key pressed most (Ask). Drawn icons in one 1.75 stroke. No texture, no glow on chrome.

STORY: The visitor picks a badge, asks in their own words or plays the tour, and watches the stepper advance: understood, the door's three rules, details, department, screen. The schematic screen then lights the columns and the button. They leave believing it helps only with HIS work, refuses outside the role with the rule cited, and never guesses a screen.

FIRST VIEWPORT (1366x768): a 3.25rem product bar (mark, name, status pill, badge segment with task counts, Tour key). Below, two columns. Left 42%: the desk as one glass panel (conversation, common tasks, the input with a white Ask key). Right 58%: the five-stop stepper on a hairline track, then the stage board (glass), then the schematic HIS screen. A quiet foot bar holds the rule-based note and keys.

FORM: user-pinned world (Portal v2 Live Flow, DESIGN-portal-v2.md), translated to the assistant; composition kept from Hospital Wayfinding (seed 0e7fd19e). Signature: the stepper fills stop by stop (190ms apart), the track filling behind it; on Screen the schematic's columns light in the department hue and the pressed button rings yellow. Motion 160-280ms, no overshoot; Space lands it.

FINISH: unreviewed and undocumented is unfinished; this build ends with the finish review, the verdict, DESIGN.md, and every shipping raster carrying its provenance. (The design record for this surface is `DESIGN-agent-portal.md` with `.impeccable/design-agent-portal.json`; `DESIGN.md` stays the Report's.)
