---
name: HIS Staff Assistant
description: The staff-guidance assistant as its own portal, drawn as hospital wayfinding. A pale corridor wall, navy sign panels set in white Atkinson Hyperlegible Next, five department colours on square pictogram tiles, red only for the staff-only door when it stays shut, green only for a check passed; one offline file with the face embedded.
colors:
  wall: "#e6eaee"
  wall-2: "#dbe1e7"
  panel: "#ffffff"
  panel-2: "#f4f6f8"
  navy: "#14315c"
  navy-2: "#1d4174"
  navy-3: "#0f2647"
  on-navy: "#ffffff"
  on-navy-2: "#c8d3e2"
  ink: "#13202d"
  ink-2: "#3c4957"
  ink-3: "#55616f"
  rule: "#c9d1d9"
  rule-2: "#e0e5ea"
  unlit: "#b8c2cc"
  you-slip: "#e4ebf4"
  go: "#1d7740"
  go-wash: "#e1f1e6"
  stop: "#c8102e"
  stop-wash: "#fbe5e8"
  amber: "#e8a400"
  amber-ink: "#2b1d00"
  d-patient-administration: "#1f63c0"
  d-clinical-ehr: "#0b7a85"
  d-ancillary-departmental: "#6a44b8"
  d-administrative-financial: "#a8650a"
  d-infrastructure-integration: "#4b5b6b"
  replica-chrome: "#2c3238"
  replica-ground: "#f3f4f5"
typography:
  title:
    fontFamily: "\"Atkinson Hyperlegible Next\", \"Segoe UI\", system-ui, sans-serif"
    fontSize: "1.125rem"
    fontWeight: 700
    lineHeight: 1.45
    letterSpacing: "0.005em"
  board-head:
    fontFamily: "\"Atkinson Hyperlegible Next\", \"Segoe UI\", system-ui, sans-serif"
    fontSize: "1rem"
    fontWeight: 700
    lineHeight: 1.45
  said:
    fontFamily: "\"Atkinson Hyperlegible Next\", \"Segoe UI\", system-ui, sans-serif"
    fontSize: "1.0625rem"
    fontWeight: 400
    lineHeight: 1.45
  body:
    fontFamily: "\"Atkinson Hyperlegible Next\", \"Segoe UI\", system-ui, sans-serif"
    fontSize: "1rem"
    fontWeight: 400
    lineHeight: 1.45
    fontFeature: "\"tnum\", \"lnum\""
  sign-name:
    fontFamily: "\"Atkinson Hyperlegible Next\", \"Segoe UI\", system-ui, sans-serif"
    fontSize: "0.9375rem"
    fontWeight: 700
    lineHeight: 1.15
  chip:
    fontFamily: "\"Atkinson Hyperlegible Next\", \"Segoe UI\", system-ui, sans-serif"
    fontSize: "0.875rem"
    fontWeight: 400
    lineHeight: 1.45
  label:
    fontFamily: "\"Atkinson Hyperlegible Next\", \"Segoe UI\", system-ui, sans-serif"
    fontSize: "0.8125rem"
    fontWeight: 400
    lineHeight: 1.2
  key-cap:
    fontFamily: "\"Atkinson Hyperlegible Next\", \"Segoe UI\", system-ui, sans-serif"
    fontSize: "0.8125rem"
    fontWeight: 700
    lineHeight: 1
  stamp:
    fontFamily: "\"Atkinson Hyperlegible Next\", \"Segoe UI\", system-ui, sans-serif"
    fontSize: "0.8125rem"
    fontWeight: 700
    lineHeight: 1.45
    letterSpacing: "0.02em"
rounded:
  key: "4px"
  tile: "5px"
  sign: "6px"
  panel: "8px"
  you-slip: "8px 8px 2px 8px"
spacing:
  hair: "0.0625rem"
  xs: "0.25rem"
  sm: "0.375rem"
  md: "0.5rem"
  step: "0.625rem"
  lg: "0.75rem"
  xl: "0.875rem"
  floor-y: "1rem"
  floor-x: "1.25rem"
  stage-gap: "1.375rem"
  board-h: "12.5rem"
  board-h-short: "12rem"
