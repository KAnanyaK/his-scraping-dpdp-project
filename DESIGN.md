---
name: DPDP Evidence Report
description: The benchmark set out as a trial report, one offline page; techniques are arms, ours is the reference, every finding a numbered figure.
colors:
  paper: "#ffffff"
  paper-2: "#f3f5f5"
  paper-3: "#e9eded"
  rule: "#d3d9da"
  rule-2: "#e6eaea"
  ink: "#121417"
  ink-2: "#454c51"
  ink-3: "#5f676d"
  teal: "#00737a"
  teal-2: "#005a60"
  teal-wash: "#e3f1f1"
  ctrl: "#5d666c"
  harm: "#c0392b"
  harm-wash: "#fbe9e6"
  held: "#1d7a4a"
  held-wash: "#e3f2e9"
  caution: "#8a6100"
  caution-wash: "#fbf1d9"
  on: "#ffffff"
  model-m0: "#b26d12"
  model-m1: "#3a76b8"
  model-m2: "#a8457c"
  model-m3: "#6a46ad"
  model-m4: "#4f8136"
  model-m5: "#8a5a3c"
  layer-l0: "#3a76b8"
  layer-l1: "#2e8b57"
  layer-l2: "#0e8a95"
  layer-l3: "#c9622d"
  layer-l4: "#8a6d3b"
  code-slab: "#121619"
  code-ink: "#d6dde2"
  dark-paper: "#111416"
  dark-paper-2: "#181c1f"
  dark-paper-3: "#20262a"
  dark-rule: "#333b40"
  dark-rule-2: "#262d31"
  dark-ink: "#eceff0"
  dark-ink-2: "#b2babe"
  dark-ink-3: "#8c959a"
  dark-teal: "#3fb7bd"
  dark-teal-2: "#6fd0d4"
  dark-teal-wash: "#12302f"
  dark-ctrl: "#9aa3a8"
  dark-harm: "#f07263"
  dark-harm-wash: "#3a1e1b"
  dark-held: "#4cc283"
  dark-held-wash: "#143225"
  dark-caution: "#e0ad48"
  dark-caution-wash: "#382c14"
  dark-on: "#111416"
  dark-model-m0: "#e19a3d"
  dark-model-m1: "#6fa6e6"
  dark-model-m2: "#e07ab4"
  dark-model-m3: "#a98bf0"
  dark-model-m4: "#8cc06a"
  dark-model-m5: "#c99a78"
typography:
  display:
    fontFamily: "Segoe UI Variable Display, Segoe UI Variable Text, Segoe UI, system-ui, -apple-system, Roboto, sans-serif"
    fontSize: "clamp(2rem, 1.2rem + 2.6vw, 3.05rem)"
    fontWeight: 650
    lineHeight: 1.06
    letterSpacing: "-0.026em"
  headline:
    fontFamily: "Segoe UI Variable Display, Segoe UI Variable Text, Segoe UI, system-ui, sans-serif"
    fontSize: "1.75rem"
    fontWeight: 650
    lineHeight: 1.12
    letterSpacing: "-0.018em"
  section-number:
    fontFamily: "Bahnschrift, DIN Alternate, DIN 2014, Segoe UI Variable Display, Arial Narrow, sans-serif"
    fontSize: "2.3rem"
    fontWeight: 600
    lineHeight: 1
  key-figure:
    fontFamily: "Bahnschrift, DIN Alternate, DIN 2014, Segoe UI Variable Display, Arial Narrow, sans-serif"
    fontSize: "1.9rem"
    lineHeight: 1.05
    letterSpacing: "-0.01em"
    fontFeature: "tnum"
  title:
    fontFamily: "Segoe UI Variable Text, Segoe UI, system-ui, -apple-system, Roboto, Helvetica Neue, Arial, sans-serif"
    fontSize: "1.04rem"
    fontWeight: 600
    lineHeight: 1.35
  standfirst:
    fontFamily: "Segoe UI Variable Text, Segoe UI, system-ui, sans-serif"
    fontSize: "1.16rem"
    lineHeight: 1.45
  body:
    fontFamily: "Segoe UI Variable Text, Segoe UI, system-ui, -apple-system, Roboto, Helvetica Neue, Arial, sans-serif"
    fontSize: "1rem"
    fontWeight: 400
    lineHeight: 1.55
  caption:
    fontFamily: "Segoe UI Variable Text, Segoe UI, system-ui, sans-serif"
    fontSize: "0.88rem"
    lineHeight: 1.5
  label:
    fontFamily: "Bahnschrift, DIN Alternate, DIN 2014, Segoe UI Variable Display, Arial Narrow, sans-serif"
    fontSize: "0.78rem"
    fontWeight: 600
    letterSpacing: "0.02em"
  data:
    fontFamily: "Cascadia Mono, ui-monospace, Consolas, SF Mono, Menlo, monospace"
    fontSize: "0.88em"
