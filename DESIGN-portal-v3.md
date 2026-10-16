---
name: Catalogue of a Run
description: Portal version 3, The Catalogue. The recorded run catalogued like a museum's collection, an open book lying on a linen table under a lamp; one spread at a time, a plate (one real object the run left behind) tipped in on the left, its catalogue entry with one figure set monumental on the right; grained paper pages, each comparandum printed on its own stock (viridian, ultramarine, ochre), stone for shared plates, one red for a breach, a night-plate frontispiece; leaves that turn and plates that play; one offline file with Archivo embedded.
colors:
  paper: "#fdfcf9"
  table: "#e2ddd3"
  umber: "#3e3018"
  plate: "#eef0f1"
  plate-2: "#e3e7e8"
  ink: "#15181a"
  ink-2: "#474e53"
  ink-3: "#61686d"
  ghost: "#7a8186"
  rule: "#d2d7da"
  red: "#b3261e"
  stock-a: "#0b7a62"
  stock-a-tint: "#dbeee6"
  stock-b: "#3b45b0"
  stock-b-tint: "#e3e5f8"
  stock-c: "#a3610f"
  stock-c-tint: "#f5e7cd"
  night: "#16191c"
typography:
  figure:
    fontFamily: "Archivo, \"Segoe UI Variable Text\", \"Segoe UI\", system-ui, sans-serif"
    fontSize: "7rem"
    fontWeight: 220
    lineHeight: 0.86
    letterSpacing: "-0.035em"
    fontVariation: "\"wdth\" 125"
    fontFeature: "\"tnum\", \"lnum\""
  figure-mid:
    fontFamily: "Archivo, \"Segoe UI Variable Text\", \"Segoe UI\", system-ui, sans-serif"
    fontSize: "5rem"
    fontWeight: 220
    lineHeight: 0.86
    letterSpacing: "-0.03em"
    fontVariation: "\"wdth\" 125"
  figure-long:
    fontFamily: "Archivo, \"Segoe UI Variable Text\", \"Segoe UI\", system-ui, sans-serif"
    fontSize: "3.75rem"
    fontWeight: 220
    lineHeight: 0.86
    letterSpacing: "-0.02em"
    fontVariation: "\"wdth\" 125"
  figure-unit:
    fontFamily: "Archivo, \"Segoe UI Variable Text\", \"Segoe UI\", system-ui, sans-serif"
    fontSize: "1.5rem"
    fontWeight: 300
    fontVariation: "\"wdth\" 112"
  cover-title:
    fontFamily: "Archivo, \"Segoe UI Variable Text\", \"Segoe UI\", system-ui, sans-serif"
    fontSize: "4.75rem"
    fontWeight: 240
    lineHeight: 0.92
    letterSpacing: "-0.035em"
    fontVariation: "\"wdth\" 125"
  blade-figure:
    fontFamily: "Archivo, \"Segoe UI Variable Text\", \"Segoe UI\", system-ui, sans-serif"
    fontSize: "3.25em"
    fontWeight: 230
    lineHeight: 1
    letterSpacing: "-0.03em"
    fontVariation: "\"wdth\" 125"
  plate-number:
    fontFamily: "Archivo, \"Segoe UI Variable Text\", \"Segoe UI\", system-ui, sans-serif"
    fontSize: "1.5rem"
    fontWeight: 300
    fontVariation: "\"wdth\" 125"
  entry-title:
    fontFamily: "Archivo, \"Segoe UI Variable Text\", \"Segoe UI\", system-ui, sans-serif"
    fontSize: "1.5rem"
    fontWeight: 620
    lineHeight: 1.15
    letterSpacing: "-0.015em"
  catalogue-title:
    fontFamily: "Archivo, \"Segoe UI Variable Text\", \"Segoe UI\", system-ui, sans-serif"
    fontSize: "1.0625rem"
    fontWeight: 640
    letterSpacing: "-0.01em"
  body:
    fontFamily: "Archivo, \"Segoe UI Variable Text\", \"Segoe UI\", system-ui, sans-serif"
    fontSize: "1rem"
    fontWeight: 400
    lineHeight: 1.4
    fontVariation: "\"wdth\" 100"
    fontFeature: "\"tnum\", \"lnum\""
  entry:
    fontFamily: "Archivo, \"Segoe UI Variable Text\", \"Segoe UI\", system-ui, sans-serif"
    fontSize: "0.9375rem"
    fontWeight: 400
    lineHeight: 1.4
  label:
    fontFamily: "Archivo, \"Segoe UI Variable Text\", \"Segoe UI\", system-ui, sans-serif"
    fontSize: "0.8125rem"
    fontWeight: 500
    fontVariation: "\"wdth\" 90"
  stock-tab:
    fontFamily: "Archivo, \"Segoe UI Variable Text\", \"Segoe UI\", system-ui, sans-serif"
    fontSize: "0.875rem"
    fontWeight: 640
    lineHeight: 1
    fontVariation: "\"wdth\" 112"
  plate-field:
    fontFamily: "Archivo, \"Segoe UI Variable Text\", \"Segoe UI\", system-ui, sans-serif"
    fontSize: "1.0625em"
    fontWeight: 400
    lineHeight: 1.45
    fontVariation: "\"wdth\" 90"
  plate-log:
    fontFamily: "Archivo, \"Segoe UI Variable Text\", \"Segoe UI\", system-ui, sans-serif"
    fontSize: "0.8125em"
    fontWeight: 400
    lineHeight: 1.45
    fontVariation: "\"wdth\" 76"
  record-mono:
    fontFamily: "\"Cascadia Mono\", Consolas, \"SF Mono\", Menlo, ui-monospace, monospace"
    fontSize: "0.8125em"
    fontWeight: 400
    lineHeight: 1.5
  key-cap:
    fontFamily: "Archivo, \"Segoe UI Variable Text\", \"Segoe UI\", system-ui, sans-serif"
    fontSize: "0.8125rem"
    fontWeight: 600
    lineHeight: 1
    fontVariation: "\"wdth\" 90"
