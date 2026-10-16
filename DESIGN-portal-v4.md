---
name: Technique Datasheets
description: Portal version 4, The Datasheet. Each extraction technique specified like an electronic component in a four-page datasheet; a matte grey desk under a lamp and a stack of white landscape sheets with a paper tooth, ink, hairline tables with a shaded head row, one engineering blue, red only where a rating is exceeded or a rule breaks; every move a recorded fact being set; Barlow and Barlow Semi Condensed embedded in one offline file.
colors:
  desk: "#dde1e5"
  sheet: "#ffffff"
  ink: "#121417"
  ink-2: "#3f464c"
  ink-3: "#596167"
  not-connected: "#858d93"
  rule: "#c5ccd2"
  rule-2: "#e3e7ea"
  head: "#eef1f4"
  blue: "#0a58a8"
  blue-wash: "#e6eef8"
  red: "#c0271b"
  grey-curve: "#9aa2a8"
  slate: "rgb(18, 20, 23)"
typography:
  part-number:
    fontFamily: "\"Barlow Semi Condensed\", \"Barlow\", \"Segoe UI\", system-ui, sans-serif"
    fontSize: "2rem"
    fontWeight: 500
    lineHeight: 1
    letterSpacing: "-0.01em"
  part-title:
    fontFamily: "\"Barlow\", \"Segoe UI Variable Text\", \"Segoe UI\", system-ui, sans-serif"
    fontSize: "1rem"
    fontWeight: 500
    lineHeight: 1.25
  section-head:
    fontFamily: "\"Barlow\", \"Segoe UI Variable Text\", \"Segoe UI\", system-ui, sans-serif"
    fontSize: "1rem"
    fontWeight: 600
    lineHeight: 1.2
  body:
    fontFamily: "\"Barlow\", \"Segoe UI Variable Text\", \"Segoe UI\", system-ui, sans-serif"
    fontSize: "1rem"
    fontWeight: 400
    lineHeight: 1.4
    fontFeature: "\"tnum\", \"lnum\""
  text:
    fontFamily: "\"Barlow\", \"Segoe UI Variable Text\", \"Segoe UI\", system-ui, sans-serif"
    fontSize: "0.9375rem"
    fontWeight: 400
    lineHeight: 1.45
  table:
    fontFamily: "\"Barlow Semi Condensed\", \"Barlow\", \"Segoe UI\", system-ui, sans-serif"
    fontSize: "0.875rem"
    fontWeight: 400
    lineHeight: 1.3
    fontFeature: "\"tnum\", \"lnum\""
  table-head:
    fontFamily: "\"Barlow Semi Condensed\", \"Barlow\", \"Segoe UI\", system-ui, sans-serif"
    fontSize: "0.8125rem"
    fontWeight: 600
    lineHeight: 1.2
    letterSpacing: "0.02em"
  caption:
    fontFamily: "\"Barlow Semi Condensed\", \"Barlow\", \"Segoe UI\", system-ui, sans-serif"
    fontSize: "0.8125rem"
    fontWeight: 400
    lineHeight: 1.35
  chrome:
    fontFamily: "\"Barlow Semi Condensed\", \"Barlow\", \"Segoe UI\", system-ui, sans-serif"
    fontSize: "0.9375rem"
    fontWeight: 500
    lineHeight: 1.2
  key-cap:
    fontFamily: "\"Barlow Semi Condensed\", \"Barlow\", \"Segoe UI\", system-ui, sans-serif"
    fontSize: "0.8125rem"
    fontWeight: 500
    lineHeight: 1
rounded:
  none: "0"
  mark: "1px"
  key: "3px"
spacing:
  hair: "0.1875rem"
  xs: "0.3125rem"
  sm: "0.5rem"
  md: "0.875rem"
  lg: "1.25rem"
  sheet-x: "1.5rem"
  col-gap: "1.75rem"