components:
  band:
    backgroundColor: "{colors.navy-3}"
    textColor: "{colors.on-navy}"
    height: "3.5rem"
    padding: "0 1.25rem"
  badge:
    textColor: "{colors.on-navy-2}"
    rounded: "{rounded.sign}"
    height: "2.5rem"
    padding: "0 0.75rem 0 0.5rem"
  badge-pressed:
    backgroundColor: "{colors.on-navy}"
    textColor: "{colors.navy}"
  tour-button:
    backgroundColor: "{colors.amber}"
    textColor: "{colors.amber-ink}"
    rounded: "{rounded.sign}"
    height: "2.5rem"
    padding: "0 0.875rem 0 0.75rem"
  tile:
    backgroundColor: "{colors.navy}"
    textColor: "{colors.on-navy}"
    rounded: "{rounded.tile}"
    size: "1.75rem"
  stage-sign:
    backgroundColor: "{colors.wall-2}"
    textColor: "{colors.ink-3}"
    rounded: "{rounded.sign}"
    height: "3.75rem"
    padding: "0.4375rem 0.5rem"
  stage-sign-current:
    backgroundColor: "{colors.navy-2}"
    textColor: "{colors.on-navy}"
  stage-sign-passed:
    backgroundColor: "{colors.navy}"
    textColor: "{colors.on-navy}"
  stage-sign-stopped:
    backgroundColor: "{colors.stop}"
    textColor: "{colors.on-navy}"
  stage-sign-unknown:
    backgroundColor: "{colors.panel}"
    textColor: "{colors.ink-2}"
  desk:
    backgroundColor: "{colors.panel}"
    textColor: "{colors.ink}"
    rounded: "{rounded.panel}"
  board:
    backgroundColor: "{colors.panel}"
    textColor: "{colors.ink}"
    rounded: "{rounded.panel}"
    height: "{spacing.board-h}"
    padding: "0.75rem 1rem"
  step-sign:
    backgroundColor: "{colors.panel}"
    textColor: "{colors.ink}"
    rounded: "{rounded.sign}"
    padding: "0.5rem 0.625rem"
  chip:
    backgroundColor: "{colors.panel}"
    textColor: "{colors.ink}"
    typography: "{typography.chip}"
    rounded: "{rounded.sign}"
    height: "2rem"
    padding: "0.25rem 0.625rem"
  chip-out:
    textColor: "{colors.ink-2}"
  chip-play:
    backgroundColor: "#fff7e2"
  you-slip:
    backgroundColor: "{colors.you-slip}"
    textColor: "{colors.ink}"
    rounded: "{rounded.you-slip}"
    padding: "0.5rem 0.75rem"
  refusal:
    backgroundColor: "{colors.stop-wash}"
    textColor: "{colors.ink}"
    rounded: "{rounded.sign}"
    padding: "0.625rem 0.75rem"
  ask-input:
    backgroundColor: "{colors.panel}"
    textColor: "{colors.ink}"
    typography: "{typography.body}"
    rounded: "{rounded.sign}"
    height: "2.75rem"
    padding: "0 0.875rem"
  send-button:
    backgroundColor: "{colors.navy}"
    textColor: "{colors.on-navy}"
    rounded: "{rounded.sign}"
    height: "2.75rem"
    padding: "0 1rem"
  send-button-hover:
    backgroundColor: "{colors.navy-2}"
  replica:
    backgroundColor: "{colors.replica-ground}"
    rounded: "{rounded.panel}"
  replica-chrome:
    backgroundColor: "{colors.replica-chrome}"
    height: "2rem"
    padding: "0 0.75rem"
  pin:
    backgroundColor: "{colors.navy}"
    textColor: "{colors.on-navy}"
    typography: "{typography.label}"
    rounded: "{rounded.tile}"
    padding: "0.1875rem 0.5rem 0.1875rem 0.3125rem"
  key-cap:
    backgroundColor: "{colors.panel}"
    textColor: "{colors.ink-2}"
    typography: "{typography.key-cap}"
    rounded: "{rounded.key}"
    height: "1.25rem"
---

# Design System: HIS Staff Assistant

## Overview

**Creative North Star: "The Enquiry Desk"**

The HIS Staff Assistant shows a request as a route through the hospital's own screens. The visitor puts on a staff badge (Reception, Nurse, Administrator) and asks at the enquiry desk in their own words, or plays that badge's tour. The request then walks five fixed stage signs: Enquiry (understood, from which words), Staff only (the DPDP check for this badge, before any detail is asked), Details (each one shape-checked), Department (the modules the steps need) and Screen (each step placed on the screen where it happens). Under the signs, the active stage's board, and under that a replica of the hospital's portal that lights the column and the button the step uses. It refuses the chatbot with a side panel and the node-graph "AI pipeline".

