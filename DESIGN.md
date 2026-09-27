---
name: DPDP-compliant HIS extraction — Review demo pages
description: Offline, self-contained demo pages that make a compliance benchmark visible at a glance; the presenter explains.
colors:
  paper: "#f3f4f6"
  paper-glow: "#e9ecf1"
  card: "#ffffff"
  card-recess: "#f0f2f5"
  hairline: "#e1e5ea"
  ink: "#121417"
  ink-soft: "#4d5560"
  ink-quiet: "#686e76"
  ours-blue: "#266ec4"
  agent-violet: "#7d52dd"
  baseline-amber: "#bc7f00"
  good: "#187d43"
  good-wash: "#e1f4e9"
  bad: "#c53232"
  bad-wash: "#fbe5e5"
  warn: "#976419"
  warn-wash: "#fcf1dd"
  on-fill: "#ffffff"
  layer-patient-admin: "#266ec4"
  layer-clinical: "#1baf7a"
  layer-ancillary: "#0e9aa7"
  layer-financial: "#eb6834"
  layer-integration: "#8a6d3b"
  model-a0: "#eb6834"
  model-a1: "#1baf7a"
  model-a2: "#8b5cf6"
  model-a3: "#0e9aa7"
  model-a4: "#d6409f"
  model-a5: "#8a6d3b"
  terminal: "#0d1014"
  terminal-ink: "#d7dde3"
  night-paper: "#0f1114"
  night-paper-glow: "#15181d"
  night-card: "#1a1d22"
  night-card-recess: "#23272d"
  night-hairline: "#2c3138"
  night-ink: "#f1f3f5"
  night-ink-soft: "#a9b1ba"
  night-ink-quiet: "#878e95"
  night-ours-blue: "#4b95ee"
  night-agent-violet: "#a78bfa"
  night-baseline-amber: "#d99a1a"
  night-good: "#3cc279"
  night-bad: "#ee6b6b"
  night-warn: "#dca13a"
typography:
  display:
    fontFamily: "Segoe UI Variable Display, Segoe UI Variable Text, system-ui, -apple-system, Segoe UI, Roboto, sans-serif"
    fontSize: "2.1rem"
    fontWeight: 700
    lineHeight: 1.1
    letterSpacing: "-0.025em"
  hero-number:
    fontFamily: "Segoe UI Variable Display, Segoe UI Variable Text, system-ui, -apple-system, Segoe UI, Roboto, sans-serif"
    fontSize: "2.1rem"
    fontWeight: 700
    lineHeight: 1.1
    letterSpacing: "-0.03em"
    fontFeature: "tnum"
  headline:
    fontFamily: "Segoe UI Variable Display, Segoe UI Variable Text, system-ui, -apple-system, Segoe UI, Roboto, sans-serif"
    fontSize: "1.08rem"
    fontWeight: 650
    letterSpacing: "-0.01em"
  title:
    fontFamily: "Segoe UI Variable Text, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif"
    fontSize: "0.9rem"
    fontWeight: 650
  lead:
    fontFamily: "Segoe UI Variable Text, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif"
    fontSize: "1.05rem"
    fontWeight: 400
    lineHeight: 1.45
  body:
    fontFamily: "Segoe UI Variable Text, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif"
    fontSize: "1rem"
    fontWeight: 400
    lineHeight: 1.45
  label:
    fontFamily: "Segoe UI Variable Text, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif"
    fontSize: "0.74rem"
    fontWeight: 600
  data:
    fontFamily: "ui-monospace, Cascadia Mono, Consolas, Courier New, monospace"
    fontSize: "0.8rem"
    fontWeight: 400
    fontFeature: "tnum"
rounded:
  hairline: "3px"
  cell: "6px"
  field: "8px"
  inset: "10px"
  card: "14px"
  pill: "999px"
spacing:
  xs: "6px"
  sm: "10px"
  md: "14px"
  lg: "18px"
  card: "16px"
  page-bottom: "48px"
