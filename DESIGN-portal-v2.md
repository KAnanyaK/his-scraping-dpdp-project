---
name: DPDP Pipeline Live Flow
description: The recorded pipeline run as a live data stream; the hospital drawn as 680 category-coloured values, each value a technique reads flying as a particle of light through its lane's Extract, Score, Export and Erase; dark product chrome, one offline file with Inter embedded.
colors:
  night: "#070a12"
  night-2: "#0b1019"
  ground-tint-teal: "rgba(46, 230, 201, .07)"
  ground-tint-violet: "rgba(150, 120, 255, .06)"
  panel: "rgba(255, 255, 255, .028)"
  panel-2: "rgba(255, 255, 255, .05)"
  hairline: "rgba(160, 175, 200, .13)"
  hairline-2: "rgba(160, 175, 200, .22)"
  text: "#edf2fa"
  text-2: "#aeb8c9"
  text-3: "#8792a6"
  nil: "#3a4558"
  tooltip: "#141b2a"
  lane-a: "#2ee6c9"
  lane-b: "#ff5cae"
  lane-c: "#ff9d4d"
  roundel-ink: "#06120f"
  breach: "#ff4d6a"
  lit: "#ffd84d"
  token: "#ffffff"
  next-key-low: "#dfe7f1"
  next-key-ink: "#08110f"
  cat-direct-identifier: "#b392ff"
  cat-quasi-identifier: "#e5d0ff"
  cat-contact: "#6cb6ff"
  cat-clinical: "#4be38a"
  cat-financial: "#ffd447"
  cat-administrative: "#9aa7bb"
typography:
  kpi-value:
    fontFamily: "Inter, \"Segoe UI Variable Text\", \"Segoe UI\", system-ui, sans-serif"
    fontSize: "1.25rem"
    fontWeight: 650
    lineHeight: 1
    letterSpacing: "-0.02em"
    fontFeature: "\"cv11\", \"ss01\", \"tnum\""
  readout-figure:
    fontFamily: "Inter, \"Segoe UI Variable Text\", \"Segoe UI\", system-ui, sans-serif"
    fontSize: "1.0625rem"
    fontWeight: 650
    lineHeight: 1.15
    letterSpacing: "-0.01em"
    fontFeature: "\"cv11\", \"ss01\", \"tnum\""
  section-title:
    fontFamily: "Inter, \"Segoe UI Variable Text\", \"Segoe UI\", system-ui, sans-serif"
    fontSize: "1.125rem"
    fontWeight: 650
    letterSpacing: "-0.015em"
  brand:
    fontFamily: "Inter, \"Segoe UI Variable Text\", \"Segoe UI\", system-ui, sans-serif"
    fontSize: "1rem"
    fontWeight: 650
    letterSpacing: "-0.01em"
  patient-id:
    fontFamily: "Inter, \"Segoe UI Variable Text\", \"Segoe UI\", system-ui, sans-serif"
    fontSize: "1rem"
    fontWeight: 650
    letterSpacing: "0.01em"
  lane-name:
    fontFamily: "Inter, \"Segoe UI Variable Text\", \"Segoe UI\", system-ui, sans-serif"
    fontSize: "0.9375rem"
    fontWeight: 650
    letterSpacing: "-0.01em"
  body:
    fontFamily: "Inter, \"Segoe UI Variable Text\", \"Segoe UI\", system-ui, sans-serif"
    fontSize: "0.875rem"
    fontWeight: 400
    lineHeight: 1.4
    fontFeature: "\"cv11\", \"ss01\", \"tnum\""
  job-tab:
    fontFamily: "Inter, \"Segoe UI Variable Text\", \"Segoe UI\", system-ui, sans-serif"
    fontSize: "0.84375rem"
    fontWeight: 550
  secondary:
    fontFamily: "Inter, \"Segoe UI Variable Text\", \"Segoe UI\", system-ui, sans-serif"
    fontSize: "0.8125rem"
    fontWeight: 550
    lineHeight: 1.35
  metric-label:
    fontFamily: "Inter, \"Segoe UI Variable Text\", \"Segoe UI\", system-ui, sans-serif"
    fontSize: "0.8125rem"
    fontWeight: 550
  id-chip:
    fontFamily: "\"Cascadia Mono\", Consolas, \"SF Mono\", Menlo, ui-monospace, monospace"
    fontSize: "0.71875rem"
    fontWeight: 600
    lineHeight: 1
    letterSpacing: "0.01em"
