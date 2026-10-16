---
name: One Patient's Record
description: Portal version 5, The Redacted Record. One patient's record typeset in a manila case folder on a slate desk under a warm lamp; every value under a marker-ink redaction bar, lifted only where a run read it; a red pencil only for a value read outside the purpose; rubber-stamp ink for the copy's destruction; Source Serif 4 embedded in one offline file.
colors:
  slate: "#3a4651"
  chrome: "rgba(36, 45, 53, .92)"
  on-slate: "#eef1f4"
  on-slate-2: "#c2ccd4"
  manila: "#dfc58c"
  manila-edge: "#b89c5f"
  manila-ink: "#4f3f1e"
  tab-tucked: "#c4a868"
  umber: "rgb(70, 52, 20)"
  paper: "#fffefb"
  paper-copy: "#f6f5f1"
  stack-odd: "#eceae2"
  stack-edge: "#d9d5c8"
  ink: "#1b1d20"
  ink-2: "#474c51"
  ink-3: "#62676c"
  rule: "#e2e0d9"
  bar: "#17191c"
  red: "#b8322a"
  stamp: "#33479a"
  slip-current: "#fbf5e4"
typography:
  title:
    fontFamily: "\"Source Serif 4\", \"Iowan Old Style\", \"Palatino Linotype\", Georgia, serif"
    fontSize: "1.125rem"
    fontWeight: 600
    lineHeight: 1
    letterSpacing: "-0.005em"
  letterhead:
    fontFamily: "\"Source Serif 4\", \"Iowan Old Style\", \"Palatino Linotype\", Georgia, serif"
    fontSize: "1.375rem"
    fontWeight: 600
    lineHeight: 1.1
    letterSpacing: "-0.01em"
  figure:
    fontFamily: "\"Source Serif 4\", \"Iowan Old Style\", \"Palatino Linotype\", Georgia, serif"
    fontSize: "4.25rem"
    fontWeight: 300
    lineHeight: 0.9
    letterSpacing: "-0.02em"
  module-head:
    fontFamily: "\"Source Serif 4\", \"Iowan Old Style\", \"Palatino Linotype\", Georgia, serif"
    fontSize: "1.0625rem"
    fontWeight: 600
    lineHeight: 1.2
    letterSpacing: "0.06em"
    fontFeature: "\"c2sc\", \"smcp\""
  record-number:
    fontFamily: "\"Source Serif 4\", \"Iowan Old Style\", \"Palatino Linotype\", Georgia, serif"
    fontSize: "1rem"
    fontWeight: 600
    lineHeight: 1
    letterSpacing: "0.02em"
    fontFeature: "\"tnum\", \"lnum\""
  body:
    fontFamily: "\"Source Serif 4\", \"Iowan Old Style\", \"Palatino Linotype\", Georgia, serif"
    fontSize: "1rem"
    fontWeight: 400
    lineHeight: 1.4
    fontFeature: "\"tnum\", \"lnum\""
    fontVariation: "\"opsz\" auto"
  value:
    fontFamily: "\"Source Serif 4\", \"Iowan Old Style\", \"Palatino Linotype\", Georgia, serif"
    fontSize: "0.9375rem"
    fontWeight: 400
    lineHeight: 1.22
  label:
    fontFamily: "\"Source Serif 4\", \"Iowan Old Style\", \"Palatino Linotype\", Georgia, serif"
    fontSize: "0.8125rem"
    fontWeight: 400
    lineHeight: 1.3
  stamp:
    fontFamily: "\"Source Serif 4\", \"Iowan Old Style\", \"Palatino Linotype\", Georgia, serif"
    fontSize: "0.9375rem"
    fontWeight: 700
    lineHeight: 1.2
    letterSpacing: "0.08em"
  chrome:
    fontFamily: "\"Source Serif 4\", \"Iowan Old Style\", \"Palatino Linotype\", Georgia, serif"
    fontSize: "0.9375rem"
    fontWeight: 400
    lineHeight: 1.2
  key-cap:
    fontFamily: "\"Source Serif 4\", \"Iowan Old Style\", \"Palatino Linotype\", Georgia, serif"
    fontSize: "0.8125rem"
    fontWeight: 600
    lineHeight: 1
