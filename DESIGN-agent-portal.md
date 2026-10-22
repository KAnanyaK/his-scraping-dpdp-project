---
name: HIS Staff Assistant
description: The staff-guidance assistant as its own portal, in Portal v2's dark console. A night ground with faint glass panels and hairlines, Inter embedded; a five-stop stepper shows the run through the assistant, and a dark schematic of the HIS screen lights only the columns and the button a step uses. Lit yellow means here, teal a check passed, red the staff-only door shut, five department hues the modules. One offline file.
colors:
  night: "#070a12"
  night-2: "#0b1019"
  well: "#0c111b"
  panel: "rgba(255, 255, 255, .028)"
  panel-2: "rgba(255, 255, 255, .05)"
  panel-3: "rgba(255, 255, 255, .08)"
  hairline: "rgba(160, 175, 200, .13)"
  hairline-2: "rgba(160, 175, 200, .22)"
  hairline-3: "rgba(160, 175, 200, .36)"
  schematic: "rgba(5, 8, 14, .55)"
  text: "#edf2fa"
  text-2: "#aeb8c9"
  text-3: "#8792a6"
  passed: "#2ee6c9"
  door: "#ff4d6a"
  door-text: "#ff7a8f"
  lit: "#ffd84d"
  lit-text: "#ffe48a"
  ask-key: "#ffffff"
  ask-key-low: "#dfe7f1"
  key-ink: "#08110f"
  key-off: "#2a3446"
  dept-patient-administration: "#6cb6ff"
  dept-clinical-ehr: "#4be38a"
  dept-ancillary-departmental: "#b392ff"
  dept-administrative-financial: "#ff9f5a"
  dept-infrastructure-integration: "#9aa7bb"
  on-dept: "#07101a"
typography:
  brand:
    fontFamily: "Inter, \"Segoe UI Variable Text\", \"Segoe UI\", system-ui, sans-serif"
    fontSize: "1rem"
    fontWeight: 650
    letterSpacing: "-0.01em"
  title:
    fontFamily: "Inter, \"Segoe UI Variable Text\", \"Segoe UI\", system-ui, sans-serif"
    fontSize: "1rem"
    fontWeight: 650
    lineHeight: 1.35
    letterSpacing: "-0.01em"
  enquiry-echo:
    fontFamily: "Inter, \"Segoe UI Variable Text\", \"Segoe UI\", system-ui, sans-serif"
    fontSize: "1.0625rem"
    fontWeight: 400
    lineHeight: 1.5
  screen-title:
    fontFamily: "Inter, \"Segoe UI Variable Text\", \"Segoe UI\", system-ui, sans-serif"
    fontSize: "0.9375rem"
    fontWeight: 650
    letterSpacing: "-0.005em"
  body:
    fontFamily: "Inter, \"Segoe UI Variable Text\", \"Segoe UI\", system-ui, sans-serif"
    fontSize: "0.9375rem"
    fontWeight: 400
    lineHeight: 1.5
    fontFeature: "\"cv11\", \"ss01\""
  label:
    fontFamily: "Inter, \"Segoe UI Variable Text\", \"Segoe UI\", system-ui, sans-serif"
    fontSize: "0.875rem"
    fontWeight: 600
    lineHeight: 1.25
  secondary:
    fontFamily: "Inter, \"Segoe UI Variable Text\", \"Segoe UI\", system-ui, sans-serif"
    fontSize: "0.8125rem"
    fontWeight: 500
    lineHeight: 1.3
    fontFeature: "\"cv11\", \"ss01\", \"tnum\""
rounded:
  kbd: "0.3125rem"
  inline-key: "0.375rem"
  segment: "0.4375rem"
  control: "0.625rem"
  field: "0.75rem"
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
  3xl: "1.25rem"
  gutter: "1.5rem"