rounded:
  cell: "1.6px"
  kbd: "0.3125rem"
  chip: "0.4375rem"
  tip: "0.5rem"
  control: "0.625rem"
  surface: "0.875rem"
  pill: "999px"
  round: "50%"
spacing:
  xxs: "0.125rem"
  xs: "0.25rem"
  sm: "0.375rem"
  md: "0.5rem"
  lg: "0.625rem"
  xl: "0.75rem"
  2xl: "1rem"
  gutter: "1.5rem"
components:
  status-pill:
    backgroundColor: "{colors.panel}"
    textColor: "{colors.text-2}"
    typography: "{typography.secondary}"
    rounded: "{rounded.pill}"
    height: "1.75rem"
    padding: "0 0.75rem 0 0.625rem"
  status-pill-running:
    backgroundColor: "{colors.panel}"
    textColor: "{colors.text}"
    rounded: "{rounded.pill}"
  model-picker:
    backgroundColor: "{colors.panel}"
    textColor: "{colors.text}"
    rounded: "{rounded.control}"
    height: "2.125rem"
    padding: "0 0.5rem 0 0.375rem"
  briefing-segment:
    backgroundColor: "{colors.panel}"
    textColor: "{colors.text-2}"
    rounded: "{rounded.control}"
    padding: "0.1875rem"
  briefing-option-active:
    backgroundColor: "{colors.lane-b}"
    textColor: "{colors.token}"
    rounded: "0.4375rem"
    height: "1.75rem"
    padding: "0 0.75rem"
  job-tab:
    textColor: "{colors.text-2}"
    typography: "{typography.job-tab}"
    padding: "0 0.75rem"
  job-tab-selected:
    textColor: "{colors.text}"
  roundel-a:
    backgroundColor: "{colors.lane-a}"
    textColor: "{colors.roundel-ink}"
    rounded: "{rounded.round}"
    size: "1.5rem"
  roundel-b:
    backgroundColor: "{colors.lane-b}"
    textColor: "{colors.token}"
    rounded: "{rounded.round}"
    size: "1.5rem"
  roundel-c:
    backgroundColor: "{colors.lane-c}"
    textColor: "{colors.roundel-ink}"
    rounded: "{rounded.round}"
    size: "1.5rem"
  lane-pipe:
    backgroundColor: "{colors.panel}"
    rounded: "{rounded.surface}"
    height: "clamp(3.5rem, 11vh - 1.75rem, 7rem)"
  kpi:
    textColor: "{colors.text}"
    typography: "{typography.kpi-value}"
    width: "5.25rem"
  patient-card:
    backgroundColor: "{colors.panel}"
    textColor: "{colors.text}"
    rounded: "{rounded.surface}"
    padding: "0.875rem 0.875rem 0.75rem"
  chip-token:
    backgroundColor: "rgba(255, 255, 255, .08)"
    textColor: "{colors.token}"
    typography: "{typography.id-chip}"
    rounded: "{rounded.chip}"
    height: "1.375rem"
    padding: "0 0.5rem"
  chip-raw:
    backgroundColor: "rgba(255, 77, 106, .22)"
    textColor: "{colors.token}"
    typography: "{typography.id-chip}"
    rounded: "{rounded.chip}"
    height: "1.375rem"
    padding: "0 0.5rem"
  chip-none:
    backgroundColor: "{colors.panel-2}"
    textColor: "{colors.text-2}"
    rounded: "{rounded.chip}"
    height: "1.375rem"
    padding: "0 0.5rem"
  transport-key:
    backgroundColor: "{colors.panel}"
    textColor: "{colors.text}"
    rounded: "{rounded.control}"
    size: "2.25rem"
  next-key:
    backgroundColor: "{colors.token}"
    textColor: "{colors.next-key-ink}"
    rounded: "{rounded.control}"
    height: "2.5rem"
    padding: "0 0.875rem 0 0.75rem"
  tooltip:
    backgroundColor: "{colors.tooltip}"
    textColor: "{colors.text}"
    rounded: "{rounded.tip}"
    padding: "0.4375rem 0.625rem"