rounded:
  none: "0"
  card: "2px"
  stamp: "3px"
  key: "4px"
  folder: "6px"
spacing:
  hair: "0.0625rem"
  xs: "0.25rem"
  tab-gap: "0.3125rem"
  sm: "0.5rem"
  md: "0.875rem"
  lg: "1.25rem"
  desk-x: "1.5rem"
  col-gap: "2rem"
components:
  chrome-bar:
    backgroundColor: "{colors.chrome}"
    textColor: "{colors.on-slate}"
    height: "3.25rem"
    padding: "0 1.5rem"
  next-key:
    backgroundColor: "{colors.manila}"
    textColor: "{colors.manila-ink}"
    rounded: "{rounded.key}"
    height: "2.25rem"
    padding: "0 0.5rem 0 0.875rem"
  back-key:
    textColor: "{colors.on-slate}"
    rounded: "{rounded.key}"
    size: "2.25rem"
  picker:
    textColor: "{colors.on-slate}"
    typography: "{typography.chrome}"
    rounded: "{rounded.none}"
    padding: "0.1875rem 1.25rem 0.1875rem 0"
  told-option:
    textColor: "{colors.on-slate-2}"
    typography: "{typography.chrome}"
    padding: "0.1875rem 0"
  told-option-checked:
    textColor: "{colors.on-slate}"
  leaf-tab:
    textColor: "{colors.on-slate-2}"
    typography: "{typography.chrome}"
    padding: "0.5rem 0.75rem"
  leaf-tab-current:
    textColor: "{colors.on-slate}"
  leaf-marker:
    backgroundColor: "{colors.manila}"
    height: "2px"
  folder:
    backgroundColor: "{colors.manila}"
    rounded: "{rounded.folder}"
    padding: "0.5rem 1.25rem 1.25rem 0.625rem"
  index-tab:
    backgroundColor: "{colors.tab-tucked}"
    textColor: "{colors.ink-3}"
    typography: "{typography.chrome}"
    width: "2.6875rem"
    padding: "0.875rem 0"
  index-tab-chosen:
    backgroundColor: "{colors.manila}"
    textColor: "{colors.ink}"
  sheet:
    backgroundColor: "{colors.paper}"
    textColor: "{colors.ink}"
    rounded: "{rounded.none}"
    padding: "0.875rem 1.375rem 0.75rem"
  sheet-copy:
    backgroundColor: "{colors.paper-copy}"
  redaction-bar:
    backgroundColor: "{colors.bar}"
  reading-card:
    backgroundColor: "{colors.paper}"
    textColor: "{colors.ink}"
    rounded: "{rounded.card}"
    width: "20rem"
    padding: "1.125rem 1.25rem 1rem"
  destruction-stamp:
    textColor: "{colors.stamp}"
    typography: "{typography.stamp}"
    rounded: "{rounded.stamp}"
    padding: "0.375rem 0.75rem"
  destruction-stamp-never:
    textColor: "{colors.red}"
  slip-row-current:
    backgroundColor: "{colors.slip-current}"
---

# Design System: One Patient's Record

## Overview

**Creative North Star: "The Records Room"**

Portal version 5 shows privacy as what stays covered. There is one person on the page: the patient the single-patient jobs are about. Their record is typeset as a real document and laid in a manila case folder, every value under a redaction bar. Three readers (a ours, b an AI model at a briefing, c the baseline) are index tabs on the folder's edge; choosing one lifts exactly the bars that run read. A second leaf is the copy that left the hospital, each field as the export carried it, with a destruction stamp; turning to its erase date empties it. A third leaf is the record's access slip, every reading of this record as the patient would be told. It refuses the dashboard, the pipeline diagram and the race.

