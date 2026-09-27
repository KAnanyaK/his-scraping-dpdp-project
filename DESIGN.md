---
name: HIS Portal (mock portal fixture)
description: A stranger's front-office grid client; module colour is the address, the grid stays achromatic.
colors:
  titlebar-slate: "#1c2530"
  titlebar-ink: "#e9edf1"
  titlebar-ink-muted: "#9fabb8"
  chrome-steel: "#d9dde2"
  chrome-highlight: "#f4f5f7"
  chrome-edge: "#98a1ac"
  workspace-face: "#eceef1"
  paper: "#ffffff"
  zebra: "#f6f7f9"
  rule-line: "#c3c9d0"
  grid-line: "#e1e4e8"
  grid-column: "#eef0f2"
  ink: "#15191e"
  ink-secondary: "#3a434d"
  ink-tertiary: "#5c6570"
  control-edge: "#8f98a3"
  disabled-ink: "#9aa2ab"
  logon-desk: "#c9ced5"
  module-registration-teal: "#0b6e6e"
  module-clinical-crimson: "#a4262c"
  module-departments-plum: "#7b2d73"
  module-billing-olive: "#56691b"
  module-audit-slate: "#4b5663"
  caution-fill: "#fdf3d8"
  caution-edge: "#c9a54a"
  caution-ink: "#4a3a0a"
typography:
  display:
    fontFamily: "Tahoma, \"Segoe UI\", Verdana, \"DejaVu Sans\", sans-serif"
    fontSize: "2rem"
    fontWeight: 700
    lineHeight: 1.1
    letterSpacing: "-0.01em"
  headline:
    fontFamily: "Tahoma, \"Segoe UI\", Verdana, \"DejaVu Sans\", sans-serif"
    fontSize: "1.45rem"
    fontWeight: 700
    lineHeight: 1.35
  title:
    fontFamily: "Tahoma, \"Segoe UI\", Verdana, \"DejaVu Sans\", sans-serif"
    fontSize: "1.15rem"
    fontWeight: 700
    lineHeight: 1.35
  body:
    fontFamily: "Tahoma, \"Segoe UI\", Verdana, \"DejaVu Sans\", sans-serif"
    fontSize: "1rem"
    fontWeight: 400
    lineHeight: 1.35
    fontFeature: "tnum"
  label:
    fontFamily: "Tahoma, \"Segoe UI\", Verdana, \"DejaVu Sans\", sans-serif"
    fontSize: ".93rem"
    fontWeight: 400
    lineHeight: 1.35
    fontFeature: "tnum"
  module-code:
    fontFamily: "Tahoma, \"Segoe UI\", Verdana, \"DejaVu Sans\", sans-serif"
    fontSize: ".95rem"
    fontWeight: 700
    letterSpacing: ".12em"
rounded:
  none: "0"
  chip: "1px"
  control: "2px"
spacing:
  gap-xs: "4px"
  gap-sm: "6px"
  gap-md: "8px"
  gutter: "18px"
  control-height: "28px"
  row-height: "26px"
  header-row-height: "30px"
  tab-height: "30px"
  titlebar-height: "34px"