---

# Design System: DPDP Pipeline Live Flow

## Overview

**Creative North Star: "Light That Means Something"**

Portal version 2 is the recorded pipeline run drawn as a live data stream on a night ground. The hospital is not a picture of a hospital; it is what the hospital holds, 20 patients by 34 fields, 680 values, each a small rounded cell in the colour of its DPDP data category. For the chosen job, every value a technique reads leaves its cell as a point of light, funnels through the gate's lock, and travels down its lane through four stretches: Extract, Score, Export, Erase. Every glow on the stage is a value or a verdict. Breaches happen in the stream, where the room can see them: a red halo on a value out of purpose, a raw identifier leaving red, the baseline's never-erased values sitting in one red frame at the end of its pipe.

The chrome around the stream is a dark product console in the register the user named (Linear, Vercel, Datadog live tail, Stripe data-flow heroes): hairline borders, faint glass panels, a status pill, metric labels over tabular numerals, a segmented control, one white key. The chrome is quiet so the data can be loud. It is one offline, self-contained file; Inter is embedded (variable WOFF2, OFL) by a user-approved exception to the Portal brief's no-web-fonts rule, so the file stays single and works with no network.

Density is presentation density for a projected 1366x768 laptop: four fixed frame rows, nothing scrolls on a laptop, figures large enough to read from the back of the room, words held to labels; the presenter explains.

**Key Characteristics:**
- Night ground with two faint radial tints; all colour on stage is data.
- Three lane accents (teal ours, pink the AI model, orange the baseline), six category colours, breach red, lit yellow for "here", white for tokens.
- One typeface, Inter, at weights 400 / 550 / 600 / 650 / 700, tabular numerals throughout.
- A canvas particle layer over a DOM frame; the canvas never carries text.
- Every step is a state the presenter lands on; motion only travels between states.

## Colors

A night palette where hue is reserved for meaning: lane identity, data category, breach, and the current position.

### Primary
- **Reference Teal** (lane-a): Lane A, ours. Its roundel, its hot KPI figures, its pipe's left-edge glow, the ring around every cell it took, "good" readouts (held, pseudonymised, within purpose), passed rule lamps, the "Run complete" status dot, text selection.
- **Model Pink** (lane-b): Lane B, the chosen AI model. Its roundel (white letter), KPI figures, pipe glow, cell rings; it also fills the active briefing segment, because the briefing is something told to lane B.
- **Baseline Orange** (lane-c): Lane C, the baseline. Roundel, KPI figures, pipe glow. Cells the baseline took get no ring; they only go hollow.

### Secondary: the six data categories
- **Identifier Violet** (cat-direct-identifier), **Quasi-identifier Lilac** (cat-quasi-identifier), **Contact Sky** (cat-contact), **Clinical Green** (cat-clinical), **Financial Gold** (cat-financial), **Administrative Slate** (cat-administrative). Each value's cell, particle and afterimage carry its category colour. The job bar's purpose key is the legend: allowed categories show their dot and name; out-of-purpose ones are struck through in breach red with a dimmed dot.

### Tertiary: signals
- **Breach Red** (breach): only for a breach. A soft red halo sprite around a value out of purpose or an identifier leaving raw, a red ring on its afterimage, the raw-identifier chip with its red glow, broken rule lamps, "Kept indefinitely", the never-erased frame, the trap flag dot on a job tab, struck-through categories.
- **Lit Yellow** (lit): "here". The gate bar and lock once the gate is passed, the discovery beam and its "modules found" line, the current stop name over the lanes, the spotlight wash over the current pipe stretch and its divider, the current stepper dot, the running status beacon, and the keyboard focus ring.
- **Token White** (token): an identifier that left as a keyed token is a white diamond, never a category dot; the token chip is white on faint glass. White is also the Next key and the outline around the followed patient's row.