components:
  next-key:
    backgroundColor: "{colors.ink}"
    textColor: "{colors.sheet}"
    rounded: "{rounded.key}"
    height: "2.25rem"
    padding: "0 0.5rem 0 0.875rem"
  back-key:
    backgroundColor: "{colors.sheet}"
    textColor: "{colors.ink}"
    rounded: "{rounded.key}"
    size: "2.25rem"
  key-cap:
    backgroundColor: "{colors.sheet}"
    textColor: "{colors.ink-2}"
    typography: "{typography.key-cap}"
    rounded: "{rounded.key}"
    height: "1.375rem"
    padding: "0 0.3125rem"
  part-tab:
    textColor: "{colors.ink-2}"
    typography: "{typography.chrome}"
    rounded: "{rounded.key}"
    height: "2.125rem"
    padding: "0 0.75rem"
  part-tab-hover:
    backgroundColor: "rgba(18, 20, 23, .06)"
    textColor: "{colors.ink}"
  part-tab-marker:
    backgroundColor: "{colors.sheet}"
    textColor: "{colors.ink}"
    rounded: "{rounded.key}"
    height: "2.125rem"
  picker:
    textColor: "{colors.ink}"
    typography: "{typography.chrome}"
    rounded: "{rounded.none}"
    padding: "0.1875rem 1.25rem 0.1875rem 0"
  told-option:
    textColor: "{colors.ink-3}"
    typography: "{typography.chrome}"
    padding: "0.1875rem 0"
  told-option-checked:
    textColor: "{colors.ink}"
  page-tab:
    textColor: "{colors.ink-3}"
    padding: "0.5rem 0.625rem"
  page-tab-current:
    textColor: "{colors.ink}"
  page-rule:
    backgroundColor: "{colors.blue}"
    height: "2px"
  sheet:
    backgroundColor: "{colors.sheet}"
    textColor: "{colors.ink}"
    rounded: "{rounded.none}"
    padding: "1rem 1.5rem 0.625rem"
  table-head-row:
    backgroundColor: "{colors.head}"
    textColor: "{colors.ink-2}"
    typography: "{typography.table-head}"
    padding: "0.3125rem 0.5rem"
  table-cell:
    textColor: "{colors.ink}"
    typography: "{typography.table}"
    padding: "0.25rem 0.5rem"
  table-row-current:
    backgroundColor: "{colors.blue-wash}"
  table-cell-over:
    textColor: "{colors.red}"
---

# Design System: Technique Datasheets

## Overview

**Creative North Star: "The Component Datasheet"**

Portal version 4 specifies each extraction technique the way an electronic component is specified, for an engineering panel that reads datasheets every week. A technique is a part: ours the reference design (part number `compliance-aware`), an AI model at a briefing (`<model>-<briefing>`), the baseline (`unconstrained`). Each part has a four-page datasheet: 1 the front page (features, applications, description, the pin configuration of the 34 fields, a device comparison table), 2 specifications (absolute maximum ratings from the job's purpose policy, recommended operating conditions from the job's expert field list, characteristics MIN / TYP / MAX over five runs), 3 typical characteristics (curves), 4 application information (the manifest as a register map, the export as the package, ordering information as the briefings, revision history). Switching the part, the job or what the model was told re-specifies the sheet in place.

The world is a well-set datasheet lying on a desk under a lamp. The desk is matte grey with a fine grain, a soft pool of light near the middle and a slate fall-off to the edges; the viewer strip and the foot are cut from the same desk, so a lifting sheet passes under them. The datasheet is a stack: the pages still to read lie beneath the open one, edge on edge, so the stack's depth says which page you are on. The sheet itself has a paper tooth and a faint lamp gradient; on it, near-black ink, hairline table rules under a shaded head row and an ink top rule, and a printed blue masthead band. One engineering blue carries the band, section numbers, this part's own curve, the current row, the page rule and focus; red appears only in the cell where a rating is exceeded or a rule breaks. Type is the material: the part number and the tables carry the page. Barlow sets text; Barlow Semi Condensed sets tables, part numbers, figure labels, field names, registers and tokens. Drawings are drawn from the data as SVG.