rounded:
  hair: "2px"
  chip: "3px"
  control: "4px"
  panel: "6px"
  window: "8px"
spacing:
  rail: "232px"
  report-x: "48px"
  report-top: "34px"
  section-gap: "104px"
  figure-gap: "52px"
  section-lede: "34px"
  page-max: "1320px"
  section-max: "1060px"
components:
  button-primary:
    backgroundColor: "{colors.teal}"
    textColor: "{colors.on}"
    rounded: "{rounded.control}"
    padding: "5px 13px"
  button-primary-hover:
    backgroundColor: "{colors.teal-2}"
    textColor: "{colors.on}"
  button-ghost:
    backgroundColor: "{colors.paper}"
    textColor: "{colors.ink}"
    rounded: "{rounded.control}"
    padding: "5px 13px"
  button-ghost-hover:
    backgroundColor: "{colors.paper-2}"
  seg-button:
    backgroundColor: "{colors.paper}"
    textColor: "{colors.ink-2}"
    padding: "4px 11px"
  seg-button-pressed:
    backgroundColor: "{colors.ink}"
    textColor: "{colors.paper}"
  rail-tool:
    backgroundColor: "{colors.paper}"
    textColor: "{colors.ink-2}"
    rounded: "{rounded.control}"
    height: "2rem"
  keypoints-panel:
    backgroundColor: "{colors.teal-wash}"
    textColor: "{colors.ink}"
    rounded: "{rounded.panel}"
    padding: "18px 22px 20px"
  chip-need:
    backgroundColor: "{colors.teal-wash}"
    textColor: "{colors.teal-2}"
    typography: "{typography.data}"
    rounded: "{rounded.chip}"
    padding: "1px 6px"
  chip-out-of-scope:
    backgroundColor: "{colors.harm}"
    textColor: "{colors.on}"
    rounded: "{rounded.chip}"
    padding: "1px 6px"
  flag-held:
    backgroundColor: "{colors.held-wash}"
    textColor: "{colors.held}"
    rounded: "{rounded.chip}"
    padding: "1px 7px"
  flag-harm:
    backgroundColor: "{colors.harm-wash}"
    textColor: "{colors.harm}"
    rounded: "{rounded.chip}"
    padding: "1px 7px"
  flag-caution:
    backgroundColor: "{colors.caution-wash}"
    textColor: "{colors.caution}"
    rounded: "{rounded.chip}"
    padding: "1px 7px"
---

# Design System: DPDP Evidence Report

This records **the Report**, `docs/review/report.html`, built by `tools/build_report.py` from `tools/report/`. The **Portal** (`docs/review/portal-v1.html`) is a separate surface with its own direction, recorded in `DESIGN-portal.md`, so this system does not bind it.

## Overview

**Creative North Star: "The Evidence Report"**

The benchmark is a trial and the page is its evidence report. Techniques are arms of the trial: ours is the reference arm in the house teal, each AI model is an arm in its own muted hue, the take-everything baseline is the grey control arm, and harm is red. Every finding is a numbered figure with a caption that is only a key to its marks. The page reads like a journal article set on white paper: a heavy ink rule over the masthead, a one-line standfirst, a byline with dates, a tinted key-points panel, then numbered sections, each opened by a 3px ink rule.