### Neutral
- **Night** (night): the ground, behind two radial tints: teal at 72% / 46% (60% x 55%, 0.07) behind the lanes and violet at 12% / 40% (40% x 50%, 0.06) behind the hospital.
- **Night 2** (night-2): the lock's disc and the opaque phone transport.
- **Panel / Panel 2** (panel, panel-2): glass fills at 2.8% and 5% white for controls, the card and pipes; Panel 2 is hover.
- **Hairline / Hairline 2** (hairline, hairline-2): 13% and 22% blue-grey; Hairline separates frame rows and outlines surfaces, Hairline 2 outlines controls, stretch dividers and the stepper track.
- **Text / Text 2 / Text 3** (text, text-2, text-3): figures and names; subs and inactive tabs; metric labels and unlit stops.
- **Nil** (nil): the en dash a KPI shows before Extract.
- **Tooltip** (tooltip): the hover tip's fill.

### Named Rules
**The Honest Token Rule.** A token on the page is made by the project's own pseudonymiser with a fixed display key per technique (each export has its own key, so two lanes never show the same token for one patient), and the export audit that decides "token" or "raw" matches a number's digits only within one field.

**The 13px Floor Rule.** Everything the panel reads (metric labels, stage names, readouts, the card, the checks, identifier chips) is at least 0.8125rem, 13px at the 1366 root; only key caps, stepper labels and tooltips sit at 0.75rem. On a phone the stacked gate gives its four checks their own height, and the lock sits in the middle of its own bar.

**The Light Is Data Rule.** A glow on the stage is a value, a verdict or the current position. Particles, rule lamps and the raw chip glow; panels, cards and labels never do. Lit yellow's glow marks "here" (gate, current stretch divider, current stop) and nothing else. The one exception on chrome is the Next key's soft white lift, because it is the control pressed every step.

**The Lane Owns Its Hue Rule.** Teal, pink and orange name a lane wherever they appear: roundel, figures, pipe glow, cell ring, stepper fill. A lane colour is never used for a state that is not that lane's.

**The Red Is A Breach Rule.** Breach red appears only where a value, rule, identifier or retention breaks the purpose. A neutral warning or an emphasis never borrows it.

## Typography

**Display Font:** Inter (embedded variable WOFF2, weights 100-900; fallback Segoe UI Variable Text, Segoe UI, system-ui)
**Body Font:** Inter
**Label/Mono Font:** Cascadia Mono (platform face, fallback Consolas, SF Mono, Menlo) for identifier chips only

**Character:** One neutral product face carrying everything, tightened at display sizes (-0.02em) and set with tabular numerals and Inter's cv11 / ss01 alternates so counters climb without jitter. Hierarchy comes from size and weight steps of 50 (550, 600, 650), not from a second face.

### Hierarchy
- **KPI value** (650, 1.25rem, 1): page loads, patients and values read in each lane header; Nil before Extract, the lane's colour once counting.
- **Readout figure** (650, 1.0625rem, 1.2; an erase date 1rem, never wrapped): the figure under each stretch: values read, the score, identifiers tokenised, HL7 messages, the erase date.
- **Section title** (650, 1rem): "Hospital".
- **Brand / Patient id** (650, 1rem): the product name; the followed patient's masked record number.
- **Lane name** (650, 0.9375rem): Ours, the model's name, Baseline; also the Next key.
- **Body** (400, 0.875rem, 1.4): base text and the model select.
- **Job tab** (550, 0.84375rem): the four jobs.
- **Secondary** (550, 0.8125rem, 1.35): status, briefing options, hospital sub-line, discovery line, gate checks, module names, readout lines, the card's table, the hint.
- **Metric label** (550-600, 0.8125rem): KPI labels, the stop names over the lanes, the card's column heads; stepper labels and tooltip text at 0.75rem.
- **Id chip** (mono 600, 0.71875rem, 0.01em): the token or raw identifier.

### Named Rules
**The One Face Rule.** Inter for every word and figure; the only other face is the mono identifier chip. Inter is embedded, so the projected room sees what was designed.

**The Tabular Figures Rule.** Every number on the page uses tabular figures and a fixed-width column (each KPI figure right-aligned in a 3.25rem cell, each column a fixed minimum width) so a counter climbing from 0 to 680 never shifts its neighbours.

## Layout