The world is hospital wayfinding signage. The ground is a pale cool corridor wall (Wall). Signs are navy panels set in white Atkinson Hyperlegible Next. The five HIS modules are departments, each with its own colour on a square pictogram tile, drawn in one stroked family; arrows are drawn too. State colours are earned: red for the staff-only door when it stays shut, green for a check passed, amber for "you are here". Signs hold fixed positions and only their state changes. The answer on the desk is a set of step signs in their departments' colours. Each pairs with the replica screen that proves where it happens. The replica is the hospital's portal, not ours: a grey chrome bar, tabs, a page with the module's buttons and columns, and blank ruled rows. No patient value appears anywhere.

The standing bar holds: **elegant and professional.** The system keeps it as restraint. There is no decorative gradient, no glass and no side stripe. A shadow appears only where a sign stands off the wall. Motion is short and explains a decision, then stops: signs light in order, an arrow is drawn into the next sign, the board and replica repaint from the new state. Density is presentation density for the presenting laptop (1366x768). The desk scrolls; the route holds one geometry per screen size, and the presenter explains.

**Key Characteristics:**
- A pale corridor wall, a navy sign band, an enquiry desk (about 42%) beside the route (about 58%).
- Five stage signs in fixed positions, joined by drawn arrows; only their state changes (waiting, current, passed, stopped, unknown).
- Five department colours on square pictogram tiles, one drawn and stroked family, never glyphs.
- Red only for the staff-only door when it stays shut; green only for a check passed; amber for "you are here".
- Every step on the desk pairs with a replica of the hospital's screen, its column and button lit, with no patient value shown.
- Atkinson Hyperlegible Next throughout, embedded; 13px floor.
- A new turn lands what is playing; reduced motion lands every state at once.

## Colors

Wayfinding colour: a cool neutral wall and white panels carry the floor, navy carries the signs, five department colours carry where things are, and three state colours are earned by what the engine decided.

### Primary
- **Sign Navy** (navy): passed stage signs, the send button, the "you are here" pin, the arrows once lit, the pressed badge's text, text selection. **Sign Navy Light** (navy-2): the current stage sign and the send button's hover. **Band Navy** (navy-3): the top sign band.
- **On Navy / On Navy 2** (on-navy, on-navy-2): text on navy. On Navy 2 is the status line on a lit sign and an unpressed badge.

### Secondary
- **Department colours** (d-patient-administration blue, d-clinical-ehr teal, d-ancillary-departmental violet, d-administrative-financial amber-brown, d-infrastructure-integration slate): one colour per HIS module, as the crawler's layers name them. Each appears on the module's pictogram tile, on a step sign's number and pressed outline, on the replica's current tab underline, lit column tint (11%) and pressed button, and on the Department sign's tile once passed. Text in a department colour is mixed 82% with black (`--dc-ink`). Clinical is teal, not green, because green is reserved for a passed check.

### Tertiary
- **No Entry Red** (stop, with stop-wash): the Staff only sign when the door stays shut, its no-entry tile, the refusal on the desk (wash ground, red head), and the no-entry pictogram on the "Outside your role" chip.
- **Clear Green** (go, with go-wash): a check passed. The tick tile on a passed sign, each rule that passed on the door's board, each detail given, the answer's tile, and the foot's self-check.
- **Wayfinding Amber** (amber, amber-ink): "you are here". Focus outlines, the Tour button, the pin's ring, the current board's sign outline, the tour chip's border, the underline under the words the enquiry matched, and the ask box's focus halo (45%).

### Neutral
- **Corridor Wall** (wall): the page. **Wall 2** (wall-2): a waiting stage sign.
- **Panel / Panel 2** (panel, panel-2): the desk, the board, chips, step signs; Panel 2 for hover, a question, a disabled input.
- **Ink / Ink 2 / Ink 3** (ink, ink-2, ink-3): text; secondary; labels, status, quiet notes.
- **Rule / Rule 2** (rule, rule-2): borders of chips, signs and inputs; hairlines on the desk.
- **Unlit** (unlit): a waiting sign's tile and an unused department on the board.
- **Your Slip** (you-slip): the visitor's own message.
- **Replica Chrome / Replica Ground** (replica-chrome, replica-ground): the hospital portal's own greys, kept apart from our navy so the replica reads as their screen.

