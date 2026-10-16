---
name: DPDP Pipeline Portal
description: The recorded pipeline run drawn as a metro line map; three straight lines (ours, an AI model, the baseline) through seven stations, Hospital to Erased, each calling at one square per page load between Acquire and Extract; one offline file.
colors:
  paper: "#ffffff"
  ink: "#101418"
  ink-2: "#39414a"
  ink-3: "#5a636c"
  navy: "#0b1f3a"
  navy-2: "#163463"
  navy-3: "#24477d"
  on-navy: "#ffffff"
  on-navy-2: "#b9c7dc"
  line-a: "#00a091"
  line-b: "#d1006f"
  line-c: "#f28c00"
  line-a-ink: "#00766b"
  line-b-ink: "#b0005d"
  line-c-ink: "#a85d00"
  zone-1: "#fff6d6"
  zone-2: "#e6f2fc"
  zone-3: "#fde8f1"
  zone-1-ink: "#7a5a00"
  zone-2-ink: "#1a5c8c"
  zone-3-ink: "#a3245c"
  disruption: "#e10600"
  disruption-ink: "#c40500"
  disruption-edge: "#9a0400"
  lit: "#ffe36e"
  signal: "#ffcc00"
  signal-hover: "#ffd83d"
  cat-direct-identifier: "#6a2c91"
  cat-quasi-identifier: "#a07fd2"
  cat-contact: "#1f78c8"
  cat-clinical: "#1e9b4f"
  cat-financial: "#e0a100"
  cat-administrative: "#7d8790"
  ticket-rail: "#eef1f5"
  ticket-rule: "#d5dbe2"
  ticket-row-rule: "#edf0f3"
  perforation: "#cdd5de"
  unreached: "#b4bdc8"
  chip-none: "#e4e8ec"
typography:
  ticket-id:
    fontFamily: "Bahnschrift, \"DIN Alternate\", \"Roboto Condensed\", \"Arial Narrow\", Arial, sans-serif"
    fontSize: "1.85rem"
    fontWeight: 600
    lineHeight: 1
    letterSpacing: "0.02em"
  page-loads:
    fontFamily: "Bahnschrift, \"DIN Alternate\", \"Roboto Condensed\", \"Arial Narrow\", Arial, sans-serif"
    fontSize: "29px"
    fontWeight: 600
    lineHeight: 1
    letterSpacing: "-0.005em"
  score:
    fontFamily: "Bahnschrift, \"DIN Alternate\", \"Roboto Condensed\", \"Arial Narrow\", Arial, sans-serif"
    fontSize: "23px"
    fontWeight: 600
    lineHeight: 1
  station-name:
    fontFamily: "Bahnschrift, \"DIN Alternate\", \"Roboto Condensed\", \"Arial Narrow\", Arial, sans-serif"
    fontSize: "17.5px"
    fontWeight: 600
    lineHeight: 1.2
    letterSpacing: "0.005em"
  line-name:
    fontFamily: "Bahnschrift, \"DIN Alternate\", \"Roboto Condensed\", \"Arial Narrow\", Arial, sans-serif"
    fontSize: "16px"
    fontWeight: 600
    lineHeight: 1.2
  zone-label:
    fontFamily: "Bahnschrift, \"DIN Alternate\", \"Roboto Condensed\", \"Arial Narrow\", Arial, sans-serif"
    fontSize: "14px"
    fontWeight: 600
    lineHeight: 1.2
    letterSpacing: "0.01em"
  brand:
    fontFamily: "Bahnschrift, \"DIN Alternate\", \"Roboto Condensed\", \"Arial Narrow\", Arial, sans-serif"
    fontSize: "1.22rem"
    fontWeight: 600
    lineHeight: 1
    letterSpacing: "0.01em"
  signage-label:
    fontFamily: "Bahnschrift, \"DIN Alternate\", \"Roboto Condensed\", \"Arial Narrow\", Arial, sans-serif"
    fontSize: "0.92rem"
    fontWeight: 600
    lineHeight: 1
    letterSpacing: "0.01em"
  ticket-value:
    fontFamily: "Bahnschrift, \"DIN Alternate\", \"Roboto Condensed\", \"Arial Narrow\", Arial, sans-serif"
    fontSize: "0.95rem"
    fontWeight: 600
    lineHeight: 1.2
  reading:
    fontFamily: "\"Segoe UI Variable Text\", \"Segoe UI\", system-ui, -apple-system, Roboto, Arial, sans-serif"
    fontSize: "13px"
    fontWeight: 700
    lineHeight: 1.2
  sub:
    fontFamily: "\"Segoe UI Variable Text\", \"Segoe UI\", system-ui, -apple-system, Roboto, Arial, sans-serif"
    fontSize: "13px"
    fontWeight: 400
    lineHeight: 1.3
  body:
    fontFamily: "\"Segoe UI Variable Text\", \"Segoe UI\", system-ui, -apple-system, Roboto, Arial, sans-serif"
    fontSize: "0.9rem"
    fontWeight: 400
    lineHeight: 1.35
  id-chip:
    fontFamily: "\"Cascadia Mono\", Consolas, \"SF Mono\", Menlo, ui-monospace, monospace"
    fontSize: "12px"
    fontWeight: 600
    lineHeight: 1