components:
  status-pill:
    backgroundColor: "{colors.panel}"
    textColor: "{colors.text-2}"
    typography: "{typography.secondary}"
    rounded: "{rounded.pill}"
    height: "1.75rem"
    padding: "0 0.75rem 0 0.625rem"
  badge-segment:
    backgroundColor: "{colors.panel}"
    rounded: "{rounded.control}"
    padding: "0.1875rem"
  badge:
    textColor: "{colors.text-2}"
    typography: "{typography.label}"
    rounded: "{rounded.segment}"
    height: "2rem"
    padding: "0 0.75rem"
  badge-active:
    backgroundColor: "rgba(255, 255, 255, .11)"
    textColor: "{colors.ask-key}"
    rounded: "{rounded.segment}"
  tour-key:
    backgroundColor: "{colors.panel}"
    textColor: "{colors.text}"
    typography: "{typography.label}"
    rounded: "{rounded.control}"
    height: "2.5rem"
    padding: "0 0.9375rem 0 0.8125rem"
  tour-key-playing:
    backgroundColor: "rgba(255, 216, 77, .09)"
    textColor: "{colors.text}"
    rounded: "{rounded.control}"
  desk:
    backgroundColor: "{colors.panel}"
    textColor: "{colors.text}"
    rounded: "{rounded.surface}"
  you-slip:
    backgroundColor: "rgba(255, 255, 255, .075)"
    textColor: "{colors.text}"
    rounded: "{rounded.surface}"
    padding: "0.4375rem 0.8125rem"
  task-chip:
    backgroundColor: "{colors.panel}"
    textColor: "{colors.text}"
    typography: "{typography.secondary}"
    rounded: "{rounded.control}"
    height: "1.875rem"
    padding: "0.25rem 0.625rem"
  task-chip-hover:
    backgroundColor: "{colors.panel-3}"
  ask-field:
    backgroundColor: "rgba(0, 0, 0, .3)"
    textColor: "{colors.text}"
    typography: "{typography.body}"
    rounded: "{rounded.field}"
    height: "2.75rem"
    padding: "0 0.9375rem"
  ask-key:
    backgroundColor: "{colors.ask-key}"
    textColor: "{colors.key-ink}"
    rounded: "{rounded.field}"
    height: "2.75rem"
    padding: "0 0.9375rem 0 1.0625rem"
  ask-key-disabled:
    backgroundColor: "{colors.key-off}"
    textColor: "{colors.text-3}"
  step-row:
    textColor: "{colors.text}"
    typography: "{typography.body}"
    rounded: "{rounded.field}"
    padding: "0.5625rem 0.625rem"
  step-row-selected:
    backgroundColor: "{colors.panel-2}"
  step-number:
    backgroundColor: "{colors.dept-administrative-financial}"
    textColor: "{colors.on-dept}"
    rounded: "{rounded.round}"
    size: "1.5rem"
  question-card:
    backgroundColor: "{colors.panel-2}"
    textColor: "{colors.text}"
    rounded: "{rounded.field}"
    padding: "0.625rem 0.8125rem 0.6875rem"
  refusal-card:
    backgroundColor: "rgba(255, 77, 106, .07)"
    textColor: "{colors.text}"
    rounded: "{rounded.field}"
    padding: "0.6875rem 0.875rem 0.75rem"
  stop-tile:
    backgroundColor: "{colors.night-2}"
    textColor: "{colors.text-3}"
    rounded: "{rounded.round}"
    size: "2rem"
  stop-tile-current:
    backgroundColor: "{colors.night-2}"
    textColor: "{colors.lit}"
    rounded: "{rounded.round}"
    size: "2rem"
  stop-tile-passed:
    backgroundColor: "{colors.ask-key}"
    textColor: "{colors.key-ink}"
    rounded: "{rounded.round}"
    size: "2rem"
  stop-tile-stopped:
    backgroundColor: "{colors.door}"
    textColor: "{colors.ask-key}"
    rounded: "{rounded.round}"
    size: "2rem"
  board:
    backgroundColor: "{colors.panel}"
    textColor: "{colors.text}"
    rounded: "{rounded.surface}"
    padding: "0.875rem 1.125rem"
  step-selector:
    backgroundColor: "{colors.panel}"
    textColor: "{colors.text-2}"
    typography: "{typography.label}"
    rounded: "{rounded.round}"
    size: "2rem"
  schematic-screen:
    backgroundColor: "{colors.schematic}"
    textColor: "{colors.text-3}"
    typography: "{typography.secondary}"
    rounded: "{rounded.surface}"
  screen-button:
    backgroundColor: "{colors.panel}"
    textColor: "{colors.text-2}"
    typography: "{typography.secondary}"
    rounded: "0.5rem"
    height: "1.75rem"
    padding: "0 0.6875rem"
  screen-button-press:
    backgroundColor: "rgba(255, 216, 77, .09)"
    textColor: "{colors.ask-key}"
    rounded: "0.5rem"
    height: "1.75rem"
  step-pin:
    backgroundColor: "rgba(255, 216, 77, .1)"
    textColor: "{colors.lit-text}"
    typography: "{typography.secondary}"
    rounded: "{rounded.pill}"
    height: "1.75rem"
    padding: "0 0.75rem 0 0.5rem"
  key-cap:
    textColor: "{colors.text-2}"
    typography: "{typography.secondary}"
    rounded: "{rounded.kbd}"
    height: "1.375rem"
    padding: "0 0.3125rem"