rounded:
  none: "0"
  tab: "2px"
  kbd: "3px"
  key: "4px"
spacing:
  hair: "0.1875rem"
  xs: "0.3125rem"
  sm: "0.5rem"
  md: "0.875rem"
  lg: "1.25rem"
  gutter: "1.5rem"
  plate-x: "1.75rem"
  spread-gap: "2.75rem"
components:
  table:
    backgroundColor: "{colors.table}"
  page:
    backgroundColor: "{colors.paper}"
    textColor: "{colors.ink}"
    rounded: "{rounded.tab}"
    padding: "1.75rem 1.5rem 0.75rem 2.375rem"
  next-key:
    backgroundColor: "{colors.ink}"
    textColor: "{colors.paper}"
    rounded: "{rounded.key}"
    height: "2.25rem"
    padding: "0 0.5rem 0 0.875rem"
  turn-key:
    backgroundColor: "{colors.paper}"
    textColor: "{colors.ink}"
    rounded: "{rounded.key}"
    size: "2.25rem"
  key-cap:
    backgroundColor: "{colors.paper}"
    textColor: "{colors.ink-2}"
    typography: "{typography.key-cap}"
    rounded: "{rounded.kbd}"
    height: "1.375rem"
    padding: "0 0.3125rem"
  picker:
    textColor: "{colors.ink}"
    rounded: "{rounded.none}"
    padding: "0.1875rem 1.25rem 0.1875rem 0"
  told-option:
    textColor: "{colors.ink-3}"
    padding: "0.1875rem 0"
  told-option-checked:
    textColor: "{colors.ink}"
  plate:
    backgroundColor: "{colors.plate}"
    textColor: "{colors.ink}"
    rounded: "{rounded.none}"
    padding: "1.5rem 1.75rem"
  plate-a:
    backgroundColor: "{colors.stock-a-tint}"
    textColor: "{colors.ink}"
  plate-b:
    backgroundColor: "{colors.stock-b-tint}"
    textColor: "{colors.ink}"
  plate-c:
    backgroundColor: "{colors.stock-c-tint}"
    textColor: "{colors.ink}"
  plate-cover:
    backgroundColor: "{colors.night}"
  stock-tab-a:
    backgroundColor: "{colors.stock-a}"
    textColor: "{colors.paper}"
    typography: "{typography.stock-tab}"
    rounded: "{rounded.tab}"
    size: "1.375rem"
  stock-tab-b:
    backgroundColor: "{colors.stock-b}"
    textColor: "{colors.paper}"
    typography: "{typography.stock-tab}"
    rounded: "{rounded.tab}"
    size: "1.375rem"
  stock-tab-c:
    backgroundColor: "{colors.stock-c}"
    textColor: "{colors.paper}"
    typography: "{typography.stock-tab}"
    rounded: "{rounded.tab}"
    size: "1.375rem"
  comparandum:
    textColor: "{colors.ink-2}"
    typography: "{typography.entry}"
    rounded: "{rounded.none}"
    padding: "0.3125rem 0.5rem"
  comparandum-hover:
    textColor: "{colors.ink}"
  comparandum-a-pressed:
    backgroundColor: "{colors.stock-a-tint}"
    textColor: "{colors.ink}"
  comparandum-b-pressed:
    backgroundColor: "{colors.stock-b-tint}"
    textColor: "{colors.ink}"
  comparandum-c-pressed:
    backgroundColor: "{colors.stock-c-tint}"
    textColor: "{colors.ink}"
  swatch-blade-a:
    backgroundColor: "{colors.stock-a-tint}"
    textColor: "{colors.ink}"
    rounded: "{rounded.tab}"
    height: "6.25em"
  swatch-blade-b:
    backgroundColor: "{colors.stock-b-tint}"
    textColor: "{colors.ink}"
    rounded: "{rounded.tab}"
    height: "6.25em"
  swatch-blade-c:
    backgroundColor: "{colors.stock-c-tint}"
    textColor: "{colors.ink}"
    rounded: "{rounded.tab}"
    height: "6.25em"
  index-tab:
    textColor: "{colors.ink-3}"
    typography: "{typography.label}"
    padding: "0.5rem 0.5rem 0.4375rem"
  index-tab-current:
    textColor: "{colors.ink}"