components:
  card:
    backgroundColor: "{colors.card}"
    textColor: "{colors.ink}"
    rounded: "{rounded.card}"
    padding: "16px"
  hero-number:
    backgroundColor: "{colors.card}"
    textColor: "{colors.ink}"
    typography: "{typography.hero-number}"
    rounded: "{rounded.card}"
    padding: "12px 14px 11px"
  sitenav:
    backgroundColor: "{colors.card}"
    rounded: "{rounded.pill}"
    padding: "4px"
  sitenav-link:
    textColor: "{colors.ink-soft}"
    rounded: "{rounded.pill}"
    padding: "5px 13px"
  sitenav-link-current:
    backgroundColor: "{colors.ink}"
    textColor: "{colors.paper}"
    rounded: "{rounded.pill}"
    padding: "5px 13px"
  step:
    backgroundColor: "{colors.card}"
    textColor: "{colors.ink-soft}"
    rounded: "{rounded.pill}"
    padding: "8px 14px 8px 8px"
  step-selected:
    backgroundColor: "{colors.ink}"
    textColor: "{colors.paper}"
    rounded: "{rounded.pill}"
    padding: "8px 14px 8px 8px"
  seg-button:
    backgroundColor: "{colors.card-recess}"
    textColor: "{colors.ink-soft}"
    rounded: "{rounded.pill}"
    padding: "5px 12px"
  seg-button-pressed:
    backgroundColor: "{colors.card}"
    textColor: "{colors.ink}"
    rounded: "{rounded.pill}"
    padding: "5px 12px"
  badge:
    backgroundColor: "{colors.card-recess}"
    textColor: "{colors.ink-soft}"
    rounded: "{rounded.pill}"
    padding: "3px 10px"
  badge-good:
    backgroundColor: "{colors.good-wash}"
    textColor: "{colors.good}"
    rounded: "{rounded.pill}"
    padding: "3px 10px"
  badge-bad:
    backgroundColor: "{colors.bad-wash}"
    textColor: "{colors.bad}"
    rounded: "{rounded.pill}"
    padding: "3px 10px"
  badge-warn:
    backgroundColor: "{colors.warn-wash}"
    textColor: "{colors.warn}"
    rounded: "{rounded.pill}"
    padding: "3px 10px"
  button-play:
    backgroundColor: "{colors.ours-blue}"
    textColor: "{colors.on-fill}"
    rounded: "{rounded.pill}"
    padding: "9px 18px"
  tool-button:
    backgroundColor: "{colors.card}"
    textColor: "{colors.ink-soft}"
    rounded: "{rounded.pill}"
    size: "2.4rem"
  track:
    backgroundColor: "{colors.card-recess}"
    rounded: "{rounded.pill}"
    height: "14px"
  terminal:
    backgroundColor: "{colors.terminal}"
    textColor: "{colors.terminal-ink}"
    typography: "{typography.data}"
    rounded: "{rounded.field}"
    padding: "8px 10px"
---

# Design System: DPDP-compliant HIS extraction — Review demo pages

## Overview

**Creative North Star: "The Instrument Panel"**

Every page is a quiet grey desk with a few white instruments laid on it, and the instruments carry the numbers. The page itself says one line; a presenter says the rest. What the eye lands on is a count (page loads, trap runs held, a compliance score), coloured by who produced it, arriving with a small, deliberate motion. Nothing on the page decorates; every coloured mark identifies a technique, a layer, a model or a verdict.

Density is moderate and laptop-first: one 1180px column, cards that tile with `auto-fit`, a pill navigation bar and a pill stepper that turn each page into a short sequence of panes. The surface is flat paper with soft, low ambient shadows under white cards; there are no borders on cards and no side stripes. Two themes exist and are equal citizens (system preference, overridable by a header switch), plus an A+ switch that lifts the root size from 15px to 18px for a projector.