rounded:
  key-cap: "4px"
  zone-num: "4px"
  briefing: "5px"
  tip: "6px"
  zone-stamp: "6px"
  briefing-track: "7px"
  next-key: "8px"
  ticket: "12px"
  pill: "999px"
spacing:
  xs: "4px"
  sm: "6px"
  md: "10px"
  lg: "16px"
  xl: "20px"
  xxl: "26px"
  root: "clamp(15px, 0.6vw + 7.8px, 20px)"
  header: "3.625rem"
  route-strip: "4.25rem"
  ticket-rail: "19.75rem"
components:
  line-badge:
    textColor: "{colors.on-navy}"
    typography: "{typography.signage-label}"
    height: "34px"
  model-picker:
    backgroundColor: "{colors.navy-2}"
    textColor: "{colors.on-navy}"
    typography: "{typography.signage-label}"
    rounded: "{rounded.tip}"
    padding: "0 28px 0 10px"
    height: "32px"
  briefing-segment:
    backgroundColor: "transparent"
    textColor: "{colors.on-navy-2}"
    typography: "{typography.signage-label}"
    rounded: "{rounded.briefing}"
    padding: "0 12px"
    height: "30px"
  briefing-segment-on:
    backgroundColor: "{colors.line-b}"
    textColor: "{colors.on-navy}"
    rounded: "{rounded.briefing}"
  briefing-segment-hover:
    backgroundColor: "{colors.navy-2}"
    textColor: "{colors.on-navy}"
  next-key:
    backgroundColor: "{colors.signal}"
    textColor: "{colors.navy}"
    typography: "{typography.signage-label}"
    rounded: "{rounded.next-key}"
    padding: "0 12px"
    height: "40px"
  next-key-hover:
    backgroundColor: "{colors.signal-hover}"
  route-key:
    backgroundColor: "{colors.navy-2}"
    textColor: "{colors.on-navy}"
    rounded: "{rounded.pill}"
    size: "36px"
  route-key-hover:
    backgroundColor: "{colors.navy-3}"
  ticket:
    backgroundColor: "{colors.paper}"
    textColor: "{colors.ink}"
    rounded: "{rounded.ticket}"
  ticket-head:
    backgroundColor: "{colors.navy}"
    textColor: "{colors.on-navy}"
    typography: "{typography.ticket-id}"
    padding: "15px 16px 14px"
  zone-stamp-1:
    backgroundColor: "{colors.zone-1}"
    textColor: "{colors.zone-1-ink}"
    rounded: "{rounded.zone-stamp}"
    size: "30px"
  zone-stamp-2:
    backgroundColor: "{colors.zone-2}"
    textColor: "{colors.zone-2-ink}"
    rounded: "{rounded.zone-stamp}"
    size: "30px"
  zone-stamp-3:
    backgroundColor: "{colors.zone-3}"
    textColor: "{colors.zone-3-ink}"
    rounded: "{rounded.zone-stamp}"
    size: "30px"
  id-chip-token:
    backgroundColor: "{colors.navy}"
    textColor: "{colors.on-navy}"
    typography: "{typography.id-chip}"
    rounded: "{rounded.pill}"
    width: "96px"
    height: "24px"
  id-chip-raw:
    backgroundColor: "{colors.disruption}"
    textColor: "{colors.on-navy}"
    typography: "{typography.id-chip}"
    rounded: "{rounded.pill}"
    width: "96px"
    height: "24px"
  id-chip-none:
    backgroundColor: "{colors.chip-none}"
    textColor: "{colors.ink-3}"
    typography: "{typography.id-chip}"
    rounded: "{rounded.pill}"
    width: "96px"
    height: "24px"
  terminus-pill:
    backgroundColor: "{colors.ink}"
    textColor: "{colors.on-navy}"
    rounded: "{rounded.pill}"
    height: "24px"
  no-erase-pill:
    backgroundColor: "{colors.disruption}"
    textColor: "{colors.on-navy}"
    rounded: "{rounded.pill}"
    height: "24px"
  ticket-value-bad:
    backgroundColor: "{colors.disruption}"
    textColor: "{colors.on-navy}"
    typography: "{typography.ticket-value}"
    rounded: "{rounded.key-cap}"
    padding: "1px 5px"
  tooltip:
    backgroundColor: "{colors.navy}"
    textColor: "{colors.on-navy}"
    rounded: "{rounded.tip}"
    padding: "6px 9px"