---

# Design System: HIS Staff Assistant

## Overview

**Creative North Star: "Only The Decision Is Lit"**

The HIS Staff Assistant is the project's rule-based staff-guidance agent as its own portal, set in Portal v2's dark product console. A staff request is treated as a run through the assistant: it is understood, it meets the staff-only door (the DPDP check for the role, run before any detail is asked), the details are collected and shape-checked, it is routed to a department, and its steps are placed on a screen. Each of those five stops lights on a stepper as the engine decides it, and a dark schematic of the HIS screen then lights the columns and the one button the chosen step uses. Everything else is quiet glass on a night ground.

The page refuses two things: the light signage panel of the earlier wayfinding build, and the chatbot with a sidebar. The conversation is one half of the floor; the other half is the route the request took, so the room sees the gate and the placement, not just a reply. The reply wording is the engine's own, replayed and self-checked against 1,053 recorded Python conversations on open; this system governs presentation only. No patient value appears anywhere: example inputs are the registry's own, and the schematic's rows are blank.

Density is a working console sized for the presenting laptop (1366x768): three fixed frame rows, the stepper and board at fixed heights so the geometry never jumps between tasks, and every word the panel reads at 13px or more.

**Key Characteristics:**
- Night ground with two faint radial tints (teal behind the route, violet behind the desk); glass panels at 2.8 to 5% white with blue-grey hairlines.
- One face, Inter, embedded, weights 400 to 700, tabular figures on every count.
- Lit yellow for "here" only; teal for a check passed; red for the staff-only door shut; five department hues for the modules; white for the Ask key and for stops already passed.
- A five-stop stepper whose track fills behind each stop, 190ms apart.
- A schematic HIS screen with empty rows, lighting only what the current step uses.
- Drawn SVG icons in one 1.75 stroke, held in round tiles.

## Colors

A night palette where hue is spent only on a decision: where the run is, what passed, what was refused, and which department it went to.

### Primary
- **Lit Yellow** (lit, with lit-text for words): "here". The current stop's tile ring and halo, its caption, the button to press on the schematic and its ring, the step pin, the input's caret and focus ring, the playing Tour key's border and stop glyph, the status beacon while a run plays, and every keyboard focus outline.

### Secondary: the five departments
- **Registration Sky** (dept-patient-administration), **Clinical Green** (dept-clinical-ehr), **Orders Violet** (dept-ancillary-departmental), **Billing Orange** (dept-administrative-financial), **Audit Slate** (dept-infrastructure-integration). The module a step is routed to, wherever it shows: the step's number disc and module name, the selected step's ring, the Department stop's tile once passed, the board's module row and step selector, the schematic's active tab underline, its lit column heads and lit record fields. They are brightened for the night ground and carry dark ink (on-dept) when filled.

### Tertiary: signals
- **Passed Teal** (passed): a check that passed. The rule ticks on the board, the "steps placed" status dot and border, the matched words underlined in the echoed enquiry, the foot's self-check dot, text selection.
- **Door Red** (door, with door-text for words): the staff-only door shut, and nothing else. The stopped stop's solid tile and halo, the track into it, the refusal card's tint and title, the refused status pill, the failed rule's id and name. The "Outside your role" sample chip carries the same no-entry sign in red, because it is the door offered as a demonstration.
- **Ask White** (ask-key, ask-key-low, key-ink): the Ask key, a white to #dfe7f1 gradient with dark ink, and the solid white tile of every stop already passed. The active badge is a soft white glass, not solid.