The pages are built to open offline by double-click, so the system is deliberately made from what every machine already has: system fonts, inline SVG drawn icons, inline CSS and script. That constraint is a design commitment, not a limitation to work around.

**Key Characteristics:**
- Grey paper, white cards, soft ambient shadow; no card borders, no stripes.
- Fixed technique colours shared with the deck: ours blue, AI agents violet, baseline amber.
- Large tabular hero numbers in the display face; one-line briefs in soft ink.
- Everything rounded: 14px cards, full pills for every control.
- System fonts only; mono only for data, field names, codes and paths.
- One arrival motion for every pane; one authored moment per page.

## Colors

A cool neutral ground with a small, fixed set of identity hues; colour means *who* or *what verdict*, never decoration.

### Primary
- **Ours Blue** (ours-blue; night-ours-blue in dark): our compliance-aware technique, everywhere it appears. Also the system's working accent: focus rings, selection tint, caret, the play button, the active crumb, the user's chat bubble.

### Secondary
- **Agent Violet** (agent-violet; night-agent-violet): the publicly available AI agents, as a group.
- **Baseline Amber** (baseline-amber; night-baseline-amber): the coverage-optimised baseline.

### Tertiary
- **Verdict Green / Red / Ochre** (good, bad, warn, each with a pale wash): held / fell / caution. Text in the solid hue sits on its own wash for badges, pills and chips; a solid red fill with on-fill text marks a fallen trap cell or a cited rule chip. Text on any solid fill uses `--on-fill`: white in the light theme, near-black (#0f1114) in the dark theme, where the lighter identity and verdict hues cannot carry white at 4.5:1.
- **Layer hues** (layer-patient-admin, layer-clinical, layer-ancillary, layer-financial, layer-integration): the five HIS layers, used in legends, swatches and heat tables.
- **Model palette** (model-a0 to model-a5): the rules page's per-model series, one hue per recorded model, with lighter dark-theme twins in that page's stylesheet.

### Neutral
- **Paper** (paper) with **Paper Glow** (paper-glow) as a soft radial wash at the top of the page (1200 by 420px, fading by 70%).
- **Card** (card) for every instrument; **Card Recess** (card-recess) for inset regions, tracks, segmented-control wells, inactive chips and stat tiles.
- **Hairline** (hairline): table rules and the few internal dividers only.
- **Ink / Ink Soft / Ink Quiet** (ink, ink-soft, ink-quiet): headings and values / body and briefs / footers, legends, secondary labels.
- **Terminal** (terminal, terminal-ink): a theme-invariant dark slab for command lines and the gate log, identical in both themes.
- Dark theme: the night-* keys replace their light twins one for one.

### Named Rules
**The Fixed Identity Rule.** Ours is blue, AI agents are violet, the baseline is amber, on every page and in the deck. No page may reassign these hues or use them for anything else.

**The Dot, Not Stripe Rule.** Identity colour is carried by a small round dot before a name (0.62em) and by coloured numbers. Never by a coloured side border, top stripe or tinted card background.

**The 4.5 Floor Rule.** Every text colour holds at least 4.5:1 on paper, card and card-recess in both themes. The light ink-quiet, good, bad, warn and the three identity hues were tuned to that floor; a new text colour must be checked the same way before it ships.

## Typography

**Display Font:** Segoe UI Variable Display (with Segoe UI Variable Text, system-ui, -apple-system, Segoe UI, Roboto, sans-serif)
**Body Font:** Segoe UI Variable Text (with system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif)
**Label/Mono Font:** ui-monospace (with Cascadia Mono, Consolas, Courier New, monospace)

**Character:** One humanist system family in two optical sizes: the Display cut is tight and heavy for titles and numbers, the Text cut is open and calm for briefs. Mono appears only where the content is literally data.

### Hierarchy
- **Display** (700, 2.1rem, 1.1, -0.025em, balanced wrap): the page title. The index hero lifts it to 2.6rem.
- **Hero number** (700, 2.1rem, -0.03em, tabular figures): the funnel numbers; demo tiles and big counts run 1.8–2.6rem at 750–780.
- **Headline** (650, 1.08rem, -0.01em): card and section titles.
- **Title** (650, 0.9rem, ink-soft): sub-headings inside cards.
- **Lead** (400, 1.05rem, max 90ch): the one-line brief under a step.
- **Body** (400, 1rem on a 15px root, 1.45, paragraphs capped at 78ch).
- **Label** (600, 0.74rem, ink-soft): hero-number captions and table headers, sentence case.
- **Data** (mono, 0.7–0.88rem, tabular): field names, URLs, codes, paths, terminal text and right-aligned numeric table cells.

### Named Rules
**The System Fonts Only Rule.** No downloaded or web fonts, by team decision: the pages must open offline by double-click. Use the three stacks above and nothing else.

**The Mono Means Data Rule.** Monospace is for things a machine reads: field names, codes, URLs, paths, commands and numeric columns. Never for headings, briefs or decoration.

**The Tabular Numbers Rule.** Every number that can change or be compared uses tabular figures.

## Layout

A single centred column (max 1180px, padded 18px 16px 48px). The header row puts the page title and its one-line brief on the left and the tool buttons (A+, theme) on the right, above a pill navigation bar with one link per page. Below it, a funnel of hero numbers (`auto-fit`, min 140px) and then a pill stepper whose panes hold the content.

Inside panes, cards tile in fluid grids (`auto-fit` with 260–320px minimums) at a 14px gap; paired views use a 5:7 or 7:5 split that collapses to one column at 860–900px. Gaps step 6 / 10 / 14 / 18px; cards pad 16px. Wide tables sit in a horizontal scroller. The root font size is the only density knob: 15px normally, 18px under A+, and everything scales in rem with it.

### Named Rules
**The One-Line Brief Rule.** A page carries a title, a one-line brief, and a short lead per step. The presenter explains; the page never grows paragraphs of explanation, and every number stays labelled so an offline reader can still read it.

## Elevation & Depth

Flat paper with ambient lift. Cards, the navigation bar, steps, tool buttons and the pressed segment sit on one soft two-layer shadow; interactive tiles lift to a deeper one on hover with a small upward move. Depth is also tonal: card-recess insets sit *into* a card without shadow. Dark theme deepens the same two shadows rather than adding glow.

### Shadow Vocabulary
- **Rest** (`box-shadow: 0 1px 2px rgba(16,20,26,.05), 0 6px 20px -8px rgba(16,20,26,.12)`): every card and floating control.
- **Lifted** (`box-shadow: 0 2px 4px rgba(16,20,26,.06), 0 14px 32px -10px rgba(16,20,26,.22)`): hover on clickable cards (demo tiles, role cards).

### Named Rules
**The Soft Lift Rule.** Shadows are diffuse and offset only downward with negative spread. No hard offset shadows, no coloured glows, no borders standing in for elevation.

## Shapes

Everything is rounded, and every control is a full pill. Cards use a 14px radius; inset tiles and notes 10–12px; terminals and form fields 8px; small data cells 6px; legend keys and kbd 3–4px; buttons, chips, badges, tracks, the navigation bar and the stepper are fully rounded (999px). Round markers (dots, step numbers, tool buttons) are circles. Hairline borders appear only as table rules, the chat divider, dashed outlines for "missed" or "differs" states, and the kbd key.

## Components

### Buttons
- **Shape:** full pill (999px); tool buttons are 2.4rem circles.
- **Primary (play):** Ours Blue fill, on-fill bold text, 9px 18px, rest shadow; lifts 1px on hover; 55% opacity when disabled.
- **Tool buttons (A+, theme):** card circles with the rest shadow; pressed state inverts to ink on paper.
- **Hover / Focus:** hover lifts 1px (translateY) and darkens text to ink; focus is a 2px Ours Blue outline at 2px offset on every control.

### Segmented control
- **Style:** a card-recess pill well with 3px padding; segments are text-only pills.
- **State:** the pressed segment becomes a white card pill with the rest shadow and ink text.

### Chips and badges
- **Style:** small pills (0.7–0.78rem, 600–700 weight). Neutral chips on card-recess in ink-soft; verdict chips in the solid verdict hue on its wash. Field-name chips are mono.
- **State:** "only in detail pages" or "missed" is a dashed outline, never a new colour.

### Cards / Containers
- **Corner Style:** 14px.
- **Background:** card on paper; insets in card-recess.
- **Shadow Strategy:** Rest; clickable cards take Lifted on hover (see Elevation & Depth).
- **Border:** none.
- **Internal Padding:** 16px (tiles 18–20px).

### Inputs / Fields
- **Style:** borderless card-recess pills for selects; the portal replay's login fields are 8px-radius outlined mono fields on paper.
- **Focus:** the active field takes an Ours Blue border and a 3px blue halo at 20% mix.

### Navigation
- **Style:** one pill bar per page (0.82rem), a link per demo page; links are ink-soft pills that take card-recess on hover. The current page inverts to ink on paper, weight 650. Scrolls horizontally without a scrollbar on narrow screens.

### Stepper (signature)
A row of pill tabs with a numbered circle each, driven by `Kit.steps` with tab semantics: number keys and arrows move between panes, the hash records the step. The selected step inverts to ink; steps already visited mark their number circle in verdict green on its wash.

### Hero numbers (signature)
White tiles in an auto-fit funnel: a large tabular display number coloured by its owner (identity or verdict hue) over a short label. Numbers count up when their pane arrives (`Kit.countIn`).

### Bars and tracks
A 14px card-recess pill track with a rounded fill in the owner's hue; fills grow from the left (0.9s, staggered 50ms per row) whenever their pane is shown.

### Icons
One drawn stroke family in `Kit.icon`: 24-unit grid, 2.2 stroke, round caps and joins, `currentColor`, sized 1em. Check, x, play, pause, replay, lock, grid, ban, file, alert, stop, shield, theme, arrow, flag.

### Motion
One pane arrival for every page: rise from opacity .35 and 8px down over 0.42s on the house ease (cubic-bezier(.16,1,.3,1)). Bars grow, hero numbers count up, small elements pop in (scale .86 to 1). Each page keeps exactly one authored moment: the portal page's sign-in replay and crawl, the dataset page's gate terminal, the assistant's three checks ticking in, the rules page's trap results revealing, the index tiles counting up. Reduced motion switches every animation and transition off.

## Do's and Don'ts

### Do:
- **Do** colour a technique by its fixed hue (ours blue, agents violet, baseline amber) through a dot before its name and its numbers.
- **Do** use only the system font stacks; keep monospace for data, field names, codes and paths.
- **Do** check every new text colour at 4.5:1 or better on paper, card and card-recess in both themes.
- **Do** read every number from a committed artefact and give it a label.
- **Do** draw icons from `Kit.icon` (24 grid, 2.2 stroke, round joins).
- **Do** give every control a visible 2px Ours Blue focus outline and a keyboard path.
- **Do** let panes arrive with the shared rise and keep one authored moment per page; honour reduced motion.

### Don't:
- **Don't** load web fonts, CDNs or any external asset; the pages open offline.
- **Don't** put an eyebrow or kicker line above a heading.
- **Don't** add explanatory paragraphs; one-line briefs only, the presenter explains.
- **Don't** mark identity with side stripes, top borders or tinted card fills.
- **Don't** use emoji or unicode glyphs as icons.
- **Don't** use hard offset shadows or borders for elevation.
- **Don't** reassign or reuse the three technique hues for anything else.