The frame is a four-row grid filling the viewport (100dvh), no page scroll on a laptop: the product bar (3.5rem), the job bar (2.875rem), the stage (the rest), the transport (4rem). Bar, job bar and transport share a 1.5rem side gutter and are divided by hairlines.

- **Product bar:** brand mark and name, the status pill, then right-aligned the model picker and the three-way briefing segment.
- **Job bar:** four job tabs on the left (the selected one underlined in Text, 2px), the purpose and its six-category key on the right.
- **Stage:** three columns, hospital (24.5rem), gate (8.5rem), lanes (the rest), padded 1rem 1.5rem 0.75rem. A full-stage canvas sits above all three so particles cross the column boundaries.
- **Hospital column:** title line, the module labels over their column groups (7px gaps between modules), the matrix (`clamp(12.5rem, 30vh - 3rem, 19rem)` tall, growing on tall screens; pitch fitted to width and height, cells 74% of the pitch), then the patient card.
- **Gate column:** a 2px vertical bar with the lock placed level with the middle of the hospital matrix, and the four checks stacked at its top.
- **Lanes column:** a stop row (Extract, Score, Pseudonymise, Shape, Export, Erase) and three lanes, vertically centred and separated by hairlines. A lane's pipe and its readout row split at 24 / 16 / 15 / 15 / 15 / 15% (one `SEG` table drives the stops, the dividers, the readouts and the canvas).

Scaling is in rem off one root clamp, `clamp(14.5px, 0.5vw + 9px, 18px)` (about 15.8px at 1366 wide, 16.7px at 1536, 18px at 1920), so the frame, the matrix and the canvas geometry grow together; sized for the presenting laptop (2026-10-12: "this will only be presented on my laptop"). The bars are 3.25rem (product), 2.625rem (jobs) and 3.5rem (transport).

## Elevation & Depth

Depth is light on dark, not shadow. Surfaces are glass: a top-to-bottom white gradient of 4.5% to 1-2% over the night ground, with a hairline. Layers stack as ground, frame, then the additive particle canvas (composited with "lighter", so overlapping values brighten into a mass). The few shadows are light, not lift.

### Shadow Vocabulary
- **Gate lit** (`0 0 14px rgba(255,216,77,.7), 0 0 40px rgba(255,216,77,.25)`): the gate bar once passed.
- **Current stretch divider** (`0 0 10px rgba(255,216,77,.5)`): the divider the values are crossing.
- **Current stop** (`0 0 0 4px rgba(255,216,77,.18), 0 0 16px rgba(255,216,77,.7)`): the stepper's current dot.
- **Running beacon** (`0 0 0 0 -> 7px rgba(255,216,77,.6 -> 0)`, 1.1s): the status dot while a step plays.
- **Rule lamp** (`0 0 6px rgba(46,230,201,.7)`; broken `0 0 8px rgba(255,77,106,.9)`).
- **Raw identifier** (`inset 0 0 0 1px rgba(255,77,106,.7), 0 0 14px -2px rgba(255,77,106,.7)`).
- **Next key** (`0 0 0 1px rgba(255,255,255,.4), 0 6px 14px -6px rgba(0,0,0,.6)`): the one key that is pressed every step; it lifts with a plain shadow, not a glow.
- **Stepper fill** (`0 0 12px rgba(255,255,255,.25)`).
- **Tooltip** (`0 12px 30px -10px rgba(0,0,0,.7)`): the only dark shadow.

### Named Rules
**The Glass Not Card Rule.** Panels are glass over the ground with a hairline; none is lifted by a dark shadow. The tooltip is the one floating element.

## Shapes

Soft, small, consistent radii on a product console: data cells nearly square (1.6px), chips 0.4375rem, controls and keys 0.625rem, the pipes and the patient card 0.875rem, status pill and brand tag fully round, roundels and every dot circular. The gate is a straight 2px bar; the lock is a circle. Particles are round light sprites; the one other particle form is the token diamond. The kept block is a grid of small squares inside one rounded (4px) red frame.

## Components