### Named Rules
**The Earned State Rule.** Red means the staff-only door stayed shut, green means a check passed, amber means "you are here". None of the three marks anything else.

**The Department Colour Rule.** A department colour belongs to its module. It appears wherever a step goes to that module (tile, step number, replica tab, column, button), never as decoration. The Department sign takes its module's colour only once passed.

**The Their Screen Rule.** The replica keeps the hospital portal's own greys. Our navy appears on it only as the pin.

## Typography

**Body Font:** Atkinson Hyperlegible Next (SIL OFL; embedded latin WOFF2, variable weight 200-800, font-display: block; fallback Segoe UI, system-ui, sans-serif)

**Character:** One signage face built for legibility, set like wayfinding: bold short names on signs, regular status beneath, tabular lining figures everywhere.

### Hierarchy
- **Title** (700, 1.125rem, +0.005em): "HIS Staff Assistant" in the band.
- **Board head** (700, 1rem): the board's stage name, with a muted 400 aside; the reply heads on the desk.
- **Said** (400, 1.0625rem): the visitor's words on the Enquiry board, matched words in navy 700 over a 2px amber underline.
- **Body** (400, 1rem, lh 1.45): replies, the ask box, step text.
- **Sign name** (700, 0.9375rem, lh 1.15; 0.875rem on compact signs): stage names, badge names, the Tour button.
- **Chip** (400, 0.875rem): task chips, rule ids, slot names.
- **Label** (400, 0.8125rem, lh 1.2): sign status, step "where" lines, facts, group heads (700, Ink 3), badge task counts, everything on the replica, the foot.
- **Key cap** (700, 0.8125rem): the foot's key caps.
- **Stamp** (700, 0.8125rem, uppercase, +0.02em): the "Stopped" stamp on a cancelled request; the only uppercase.

### Named Rules
**The One Face Rule.** Atkinson Hyperlegible Next sets everything, the replica included. No second face and no monospace.

**The 13px Floor Rule.** Nothing read is set below 0.8125rem of a root that is never below 16px (`clamp(16px, 0.6vw + 8px, 19px)`).

## Layout

The page is a three-row grid filling the viewport (100dvh): the band (3.5rem), the floor, the foot (2.25rem). The floor is two columns, the desk (42fr) and the route (58fr), 1.25rem apart, padded 1rem 1.25rem .875rem.

- **Band:** the information tile and the title at left; the three badges (pictogram, name, task count) at right; the Tour button (amber, "Tour · Reception").
- **Desk:** the conversation (scrolls), the task strip, the ask bar. The welcome carries the badge's task directory in a disclosure ("Your tasks · n"), open on desktop and closed on a phone. The task strip is a two-column grid: a label column ("Common", "Outside your role") and a row of chips (three common tasks and "All tasks"; one dashed chip for a task outside the role).
- **Route:** three rows: the stage signs, the board at a fixed height (`--board-h`), the replica filling the rest. The five signs share one row, 1.375rem apart, a drawn arrow in each gap.
- **Fixed route geometry.** A sign is a fixed height (3.75rem) with its status clamped to two lines; the board is `--board-h` (12.5rem; 12rem at ≤760px viewport height) and scrolls only as a fallback. Driving every task and probe at 1280/1366/1440/1600/1920 gives one route geometry per screen size: the signs, board and replica never move as answers change.
- **Replica:** a chrome bar (2rem: "HIS Portal", the access notice, "signed in: role"), the module tabs, then the page. On the home view it shows a two-column directory of the five modules. On a step it shows the module's title line with the pin inline at its right, the buttons, and the list table (four blank ruled rows) or the record page (label column and blank values), then "No patient data is shown here."
- **Foot:** the self-check line (or the typing-off notice), "Screens as of" the crawl date, the keys at right.
- **Scale:** root `clamp(16px, 0.6vw + 8px, 19px)`; everything in rem.
- **Compact signs** (861-1680px wide): stages 1rem apart, arrows .875rem, sign tiles 1.5rem, sign names .875rem.
- **1320px and narrower:** the "Screens as of" line goes.
- **1180px and narrower:** badges drop their task count.
- **Short screens** (max-height 760px, wider than 860px): band 3.25rem, foot 2rem, floor padding .75rem, signs 3.375rem, board 12rem.
- **860px and narrower (phone):** the page scrolls; the band wraps with the badges as a full-width row (no pictogram) and Tour without its role. The floor is one column. The conversation grows with its answers, each new answer scrolls to its start, and the ask bar sticks to the bottom of the screen. The task strip is one column. The route becomes a stack of signs (no arrows, status on one line at the right). The board grows, the replica is at least 22rem with a sideways-scrolling table, and the keys go.
- **520px and narrower:** the ask box's placeholder shortens to "Ask for an HIS task".