Density is that of a well-set paper, not a dashboard. One report column beside a sticky contents rail; booktabs tables (ink rules top and bottom, nothing in between but a 1px ink rule under the head); forest plots with a marker, an interval bar and a dashed teal reference line; small multiples of run dots. Text is cut to the bone: a heading and at most one short line per section, the presenter explains. Motion is reserved for evidence: when the briefing switch changes, every marker slides to its new estimate; when a figure first scrolls into view, its marks arrive.

The file opens offline by double-click, so it is built from what the machine already has: Segoe UI Variable for text and headings, Bahnschrift for figure numbers, labels and figures, Cascadia Mono for data, inline SVG, inline CSS and script, no network asset. Light and dark are equal themes (system preference, overridable from the rail), and an A+ switch lifts the root from 16px to 19px for a projector. It rejects the dashboard of tabs with KPI cards and the dark neon "AI vs rules" page.

**Key Characteristics:**
- White journal page, ink text, one house teal for figure numbers, section numbers, links, focus, selection and the reference arm.
- Arms keep fixed identities: ours teal, each model its own muted hue, baseline grey control, harm red.
- Sections bounded by a 3px ink rule and a large teal Bahnschrift number; figures inside take a 1px rule.
- Booktabs tables and forest plots, not cards and gauges.
- A heading and at most one short line; captions are keys to the marks.
- Motion carries evidence: markers slide to the new estimate (0.75s, the house ease).

## Colors

A near-neutral cool paper and ink, one house teal, a set of muted arm hues, and three verdict hues each with its own wash.

### Primary
- **House Teal** (light `teal`, dark `dark-teal`): figure numbers, section numbers, links, the current contents entry and its 2px ink bar, focus outlines, the dashed reference line, the primary button, and the reference arm (ours) in every chart. **Deep Teal** (`teal-2`) is its hover and its text form on the teal wash; **Teal Wash** (`teal-wash`) is the key-points panel, a selected row, step or role, and the fields a job needs.

### Secondary
- **Control Grey** (`ctrl`): the take-everything baseline, the control arm, in every chart and bar.
- **Model hues** (`model-m0` to `model-m5`, amber, blue, plum, violet, moss, umber; brighter twins in dark): one per AI model, assigned by the model's id in a fixed order so a model is the same hue in every figure.

### Tertiary
- **Harm Red** (`harm`, wash `harm-wash`): a trap run that fell, a raw identifier, an out-of-scope field, a retention past the ceiling, a failing rule id. Solid red with `on` text only where the failure is the finding (an out-of-scope chip, a failing rule).
- **Held Green** (`held`, wash `held-wash`): a rule held, a gate passed, an answer given.
- **Caution Ochre** (`caution`, wash `caution-wash`): withheld, partial, attested rather than demonstrated, overdue.
- **Layer hues** (`layer-l0` to `layer-l4`): the five HIS layers on module and field marks only.

### Neutral
- **Paper** (`paper`): the page. **Paper 2 / Paper 3** (`paper-2`, `paper-3`): row hover, quiet chips, empty tracks and run squares.
- **Rule / Rule 2** (`rule`, `rule-2`): figure rules, control borders, in-table and rail dividers.
- **Ink / Ink 2 / Ink 3** (`ink`, `ink-2`, `ink-3`): text, secondary text and ledes, labels and axes. Ink also draws the section rules, the masthead rule, booktabs rules and the pressed segment.
- **Code Slab** (`code-slab`, `code-ink`): the one theme-invariant dark block, for HL7 / FHIR output, with teal-green tokens and red raw values inside it.

### Named Rules
**The Arm Identity Rule.** Ours is teal, the baseline is control grey, each model keeps the hue its id assigns, in every figure, table and legend. No chart reassigns them, and no hue is given to an arm that would collide with another (the baseline left amber for that reason).

**The One House Hue Rule.** Teal is the only accent. Structure is carried by ink rules and weight; any other hue on the page must name an arm, a layer or a verdict.

**The 4.5 Floor Rule.** Small text holds 4.5:1 on its own background in both themes, including a verdict hue on its own wash. The model and layer hues are for marks, swatches and large figures (2rem and up); never set small text in them.

## Typography

**Display Font:** Segoe UI Variable Display (with Segoe UI, system-ui, Roboto)
**Body Font:** Segoe UI Variable Text (with Segoe UI, system-ui, Helvetica Neue, Arial)
**Label/Figure Font:** Bahnschrift (with DIN Alternate, DIN 2014, Arial Narrow)
**Data Font:** Cascadia Mono (with ui-monospace, Consolas, Menlo)