### The hospital matrix (signature)
Twenty rows by 34 columns in five module groups (Registration, Clinical, Orders, Billing, Audit) labelled above with an underline that whitens as the crawler finds each one. Before Acquire every cell sits dim (34% opacity); the discovery beam, a 52px yellow gradient, sweeps left to right over 1.25s and lights cells behind it (82%) and the "N modules found in M page loads" line. The followed patient's row is outlined in white (1.2px, 3px radius) with a white pointer at its left. A cell flashes white with a lane-coloured edge as its value leaves; once read it is **hollow** (fill 14%, outline 42%) and, if ours or the model took it, ringed tightly (1.3px, 0.9px out) in that lane's colour. The hospital visibly drains under the baseline.

### The gate
A 2px bar in Hairline 2 that turns lit yellow with its glow when the gate is passed; its circular lock (1.75rem, Night 2 fill, padlock drawn in SVG) turns yellow with it. Four checks (TLS observed, robots.txt, Authorised, Signed in) tick in at 0.22s intervals, from 35% opacity to Text with a teal check. Every value's flight passes through the lock, which acts as a funnel.

### Lanes
- **Header row:** roundel (1.5rem, lane colour, letter A/B/C), lane name, a one-line sub (ellipsised; a model lane says "told the policy · run 1 of 5"), then three KPI columns that read as one line: a 1.5rem figure right-aligned in a 3.25rem cell, its words beside it in Text 3 ("page loads", "patients" or "rows, unnamed", "values read"). Each column has a fixed minimum width, so the three lanes' figures stack.
- **Separation:** lanes are spaced `clamp(0.875rem, 2.6vh - 0.35rem, 2rem)` apart with a hairline between them, so each technique reads as its own group.
- **Pipe:** a glass tube (height `clamp(3.5rem, 13vh - 2.6rem, 7.5rem)`, growing on tall screens, 0.875rem radius, hairline) with the lane's colour glowing in from the left edge (to 22%, 14% opacity), three dividers at 40/60/80%, and a faint yellow spotlight over the stretch now playing.
- **Pseudonymise and Shape (the stages between the rules and the export):** at Pseudonymise an identifier becomes a white diamond (a keyed token) and a quasi-identifier a hollow ring in its colour (generalised: date of birth to year, PIN to 3 digits); a lane that does not pseudonymise keeps its identifiers with a red halo and reads "left raw". At Shape the values regroup into one envelope per module (a faint outline), the way each module is shaped into its own HL7 v2 messages and FHIR resources; the readout carries the exact counts. Envelopes drawn there stay as quiet outlines; at Export one more outline frames the whole file, red when raw identifiers left.
- **Erase:** values glide in whole. Erased: each then dissolves where it stands (fades, shrinks, rises 6px). Never erased: the block cross-fades into a still miniature of the hospital (rows by fields) while its red frame draws itself in; the readout says "Never erased".
- **Readouts:** under each stretch, fading in as that lane's values arrive: Extract (values and needed fields; "all within purpose" in teal or "N out of purpose" plus the trap tally in red), Score (score, seven rule lamps lighting 70ms apart from 120ms, verdict, and for a model the five-run mean), Export (the identifier chip and "pseudonymised" or "N raw ids out"), Erase (the date and retention, or "Kept indefinitely").

### Particles (signature)
- **Sprite:** a cached radial gradient per colour: white core, the colour at 16%, 42% alpha at 38%, transparent at the edge.
- **Flight:** 0.75s per value, staggered by the lane's page loads (each page load 0.045s), in three legs: a curve from the cell to the gate's lock (first 40%), down or up beside the gate to the lane's level (to 74%), then level into the pipe's mouth and on to its place. Near the lanes a value only travels at pipe height. A short trail (the last 9% of the path, half alpha) follows it.
- **Arrangement:** inside a stretch a few values sit in one even row; many fill column by column, grouped by data category with the values out of purpose last, so a dense cluster reads as bands of colour ending in one red block (never moiré). The kept miniature alone keeps the hospital's own row-by-field order.
- **Density scaling:** glow per value scales by `clamp(sqrt(36 / n), 0.2, 1)` and the halo shrinks above 120 values, so the baseline's 680 read as a mass, not a white-out.
- **Moves:** between stretches each value eases over 0.9s. A block slides as one wave, its leading edge first (the stagger is by position, never by hospital order, so nothing crosses); into Shape the values go module by module, the one regrouping in the run. Only a value flying out of the hospital glows at full strength; a lane moving together is dimmed by its density, so the baseline never smears.
- **Afterimages:** each stretch a value has left keeps a still trace at 16%; a value out of purpose, or an identifier that left raw, keeps a red ring; a token keeps a dim white diamond.
- **Breach halo:** a red sprite around a value out of purpose or a raw identifier, pulsing gently.
- **Tokens:** at Export an identifier that is pseudonymised becomes a white diamond with a soft white glow.
- **Erase:** a lane with an erase date dissolves (fades, shrinks to 45%, rises 7px). A lane with none lands its values as a crisp miniature of the hospital (rows by fields, squares, raw identifiers in red) inside one glowing red frame.