components:
  button:
    textColor: "{colors.ink}"
    rounded: "{rounded.control}"
    height: "{spacing.control-height}"
    padding: "0 11px"
  button-disabled:
    backgroundColor: "{colors.workspace-face}"
    textColor: "{colors.disabled-ink}"
    rounded: "{rounded.control}"
    height: "{spacing.control-height}"
  button-logon:
    backgroundColor: "{colors.titlebar-slate}"
    textColor: "{colors.paper}"
    rounded: "{rounded.control}"
    height: "34px"
  input-text:
    backgroundColor: "{colors.paper}"
    textColor: "{colors.ink}"
    rounded: "{rounded.control}"
    height: "{spacing.control-height}"
    padding: "0 8px"
  titlebar:
    backgroundColor: "{colors.titlebar-slate}"
    textColor: "{colors.titlebar-ink}"
    height: "{spacing.titlebar-height}"
    padding: "0 12px"
  tab:
    backgroundColor: "{colors.chrome-steel}"
    textColor: "{colors.ink-secondary}"
    rounded: "2px 2px 0 0"
    height: "{spacing.tab-height}"
    padding: "0 13px"
  tab-active-registration:
    backgroundColor: "{colors.module-registration-teal}"
    textColor: "{colors.paper}"
    height: "33px"
  module-band-clinical:
    backgroundColor: "{colors.module-clinical-crimson}"
    textColor: "{colors.paper}"
    typography: "{typography.display}"
    padding: "12px 18px 13px"
  module-band-plain:
    backgroundColor: "{colors.chrome-steel}"
    textColor: "{colors.ink}"
    typography: "{typography.display}"
    padding: "12px 18px 13px"
  grid-cell:
    backgroundColor: "{colors.paper}"
    textColor: "{colors.ink}"
    typography: "{typography.body}"
    height: "{spacing.row-height}"
    padding: "0 10px"
  grid-header:
    textColor: "{colors.ink-secondary}"
    typography: "{typography.label}"
    height: "{spacing.header-row-height}"
    padding: "0 10px"
  status-slot:
    backgroundColor: "{colors.chrome-steel}"
    textColor: "{colors.ink-secondary}"
    typography: "{typography.label}"
    height: "24px"
    padding: "0 10px"
  caution-message:
    backgroundColor: "{colors.caution-fill}"
    textColor: "{colors.caution-ink}"
    rounded: "{rounded.control}"
    padding: "8px 10px"
---

# Design System: HIS Portal (mock portal fixture)

## Overview

**Creative North Star: "The Front-Office Client"**

This system governs **only the mock HIS portal fixture** (`tools/mock_portal/`): the login-gated site the Tier 2 browser crawls. It is not the project's own look. The review pages (`docs/review/*.html`, built from `tools/*_page.html` with `tools/page_base.css` and `page_base.js`) are a separate, frozen look with rounded cards, soft shadows and blue/violet/amber technique colours; nothing here applies to them and nothing of theirs belongs here. Every value below is read from `tools/mock_portal/templates/base.html`, where all tokens and CSS live inline.

The portal is the grid-control client staff run at a registration counter: a dark title bar, a steel-grey module tab strip, a full-width band in the module's colour, a toolbar, a dense achromatic grid on white, and a status bar of fixed, sunken slots pinned to the bottom. It stands in for a third-party system, so it carries no project branding, no vendor's look and a generic name ("HIS Portal"). It rejects the blue-navbar-plus-bordered-table web portal where module identity depends on reading a title: here the colour tells a watcher which module the browser is in before any text is read, and the status bar says "page 03 / 20" in one fixed spot as each load ticks by.

The system has two readers, and the second one is a machine. The Tier 2 scraper reads this DOM with generic selectors and text, and page loads are the benchmark's cost metric. Styling is presentation only: it may never change what the scraper reads or how many pages it loads.

**Key Characteristics:**
- Application frame (title bar, tabs, workspace, status bar) filling the viewport; only the grid scrolls.
- Squared 2px corners, 1px bevel-lite borders, light top-to-bottom gradients on raised chrome.
- Tahoma/Segoe workhorse type at a 14px root, tabular figures everywhere.
- Five module colours used as code and nowhere else; the grid itself stays achromatic.
- Fixed 26px data rows, 30px header row, 28px controls.
- One motion: a changed status slot flashes once in the module colour on each page load.

## Colors

A cool steel-grey application chrome around white paper, with five saturated but darkened module hues that act as an address and appear nowhere in the data.

### Primary
The system has no single brand accent. Its accent is the **current module's colour**, held in one custom property (`--m`) that each module class overrides, and that every module-marked element reads.