The world is a records room. A slate desk (#3a4651) lies under a warm lamp: a soft pool of warm light (13%), a dark fall-off to the edges, and a fine mottle of dust on the desk. On it the folder, in fibred manila card with its own light and a real shadow on the desk; the record sheet, the 19 other patients' records behind it and the reading card are grained paper. The sheet is set in Source Serif 4 with a real document's hierarchy: a letterhead line over a 2px ink rule, the masked record number and name, then five modules in two columns, each a small-caps head over label and value lines on hairline rules. Redaction bars are marker ink, ragged at the ends with a slight sheen; a red pencil stroke runs under a value only when it was read outside the purpose; the copy's destruction stamp is worn rubber-stamp ink in blue, or red "No destruction date" when nothing schedules one. Chrome (the top bar and the foot) is a darker band of the same slate: it belongs to the room, not the document.

Motion is at Portal v2's level and every move is a recorded fact: a bar laid over a value, a bar lifted because that run read it, the card counting each line as it comes off, a leaf put aside, a line of the copy set in or destroyed, a reading written on the slip. The user's standing bar holds over all of it: **maintain elegance and professionalism in design.** The system keeps it as restraint: material that stays quiet (dust, fibre, grain and mottle felt rather than seen) and motion that explains a change and then stops. The finish review softened several devices to meet that bar; the values below are the shipped ones. Density is presentation density for a projected 1366x768 laptop: the folder and the card fill the desk between the bars, nothing scrolls at that size, and the presenter explains.

**Key Characteristics:**
- A slate desk under a warm lamp, a fibred manila folder with index tabs down its right edge, one white record sheet with the other 19 records' edges behind it, a grained reading card beside it.
- Every value under a marker-ink redaction bar the length of its (masked) value; a run lifts exactly the bars it read.
- Red only for a breach: the pencil under a value read outside the purpose, raw identifiers on the copy, "never" destroyed, the other records fanned on a single-patient job.
- Stamp ink (blue) only for the copy's destruction: the stamp, a token's flash, the slip's destroy-after dates.
- Source Serif 4 throughout, one face, optical sizing on, tabular lining figures.
- Elegance and professionalism as the standing bar: restrained material, motion that explains a change and then stops.
- A second Space lands any step; nothing counts up from zero; no breach is shown before its reading.

## Colors

A warm document on a cool desk: manila and paper carry the record, slate carries the room, near-black ink and marker carry what is written and what is covered; two inks are earned, blue stamp ink for destruction and red for a breach.

### Primary
- **Folder Manila** (manila): the folder's card, the chosen index tab, the Next key, the leaf marker that slides under the current leaf, the told option's underline and the focus outline. Manila is the object the presenter handles.
- **Folder Edge** (manila-edge): the folder's 1px inner edge and the index tabs' inner edge.
- **Manila Ink** (manila-ink): text on manila (the Next key, a hovered or empty tab).
- **Tucked Tab** (tab-tucked): an index tab that is not chosen, tucked behind the folder.

### Secondary
- **Stamp Ink** (stamp): the destruction stamp ("Destroy after", "Destroyed"), a token's flash on the copy (at 22%), and the slip's destroy-after dates. Never for anything else.

### Tertiary
- **Pencil Red** (red): only a breach. The pencil stroke under a value read outside the purpose; a raw identifier, a date of birth as read, or an undeclared retention on the copy (as red text, with "raw" beside it); the "No destruction date" stamp and "never" on the slip; the card's breach facts; the fanned edges of other records read on a single-patient job.

### Neutral
- **Slate** (slate): the desk.
- **Chrome** (chrome): the top bar and the foot, a darker slate at 92%.
- **On Slate / On Slate 2** (on-slate, on-slate-2): chrome text; On Slate 2 for labels, unselected told options and leaves, the keys hint.
- **Paper** (paper): the record sheet and the reading card. **Copy Paper** (paper-copy): the copy that left, a shade greyer than the record.
- **Other Records** (paper-copy, stack-odd, stack-edge): the 19 sheets behind the folder, odd sheets a darker paper, each with a 1px edge.
- **Ink / Ink 2 / Ink 3** (ink, ink-2, ink-3): values and heads; secondary text; labels, the letterhead's right line, the card's fact labels.
- **Rule** (rule): the hairline under every line, the card's dividers.
- **Marker** (bar): the redaction bar (drawn as a vertical gradient from #2b2e33 through #15171a and #101214 to #1c1e21), the legend's covered swatch and text selection.
- **Umber** (umber): shade on manila and paper only, always at low alpha (the folder's foot, the tab's fold, the sheet's cast).
- **Current Reading** (slip-current): the slip's rows by the chosen reader.

### Named Rules
**The Restraint Rule.** Elegance and professionalism are the standing bar: material stays quiet, and every motion explains a change and then stops.

**The Two Inks Rule.** Blue stamp ink means destruction and red means a breach; neither marks anything else, and no other ink goes on the paper.

**The Pencil Is Earned Rule.** The red pencil goes only under a value read outside the job's purpose, and only after its bar has lifted. Raw identifiers and never-destroyed copies are red ink, not pencil.

## Typography

**Body Font:** Source Serif 4 (SIL OFL; embedded latin WOFF2, variable weight 200-900 and optical size, font-display: block; fallback Iowan Old Style, Palatino Linotype, Georgia, serif)

**Character:** One serif with a real document's hierarchy: a letterhead, small-caps module heads, quiet labels on hairlines, a light large figure on the card. Optical sizing on (`font-optical-sizing: auto`); tabular lining figures on the body.

### Hierarchy
- **Figure** (300, 4.25rem, lh 0.9, -0.02em): the card's count ("7 of 34 lines read", "12 readings"); 2.5rem for a date or "Never" on the copy; 3.5rem on short screens.
- **Letterhead** (600, 1.375rem, lh 1.1, -0.01em): "Patient record", "The copy that left", "Record access slip"; its right line in Label Ink 3.
- **Title** (600, 1.125rem, lh 1): "One patient's record" in the top bar.
- **Module head** (600, 1.0625rem, all small caps, +0.06em): the five module sections. The slip's column heads take the same treatment at 1rem, +0.05em, Ink 2.
- **Record number** (600, 1rem, +0.02em, tabular): the masked record number under the letterhead and the card's reader name.
- **Value** (400, 0.9375rem, lh 1.22): every value on the record and the copy; 0.875rem on short screens.
- **Label** (400, 0.8125rem, Ink 3): line labels, card fact labels, the copy's "token", "raw", "coarsened" tags.
- **Stamp** (700, 0.9375rem, uppercase, +0.08em; its second line 600 0.8125rem +0.04em): the destruction stamp only.
- **Chrome** (400, 0.9375rem): pickers, told options, leaves, index tabs; picker labels 0.8125rem.
- **Key cap** (600, 0.8125rem).

### Named Rules
**The One Face Rule.** Source Serif 4 sets everything, chrome included. No second face and no monospace; tokens are set in the serif at 600.

**The 13px Floor Rule.** Nothing read is set below 0.8125rem of a root that is never below 16px (`clamp(16px, 0.62vw + 7.6px, 20px)`).

**The Stamp Speaks In Capitals Rule.** Uppercase belongs to the rubber stamp; heads use small caps, never uppercase.

## Layout

The room is a three-row grid filling the viewport (100dvh): the top bar (3.25rem), the desk, the foot (3.5rem). The desk is two columns, the folder and a 20rem reading card, 1.5rem apart, padded .625rem 1.5rem .5rem.

- **Top bar:** the title at left; at right the Job picker, the Model picker and the Told options (task + register, the Act, the policy), 1.375rem apart.
- **Folder:** the body (the folder's card) and a column of three index tabs down its right edge, 1.25rem from the top, .3125rem apart. The other records lie in a stack inset to the folder's padding; the sheet lies over them.
- **Sheet:** a letterhead row (2px ink rule), the "whom" line (record number, name, "34 lines, five modules"), then five modules in two columns 2rem apart (registration and clinical left; orders, billing and the audit log right). A line is an 8.25rem label column and a value, on a hairline, at least 1.3125rem high. Each bar is exactly its value's length.
- **Copy:** the same grid with each field as the export carried it; the stamp sits bottom left (1.5rem, 1rem), rotated -5°.
- **Slip:** a letterhead row and one table (Read by, For, Lines, Left as, Destroy after).
- **Card:** who, the figure, a fact list (labels left, values right) over a rule, the legend (covered, outside the purpose, needed and still covered) or a provenance line.
- **Foot:** Back and Next at left, the three leaves centred over the sliding manila marker, the keys hint at right.
- **Scale:** root `clamp(16px, 0.62vw + 7.6px, 20px)`; everything in rem.
- **Short screens** (max-height 760px, wider than 860px): bars 2.875rem / 3rem, lines 1.1875rem, values 0.875rem, letterhead 1.25rem, tabs and card tightened, figure 3.5rem.
- **1320px and narrower:** the keys hint goes; the card is 18rem.
- **860px and narrower:** the room scrolls; the top bar wraps; the desk is one column; the index tabs run along the top of the folder (rounded at the top, flat, no tuck); modules are one column with a 7rem label column; the stamp sits in the flow at the foot of the copy; the foot sticks to the bottom with only the current leaf; leaf turns fall back to a short slide-in.
- **600px and narrower:** the slip's token breaks once in the middle, two lines of eight characters, and the line count folds under the job.

## Elevation & Depth

Paper and card on a lit desk. Depth comes from the lamp (a radial warm pool and a dark fall-off over the dust), the folder lying on the desk, the paper lying on the folder, and the tabs tucked behind it. Everything written on the sheet is flat: separation there is hairlines and the letterhead rule. Textures are drawn once as SVG noise and tiled; none of them move.

### Shadow Vocabulary
- **Folder** (`box-shadow: inset 0 0 0 1px #b89c5f, inset 0 -2px 0 rgba(70, 52, 20, .12), 0 2px 3px rgba(0, 0, 0, .28), 0 20px 34px -14px rgba(0, 0, 0, .55)`): the case folder on the desk, with its edge and a heavier foot.
- **Sheet** (`box-shadow: 0 1px 1px rgba(0, 0, 0, .14), 0 7px 16px -8px rgba(70, 52, 20, .5)`): the record sheet on the folder, cast in umber.
- **Reading card** (`box-shadow: 0 1px 1px rgba(0, 0, 0, .2), 0 14px 26px -12px rgba(0, 0, 0, .55)`): the card on the desk.
- **Index tab** (`box-shadow: inset 1px 0 0 #b89c5f, 3px 3px 6px -2px rgba(0, 0, 0, .35)`; chosen `3px 3px 6px -2px rgba(0, 0, 0, .3)`): the tab on the desk; the chosen one drops its tuck fold and comes forward in z-order.
- **Chrome** (`0 1px 0 rgba(255, 255, 255, .05), 0 8px 18px -12px rgba(0, 0, 0, .7)` on the top bar, mirrored upward on the foot): the bars over the desk.
- **Next key** (`inset 0 1px 0 rgba(255, 255, 255, .3), 0 3px 8px -3px rgba(0, 0, 0, .5)`): flat manila with a soft lip.
- **Leaf put aside** (from `0 1px 1px rgba(0, 0, 0, .14)` to `0 12px 22px -12px rgba(0, 0, 0, .45)`): the sheet lifting off the folder.
- **Other records:** no shadow; each sheet a 1px edge, stepped .3px a sheet at rest.

### Named Rules
**The Paper On Card Rule.** Depth belongs to the desk's objects: folder, paper, tabs, card and keys. Nothing written on a sheet casts a shadow.

**The Quiet Texture Rule.** Dust, fibre, grain and mottle are felt, not seen: dust at baseFrequency .15 and alpha .12n-.02 on white; fibre short and near-isotropic (.55 .25, alpha .35n-.1); mottle broad (.018, alpha .16n-.04). None is raised for effect.

## Shapes

Square paper on a rounded folder. The sheet and the other records have no radius; the folder has a 6px corner, its index tabs 0 6px 6px 0 (6px 6px 0 0 along the top on a phone); the reading card 2px; the stamp 3px with a 3px double border; key caps 3px; the foot's keys 4px. Lines are a material: a 2px ink rule under each letterhead and a 1px ink rule under the slip's heads; 1px Rule hairlines under every line; a needed-but-unread line's label underlined in a dashed Ink 3 rule. The redaction bar is a rectangle cut by a ragged mask (`--rough`, a hand-drawn outline in a 100x20 box stretched to the value), overhanging its value by .1875rem each side. The pencil is two hand-drawn red strokes (1.8 and 0.9 wide) under the value. The stamp is a rotated (-5°) double-ruled box in ink masked by a worn-ink noise (`--inkmask`) and multiplied into the paper.

## Components

### Redaction line (signature)
A label on a hairline and a value under a marker-ink bar the length of its masked value. Read: the bar lifts and the value is shown whole in ink. Read outside the purpose: the pencil under it, drawn after its bar lifts. Needed but unread: the label in Ink 2 with a dashed underline, from the first view. An empty value is an em dash.

### Index tabs
Three fibred tabs (a Ours, b the model with its briefing in small type, c Baseline) set vertically down the folder's right edge. Unchosen tabs are tucked .3125rem behind the folder (Tucked Tab, Ink 3); the chosen tab comes forward by transform (.45s) and z-order, in Folder Manila and Ink at 600. Hover warms the tab (#cfb373, Manila Ink).

### The other records
The 19 other patients' records lie behind the sheet, stepped .3px a sheet. When the run reads them too they fan out 0.9px a sheet (plus 3px), .6s with an 18ms stagger, their edges in Ink 3, red only when the job is about one patient; the folder clips them.

### Destruction stamp
"Destroy after" with the date, or "Destroyed" with the date and "n files, after n days" from the purge, in Stamp Ink; "No destruction date / kept indefinitely" in red. Worn but continuous: masked ink, multiplied, over a 35% white ground.

### Access slip
One row per reading of this record by the three readers across the four jobs: reader (the model with its briefing in Ink 3), job, lines, how it left (a token in 600, "raw" in red, "nothing" in Ink 3), destroy after (the date in Stamp Ink 600, or "never" in red). The chosen reader's rows sit on Current Reading.

### Reading card
Who (600) over a small subtitle; the figure; facts (labels in Label Ink 3, breaches in red); the legend on the record (covered: a marker swatch; outside the purpose: the pencil; needed, still covered: a dashed rule) or a one-line provenance on the copy and the slip.

### Buttons
- **Next key:** flat manila, Manila Ink 700, 4px corner, a Space cap outlined in 40% Manila Ink; reads "Again" on the last beat.
- **Back key:** 2.25rem, transparent with a 30% white border and a drawn chevron; On Slate border on hover; 1px down when pressed.
- **Focus:** a 2px manila outline, 2px offset.

### Inputs / Fields
- **Pickers:** native selects with no box, a 35% white underline and a drawn chevron, max 15rem.
- **Told options:** three text options; the checked one On Slate with a 1px manila underline.

### Navigation
- **Leaves:** 1 The record, 2 The copy, 3 The slip; number 600; the current one On Slate over a 2px manila marker that slides by FLIP (`slideTo`, 580ms).
- **Keys:** Space next (through the readers, then the next leaf), Shift+Space back, arrows a leaf, 1-3 a leaf, Home / End, a b c a reader, E the erase date, J job, M model, T told (Shift reverses); `#<leaf><reader><e>` deep links (`#2ae`). A second Space while a step plays lands it.

### Motion
One ease for entrances and markers, `cubic-bezier(.16, 1, .3, 1)`; one engine (`anim`, `tween`, `land`, `busy`) tracks every running animation and tween, so a press while busy lands the step whole and nothing moves once it has landed.
- **Opening the record:** the letterhead rises, then a bar is laid over every value by a clip-path draw (360ms, ease in-out, 22ms apart), module by module, the labels and heads fading in with them.
- **Choosing a reader:** exactly the bars that run read lift by a clip-path wipe (360ms, ease-in, 18ms apart down the page), with no edge-on sliver; values are revealed whole in ink. The card counts each line as it comes off. The pencil is drawn (480ms) after its bar lifts. The card's breakdown (`patchCard`, `cardIn` factsAt) and the fan (`fan()`) wait for the wave to finish.
- **A reader, job, model or briefing on the same leaf** re-sets in place (`lift`, `reset`, `respec`): bars settle or lift where they are; the copy or the slip's model rows are set again; only what changed on the card is rewritten.
- **Turning a leaf (`slideLeaf`, 600ms, ease in-out):** the top sheet is put aside to the left, opaque, rotated at most 2°, with a soft shadow, fading only once it has cleared the folder; going back, the finished sheet is laid on again with nothing replayed.
- **The copy:** lines set in one by one (320ms, at most 26ms apart); a token flashes in stamp ink; the stamp lands from opacity 0 and scale 1.08 in 260ms with no overshoot while the sheet settles to .996 and back; the card's verdict waits for the stamp.
- **E:** stamps "Destroyed" and the copy's lines go out one by one (450ms, 28ms apart); only a copy with an erase date empties (the baseline's stays whole), and the card is patched in place, never re-run.
- **The slip:** each reading is printed (180ms, cells 50ms apart, its date printed in stamp ink like the other cells); the count waits for the rows.
- **Never:** counting up from zero; a breach shown before its reading.
- **Reduced motion:** every state lands whole. Below 860px a leaf turn is a 0.4s slide-in.

## Do's and Don'ts

### Do:
- **Do** show privacy as what stays covered: one patient's record, every value under a bar, lifted only where the recorded run read it.
- **Do** keep every value the recorded one, computed by the project's code, and every identifier, contact detail and quasi-identifier masked; the builder audits with v1's check and refuses to write otherwise.
- **Do** keep red for a breach and stamp blue for destruction, and no other ink on the paper.
- **Do** draw the pencil only under a value read outside the purpose, after its bar lifts.
- **Do** set everything in Source Serif 4: a letterhead, small-caps module heads, labels on hairline rules, a light large figure.
- **Do** keep depth in the desk's objects: folder, paper, tabs, card, keys; textures quiet and still.
- **Do** keep the standing bar, elegance and professionalism: restrained material, motion that explains a change and then stops.
- **Do** make every move a recorded fact (a bar laid or lifted, a line set or destroyed, a reading written), and let a second Space land it.
- **Do** keep the file single and offline with the face embedded.

### Don't:
- **Don't** add a hue beyond manila, the two inks and the neutrals.
- **Don't** add a second face or monospace.
- **Don't** set uppercase anywhere but the stamp.
- **Don't** cast a shadow from anything written on a sheet, or put a dark offset slab under any element.
- **Don't** count a figure up from zero, or show a breach before its reading.
- **Don't** let a sheet go edge-on, overshoot, bounce or fade before it has cleared the folder.
- **Don't** empty a copy that has no erase date.
- **Don't** add lanes, dots, flows, metro lines, dark neon, glow, KPI tiles, pills or a dashboard.
- **Don't** set anything read below 0.8125rem (13px at the floor of the root clamp).
- **Don't** add explanatory prose to a leaf; the presenter explains.