### Patient card
Glass, 0.875rem radius, 1px hairline. The masked record number (1rem, 650) and masked name, then a five-column table: technique (with a small roundel), Theirs, Others, Leaves as, Kept until. Each cell shows an en dash until that lane reaches the stage, then flips in (0.45s); token in teal, raw id and never in red.

### Buttons and controls
- **Shape:** 0.625rem radius, Hairline 2 border, Panel fill; Panel 2 on hover.
- **Next key:** the one solid white control, a white-to-#dfe7f1 gradient with dark ink, play glyph, label (Start / Next / Again) and a Space kbd; pure white on hover, 1px down on press.
- **Transport keys:** 2.25rem square, Home and Back glyphs drawn as SVG.
- **Focus:** a 2px lit-yellow outline, 2px offset, on every control.

### Chips
- **Token:** mono, white on 8% white with a 1px white inset at 35%.
- **Raw:** mono, white on breach red at 22% with a red inset and red glow.
- **None:** "no identifier" in Inter on Panel 2.

### Navigation
- **Status pill:** Ready (grey dot), Running (yellow beacon), At a stop (yellow dot), Run complete (teal dot, teal-tinted border).
- **Model picker:** a lane-B roundel then a native select with a drawn chevron.
- **Briefing segment:** three options in a glass track; the active one is filled with a pink gradient and a pink inset ring.
- **Job tabs:** text tabs; selected in Text with a 2px underline; the trap job carries a red dot.
- **Stepper:** nine stops on a hairline track (Hospital, Gate, Acquire, Extract, Score, Pseudonymise, Shape, Export, Erase); done stops white, the current stop lit yellow with its halo; the fill runs teal to pink to orange as the run advances.

### Motion
One ease, `cubic-bezier(.16, 1, .3, 1)`. Step lengths: Gate 1.35s, Acquire 1.5s, Extract the slowest lane's page loads plus 1s, Score, Pseudonymise and Export 1.6s, Shape 1.9s, Erase 2.3s. Readouts fade in as a lane arrives; the rule lamps light 70ms apart; ticket-style card values flap in.

## Do's and Don'ts

### Do:
- **Do** draw every value from the recorded run: a lane's flight time is its recorded page loads at 0.045s each, and its particles are the cells that run read.
- **Do** keep the category colour on a value from cell to particle to afterimage; only tokenisation (white diamond) or a raw identifier at the never-erased block (red) changes it.
- **Do** route every value through the gate's lock and keep it at pipe height near the lanes.
- **Do** keep KPI figures at 1.25rem and readout figures at 1.0625rem, tabular, in fixed-width columns.
- **Do** scale everything from the root clamp in rem so the projected 1366x768 frame and a 1920 screen keep the same composition.
- **Do** keep the file single and offline: Inter embedded, canvas, SVG and CSS only.

### Don't:
- **Don't** put glow, gradients or colour on chrome that does not carry a value, a verdict or the current position.
- **Don't** set anything the panel reads below 0.8125rem (13px at the 1366 root).
- **Don't** use a lane colour for anything but its lane, or breach red for anything but a breach.
- **Don't** show a raw identifier, contact detail or quasi-identifier; the patient's record number and name are masked and the builder audits the output.
- **Don't** add explanatory prose to the stage; labels and figures only, the presenter explains.
- **Don't** let a dense lane white out: keep the density scaling and the smaller halo above 120 values.