**Character:** a plain humanist text face carries the words; a condensed DIN-like face carries every number and every figure label, so the eye learns that Bahnschrift means "this is evidence".

### Hierarchy
- **Display** (650, clamp 2rem to 3.05rem, 1.06, -0.026em): the masthead title only, balanced, at most 22ch.
- **Headline** (650, 1.75rem, 1.12): section headings, set on a grid beside the section number.
- **Section number** (Bahnschrift 600, 2.3rem, teal): the large number opening each section.
- **Key figure** (Bahnschrift, 1.9rem, tabular): the key-points numbers; lane counts, tallies and leak counts run 1.4rem to 3rem in the same face.
- **Title** (600, 1.04rem): a figure's title, after its teal Bahnschrift "Figure n".
- **Standfirst** (1.16rem, 1.45, ink-2): the one line under the title, at most 62ch.
- **Body** (400, 1rem, 1.55): the one-line section ledes (1.04rem, ink-2, at most 70ch).
- **Caption** (0.88rem, 1.5, ink-2): a figure's key to its marks, at most 84ch.
- **Label** (Bahnschrift, 0.72rem to 0.9rem): axis ticks, the rail heading, figure values, the key-points heading.
- **Data** (Cascadia Mono, 0.88em): field names, rule ids, codes, record tokens, paths.

### Named Rules
**The Bahnschrift Means Evidence Rule.** Figure numbers, section numbers, axis ticks, plotted values and key figures are Bahnschrift with tabular figures; headings and prose are never Bahnschrift.

**The Offline Faces Rule.** Platform faces only, each with a full fallback stack. No web fonts, no font files, no network request.

**The Sentence Case Rule.** Labels are short sentence-case captions; no uppercase tracked labels, no eyebrow or kicker above a heading.

## Layout

A two-column page at most 1320px wide: a 232px sticky contents rail (section number and name, the current figure list opening under the current section, a 2px teal ink bar that slides to the current entry) and the report column (34px top, 48px sides). The masthead sits under a 3px ink rule; the key-points panel follows it in four columns (two under 1100px, one under 520px). Sections are at most 1060px wide, 104px apart (72px on a phone), each opened by its rule, number and heading; the one-line lede is indented to the heading's text and leaves 34px before the first figure. Figures are 52px apart. Pairs of figures sit side by side and stack under 900px.

Under 1000px the rail becomes a sticky top row of section links, the current one underlined in teal; under 700px the report padding drops to 16px and the forest plot switches to a compact layout that moves score, fields and repeatability into each row's second line.

### Named Rules
**The Heading and One Line Rule.** Every section carries its heading and at most one short line; a figure carries a title and a caption that only keys the marks. No paragraphs of explanation: the presenter explains.

**The Section Boundary Rule.** Each section opens with a 3px ink rule, a large teal section number and its heading; figures inside take a 1px rule. The section boundary always dominates the figure boundary.

**The Unbroken Numbering Rule.** Figures and tables are numbered in reading order before rendering. Anything inside a closed fold is numbered S1, S2 so the visible numbering never skips.

## Elevation & Depth

The page is flat paper. Depth is ink rules of three weights (3px section, 1.5px booktabs, 1px figure) and a tinted wash for state. Shadows appear only on the three drawn objects that are pictures of real things: the browser window in the sign-in figure, the assistant's chat window, and the notice letters.

### Shadow Vocabulary
- **Object** (`0 1px 2px rgba(18,20,23,.05), 0 10px 30px -18px rgba(18,20,23,.35)`): the drawn browser and chat windows.
- **Sheet** (`0 1px 0 rule-2, 0 14px 30px -24px rgba(18,20,23,.4)`): a notice letter.

### Named Rules
**The Paper Rule.** Figures, tables, panels and controls cast no shadow; only a depicted object (window, letter) may. Tints mark state, never structure.

## Shapes