Motion is at the level of Portal v2 and every move is a recorded fact being set: the sheet lifts over its top edge to turn a page, the next page reads itself in (pins grow from the package, readings ink in, MIN then TYP then MAX, curves traced, backings drawn), and another part is printed over the last by a print head. Datasheet furniture is honoured: a document line, numbered sections 1-10, numbered tables and figures with bold captions, superscript footnotes, a sheet footer with the part number and "n of 4". Density is presentation density for a projected 1366x768 laptop: the sheet fills the viewport between a thin viewer strip and a foot, nothing scrolls at that size, and the presenter explains.

The user's standing bar holds over all of it: maintain elegance and professionalism in design. The system keeps it as restraint: material that stays quiet (grain, tooth and lamp felt rather than seen, one blue, red only when earned) and motion that explains a change and then stops.

**Key Characteristics:**
- A matte grey desk under a lamp (grain, a light pool, a slate fall-off); the datasheet a stack of white sheets with a paper tooth, the pages still to read beneath the open one.
- One engineering blue (masthead band, section numbers, the part's curve, the current row, the page rule, focus); red per cell only where a rating is exceeded or a rule breaks.
- Two embedded OFL faces: Barlow (400/500/600) for text, Barlow Semi Condensed (400/500) for tables, part numbers, figure labels, field names, registers and tokens; tabular lining figures throughout; no monospace on the sheet.
- Hairline tables with a shaded head row and an ink top rule; uppercase only in table heads (and the package's module markings in the pin drawing).
- Four pages per part, numbered sections, tables, figures and footnotes; the pin configuration and the curves are SVG drawn from the data.
- Elegance and professionalism as the standing bar: restrained material, motion that explains a change and then stops.
- Paging lifts the sheet over its top edge; each page reads itself in; re-specifying is a print head sweeping the sheet; a second Space lands any step; nothing counts up from zero.

## Colors

Ink on white paper on a grey desk: blue names "this part, this place"; red names a rating exceeded or a rule broken; greys and a cool slate shade carry everything else.

### Primary
- **Engineering Blue** (blue): the printed masthead band, section numbers, footnote superscripts, the part-tab letters, the sliding page rule and the current page number, the told option's underline, this part's own curve and its label, the applications bullet for the current job, focus outlines and text selection.
- **Current Row Wash** (blue-wash): the sliding wash behind the current row of the device comparison, and the current row of any other table (the current briefing in ordering information).

### Tertiary
- **Rating Red** (red): only per cell, where a characteristic exceeds an absolute maximum rating or a rule is not held: the MIN / TYP / MAX cell that is over, the parameter name of a row that is over, a trap count below its total, a pin connected outside the purpose (stroke and name), an unbacked register control (struck through), retention never declared, quasi-identifiers exported as read, and raw identifiers exported only where the job's purpose requires pseudonymised identifiers. In motion it arrives as a brief red wash (20% red) on the cell, after the reading is printed.

### Neutral
- **Desk** (desk): the surface under the lamp, shared by the viewer strip and the foot.
- **Slate** (slate): the only shade colour, always at low alpha: the desk's fall-off, the stack's edges and step shadows, the paper shadow, the lifting sheet's shade and cast, the print head, hover fills on the desk (6%) and on rows (4%).
- **Sheet** (sheet): the paper, the sliding part tab, key caps and the Back key.
- **Ink** (ink): text, table top rules, the package outline, connected pins, the Next key, feature bullets.
- **Ink 2** (ink-2): the part title, running text, table head text, captions.
- **Ink 3** (ink-3): labels, the conditions line under a section head, footnotes, the sheet footer, axis lines and ticks, "needed, not connected" pins (dashed), unselected told options and page tabs.
- **Not Connected** (not-connected): a pin not connected and its name, a null register value.
- **Rule / Rule 2** (rule, rule-2): Rule for section-head underlines, a table's head-row bottom and last row, key borders, the part tab's border, unconnected pin stubs, the sheet footer's top rule; Rule 2 for hairlines between table rows and chart gridlines.
- **Table Head** (head): the shaded head row of every table.
- **Other Curve** (grey-curve): every curve that is not this part's.

### Named Rules
**The Restraint Rule.** Elegance and professionalism are the standing bar: material stays quiet, and every motion explains a change and then stops.

**The Colour Is Earned Rule.** One accent and red, nothing else. Blue points at "this part, this row, this page"; it never decorates.

**The Red Is Per Cell Rule.** Red marks the exact cell (or pin, or value) that exceeds a rating or breaks a rule, never a whole part, row band or table. A raw identifier is red only where the job's purpose rates it (requires pseudonymised identifiers); elsewhere it is reported in ink.

**The Red Is Earned In Order Rule.** A row is named a breach only after its readings are down: its label stays in ink, and its reason unwritten, until MIN, TYP and MAX are printed, then the red arrives with a brief wash on the cells over.

## Typography

**Body Font:** Barlow (SIL OFL; embedded WOFF2 at 400, 500 and 600, font-display: block; fallback Segoe UI Variable Text, Segoe UI, system-ui)
**Label Font:** Barlow Semi Condensed (SIL OFL; embedded WOFF2 at 400 and 500; fallback Barlow, Segoe UI, system-ui)

**Character:** A DIN-like engineering grotesk and its semi-condensed cut, as datasheets are set: Barlow for what is read as prose and headings, Semi Condensed for what is read as data. Tabular, lining figures on the body.

### Hierarchy
- **Part number** (Semi Condensed 500, 2rem, lh 1, -0.01em): the masthead; 1.75rem on short screens, 1.625rem and wrapping on phones.
- **Part title** (Barlow 500, 1rem, Ink 2) under it; the document line at right in Semi Condensed 0.8125rem Ink 3 with "Datasheet" in Barlow 600 1rem Ink.
- **Section head** (Barlow 600, 1rem, a Rule underline): number in blue 600 (1, 2, 6.1, 8.2), then the title.
- **Text** (Barlow 400, 0.9375rem, lh 1.45, Ink 2): features, applications, description.
- **Table** (Semi Condensed 400, 0.875rem, lh 1.3; 0.8125rem on phones and in the device comparison); **Table head** (Semi Condensed 600, 0.8125rem, uppercase, +0.02em, Ink 2).
- **Symbols** (Barlow 0.9375rem, Ink 2) with a 0.8125rem subscript: N<sub>read</sub>, t<sub>ret</sub>.
- **Caption / conditions / notes** (Semi Condensed 400, 0.8125rem): "Table 2." and "Figure 1." in 600 Ink; the conditions line under a section head in Ink 3.
- **Chrome** (Semi Condensed 500, 0.9375rem): part tabs, pickers, told options; page tabs 0.875rem.
- **Drawing labels:** pin names and pin numbers Semi Condensed 0.8125rem (rem, so the drawing's labels hold the floor); module markings 600 0.8125rem uppercase +0.04em; chart ticks and axis titles Semi Condensed 13px.

### Named Rules
**The Two Cuts Rule.** Barlow for words; Barlow Semi Condensed for data (tables, part numbers, figure labels, field names, registers, tokens). No third face, and no monospace on the sheet.

**The 13px Floor Rule.** Nothing read is set below 0.8125rem of a root that is never below 16px; SVG labels are sized in rem or at 13px.

## Layout

The desk is a three-row grid filling the viewport (100dvh): the viewer strip (3.25rem), the sheet, the foot (3.5rem). The desk carries the perspective (9000px, origin 50% 8%) that a turning page lifts in.

- **Viewer strip:** the mark (a sheet with a blue band, SVG) and "Datasheets"; three part tabs (a Reference design, b the AI model as a select, c Baseline), the letter in blue, the white tab sliding under the chosen one; at right the Job picker and the Told options. It sits above the sheet (stacked over it) and paints the desk, so a lifting sheet passes beneath it.
- **Sheet:** 0.875rem from the desk's left edge and 1.625rem from its right (room for the stack's edges), padding 1rem 1.5rem 0.625rem, three rows: the masthead (part number and title left, document line right, the printed 4px blue band beneath), the body, the sheet footer (part number, the source line, "n of 4", over a Rule).
- **Pages:** 1 three columns (0.86 / 1.04 / 1.2fr: features, applications and description; the pin configuration; the device comparison); 2 two columns (0.9 / 1.45fr: ratings and operating conditions; characteristics); 3 a full-width head over three equal figures; 4 two columns (1.05 / 1fr: register map; package, ordering, revisions). Columns 1.75rem apart.
- **Foot:** Back and Next at left, the four page tabs centred over the sliding page rule, the keys hint at right.
- **Scale:** root `clamp(16px, 0.62vw + 7.6px, 20px)`; everything in rem.
- **Short screens** (max-height 760px, wider than 860px): tighter strip and foot (3rem / 3.125rem), part number 1.75rem, table cells and gaps tightened so the sheet still fits.
- **Narrow:** at 1400px the page tabs show numbers only (the current one keeps its name); at 1300px column gaps 1.125rem and sheet sides 1.125rem; at 1200px the keys hint and the "Datasheets" title go; at 860px the desk stacks and scrolls (the desk's light no longer fixed), the strip wraps, every page becomes one column, figures take a fixed 22rem, the pin drawing is replaced by a pin functions table, the register map becomes rows, low-priority columns and notes hide, the foot sticks to the bottom with only the current page tab, and paging and re-specifying fall back to a short rise.

## Elevation & Depth

Layered paper on a lit desk. Depth comes from three things only: the lamp on the desk (a radial light pool over a slate vignette and grain, fixed to the viewport so the strip and the foot share it), the stack of sheets (the open sheet lifted softly, the unread pages beneath it as edges), and the keys on the desk (part tab, Back, Next, key caps), which sit as keys. Everything printed on the sheet is flat: separation there is hairlines and the shaded head row. The paper's tooth (a fine noise) and a lamp gradient (a little brighter top left, a little cooler at the fore-edge) sit over the whole sheet.

### Shadow Vocabulary
- **Page stack** (drawn per page by the script; for each unread page i: `{5i}px {i}px 0 -1px #fff`, `{5i}px {i}px 0 0 rgba(18,20,23,.32)`, `{5i+1}px {i+1}px 4px -1px rgba(18,20,23,.18)`; then `0 1px 2px rgba(18,20,23,.14)` and `{5n}px {14+n}px 30px -14px rgba(18,20,23,.38)`): the open sheet with the pages still to read beneath it, each stepped 5px right and 1px down as a white edge, a hairline and a soft step shadow. Three edges on page 1, none on page 4.
- **Paper** (`box-shadow: 0 1px 2px rgba(18, 20, 23, .14), 0 14px 30px -14px rgba(18, 20, 23, .38)`): the sheet at rest with nothing beneath it (the stylesheet's own value).
- **Part tab** (`box-shadow: 0 1px 0 rgba(18, 20, 23, .06), 0 3px 8px -4px rgba(18, 20, 23, .3)`): the white tab on the desk under the chosen part.
- **Key** (`box-shadow: 0 1px 0 rgba(18, 20, 23, .08), 0 2px 5px -3px rgba(18, 20, 23, .35)`): Back; it presses 1px down when active.
- **Next key** (`box-shadow: inset 0 1px 0 rgba(255, 255, 255, .12), 0 1px 0 rgba(18, 20, 23, .2), 0 4px 10px -4px rgba(18, 20, 23, .55)`): the one dark key, a 180deg ink gradient (#2a2e33 to #101214).
- **Print head** (`box-shadow: 0 -1px 0 rgba(255, 255, 255, .7), 0 5px 10px -3px rgba(18, 20, 23, .4)`): the 3px carriage that sweeps the sheet while re-specifying.
- **Lifting sheet** (shade: a slate gradient over the sheet rising to 60%; cast: a slate gradient on the page beneath, peaking at 30% of the turn): the turning page only.

### Named Rules
**The Paper Stack Rule.** Depth belongs to paper and keys: the desk, the stack of sheets and the keys on the desk. Nothing printed on the sheet casts a shadow.

**The Stack Tells The Page Rule.** The number of edges beneath the open sheet is the number of pages still to read; it is drawn from the page state, never fixed.

## Shapes

Square print. The sheet, tables, pickers and drawings have no radius; key caps, part tabs and the turn keys take a 3px corner; the mark's sheet a 1px corner. Lines are a material: the masthead's printed 4px blue band; a 1px Ink top rule over every table's shaded head; Rule 2 hairlines between rows; pins drawn solid in Ink when connected (2.4px), red when outside the purpose, dashed Ink 3 when needed but not connected, 2px Rule when not connected; in the register map a 1.5px solid underline for a demonstrated control, a 1px dashed one for an attested control, a 1.5px red strike for nothing backing it; square 0.375rem bullets. The page rule is a 2px blue line that travels under the page index; the comparison's current row is a full-width wash, never a side stripe.

## Components

### Pin configuration (signature)
A package outline (Ink 1.4px, a notch at the top) with 17 pins a side, one pin a field of the 34, numbered 1-34 counter-clockwise and grouped by module (dividers inside the package, module markings rotated in uppercase). Pin names in Semi Condensed rem: connected Ink 500, outside the purpose red, needed-not-connected Ink 3 dashed, not connected grey. A legend and "Figure 1." follow. On phones a pin functions table (pin, name, module, run 1) replaces the drawing. Read in: the outline draws with its fill (720ms), then each pin grows out of the package in number order (1 down the left, 18 up the right), its number and name after it.

### Characteristics table
Parameter (with a note or the broken rule ids), symbol with subscript, MIN, TYP (footnoted: median; for the score, the mean), MAX, unit, limit (≤ or ≥). A cell over its rating is red, and the parameter name of that row with it. Read in: rows rise in turn, MIN, TYP and MAX print one after another, then a row over a rating turns red (The Red Is Earned In Order Rule).

### Typical characteristic curves
SVG charts with gridlines in Rule 2, axes in Ink 3 and ticks at 13px: this part's curve blue 2.4px and labelled in blue 600, every other curve grey 1.6px and dashed (6 4, 2 3, 10 3 2 3) to tell them apart without hue. Read in: grid and axes, the other series, then this part's curve traced (1.1s), labels after.

### Register map
Register / Value / Backed by: register names and values in Semi Condensed, nulls grey; the backing control id underlined solid (demonstrated) or dashed (attested), or "nothing" struck red. Read in: rows print cell by cell, then each backing is drawn under its control.

### Device comparison
Every part on one table (reference, each model at the chosen briefing, baseline); a blue wash behind the current row slides to the part chosen (580ms); a row opens that part's datasheet.

### Buttons
- **Next key:** the one dark key, an ink gradient, white Barlow 600 0.9375rem, 3px corner, a Space key cap outlined in 45% white.
- **Back key:** 2.25rem square, white, Rule border, a drawn chevron and a key shadow; Ink border on hover; 1px down when pressed.
- **Focus:** a 2px blue outline, 2px offset, on every control.

### Inputs / Fields
- **Job picker:** a native select with no box, an Ink 3 underline and a drawn chevron.
- **Model picker:** a select inside part tab b, no underline.
- **Told options:** three text options; the checked one Ink with a 1px blue underline (Ink 3 when the AI part is not the one shown).

### Navigation
- **Part tabs:** a / b / c, letter in blue, transparent on the desk with a 6% slate hover; one white tab with a Rule border slides to the chosen part (FLIP, 580ms).
- **Page tabs:** number bold beside the page name; the current one Ink with a blue number, a 2px blue page rule sliding under it (FLIP, 580ms).
- **Keys:** Space / Shift+Space and arrows page, 1-4 a page, Home / End first and last page, a b c a part, J job, M model, T told (Shift reverses); `#<part><page>` deep links (`#b2`). A second Space while a step plays lands it.

### Motion
One ease for entrances and markers, `cubic-bezier(.16, 1, .3, 1)`; one engine that tracks every running animation and tween, so a press while busy lands the step whole and nothing moves once it has landed.
- **Paging (760ms):** the open sheet, copied as a leaf over the new page, lifts over its top edge in the desk's perspective: to 64° at scale .94 by 78% of the turn, gone by 80°, darkening as it rises and casting on the page beneath. Going back, the previous sheet comes down again over the current one.
- **Reading in:** each page plays its own entrance (front page, specifications, curves, register map, as in Components); a reading inks in whole (opacity with a 1px settle, 160-300ms; no clip wipe), never half printed.
- **Re-specifying (840ms):** a print head (a 3px slate ink carriage, not a blue rule) sweeps the sheet top to bottom (ease in-out). Above it the new datasheet, below it the last one; every line the head is crossing, on either sheet, is kept whole by a clip path, so no reading ever sits under the wrong part number. A reading over a rating flashes red as the head passes it; this part's curve is traced once its chart is printed; backings are drawn as the head reaches them.
- **Markers (580ms):** the part tab, the page rule and the comparison's wash travel by transform.
- **Never:** counting up from zero; a reading invented on the way.
- **Reduced motion and phones:** reduced motion lands every state whole; below 860px paging and re-specifying fall back to a 0.4s rise.

## Do's and Don'ts

### Do:
- **Do** specify a technique as a part: front page, specifications, typical characteristics, application information, every figure from the recorded run computed by the project's code.
- **Do** keep comparison where a datasheet keeps it: the device comparison table and the curves.
- **Do** colour red per cell, only where a rating is exceeded or a rule is not held; a raw identifier is red only where the job's purpose requires pseudonymised identifiers.
- **Do** keep one blue for this part, this row, this page, and focus.
- **Do** set data in Barlow Semi Condensed and words in Barlow, with tabular lining figures.
- **Do** number sections, tables, figures and footnotes, and caption every table and figure.
- **Do** draw the pin configuration and the curves from the data as SVG, labels in rem, with a table in their place on phones.
- **Do** keep depth in paper and keys: the lit desk, the page stack drawn from the page state, the keys on the desk.
- **Do** keep the standing bar, elegance and professionalism: restrained material, motion that explains a change and then stops.
- **Do** make every move a recorded fact being set (a pin connecting, a reading printed, a curve traced, a backing drawn), and let a second Space land it.
- **Do** keep the file single and offline with both faces embedded.

### Don't:
- **Don't** add a hue beyond the engineering blue and the rating red.
- **Don't** use monospace on the sheet, or a third face.
- **Don't** set uppercase outside table heads and the package's module markings.
- **Don't** cast a shadow from anything printed on the sheet, or put a dark offset slab under any element.
- **Don't** count a figure up from zero or show a reading half printed or under another part's number.
- **Don't** add lanes, dots, flows, metro lines, dark neon, KPI tiles, cards or pills.
- **Don't** mark a current row with a side stripe; it takes the full-width wash.
- **Don't** set anything read below 0.8125rem (13px at the floor of the root clamp).
- **Don't** show a raw identifier, contact detail or quasi-identifier; the builder refuses to write if one appears.
- **Don't** add explanatory prose to a page; labels, tables, figures, one caption line and footnotes; the presenter explains.