---

# Design System: DPDP Pipeline Portal (version 1)

This records **version 1** of the Portal, the metro line map, closed on 2026-10-11 after a final finish pass. A version 2 in a different direction is being built beside it; v1 stays buildable as it is.

## Overview

**Creative North Star: "The Line Map"**

The Portal is a transit map of the pipeline. Three straight lines leave the same Hospital and serve the same seven stations (Hospital, Gate, Acquire, Extract, Score, Export, Erased); line A is ours, line B is an AI model, line C is the baseline. What sets them apart is their **stopping pattern**: between Acquire and Extract each line calls at one square per page load it made, and its train moves on only as its squares fill. Ours is the express (33 squares), the baseline the all-stations service (440 squares, a solid block that fills while its train crawls). A line with no erase date does not stop at Erased: it runs on, fading off the edge of the map. Everything else is transit signage: a navy header with line roundels, three fare zones for the pipeline's stages, dotted station guides, passenger dots for the fields a line carries, a red disruption sign wherever a rule breaks or a trap is taken, and a passenger ticket for the one patient the job is about.

The register is loud on purpose: white ground, black type, three fully saturated line colours, three soft zone tints and navy signage at the top and foot. Colour is never decoration; every hue names something (a technique, a stage, a data category, a disruption, a state reached). The surface is a display stepped by a presenter, not a tool: one keypress moves the trains to the next station and the station lights its readings. It replaced a grey control-room console the user rejected ("a lot of colors and contrast", "simple flow of pipeline is enough"), and then its own first metro build, whose baseline wound back and forth below the map in switchbacks the user found "unprofessional and not presentable". It refuses the dark neon node graph, the grey dashboard and the template look ("it shouldn't look like some bootstrap project").

Density is figure-led: page-load counts in large condensed numerals over their squares, a score, seven lamps, a chip, a pill. Prose is limited to station sub-labels, the gate's four checks, a one-row key and the ticket's one-line note.

**Key Characteristics:**
- White map, black type, navy signage bands top and bottom.
- Three straight, parallel, saturated lines, 14 units wide on a 22-unit white casing, each starting at its roundel.
- The stopping pattern: one square per page load under each line between Acquire and Extract, filling as the train calls.
- A line with no erase date runs on past Erased and fades off the map.
- Three full-height fare-zone tints, each with a 4-unit top band and a numbered square.
- Stations: white discs in black rings on dotted guides; passed stations turn yellow; the station the trains head for is marked in yellow.
- Readings appear per line, per station, only when that line's train arrives.
- The map is laid out once in map units and scaled to its box; the frame scales with the screen too.

## Colors

A transit palette: three line hues at full saturation, three pale zone tints, one disruption red, two signal yellows, six category dots, on white with navy signage.