---

# Design System: Catalogue of a Run

## Overview

**Creative North Star: "The Printed Catalogue, Open on the Table"**

Portal version 3 treats the recorded run as a collection and catalogues it. Every view is the same spread of an open book lying on a linen table under a lamp: on the left page a plate, one real object the pipeline made (the field inventory, the job's request slip, the extract, the browser's page-load log, the declared manifest, the HL7 v2 messages as they left, the retention record, every recorded run, the audit chain), tipped in on its stock; on the right page its catalogue entry, a plate number, a title, one figure set monumental, the comparanda a / b / c, and a short label/value record. Ours, an AI model and the baseline are flipped in place on the same plate: a new stock is rolled across it and the object re-inks behind the roller. A frontispiece opens the book: the three stocks as a swatch fan on a night plate, beside the title and the contents. There are no lanes, no dots, no flows and no tiles.

The world is a museum catalogue printed on coloured stocks, and since the finish pass (2026-10-15) it is a physical one: warm grained paper, a gutter that curves into the spine, the leaves already turned stacked at the left fore-edge and those to come at the right, the plate tipped in with a hairline lift and the grain printed into its tint, the whole book casting a soft umber shadow onto the linen. Each comparandum has its own stock, ours viridian, the AI model ultramarine, the baseline ochre; plates that belong to no comparandum (the hospital, the request, the index) stay on stone grey. One red, reserved for a breach, overrides any stock. One face, Archivo, carries everything; its width axis does the work a second face would. The platform mono is used for the three objects that are machine records in their own right: HL7 segments, the retention record and the audit lines.

Motion is held to the finish level of Portal v2 and every move is a recorded fact being set. A leaf turns in 3D between plates; each plate then plays its own timeline (fields ink in in the order the run read them, the log prints a line a page load, a rule is drawn under each control) and the figure appears with the first mark and counts the marks; a second Space lands whatever is playing. Density is presentation density for a projected 1366x768 laptop: three frame rows, nothing scrolls at the laptop size, the figure readable from the back of the room, words held to labels; the presenter explains.

**Key Characteristics:**
- An open book on a lamp-lit linen table: grained paper pages, a shaded gutter, page-edge stacks that say where you are, the plate tipped in on its stock.
- Three stocks (viridian a, ultramarine b, ochre c) tint a comparandum's plate and ink its figure; stone grey for shared plates; red only for a breach.
- A frontispiece on a lit night plate: the three grained stocks as a swatch fan turning on a drawn eyelet rivet, the title set wide and light, a two-column contents list.
- One embedded face, Archivo (variable weight 100-900, width 62-125%); platform mono only for HL7, the retention record and the audit lines.
- One figure per entry, wide and light at up to 7rem, counted in step with the marks that make it.
- Hairline rules, square corners, no cards, no pills; shadows only where paper lies on paper or on the table, always soft and umber.
- Motion is the run being set: a 3D page turn, per-plate timelines, the comparanda roll; a second Space lands it; reduced motion lands everything.

## Colors

Ink on warm paper, printed on three coloured stocks, lying on linen: hue names whose plate you are looking at, red names a breach, greys carry everything else, umber is only ever shade.

### Primary
- **Ink** (ink): every title, read field and record value, the Next key's face, focus rings; the figure on a shared plate. On a comparandum's plate the figure, plate number, header mark, the travelling index rule, the roller's edge and the caption letter take that stock's deep colour instead. The figure prints with a multiply blend, so it sits in the paper's grain rather than on it.

### Secondary (the three stocks)
- **Viridian** (stock-a on stock-a-tint): ours. Its tab, its figure, its plates' ground, its comparanda band.
- **Ultramarine** (stock-b on stock-b-tint): the AI model. Same roles.
- **Ochre** (stock-c on stock-c-tint): the baseline. Same roles. Because ochre sits near red, an out-of-purpose field keeps its 1px red underline as a second channel on every stock.