Small, square-shouldered corners: 2px on letters, 3px on chips, flags, rule ids and run squares, 4px on controls, 6px on the key-points panel and answer boxes, 8px on the drawn windows. Run dots and forest-plot reference swatches are circles; the forest plot's markers are a square for each model and the baseline and a diamond for ours, with a 2.5px interval bar for sampled arms. Tracks are 3px to 8px high with matching radius.

## Components

### Buttons
- **Shape:** gently squared (4px).
- **Primary:** solid house teal with `on` text, 600, 5px 13px; hover Deep Teal; pressed nudges down 1px; disabled at 50%.
- **Ghost:** paper with a rule border and ink text; hover a paper-2 fill and an ink-3 border.
- **Rail tools** (A+, theme): 2rem square, rule border; pressed shows an ink border.

### Segmented control
- **Style:** one rule-bordered group at 4px, segments split by 1px rules, 0.84rem ink-2.
- **State:** the pressed segment is solid ink with paper text; hover a paper-2 fill. This is the briefing switch above Figure 1.

### Chips and flags
- **Field chips** (mono, 3px): needed fields on teal wash in Deep Teal, extra fields on paper-2 in ink-3, out-of-scope fields solid harm with `on` text.
- **Flags and categories** (600, 3px): a verdict wash with text in its solid hue: held, harm, caution, plain.

### Tables
- **Booktabs:** 1.5px ink rule over and under, 1px ink rule under the head, no vertical rules, no zebra; 0.88rem tabular; numeric columns right-aligned; row hover paper-2; group rows in small ink-3.

### Navigation (contents rail)
- **Style:** section entries with a Bahnschrift number, 0.88rem ink-2; current entry ink 600 with a teal number and the sliding 2px teal bar; the current section's figures open beneath it, the current one in teal. On narrow screens a scrolling row with a teal underline.

### Key-points panel
- Teal wash at 6px, a small Bahnschrift heading in Deep Teal, four key figures each over a one-line label; ours set in Deep Teal against the others in ink, separated by a small "vs".

### Forest plot (signature)
- One row per arm: name and a sub-line on the left, a square (model, baseline) or diamond (ours) at the share of trap runs held, a 95% Wilson interval bar for sampled models, a dashed 1.5px teal reference line at 100%, and on wide screens score, fields obtained (a mini track) and repeatability in Bahnschrift columns. Switching the briefing slides every marker, interval and row to its new place over 0.75s on the house ease `cubic-bezier(.16,1,.3,1)`.

### Presenter mode (signature)
- Arrow right / left (or Page Down / Up) steps figure to figure; the current figure stays at full strength and the rest recede to 38% opacity. Escape, a wheel or a touch stops it.

## Do's and Don'ts

### Do:
- **Do** open every section with a 3px ink rule, a 2.3rem teal Bahnschrift number and the heading, and give figures inside a 1px rule.
- **Do** number every figure and table in reading order, and number folded ones S1, S2.
- **Do** keep each section to a heading and at most one short line, and keep captions to a key of the marks.
- **Do** draw ours in the house teal, the baseline in control grey and each model in the hue its id assigns, everywhere.
- **Do** set tables as booktabs, with tabular numbers right-aligned.
- **Do** set every figure number, plotted value and key figure in Bahnschrift with tabular figures.
- **Do** check small text at 4.5:1 on its own background in both themes, and keep the model and layer hues to marks and large figures.
- **Do** keep motion for evidence: markers slide to the new estimate over 0.75s on `cubic-bezier(.16,1,.3,1)`, marks arrive once on first view, and reduced motion turns animation off.
- **Do** keep the file self-contained: platform faces, inline SVG icons from the kit's one drawn family, inline CSS and script.

### Don't:
- **Don't** build a dashboard of tabs with KPI cards, or a dark neon "AI vs rules" page.
- **Don't** add paragraphs of explanation to a section or a caption.
- **Don't** let a figure rule compete with a section rule; the section boundary dominates.
- **Don't** reassign an arm's hue, or give two arms colliding hues.
- **Don't** add shadows to figures, tables, panels or controls; only a drawn window or letter carries one.
- **Don't** use web fonts, CDNs or any network asset.
- **Don't** use uppercase tracked labels, an eyebrow or kicker line, emoji or glyph icons.
- **Don't** set small text in a model or layer hue.