### Primary
- **Line A, Reference Teal** (#00a091): ours. Line, squares, train, roundel, badge key, the first third of the ticket band. Text in this hue uses **Deep Teal** (#00766b), as do the gate's check marks.
- **Line B, Model Magenta** (#d1006f): the AI model on line B. Line, squares, train, roundel, badge key, the model picker's underline, the chosen briefing segment. Text uses **Deep Magenta** (#b0005d).
- **Line C, Baseline Orange** (#f28c00): the baseline. Line, squares, train, roundel, badge key. Text uses **Burnt Orange** (#a85d00).

### Secondary
- **Zone 1, Intake Butter** (#fff6d6) with **Ochre** ink (#7a5a00): Hospital and Gate.
- **Zone 2, Extraction Sky** (#e6f2fc) with **Harbour Blue** ink (#1a5c8c): Acquire, Extract, Score.
- **Zone 3, Export Blush** (#fde8f1) with **Raspberry** ink (#a3245c): Export and Erased.
- Each zone ink fills the zone's top band and its numbered square (white numeral) and colours its label; the same tint-and-ink pairs make the ticket's punched zone stamps.

### Tertiary
- **Disruption Red** (#e10600): the disruption sign's disc, a broken rule lamp (edged **Signal Brick**, #9a0400), the raw identifier chip, the "No erase date" pill, a bad ticket value. Sign captions use **Sign Red** (#c40500).
- **Lit Yellow** (#ffe36e): reached or here. A station disc a line's train has passed, the marker behind the station the trains head for, the ticket's current row (as a fading wash), text selection.
- **Signal Yellow** (#ffcc00): go and held. A held rule lamp, the Next key (hover **#ffd83d**, edge **#c79f00**), the route strip's current stop, the focus ring.
- **Passenger categories**, one dot per field carried: Identifier **Plum** (#6a2c91), Quasi-identifier **Lilac** (#a07fd2), Contact **Cobalt** (#1f78c8), Clinical **Leaf** (#1e9b4f), Financial **Mustard** (#e0a100), Administrative **Slate** (#7d8790).

### Neutral
- **Map White** (#ffffff): the map ground, station discs, the line casing, the ticket card.
- **Ink** (#101418): type, station rings, the terminus pill, the key's sample squares. **Ink 2** (#39414a) for sub-labels and secondary readings; **Ink 3** (#5a636c) for column heads and not-reached ticket rows. Station guides are Ink at 28% opacity, the key's rule Ink at 12%.
- **Signage Navy** (#0b1f3a): the header, the route strip, the ticket head, the token chip, the tooltip. **Navy 2** (#163463) for the model picker, route keys and segment hover; **Navy 3** (#24477d) for control borders and the strip's unlit track. **On Navy** white, **On Navy Quiet** (#b9c7dc) for the header's date, the briefing label, idle segments and idle strip labels.
- **Ticket Rail** (#eef1f5) behind the ticket, bordered **#d5dbe2**; row rules **#edf0f3**; perforation **#cdd5de**; the **No-id Chip** grey (#e4e8ec).
- **Unreached** (#b4bdc8): the dash standing in for a value not yet reached, unpunched holes and stamps. A placeholder only (1.9:1 on white); never a colour for a value someone must read.

### Named Rules
**The Line Is the Technique Rule.** Teal is ours, magenta is the model, orange is the baseline, everywhere: line, squares, train, roundel, badge, ticket column, band. No fourth line hue, and no line hue used for anything that is not that line. Text in a line's colour uses its darker ink variant. A letter set *on* a line hue (roundel, badge key, train, ticket column head) is ink on teal and orange and white on magenta, so it reads at small sizes.

**The Red Means Disruption Rule.** Red appears only where something went wrong: a rule broken, a trap taken, raw identifiers exported, no erase date, a bad ticket value. A screen with nothing wrong has no red on it.

**The Two Yellows Rule.** Lit Yellow (#ffe36e) means reached or here: stations passed, the station the trains head for, the ticket's current row. Signal Yellow (#ffcc00) means go or held: the Next key, the current stop, held rule lamps, focus. Do not swap them.

**The Zone Is the Stage Rule.** Zone tints are fixed to pipeline stages (1 Intake, 2 Extraction, 3 Export), drawn full height behind every line, and always paired with their own ink, top band and numbered square. The tints stay pale: the lines carry the colour.

## Typography

**Signage Font:** Bahnschrift (with DIN Alternate, Roboto Condensed, Arial Narrow, Arial)
**Body Font:** Segoe UI Variable Text (with Segoe UI, system-ui, -apple-system, Roboto, Arial)
**Mono Font:** Cascadia Mono (with Consolas, SF Mono, Menlo, ui-monospace), used only for the identifier chips.

**Character:** Transit signage. Bahnschrift is a DIN face, the lettering of road and rail signs, and it sets every name a passenger reads off a sign (stations, lines, zones, the brand, the controls) and every figure. The humanist sans carries the small print beneath: sub-labels, readings, the ticket note. Mono appears only where an identifier is shown as the string it is.

### Hierarchy
- **Page loads** (Bahnschrift 600, 29 units, line ink): each line's count over its squares, rolling up as its train calls.
- **Score** (Bahnschrift 600, 23 units, line ink): above each line's lamps.
- **Ticket id** (Bahnschrift 600, 1.85rem, tracking 0.02em): the masked record number heading the ticket.
- **Station name** (Bahnschrift 600, 17.5 units): the seven names along the top; the sub-label beneath at 13 units in Ink 2.
- **Line name** (Bahnschrift 600, 16 units): above each line beside its roundel; its sub-line below the line at 13 units.
- **Zone label** (Bahnschrift 600, 14 units, zone ink).
- **Brand** (Bahnschrift 600, 1.22rem): "Pipeline Line Map".
- **Signage label** (Bahnschrift 600, 0.92 to 1rem): line badges, the model picker, briefing segments, the Next key, ticket station names; route strip names at 0.84rem.
- **Reading** (700, 13 units): "16 fields", sign captions, pill text; second lines at 400 in Ink 2.
- **Body** (400, 0.9rem, 1.35): the page default; the ticket note at 0.78rem.
- **Identifier chip** (Cascadia Mono 600, 12 units): token or raw masked record number; "no id" in the body face.

Numerals are tabular throughout the frame.

### Named Rules
**The Platform Faces Constraint.** No web fonts: the Portal brief's hard rules require one offline file with "no network, no CDN, no web fonts", so the faces are the presentation machine's own. The target is the Windows projection laptop, where Bahnschrift, Segoe UI Variable and Cascadia Mono are installed. Cross-platform risk: elsewhere the stacks fall to DIN Alternate / Roboto Condensed / Arial Narrow, -apple-system / Roboto / Arial, and SF Mono / Menlo, whose widths differ. The station markers and the key strip measure their own text, but labels sit at fixed map offsets and can crowd. Check on the machine that will present; do not swap in a web font to fix it.

**The Signage Voice Rule.** Whatever a passenger would read off a sign (a station, a line, a zone, a count) is set in Bahnschrift; whatever explains it is set in the body face.

## Layout

A three-row frame filling the viewport: a 3.625rem navy header, the stage, a 4.25rem navy route strip. The stage is the map (fluid) beside a 19.75rem ticket rail (18.25rem at 1280px and below). The root font size is `clamp(15px, 0.6vw + 7.8px, 20px)`, so the frame grows with the screen as the map does. Built for a 1366x768 projector; checked at 1280x720, 1440x900 and 1920x1080.

The map is laid out once in **map units** (1030 x 648 at 1366x768) and scaled to its box by its viewBox, so a larger screen gets a larger map, not a sparser one. Hospital sits at x 190, Erased 140 units from the right edge, and the stations between take fixed shares of that run (12.5%, 13%, 26%, 14.5%, 17%, 17%), the widest being Acquire to Extract, where the squares are. Line A runs at y 122; the gap between lines is (height − 327) / 2, kept between 112 and 170. Zone labels sit at y 32, station names at 68 with sub-labels at 86.

Each line's band is the space beneath it: page loads and squares between Acquire and Extract, passengers between Extract and Score, score and lamps between Score and Export, the identifier chip between Export and Erased, each hung at a fixed offset below the line; signs sit on one row 82 units below their line. The gutter holds each line's roundel (on the line), its name above the line and its sub-line below. The gate's four checks sit in zone 1 under the last line; the key is one row along the foot of the map behind a hairline, wrapping only if the map is narrow.

**The Stopping Pattern Rule.** A line's page loads are drawn as squares (4.4 units on a 5.5 pitch), one per page load, never scaled, capped or sampled, and its train's time from Acquire to Extract is its page loads (0.02s each). Lines stay straight; length is never used to encode anything.

**Phone fallback** (860px and below): the frame stacks. The header wraps (badges wrap, the briefing segments fill the width), the map becomes a 560px-tall band that pans sideways over a fixed 980px drawing, the ticket follows below, and the route strip sticks to the bottom of the screen with its station labels hidden. At 1280px the date and the briefing label drop; at 1100px the header tightens.

## Elevation & Depth

The map is a printed card: a fine dot grid (0.75 dots on a 14-unit grid, Ink at 7%) under everything, each line laid on a 22-unit white casing that casts a faint shadow, so the lines read as raised strips. The trains ride above with their own shadow. The header and route strip are navy bands with a little light in them: a top-down gradient (#102a4d to navy), a 1px inner highlight and a soft shadow onto the map.

### Shadow Vocabulary
- **Train** (`filter: drop-shadow(0 2px 2.5px rgba(11,31,58,.32))`): the trains, the only moving things, ride just above the map.
- **Ticket lift** (`box-shadow: 0 1px 2px rgba(16,20,24,.08), 0 18px 34px -20px rgba(11,31,58,.55)`): the ticket card, a held object over its rail.
- **Punched hole** (`box-shadow: inset 0 2px 3px rgba(11,31,58,.45)` on #dde3ea): a ticket hole once its station is reached.
- **Next key edge** (`box-shadow: 0 2px 0 #c79f00`, 1px when pressed): the one physical key.
- **Current stop halo** (`box-shadow: 0 0 0 4px rgba(255,204,0,.25)`): the route strip's current stop.
- **Tooltip** (`box-shadow: 0 8px 20px -8px rgba(11,31,58,.6)`).

### Named Rules
**The Printed Card Rule.** Only the line casings (a 1.5px soft shadow) and the trains cast shadows; readings, labels and signs stay flat on the card. Glow is reserved for light sources: held lamps, the raw identifier chip, the current stop.

## Shapes

Transit geometry, straight. Lines are horizontal with round caps; a line that runs on ends in a gradient to transparent instead of a cap. Stations are circles (7.5 radius, 3.5 black ring) on dotted guides (1.3 stroke, round dots every 5.5). Roundels are 16-radius circles with a 3-unit white edge. Trains, chips and terminus pills are full pills; page-load squares have a 0.8 corner. Disruption signs are a red disc with a white horizontal bar. In the frame: the Next key and the briefing track are 7 to 8px rectangles, briefing segments 5px, the model picker and tooltip 6px, the ticket 12px, zone stamps 6px; route keys are circles.

**The Straight Line Rule.** Lines do not turn. Every difference between techniques is shown by what a line carries, not by its path.

## Components

### Line badges (header)
No container: each line is a 24px roundel in its hue with its letter in the signage face (ink on A and C, white on B) beside the line's name. Line B's name is the model picker, a navy 2 box with a navy 3 border, a white chevron and a magenta underline, listing the models by display name ("Opus 5.5").

### Briefing switch
Labelled "Line B was told", then a navy track (1px navy 3 border, 7px radius) of three segments: Task + register, The Act, The policy. Idle segments are On Navy Quiet; hover goes navy 2 and white; the chosen segment is magenta with white text, because the briefing belongs to line B. Keys 1 to 3 choose them; a switch rebuilds line B and flashes it once.

### Route strip (footer)
Home and Back as 36px navy 2 circular keys; **Next** as the one yellow key (Signal Yellow, navy signage text, 8px corners, a 2px darker edge, a "Space" key cap) reading Start, Next or Again. Beside them, the seven stations on a 4px navy 3 track that fills white as the run advances. A passed stop is a white disc, the current stop Signal Yellow with a white ring and halo, a future stop a navy disc in a navy 3 ring.

### The map's stations and readings
- **Stations**: white discs in black rings; a disc turns Lit Yellow when its line's train has passed it; the station the trains head for gets a Lit Yellow marker behind its name. Sub-labels carry data where they can ("20 patients", "5 modules found"), with the detail in a tooltip.
- **Trains**: a 38x24 pill in the line hue, white edge, carrying the line's letter.
- **Acquire to Extract**: the page-load count in line ink with "page loads", and the squares beneath, filling in reading order as the train calls.
- **Extract**: one passenger dot (3.3 radius) per distinct field taken, in its category colour, sorted by category, staggered in; then "N fields" and the share needed.
- **Score**: the score in line ink above seven lamps (4.6 radius, black edge), Signal Yellow when held, red when broken; a disruption sign when the trap was taken or a rule broke.
- **Export**: the identifier chip: navy with a truncated token, red with the raw masked record number, or grey "no id"; a disruption sign with the raw count when identifiers leaked.
- **Erased**: a black terminus pill "Erased 10 Nov" beside the last station, or, for a line that runs on, no station at all and a red "No erase date" pill below the fading line.
- **At the gate**: four checks in zone 1, ticked one by one in Deep Teal as the trains arrive.
- **Key**: one row along the foot: the page-load square, the six passenger colours, the held and broken lamps.

### Passenger ticket (signature)
A 12px rounded white card on the grey rail. The navy head carries the masked record number in large signage numerals, the job name, the masked name in On Navy Quiet. Below it a 6px tri-colour band (teal, magenta, orange thirds). Column heads are the three line roundels. Station rows have a punch hole (dashed ring until reached, then an inset grey hole) and one cell per line in that line's ink; values show a dash until the trains reach the station, the current row carries a Lit Yellow wash, a bad value becomes a white-on-red tab. A dashed perforation with half-circle notches separates the stub: three zone stamps (dashed until punched, then their zone tint and ink) and "Zones travelled" with the range in numerals.

**The Hidden Until Reached Rule.** No reading, on the map or the ticket, is visible before the trains reach its station. Stepping back hides it again. A line's route (which stations it serves) is the map itself and is always shown.

### Run status (header)
A pill beside the brand that names the run's state the way a deploy page does: **Ready** (grey dot), **Running to Extract** (Signal Yellow dot with a beacon ring), **At Score** (Lit Yellow dot), **Run complete** (teal dot with a glow). It is the screen's `aria-live` status.

### Motion (the finish pass)
- **Opening** (once, on load): each line draws out of its roundel over 1s, 90ms apart; the stations set down on them; casings, the run-on fade and the trains fade in after.
- **The race** (the focal moment): a white light streak trails each moving train (up to 70 units, 34 between Acquire and Extract); the page-load squares pop in from 20% scale as the train calls; the count rolls.
- **Arrivals**: a ring in the line's colour opens out from each station as its train arrives (0.7s).
- **Score**: the seven lamps light one after another (75ms apart); a broken one blinks twice before settling red.
- **Export**: on a pseudonymising line the chip scrambles from the masked record number through hex into its token (0.62s); a raw chip glows red.
- **Never erased**: white dashes flow along a run-on line off the edge of the map.
- **Ticket**: values flap in like a split-flap board as their station is reached; zone stamps land with a stamp's rotation.
- **Route strip**: the fill is the three line colours; the current stop glows.

### Presenter stepping
Space or the Next key sends the trains to the next station (a second press lands the step); Right / PageDown next, Left / PageUp back, Home to the start, End to Erased, 1 to 3 for the briefing. Trains run at 230 map units per second, and from Acquire to Extract each takes its page loads at 0.02s each; readings fade in over 0.35s on `cubic-bezier(.16,1,.3,1)`. The focus ring is 3px Signal Yellow, 2px offset.

**The Every State Still Rule.** Under reduced motion each step lands whole: no train travel, no fades, no flash, no strip animation, and every reading the animated run would show is shown.

## Do's and Don'ts

### Do:
- **Do** keep line A teal, B magenta, C orange in every element that names a line, and set line-coloured text in #00766b, #b0005d, #a85d00.
- **Do** draw page loads as squares, one each, and let the train's time follow them.
- **Do** keep the lines straight and parallel, cased in white, starting at their roundels.
- **Do** let a line with no erase date run on off the map.
- **Do** pair each zone tint with its own ink, top band and numbered square, and keep the tints pale.
- **Do** keep readings and ticket values hidden until the trains reach their station.
- **Do** set every sign and figure in the signage face and every identifier in the mono chip.
- **Do** check the platform faces on the presenting machine.

### Don't:
- **Don't** encode page loads as route length; switchbacks were rejected as unpresentable.
- **Don't** use red for anything but a disruption: a broken rule, a trap taken, raw identifiers out, no erase date.
- **Don't** add a fourth line hue or reuse a line hue decoratively.
- **Don't** put shadows on the map other than the line casings and the trains, or glow on anything that is not a light source.
- **Don't** box the key or the gate's checks in bordered boards; they sit on the map like map text.
- **Don't** use pill-shaped badges or generic component styling in the frame; controls are signage.
- **Don't** use the Unreached grey (#b4bdc8) for a value someone has to read.
- **Don't** load web fonts or any network asset; the file stays offline and self-contained.
- **Don't** turn the map dark or grey; the map ground is white.