### Tertiary
- **Breach Red** (red): only a breach. A field taken out of purpose (red with a 1px underline), a figure that measures a failure (fewer than 7 of 7 rules held, raw identifiers out, Never), a broken rule, an onward use, a backing the register does not give (struck through), a raw identifier in an HL7 segment, a null retention field, the missing purge, the "taken" trap tally. Red overrides the stock: a figure turns red only when it measures a breach, never because the baseline is on the plate.

### Neutral
- **Warm Paper** (paper): both pages of the book, the turn keys and key caps, the letter on a stock tab. Slightly warm so it reads as paper under a lamp, not as a screen.
- **Linen** (table): the table the book lies on, visible around the book and behind the header and foot.
- **Umber** (umber): never a fill. The colour of shade on warm paper, used only at low alpha: the lamp's fall-off to the corners, the linen weave, the gutter, the book's and the plate's shadows, the leaf's shade band and cast shadow, hover washes (6%).
- **Stone** (plate): the ground of the shared plates (1 the hospital, 2 the request, 10 the index) and the plate fallback.
- **Plate Rule** (plate-2): the rule between rows inside a plate (manifest, runs, chain, slip's trap line, retention purge line, index rows); the header mark's plate on shared views.
- **Night** (night): the cover plate only, lit from the upper left, the dark ground the swatch fan lies on.
- **Ink 2** (ink-2): captions, the figure's unit, object titles, unselected comparanda, blade sub-lines.
- **Ink 3** (ink-3): labels: record keys, picker labels, unselected index tabs and told options, log sequence numbers, "needed, not read" fields (dashed underline), the contents list's numbers.
- **Ghost** (ghost): what was not taken. A field or patient a run did not read, a value repeated from run 1, an undeclared control, HL7 field separators. Holds at least 3:1 on all three tints and on stone.
- **Rule** (rule): the comparanda's and the record's top rules, the contents list's top rule, the dashed gap in the audit chain.

### Named Rules
**The Colour Is Earned Rule.** Colour names whose plate it is (a comparandum's stock) or a breach (red), nothing else. No category hues, no decorative accent; chrome stays ink, greys and the warm neutrals of paper and linen.

**The One Stock Per Plate Rule.** A plate carries at most one stock: the pressed comparandum's. Shared plates stay stone. The tint is the plate's ground; the deep colour goes only on the figure and the small markers that point at the comparandum (plate number, header mark, travelling index rule, roller edge, caption letter, tab).

**The Ghost Is Absence Rule.** Ghost grey means "held by the hospital, not taken by this run" (or "same as run 1", or "not declared"). It never styles chrome, and a read value is never ghosted.

**The Umber Is Shade Rule.** Shade on this table is warm umber at low alpha, never black and never a solid fill. Only the night plate, a dark object on its own, takes black shadows.

## Typography

**Display Font:** Archivo (Omnibus-Type, SIL OFL; embedded variable WOFF2, weight 100-900, width 62-125%; fallback Segoe UI Variable Text, Segoe UI, system-ui)
**Body Font:** Archivo
**Label/Mono Font:** Cascadia Mono (platform face; fallback Consolas, SF Mono, Menlo) for HL7 segments, the retention record and audit lines only

**Character:** One grotesque made to do the work of a family by its width axis: the figure is set wide (125) and light (220) like a catalogue's plate number grown monumental; entries sit at normal width and medium weights (540-640); field lists at 90, the page-load log at 76. Tabular, lining figures everywhere, so a counting figure never jitters.

### Hierarchy
- **Cover title** (240, wdth 125, 4.75rem, lh 0.92, -0.035em): "Catalogue of a run" on the frontispiece only, in Ink; 3rem on phones.
- **Figure** (220, wdth 125, 7rem, lh 0.86, -0.035em): the one fact of the entry, in the stock's deep colour on a comparandum's plate, Ink on a shared one, Red when it measures a breach. Steps to 5rem for a word and 3.75rem for a date; shrinks further only if it would overflow.
- **Blade figure** (230, wdth 125, 3.25em off the plate size): the values a technique took, on its swatch blade in its stock colour; 2em on phones.
- **Figure unit** (300, wdth 112, 1.5rem, Ink 2): beside the figure on its baseline.
- **Plate number** (250-300, wdth 125, 1.5rem, the stock's deep colour; Ink 3 on shared plates) beside the **Entry title** (620, 1.5rem, lh 1.15, -0.015em).
- **Catalogue title** (640, 1.0625rem): the header title, hidden on the cover where the cover title stands in.
- **Body** (400, 1rem, lh 1.4); **Entry** (0.9375rem): captions, comparanda rows, the record's values, the contents list.
- **Label** (500, wdth 88-94, 0.8125rem, Ink 3): record keys, picker labels, captions, index tabs, the keys hint.
- **Stock tab** (640, wdth 112, 0.875rem, Paper on the stock): the comparandum letter.
- **Plate type** (in em off the plate's own size): field labels 1.0625em wdth 90; module heads 0.875em 640; the request 1.375em 420; the log 0.8125em wdth 76; object titles 0.8125em 600 wdth 92.
- **Record mono** (400, 0.8125em, lh 1.5; the retention record lh 1.6): HL7, the retention record, audit lines.

### Named Rules
**The Width Is The Material Rule.** Hierarchy comes from Archivo's width and weight axes, never a second display face. Wide and light means "the figure" (and the cover title); condensed means "a list of many"; mono means "a machine wrote this".

**The 13px Floor Rule.** Nothing read is set below 0.8125rem of a root that is never below 16px (13px). Plate type is in em off a plate size that is never below 1rem, so its smallest step (0.8125em) holds the same floor.

## Layout

The frame is a three-row grid filling the viewport (100dvh): header (3.5rem), the spread, the foot (3.75rem), with a 1.5rem side gutter. There are no frame dividers: the header and foot are the same linen table as the ground (they inherit its background, fixed to the viewport, so the lamp pool and fall-off run continuously under them), and a turning leaf passes beneath them.

- **Header:** the mark (a plate beside three ruled lines, SVG; its plate takes the stock's deep colour on a comparandum's view), the catalogue title and "recorded <date>" at left (hidden on the cover); Job, Model and Told at right, quiet underlined pickers.
- **The book:** the open volume sits inset on the table (0.625rem above, 0.5rem below, the side gutter plus 1.375rem left and right so the page-edge stacks have room). Two pages, 1.3fr plate page and 1fr entry page, meeting at the spine with no gap; each page is grained paper with its own gutter shading. The leaves stand out from both fore-edges at 2px a leaf: the plates already turned at the left, those to come at the right, so the book's thickness says where you are (cover: all ten at the right; the index: all ten at the left), easing to the new widths over 0.7s.
- **Left page:** the plate over a one-line caption ("Plate 6c" with the letter in the stock colour, or "Frontispiece"; a key at right when the plate uses marks). The plate is tipped in at the size of its object, with the page's paper as its margin; the page-load log and the cover's fan fill the page instead.
- **Right page:** the entry: plate number and title, the figure, its caption, the comparanda (plates 3-9), the record, a provenance line pinned to the bottom.
- **Cover (view 0):** left, the night plate with the fan filling it; right, the cover title, the job and recorded date, a Rule, the ten plates as a two-column contents list (each opens its plate), "Space opens the catalogue" pinned to the foot. The Next key reads "Open".
- **Foot:** Back and Next at left, the plate index 1-10 centred (one 2px rule travels above it to the current tab, in the stock's deep colour, its comparandum letter beside it), the keys hint at right.
- **Scale:** root `clamp(16px, 0.62vw + 7.6px, 20px)`; the plate sets its own size, `clamp(1rem, min(100vh / 48, (100vw - 3rem) / 85), 1.4rem)`, and every object on it, the fan included, is in em. Objects are capped (slip 38em, file and chain 42em, manifest and tables 46em).
- **Fitting, never cutting:** the log's line height gives way so it fits four columns; the export shows whole HL7 messages and counts the rest; a figure shrinks before it wraps.
- **Responsive:** at 1340px the index shows numbers only (the current tab keeps its name) and the recorded date goes; at 1100px the keys hint and picker labels go; at 860px the book stacks (entry first, then the plate; on the cover the fan comes first) and scrolls, the page-edge stacks, gutters and perspective go, the table stops being fixed, the log runs in two balanced columns, the manifest becomes rows, the foot sticks to the bottom on linen with only the current tab, and the fan opens wider (blades at -44 / -22 / 0deg) with the back blades showing figure and tab only.

## Elevation & Depth

Physical, lit from one lamp. The page is not flat print any more: it is paper lying on a table, and depth is the stack of real things on it, the table, the book, the tipped-in plate, a turning leaf, the cover's blades. Every shadow is soft and umber at low alpha (the night plate's blades and rivet take black, being on a dark ground); none is a hard offset and none is decorative. Printed things (type, rules, the figure) are never lifted; they multiply into the paper.

The ground is built in layers on the table: a warm radial lamp pool at the centre (white-cream to 72% at the core), an umber fall-off to the corners (to 36%), a fine linen weave (two 1px repeating umber lines, 3px pitch, 3% and 2.2%), and the soft linen noise, all fixed to the viewport. Paper carries a fractal grain (`--grain`) at 30% on the pages, 42% multiply on the plates and 26% on the blades; on the night plate it is inverted and screened at 10%. The gutter darkens each page toward the spine (umber 20-26% fading out over 3.25-3.75rem, with a thin highlight on the right page where the paper turns up), and the fore-edges darken faintly (6% over 1.25rem).

### Shadow Vocabulary
- **Book** (`box-shadow: 0 1px 1px rgba(62,48,24,.16), 0 6px 14px -4px rgba(62,48,24,.2), 0 26px 46px -22px rgba(62,48,24,.42)`): the open volume on the table.
- **Leaf edges** (`box-shadow: ±1px 1px 2px rgba(62,48,24,.2)` on stacks striped #f8f6f0 / #d2ccbf every 2px): the page-edge stacks at each fore-edge.
- **Tipped-in plate** (`box-shadow: 0 0 0 .5px rgba(62,48,24,.14), 0 1px 1.5px rgba(62,48,24,.14), 0 5px 12px -7px rgba(62,48,24,.38)`): a hairline lift where the plate lies on the page.
- **Turning leaf** (`box-shadow: 0 0 18px -6px rgba(62,48,24,.45)`; cast on the page beneath, a gradient from umber 42% at the spine to nothing at 75%): only while a leaf is in the air.
- **Key** (`box-shadow: 0 1px 0 rgba(62,48,24,.12), 0 2px 5px -3px rgba(62,48,24,.35)`): the paper turn keys, pressed down 1px on :active. The Next key adds an inset 12% white top highlight and `0 4px 10px -4px rgba(62,48,24,.55)`.
- **Blade** (`box-shadow: inset 0 1px 0 rgba(255,255,255,.5), 0 .15em .3em rgba(0,0,0,.35), 0 .9em 2em -.7em rgba(0,0,0,.7)`): the three swatch blades on the night plate.
- **Rivet** (`box-shadow: 0 0 0 1px rgba(0,0,0,.45), 0 .15em .4em rgba(0,0,0,.55)`): a drawn eyelet, a #d3d8db ring (.18em) round a #e9ecee pin on night.
- **Phone foot** (`box-shadow: 0 -6px 16px -10px rgba(62,48,24,.5)`): the sticky foot over the scrolling book, at 860px and below.

### Named Rules
**The Paper On Paper Rule.** A shadow is cast only where one physical thing lies on another: the book on the table, a plate on the page, a leaf over the spread, a blade on the night plate, a key on the table. Type, rules and figures never cast one.

**The One Lamp Rule.** There is one light, centre-top over the table (upper left on the night plate), and every shade, gutter and cast shadow agrees with it. Nothing glows.

## Shapes

Square paper. Plates, comparanda rows, pickers and table cells have no radius; the book and its pages take a 2px paper corner at the outer edges only. Functional corners: stock tabs and swatch blades 2px, key caps 3px (with a 2px bottom border), turn keys 4px; the rivet is the one circle. Underlines are a material: 1px solid red for a read-out-of-purpose field, 1px dashed for "needed, not read", 1.5px solid for a demonstrated control, 1px dashed for an attested one, 1.5px red strike for a backing the register does not give, 1px Ink under the checked told option and a table's head row. The comparanda marker is a full-width tint band behind the pressed row, never a side stripe.

## Components

### Plates (signature)
One real object per view, in em off the plate size, tipped in on the plate's ground (stone for 1, 2, 10; the pressed comparandum's tint for 3-9) with the grain printed into it:
- **Inventory** (1 and 3, the same object): five modules, each its portal title over its field labels, and the 20 patients as masked record numbers in two columns, the followed patient bold and underlined. On plate 3: read in Ink, not taken Ghost, needed-but-not-read Ink 3 dashed, out-of-purpose red underlined.
- **Request slip** (2): the job's sentence at 1.375em, each needed field beside why; a trap line under a Plate Rule.
- **Page-load log** (4): one line per page load in up to four columns; fills the page.
- **Manifest** (5): Control / Declared / Backed by the register; demonstrated solid, attested dashed, unbacked struck red.
- **HL7 v2 messages** (6): mono segments, MSH in Ink 3, separators Ghost, tokens bold, raw identifiers bold red.
- **Retention record** (7): the sidecar as key/value mono, nulls red; the purge line, or a red "No purge".
- **Runs table** (8): every recorded run; a cell equal to run 1 is Ghost.
- **Audit chain** (9): one entry per line with prev and this-line hashes, dashed gaps; a missing purge is a red entry.
- **Index** (10): the comparanda's values for this job, one row per plate, column heads carrying the stock tabs; a row opens its plate.

Each plate plays a timeline when it arrives, its marks set in the order the run made them, and the entry's figure counts them:
- **1 the hospital:** module heads fade, fields rise 0.3em (380ms) one after another within 780ms, each adding 20 values; the patients rise within 560ms.
- **2 the request:** the sentence rises (560ms), then each needed field (≤120ms apart within 820ms) with its reason 100ms behind, counted one each; the trap line last.
- **3 taken:** the inventory fades in Ghost, then each field the run read inks from Ghost to its colour (440ms) in read order (≤85ms apart within 1050ms), the red underline drawn 260ms after an out-of-purpose one; the figure counts the values field by field; the patients read ink in.
- **4 the cost:** each log line prints with a left-to-right wipe (230ms), ≤80ms apart within 1550ms, the figure counting loads.
- **5 declared:** rows rise within 580ms, then each backing is drawn under its control, solid, dashed or a red strike (440ms, ≤90ms apart); the entry's rules set in turn and the figure counts those held.
- **6 as it left:** segments print (360ms, ≤100ms apart); a token flashes in the stock at 32% where the record number was (1100ms); raw values turn from Ink to Red (520ms).
- **7 kept until:** keys and values print in turn, then the purge line (or its absence) rises (600ms).
- **8 repeated:** run after run rises (≤200ms apart); a cell matching run 1 settles from Ink to Ghost (900ms); each new decision is counted.
- **9 custody:** the audit lines rise 0.45em (480ms, ≤300ms apart); each line's hash and the next line's prev flash in the stock at 30% together; the figure is set at the extraction line.

### Open book (signature)
Two grained paper pages meeting at a shaded spine, the page-edge stacks at the fore-edges (2px a leaf, set from the plate index), the plate tipped in on the left page. The book is a perspective container (2400px, origin 50% 45%) for the page turn.

### Page turn
A real leaf, 880ms. Forward: the right page lifts from the spine and rotates to edge-on (440ms, ease-in), its shade band sweeping across it (an umber band with a thin white highlight, travelling across a 300%-wide gradient) and its face fading out over the last sixth as it nears edge-on, while a shadow is cast on the page beneath (rising and falling over 530ms); the other side comes down from edge-on onto the left page (440ms, ease-out), shade sweeping off, and the page beneath shades to 32% as it is covered. The new plate's object is hidden until the leaf is down, then the plate plays (from 820ms) while the entry sets in (from 150ms). Back turns the left leaf the other way; its plate plays from 170ms and the entry stands. Below 860px there is no leaf: the book slides in from 0.875rem right (0.42s) and plays.

### Comparanda roll (signature)
Flipping a / b / c rolls the new stock across the plate, 760ms on a cubic in-out: the new tint is washed in behind a 3px roller edge in the stock's deep colour (30%, fading over the last 15%); a ghost of the old object stays ahead of the roller, clipped at its edge, and the new object is revealed behind it; if the object's height changes, the plate's height eases with the roll. On plate 3 the inventory is not replaced but re-inked in place: each field changes colour (360ms) at the moment the roller reaches it. The comparanda band slides from the old row to the new one (520ms, from half way through the roll), carrying the old tint into the new.
- **Refigure:** a numeric figure counts from the old value to the new on the roll's curve, and keeps the old stock's ink (figure, unit, plate number) until half way; where either value is a word, or the breach state changes, nothing is counted: the old figure stands until mid-roll and the new one is set whole, rising from 14% below (460ms). A breach is never counted into.
- The caption (180ms), the record's values (from 160ms, 45ms apart) and the provenance line (320ms) fade in with it.

### Swatch fan (cover signature)
Three grained blades (c, b, a from back to front) on the lit night plate, each the stock's tint with a 2px corner, a top-edge highlight and the blade shadow, pinned at one drawn eyelet rivet near the left end and rotated c -36deg, b -18deg, a 0deg (phones -44 / -22 / 0). Each carries its stock tab, the technique's name with a sub-line, and the values that technique took for the job as a blade figure in its stock colour over "of 680 values taken". On arrival the fan fades in and the blades swing open together from 0deg (1250ms, a slight overshoot), their names and figures fading in once each blade is past half way. The fan is one image to assistive technology, labelled with the three counts.

### Stock tabs
The comparandum letter as a 1.375rem square on its full stock with a Paper letter, always (pressed or not). The same tab marks the Index plate's column heads (1.125rem) and each swatch blade (1.75em).

### Entry (right page)
Plate number and title on one baseline; the figure and unit; a one-line caption; the comparanda list (tab, who and a small sub-line, value; the pressed row on its stock's band; a failing value red); a label/value record under a Rule; a provenance line at the foot. On arrival the heading rises (560ms), the figure appears with the plate's first mark and counts in step with it (the unit fading in with it), the caption and the comparanda values land as the count ends, and the record and provenance fade in after. Where no mark sets the figure it rises whole (620ms).

### Buttons
- **Next key:** the one solid control, an ink face (a #2a2f33 to #121517 gradient with a top highlight), Paper text, 600 at 0.9375rem, 4px radius, a Space key cap outlined in 40% white; lighter on hover, pressed down 1px on :active. It reads "Open" on the cover and "Again" on the Index (which returns to the cover).
- **Back key:** 2.25rem square, Paper, a warm hairline border (#cfc9bd), the key shadow, a drawn chevron; Ink border on hover.
- **Focus:** a 2px Ink outline, 2px offset, on every control.

### Inputs / Fields
- **Pickers (Job, Model):** native selects with no box: an underline in Ink at 28% (full Ink on hover), a drawn chevron, 0.875rem 540.
- **Told:** three text options; the checked one in Ink, 600, with a 1px Ink underline; the rest Ink 3.

### Navigation
- **Plate index:** ten text tabs in the foot, number bold beside the label, Ink 3; the current one in Ink with its comparandum letter in the stock colour. One 2px marker rule travels above the index to the current tab (0.6s), re-colouring to the stock (0.45s).
- **Contents list (cover):** the ten plates in two columns, number light and wide in Ink 3, title in Ink, underlined on hover; each opens its plate.
- **Keys:** Space or PageDown next (a second press while a step plays lands it), Shift+Space or PageUp back, Left / Right plate, Up / Down comparandum, a b c, 1-9 and 0 for a plate, J job, M model, T told (Shift reverses), Home the cover, End the index; the address carries the view (#0 the cover, #3b) and opens there.

### Motion engine
One ease for entrances, `cubic-bezier(.16, 1, .3, 1)`; the roll and refigure on a cubic in-out. Every animation is a Web Animation that holds its first frame through its delay and lands on the page's own style; every counting figure is a requestAnimationFrame tween that lands on its last frame. Each records how long it will play, so the page knows when it is busy: a press of Space while busy finishes every animation and tween at once, and any new step lands the last one first. Reduced motion skips them all, so every state arrives whole, and no leaf turns. Once a step has landed nothing moves.

## Do's and Don'ts

### Do:
- **Do** put one real object the run produced on each plate, computed by the project's code, and set its one fact as the figure.
- **Do** flip comparanda in place on the same plate by rolling the new stock across it; never set a, b and c side by side (the cover's fan, one object holding the three stocks, is the only place they meet).
- **Do** print a comparandum's plates on its own stock: viridian for ours, ultramarine for the AI model, ochre for the baseline; keep shared plates on stone.
- **Do** let red override the stock, and only where a figure or value measures a breach; keep the red underline on out-of-purpose fields as the second channel.
- **Do** make every move a recorded fact being set, in the order the run made it, and count the figure only by the marks that make it.
- **Do** let a second Space land whatever is playing, and land every state whole under reduced motion.
- **Do** keep shade warm umber at low alpha, from one lamp, and only where paper lies on paper or on the table.
- **Do** tip the plate in at the size of its object with the page's paper as its margin; let only the log and the cover fill the page.
- **Do** size plate objects in em off the plate's font size, and chrome in rem off the root clamp.
- **Do** fit by giving way (line height, whole messages counted, the figure stepping down), never by cutting a record mid-line.
- **Do** keep the file single and offline: Archivo embedded, SVG, CSS and inline SVG noise only.

### Don't:
- **Don't** add lanes, dots, flows, metro lines, KPI tiles, cards or pills; the night ground belongs to the cover plate alone.
- **Don't** add a hue beyond the three stocks and the breach red, or use a stock for chrome, categories or decoration.
- **Don't** colour a figure red because of who measured it; only because it measures a breach, and never count a figure into or out of a breach.
- **Don't** cast a shadow from type, rules or figures, use black shadows off the night plate, or use a hard offset.
- **Don't** mark the chosen comparandum with a side stripe; it is a full-width tint band that travels.
- **Don't** animate anything that is not a recorded fact, or leave anything moving once a step has landed.
- **Don't** use mono outside HL7 segments, the retention record and the audit lines.
- **Don't** set anything read below 0.8125rem (13px at the floor of the root clamp).
- **Don't** show a raw identifier, contact detail or quasi-identifier; record numbers and names are masked and the builder refuses to write if one appears.
- **Don't** add explanatory prose to a spread; labels, figures and one caption line; the presenter explains.