- **Registration Teal** (#0b6e6e): Patient Registration (code REG).
- **Clinical Crimson** (#a4262c): Clinical Records (CLN).
- **Departments Plum** (#7b2d73): Departmental Orders (DEP).
- **Billing Olive** (#56691b): Billing & Accounts (BIL).
- **Audit Slate** (#4b5663): Audit Log (AUD).
- **Home** takes the default `--m`, the Title Bar Slate, so the Home tab reads as part of the frame and stays distinct from Audit Slate. (This default was changed after the last review capture; the screenshots in `.impeccable/review/` predate it.)

Each hue carries white text at 6:1 or better. The two derived tints are mixes of the current hue into white: 11% for row and launcher hover, 24% for text selection.

### Neutral
- **Title Bar Slate** (#1c2530): the title bar, the logon dialog's title bar and its Sign in button, and the Home default for `--m`.
- **Title Bar Ink** (#e9edf1) and **Title Bar Ink Muted** (#9fabb8): brand, user name and sign-out on the title bar; the muted value for the "Hospital Information System" subtitle and session text.
- **Chrome Steel** (#d9dde2), **Chrome Highlight** (#f4f5f7), **Chrome Edge** (#98a1ac): tab strip, inactive tab gradient, status bar and the plain (Home) band; the edge is the 1px line that separates chrome from workspace.
- **Workspace Face** (#eceef1): the page ground and the toolbar.
- **Paper** (#ffffff): grid, record sheet, launcher, logon dialog, inputs.
- **Zebra** (#f6f7f9): even grid rows.
- **Rule Line** (#c3c9d0), **Grid Line** (#e1e4e8), **Grid Column** (#eef0f2): toolbar and container borders; horizontal cell rules; the fainter vertical cell rules.
- **Ink** (#15191e), **Ink Secondary** (#3a434d), **Ink Tertiary** (#5c6570): values; headers, labels and meta; notes and "Clear search".
- **Control Edge** (#8f98a3): the 1px border on buttons and text inputs.
- **Disabled Ink** (#9aa2ab): disabled pager buttons and the em dash shown in an empty record value.
- **Logon Desk** (#c9ced5): the darker ground behind the sign-in dialog.

### Caution
- **Caution Fill / Edge / Ink** (#fdf3d8 / #c9a54a / #4a3a0a): the rejected-login message only. It is a muted ochre notice, not a module hue.

### Named Rules
**The Colour-as-Address Rule.** At rest, a module's colour marks exactly five things: its tab (the active tab fills with it; inactive tabs carry a 10px chip), the full-width title band, the favicon, the status bar's module chip, and the launcher's code cell. It appears otherwise only in response to an event: the focus ring, the 11% row and launcher hover tint (a crawl never hovers), the Open button's hover fill, the selection tint, and the status-slot tick. It never marks data, headers, buttons at rest, or text in the grid.

**The Achromatic Grid Rule.** The data grid and the record sheet are white, grey and ink only. Colour in a cell would read as meaning; the only colour that ever enters the grid is the hover tint and the "Open" button's hover fill.

**The Separate Families Rule.** Module hues stay out of the review pages' technique families: blue #2a78d6, violet #8b5cf6, amber #e39a00. A new module colour must be darkened to carry white text and must not be confusable with any of those three, or with an existing module hue.

## Typography

**Display Font:** Tahoma (with "Segoe UI", Verdana, "DejaVu Sans", sans-serif)
**Body Font:** the same stack
**Label/Mono Font:** the same stack; numbers use tabular figures (`font-variant-numeric: tabular-nums` on the body)

**Character:** One workhorse sans, of the kind installed on every counter PC, at a 14px root. The system face is part of the world here: this portal imitates a desktop line-of-business client, and a web display face would break the fiction.

### Hierarchy
- **Display** (bold, 2rem = 28px, line-height 1.1, -0.01em): the module name in the title band; 1.5rem (21px) under 760px.
- **Headline** (bold, 1.45rem, 1.35): the "Sign in" heading of the logon dialog.
- **Title** (bold, 1.15rem, 1.35): module names in the launcher and the record's subject line.
- **Body** (regular, 1rem = 14px, 1.35): grid cells, sheet values, controls, launcher descriptions. Cells do not wrap; they truncate with an ellipsis at 30ch.
- **Label** (regular, .93rem): status bar, session area, grid headers (headers set bold).
- **Module code** (bold, .95rem, .12em tracking): the three-letter code (REG, CLN, DEP, BIL, AUD) in its bordered box on the band and in the launcher's code cell. The codes are uppercase in the source (`MODULE_CODES`); no case transform produces them.

### Named Rules
**The Literal Text Rule.** Never apply `text-transform` to `th` or `td`, or to any text the scraper reads. Header text is what the adapter maps to fields; the rendered text must be the served text.

**The Fixed Digits Rule.** Counters are zero-padded to the width of their total ("Page 03 / 20", "Record 007 / 500") in tabular figures, so only digits move as pages turn.

## Layout

The signed-in frame is a three-row grid on `body` filling 100vh: header (titlebar 34px, then the tab strip), the workspace (`main`, which scrolls), and the status bar. On list pages `main` becomes a column and only the grid container scrolls, with sticky 30px column headers, so the band, toolbar, pager and status bar never leave the screen.

Horizontal rhythm is an 18px gutter shared by the band, toolbar, record sheet and launcher margin. Gaps step 4, 6, 8, 14 and 16px. Density is high: 26px data rows, 28px controls, 24px status slots. The record sheet and the launcher cap at 1100px; at 1100px and wider the sheet splits into two name/value columns.

The status bar has fixed-width slots: module 17rem, view 11rem, page 9.5rem, rows 13rem, user, then load time pushed right at 8.5rem.

Under 760px: the frame stops pinning to the viewport height and the status bar becomes sticky at the bottom; the subtitle, the user name, the First/Last pager buttons and the view, user and load slots hide; the band's meta wraps to its own line; the search input grows to fill the row; the launcher collapses to code cell plus text; grid headers stop being sticky and the grid scrolls sideways.

## Elevation & Depth

Flat, with bevel-lite chrome instead of shadows. Depth is conveyed the way a desktop client conveys it: raised chrome gets a light top-to-bottom gradient and a 1px white inner highlight, sunken fields get a faint inner shadow, and status slots are inset with a two-tone border (dark top-left, light bottom-right). Nothing floats; there are no drop shadows.

### Shadow Vocabulary
- **Raised highlight** (`box-shadow: inset 0 1px 0 #fff`): buttons at rest.
- **Pressed** (`box-shadow: inset 0 1px 2px rgba(20, 25, 30, .2)`): buttons while active.
- **Sunken field** (`box-shadow: inset 0 1px 2px rgba(20, 25, 30, .12)`): text and password inputs.
- **Dialog edge** (`box-shadow: inset 0 0 0 1px #fff, 0 1px 0 #fbfcfd`): the logon dialog only.

### Named Rules
**The Bevel, Not Shadow Rule.** Relief comes from gradients, inset lines and two-tone borders. No outer blur shadows, no hard offset shadows, no floating cards.

## Shapes

Squared. Controls, dialogs, the band's code box and inactive-tab tops round at 2px; module chips at 1px; the grid, sheet, launcher, band and status bar are square. Borders are 1px throughout except the band's code box (2px, white at 75%). Tabs are open at the bottom and overlap the strip's bottom edge by 1px, so the active tab joins its band.

**The Two-Pixel Rule.** No radius above 2px anywhere in the portal. Rounding is what the review pages do; this is a stranger's client.

## Components

### Buttons
Plain desktop push buttons.
- **Shape:** squared (2px), 28px high, 11px side padding, icon and label with a 6px gap.
- **Default:** a light vertical gradient (#fbfcfd to #e3e6ea) with the Control Edge border and the raised highlight.
- **Hover / Active:** hover goes flat white with a darker edge (#6f7882); active drops to #dfe2e6 with the pressed inset.
- **Disabled:** Workspace Face ground, Disabled Ink text, Rule Line border, no highlight. Rendered as a `span`, not a link, so it costs no page load.
- **Logon:** full width, 34px, bold white on Title Bar Slate; the one filled button.
- **Open (grid row action):** a small bordered white button in the last column; hover fills with the module colour.

### Inputs / Fields
- **Style:** white, 28px (32px in the logon dialog), Control Edge border, 2px radius, sunken inset.
- **Focus:** 2px outline in the module colour, border switching to it. Every focusable element shares the 2px module-colour focus ring.

### Navigation
- **Title bar:** brand mark (an inline SVG "H" in a rounded square) and "HIS Portal", muted subtitle; user and a bordered Sign out on the right.
- **Tab strip:** Home plus one tab per module, each with a 10px colour chip. Inactive tabs are gradient steel with Ink Secondary text; the active tab is 3px taller, bold white on the module colour, and its chip turns white. The strip scrolls sideways and the script centres the active tab.
- **Pager:** First / Previous / Next / Last as buttons, right-aligned in the toolbar. The forward link's text is exactly "Next".

### Module Band (signature)
The full-width bar under the tabs, in the module colour: the bordered three-letter code, the module name at display size, and the record count with "page N of M" pushed right. Home uses the plain variant: Chrome Steel with a bottom rule and ink text.

### Grid
The list view's single table: sticky gradient headers in bold Label, bare text; 26px rows with zebra striping; cells truncated at 30ch; the last column right-aligned and shrink-wrapped for Open. An empty result replaces the rows with one plain sentence on white.

### Record Sheet
A property sheet: one row per field, the name in a light grey (#f2f4f6) header cell, the value on white, an em dash for empty values; two columns at 1100px and wider.

### Launcher
Home's module list: one row per module with its coloured code cell, the linked name and a one-line description, and the record count at the right. The whole row is the link's hit area.

### Status Bar (signature)
Sunken fixed-width slots: module (chip, code, name), view, page, rows, user, server time. On each page load the slots whose value changed since the previous page flash once in the module colour (1400ms ease-out, holding for the first 30%); no animation under `prefers-reduced-motion`.

### Caution Message
The rejected-login notice: ochre fill and edge, dark ochre ink, a warning icon, `role="alert"`.

## Do's and Don'ts

### Do:
- **Do** read every colour, size and radius from `tools/mock_portal/templates/base.html`; it is the only stylesheet, and screenshots may lag it.
- **Do** mark module identity through `--m` and the five resting places the Colour-as-Address Rule lists; add a module by adding one hue class.
- **Do** keep one `table` per list page and one per record page: `thead th` headers, `tbody tr` rows, a blank last header for the actions column, `th` name and `td` value on the record.
- **Do** keep header cells bare: the header text alone, no icons, sort arrows or extra markup inside `th`.
- **Do** keep "page N of M" and "N record(s)" as plain text inside `main`, and the forward pager link's text starting with "Next".
- **Do** keep the login fields as `input[name='username']`, `input[name='password']` and a submit button, and search as a GET form with `q`.
- **Do** use inline SVG line icons at 14px, stroke 1.6, `currentColor`, `aria-hidden`.
- **Do** confirm after any change that the portal tests pass and the page-load counts in `benchmark-portal.json` and `navigation-map.json` are unchanged.

### Don't:
- **Don't** apply `text-transform` to `th`, `td` or any text the scraper reads.
- **Don't** put any link inside `main` on the home page other than the module links; every such link is crawled and costs a page load. Site navigation stays in the header, outside `main`.
- **Don't** give any other link in `main` text starting with "next".
- **Don't** add ids, data attributes, JSON endpoints or any other hook for the scraper's benefit.
- **Don't** use module hues in the grid, on data, or on resting buttons.
- **Don't** use the review pages' technique colours (blue #2a78d6, violet #8b5cf6, amber #e39a00) or anything close to them as module hues.
- **Don't** bring in the review pages' look: rounded cards, soft shadows, system-ui, `page_base.css`.
- **Don't** round anything beyond 2px, or add outer or hard offset shadows.
- **Don't** add project branding, scores, DPDP language, a real vendor's name or look, or a real hospital's name. The portal is a stranger's system.