## Elevation & Depth

Signs on a wall. Depth is a sign standing off the wall and nothing else: the band over the floor, the desk, board and replica as panels, a lit sign lifting slightly as it passes. Everything inside a panel is flat, separated by 1px rules and tinted washes.

### Shadow Vocabulary
- **Band** (`box-shadow: 0 1px 0 rgba(255, 255, 255, .06), 0 6px 14px -10px rgba(15, 38, 71, .7)`): the sign band over the floor.
- **Panel** (`box-shadow: 0 1px 1px rgba(19, 32, 45, .08), 0 8px 20px -14px rgba(19, 32, 45, .45)`): the desk and the board.
- **Replica** (`box-shadow: 0 1px 1px rgba(19, 32, 45, .08), 0 10px 24px -16px rgba(19, 32, 45, .55)`, with a 1px #c4cbd2 border): the hospital's screen.
- **Lit sign** (`box-shadow: 0 3px 8px -5px rgba(15, 38, 71, .8)`; stopped `0 3px 8px -5px rgba(120, 10, 25, .8)`): a passed or shut stage sign.
- **Pressed badge** (`box-shadow: 0 2px 6px -2px rgba(0, 0, 0, .45)`).
- **Tour button** (`box-shadow: inset 0 -2px 0 rgba(0, 0, 0, .14)`): a flat amber key with a lip.
- **Rings, not shadows:** the pin's amber ring (`0 0 0 2px`), a pressed step's department ring (`0 0 0 1px`), the pressed replica button's halo (`0 0 0 3px`, department at 22%), the ask box's focus halo (`0 0 0 3px rgba(232, 164, 0, .45)`).

### Named Rules
**The Off The Wall Rule.** A shadow appears only where a sign stands off the wall: the band, the panels, a lit stage sign, the pressed badge. No decorative gradient, no glass, no side stripe.

## Shapes

Sign corners. Stage signs, badges, chips, step signs, the refusal, the ask box and the Tour and send buttons are 6px; panels and the replica 8px; pictogram tiles and the pin 5px (the foot's tile 4px); key caps and the replica's buttons 4px. The visitor's own message is a slip with one tucked corner (8px 8px 2px 8px). Borders carry state: 1.5px on stage signs and the ask box, dashed for an unknown enquiry, a task outside the role, a detail still to come, a rule not reached, and a step withheld. Pictograms are drawn on a 24px grid with a 1.75 stroke (2.1 on tiles), round caps and joins. Arrows between signs are the same drawn arrow used as a mask.

## Components

### Stage signs (signature)
Five fixed signs: Enquiry, Staff only, Details, Department, Screen. Each is a tile and a name over a two-line status ("Understood", "Open: 3 of 3 rules", "All 2 given", the module, "n steps placed"). States: waiting (Wall 2, unlit tile, the stage pictogram); current (Navy Light, a white tile); passed (Navy, a green tick tile; the Department sign's tile becomes its module's pictogram in its colour, ringed white); stopped (red, a white no-entry tile, "No entry · PL‑01"); unknown (white panel, dashed Ink 3 border, a question tile). The sign whose board is shown carries a 2px amber outline. Clicking a sign shows its board.

### Boards
One per stage, under the signs at the fixed board height. Enquiry quotes the words with the matched ones underlined in amber; or, when several tasks fit, the options as chips (it asks rather than guesses). Staff only lists the badge's three rules: a tile (green tick, red no-entry, or dashed "not reached"), the rule id and the rule. Details lists each slot with how it was given. Department lists the five modules with the steps that use each, tinted 9% in its colour, the rest unlit, over Purpose, Data and Keep facts. Screen has a step selector (numbers in department colours) and the step's text.

### Replica screen
The hospital's portal as crawled: chrome, module tabs (the current one underlined in its department colour), a page title line carrying the pin, the module's buttons and its list or record layout with blank values. A lit column or field is tinted 11% in the department colour. The pressed button is outlined 2px in it, with a 3px halo. The pin is navy with an amber ring and always reads "Step n: press …" (or "the column(s) lit") inline on the title line. A step that cannot be placed shows a dashed "withheld rather than guessed" note.

### Step signs
The answer on the desk: one button a step, the number on a 1.625rem tile in its department colour, the step text, a "where" line (module in the department's ink, screen, the button in quotes) and an optional note. The pressed step takes its department border, a 7% wash and a 1px ring. Facts follow (Why, Keep).

### Refusal
A No Entry wash panel with a red 1px border: "Not for Reception: …", the engine's reason, the hand-off with a drawn arrow ("This is something nurse can do"), and "No patient details were asked for." A cancelled request keeps its turn on the desk with an outlined "Stopped" stamp.

### Buttons
- **Badge:** transparent with a 22% white border on the band; hover 8% white; pressed white with navy text and a soft shadow.
- **Tour:** amber with Amber Ink, a play pictogram, "Tour · Role"; while touring it reads "Stop" on white.
- **Send:** navy with a drawn arrow; hover Navy Light; 1px down when pressed; greyed when typing is off.
- **Chips:** white with a Rule border, hover navy border; "All tasks" bold; outside the role dashed with a red no-entry pictogram; the tour chip amber-bordered on #fff7e2.
- **Focus:** a 3px amber outline, 2px offset.

### Inputs / Fields
- **Ask box:** 2.75rem, white, 1.5px Rule border, navy caret; on focus a navy border and the amber halo; a warm #fff8e6 ground while a tour types into it.

### Navigation
- **Keys:** `/` to type, 1 2 3 a badge, T a tour, Space lands what is moving (in a tour, the next turn), Esc to stop it. Badges carry `aria-keyshortcuts`; the foot shows the keys as caps.

### Motion
One ease, `cubic-bezier(.16, 1, .3, 1)`. One timer table (`later`, `land`): a new turn calls `land()` first, so whatever was playing lands whole before the next request walks.
- **The walk:** signs that change light one after another, 190ms apart, each settling from scale .97 in 220ms. When a sign passes, the arrow into the next is drawn by a clip-path wipe on its `::before` (180ms). Colours change by 220ms transitions.
- **Board and replica:** they go quiet (opacity .45) during the walk, then repaint from the new state. The board's lines rise 4px (220ms, 60ms apart), the replica page fades in (200ms), the pin slides in 6px (240ms, +140ms), and the pressed button's halo grows once from 0 to 3px, ease-out over 280ms (+200ms).
- **The desk:** each message rises 4px in 220ms with no overshoot.
- **The tour:** it types at 26ms a character, waits 380ms, then asks; 1.8s after an answer and 1.5s after anything else; then it walks the answer's steps on the replica 1.7s apart. Space skips to the next turn.
- **Reduced motion:** every state lands at once (no transitions, no animations; timers fire immediately; the tour's waits are capped at 300ms).
- **At rest:** nothing moves.

## Do's and Don'ts

### Do:
- **Do** show every request as a route through five fixed stage signs; change only their state.
- **Do** keep red for the staff-only door when it stays shut, green for a check passed, amber for "you are here".
- **Do** give each HIS module its department colour, and use it only where a step goes to that module.
- **Do** pair every step with the replica screen that proves where it happens, its column and button lit and the pin inline on the title line.
- **Do** keep the route's geometry fixed: signs 3.75rem with the status clamped to two lines, the board at `--board-h` (12.5rem; 12rem at ≤760px viewport height).
- **Do** draw every pictogram and arrow in the one stroked family on square tiles.
- **Do** set everything in Atkinson Hyperlegible Next, embedded, at or above the 13px floor.
- **Do** call `land()` before a new turn, and land every state at once under reduced motion.
- **Do** keep the file single and offline.

### Don't:
- **Don't** show a patient value: the replica's rows stay blank and say "No patient data is shown here."
- **Don't** use green for a department; Clinical is teal because green means a check passed.
- **Don't** say "crawler", "Python" or a URL path in staff-facing text.
- **Don't** let the signs, board or replica resize as answers change.
- **Don't** add a decorative gradient, glass, a side stripe, or a shadow on anything that is not a sign standing off the wall.
- **Don't** use glyphs or an icon font for pictograms or arrows.
- **Don't** overshoot or bounce; rises are 220ms and the press halo grows once.
- **Don't** turn the page into a chatbot with a side panel or a node-graph pipeline.
- **Don't** set anything read below 0.8125rem.