### Neutral
- **Night / Night 2 / Well** (night, night-2, well): the ground; the unlit stop tiles; the opaque fill behind the sticky input on a phone.
- **Panel / Panel 2 / Panel 3** (panel, panel-2, panel-3): glass fills for controls and surfaces; hover and selected rows; chip hover.
- **Hairline / 2 / 3** (hairline, hairline-2, hairline-3): frame dividers and surface outlines; control borders and the stepper track; hover borders and dashed "waiting" outlines.
- **Schematic** (schematic): the HIS screen's darker glass, so it reads as another system inside the console.
- **Text / Text 2 / Text 3** (text, text-2, text-3): replies and names; secondary lines and inactive controls; labels, captions and unlit stops.
- **Key Off** (key-off): the Ask key when typing is switched off.

### Named Rules
**The Light Is A Decision Rule.** A glow, ring or solid fill marks something the assistant decided: the stop being decided, a check passed, the door shut, the department, the button to press. Panels, labels and the frame never glow. The Ask key's soft shadow is a lift, not light.

**The Yellow Means Here Rule.** Lit yellow names the current position and nothing else: one stop, one button, one pin, the focused control. A passed stop turns white, never stays yellow.

**The Red Is The Door Rule.** Red appears only where the staff-only door is shut for this role (or on the sample chip that demonstrates it). An answer that does not fit its shape is plain bold text, not red; a notice that typing is off is grey.

**The Department Owns Its Hue Rule.** A department hue always means that module, across the step number, the board, the tab and the lit columns; it is never used for a state.

## Typography

**Display Font:** Inter (embedded variable WOFF2, weights 100 to 900, OFL; fallback Segoe UI Variable Text, Segoe UI, system-ui)
**Body Font:** Inter
**Label/Mono Font:** none; key caps are Inter at 600

**Character:** One neutral product face carries every word and figure, tightened slightly at title sizes (-0.01em), with Inter's cv11 and ss01 alternates and tabular figures on counts. Hierarchy comes from weight steps (500, 550, 600, 650) and a narrow size range, never from a second face.

### Hierarchy
- **Brand** (650, 1rem, -0.01em): the product name in the bar.
- **Title** (650, 1rem, 1.35): a reply's heading (the task name, the refusal) and the board's heading.
- **Enquiry echo** (400, 1.0625rem): the visitor's words repeated on the board, with matched words in bold and underlined in teal.
- **Screen title** (650, 0.9375rem, -0.005em): the schematic's page heading.
- **Body** (400, 0.9375rem, 1.5): conversation text and step instructions.
- **Label** (600, 0.875rem): badge names, the Tour key, stop names, slot and module names, the step selector.
- **Secondary** (500 to 600, 0.8125rem, 1.3): stop captions, task chips, board facts and descriptions, the schematic's columns, tabs and buttons, the pin, the foot, key caps, the status pill. This is the floor.

### Named Rules
**The One Face Rule.** Inter for everything, embedded, so the projected room sees what was designed. No mono, no display face.

**The 13px Floor Rule.** Nothing the panel reads is below 0.8125rem. The root is `clamp(16px, 0.6vw + 8px, 19px)`, about 16.2px at 1366 wide, so the floor lands at 13.2px on the presenting laptop and 13px on a phone.

## Layout

The frame is a three-row grid filling the viewport (100dvh): the product bar (3.25rem), the floor (the rest), the foot (2.25rem). Bar and foot share a 1.5rem side gutter, divided from the floor by hairlines, on a 70% night fill.

- **Product bar:** mark and name, the status pill, then right-aligned the badge segment (three badges with task counts) and the Tour key.
- **Floor:** two columns, the desk 42% and the route 58%, 1.25rem apart, padded 1rem 1.5rem 0.875rem.
- **Desk:** one glass panel stacking the conversation (scrolling, its top and bottom edges faded with a 0.875rem mask), the common tasks (a two-column grid plus one task outside the role), and the input row.
- **Route:** three rows: the stepper (5.5rem), the board (12.5rem), and the schematic screen (the rest). Stepper and board heights are fixed so one geometry holds for every task at a given size; the board scrolls inside itself if it must.
- **Foot:** the rule-based note with the self-check count, the date of the screens, and the key caps on the right.

Scaling is in rem off the root clamp. Below 1320px the foot's source line goes; below 1180px the badge counts and the Tour key's role go. On a short laptop (height 760px or less, width over 860px) the bars, gaps and route rows tighten (stepper 5.25rem, board 12rem). At 860px and below the page stacks into one column and scrolls: the badges take a full row, the conversation grows with its answers, the input sticks to the bottom of the screen on the opaque well, the stepper runs down the page as rows with the caption right-aligned, and the schematic keeps at least 22rem. At 520px the status pill goes and the grids go to one column.

### Named Rules
**The Fixed Board Rule.** The stepper and board keep fixed heights at each size, measured by driving every task and probe at 1280, 1366, 1440, 1600 and 1920; content never pushes the schematic around.

## Elevation & Depth

Depth is glass and light on a dark ground, not lift. Surfaces are a top-to-bottom white gradient (4.2% to 1.4%) over the night with a hairline; the schematic is darker glass inside the console. The few shadows are decisions made visible, plus one plain lift under the Ask key.

### Shadow Vocabulary
- **Current stop** (`inset 0 0 0 1.5px #ffd84d, 0 0 0 4px rgba(255,216,77,.14), 0 0 16px rgba(255,216,77,.42)`): the stop being decided.
- **Door shut** (`0 0 0 4px rgba(255,77,106,.15), 0 0 16px rgba(255,77,106,.5)`): the stopped stop's solid red tile.
- **Button to press** (`0 0 0 3px rgba(255,216,77,.14), 0 0 16px rgba(255,216,77,.32)`): the schematic's button for this step.
- **Running beacon** (`0 0 0 0 -> 7px rgba(255,216,77,.6 -> 0)`, 1.1s): the status dot while a run plays.
- **Ask key** (`0 0 0 1px rgba(255,255,255,.4), 0 6px 14px -6px rgba(0,0,0,.6)`): the one control that lifts.
- **Department ring** (`inset 0 0 0 1px` the department hue at 44 to 62%): the selected step row, the module row on the board, a department tile.

### Named Rules
**The Glass Not Card Rule.** No panel is lifted by a dark shadow; rings are inset hairlines, and glow is reserved for the decisions above.

## Shapes

Soft, small, consistent radii in a product register: key caps 0.3125rem, inline keys 0.375rem, badges 0.4375rem, chips and controls 0.625rem, fields, step rows and cards 0.75rem, panels 0.875rem, the status pill and step pin fully round. Every icon sits in a round tile (1.5 to 2rem); stop tiles, step numbers and the step selector are circles. Waiting states are a dashed 1.5px outline in place of a fill. The visitor's own message is a slip with one tucked corner (0.25rem at bottom right). The stepper track is a 2px rounded line.

## Components

### The stepper (signature)
Five stops on one hairline track: Enquiry, Staff only, Details, Department, Screen, each a 2rem round tile with a drawn icon, a name and a two-line caption. States: waiting (night tile, grey), current (yellow ring and halo, caption in lit text), passed (solid white tile with dark ink; the Department tile fills with the module's hue), stopped (solid red tile with halo, name and caption in red, the track into it red), unknown (dashed outline). The track into a passed stop turns 60% white. The stop shown on the board is underlined in white. Stops light 190ms apart; each tile pops from 0.82 scale over 240ms and the track wipes in over 180ms behind it.

### The board
Glass, 0.875rem radius, fixed height. Its content follows the selected stop: the echoed enquiry with matched words; the three door rules (PL-01, DM-01, SS-01) as rows of tile, id and plain name, ticked teal, refused red, or dashed "not reached"; the details as slots, dashed until given; the five modules with the steps that use each; and on Screen a four-cell readout (module, page, columns lit, button to press) with round step selectors filled in the department hue. It fades in from 45% over 220ms and sits at 40% until the walk reaches it.

### The schematic HIS screen (signature)
A darker glass frame: a chrome line (portal name, the access notice, who is signed in), the module tabs with the active one underlined in its hue, then the page: a title, a row of buttons, and either a table with empty rows or a record's field list. Only the step's columns or fields light, in the department hue on a faint white wash with a 2px underline; the button to press rings yellow; a "Step n: press ..." pin sits on the title line. Before a placement it lists the modules with their button and field counts. A step the map cannot place shows a dashed "withheld" box with the reason. "No patient data is shown here" closes every page.

### The conversation
- **Assistant message:** a round tile (info, check in teal, no-entry in red) beside the text. A guidance reply has a title, a sub line, then numbered step rows.
- **Step row:** a 1.5rem disc in the department hue with dark ink, the instruction, then the module name in its hue, the page, and the button as a small inline key; selected rows ring in the hue.
- **Question card:** Panel 2 with a hairline ring, the question in 600, "Detail n of m", and an example chip. An answer that does not fit is plain bold.
- **Refusal card:** red at 7% with a red ring, the title in red, then who can do it instead, then "No patient details were asked for."
- **Visitor slip:** white glass at 7.5%, right-aligned, tucked bottom-right corner.

### Buttons
- **Ask key:** the one solid white control, a gradient to #dfe7f1 with dark ink, label and arrow; pure white on hover, 1px down on press; slate and flat when typing is off.
- **Tour key:** glass with a hairline, play glyph, "Tour" and the badge's role; while playing, a yellow border at 55% and a stop glyph in yellow.
- **Focus:** a 2px lit-yellow outline at 2px offset on every control.

### Chips
Glass with a Hairline 2 border, 0.8125rem text, Panel 3 on hover. The task outside the role is dashed with a red no-entry sign. "All tasks" is in Text 2.

### Inputs / Fields
The ask field is 2.75rem high on a 30% black well with a hairline; hover strengthens the border, focus turns it yellow at 55% with a 3px yellow ring at 13% and a yellow caret. During a tour its border holds a faint yellow and the task strip dims to 50%.

### Navigation
- **Status pill:** Ready (grey dot), running (yellow beacon), at a stop (yellow dot), steps placed (teal dot and border), refused (red dot and border), with the count in tabular figures.
- **Badge segment:** three badges in a glass track; the active one is white glass with a white inset ring.
- **Key caps:** in the foot: `/` ask, 1 2 3 badge, T tour, Space next.

### Motion
One ease, `cubic-bezier(.16, 1, .3, 1)`, durations 160 to 280ms, no overshoot. Stops 190ms apart; the schematic page fades in over 220ms, the pin slides 6px in over 240ms after 140ms, the target's ring blooms over 280ms after 200ms. In a tour, typing runs at 26ms a character and steps advance every 1.7s; Space lands whatever is moving. Reduced motion lands every state at once.

## Do's and Don'ts

### Do:
- **Do** light only what the engine decided: one current stop in yellow, passed stops in white, the door in red, the module in its department hue.
- **Do** run the door before the details: the stepper shows Staff only before any detail is asked, and a refusal leaves Details, Department and Screen waiting.
- **Do** render the engine's reply text exactly as it comes; the page is self-checked against the recorded conversations and switches typing off on any difference.
- **Do** keep the schematic's rows empty and every example input the registry's own; no patient value on the page.
- **Do** keep the stepper and board at fixed heights per size so nothing on the route jumps.
- **Do** keep the file single and offline: Inter embedded, SVG and CSS only.

### Don't:
- **Don't** set anything the panel reads below 0.8125rem (13px at the 1366 root).
- **Don't** use red for anything but the staff-only door, or yellow for anything but "here".
- **Don't** use a department hue for a state, or a state colour for a department.
- **Don't** glow chrome: panels, labels and the frame stay quiet glass and hairlines.
- **Don't** name a screen the map could not place; show the dashed withheld box with the reason instead.
- **Don't** put internal words (crawler, paths, layer names) or vendor names in staff-facing text.
