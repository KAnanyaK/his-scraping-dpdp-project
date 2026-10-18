"""Build Review-III.pptx on the institution's Review-3 template.

    python tools/build_review3_deck.py                               # keeps the template's review-info slide
    python tools/build_review3_deck.py --without-instruction-slide   # the deck as presented

The VIT/SENSE template is not kept in the repository (team decision
2026-09-17): ``REVIEW3_TEMPLATE`` names its path, or put "Review-3 Template.pptx"
at the repository root (git-ignored). As with Review-II, the template's design is
left alone: its own text boxes are filled with clones of its own paragraph
styles, slides are duplicated where the content needs room, and diagrams,
tables and pictures are added as shapes in its navy.

The order follows the School's brief for the final review (circular of
09.10.2026): overview, problem and objectives, architecture, complete
implementation, results and testing with the comparison, standards and SDGs,
the demonstration, conclusion and future scope, references. Numbers come from
the tracked artefacts through ``tools/thesis_tables.py``, the same functions
that write the thesis's tables, so the deck, the thesis and the benchmark
cannot disagree. Pictures come from ``docs/review/img/`` (written by
``tools/capture_demo_pages.py``) and ``docs/thesis/figures/`` (written by
``tools/capture_thesis_figures.py``); the demonstration video, if recorded, is
``docs/review/video/demo.mp4``.
"""

from __future__ import annotations

import argparse
import copy
import json
import os
import shutil
import sys
from pathlib import Path

from pptx import Presentation
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "tools"), str(ROOT / "src"), str(ROOT)]

import thesis_tables as tt                                                   # noqa: E402
from build_review_deck import (BLACK, GREY, LIGHT, NAVY, WHITE, _run_font,   # noqa: E402
                               _set_paragraph_text, add_arrow, add_box, add_table, add_text,
                               duplicate_slide, rewrite_plain, shape_named)

TEMPLATE_NAME = "Review-3 Template.pptx"
TEMPLATE = Path(os.environ.get("REVIEW3_TEMPLATE") or ROOT / TEMPLATE_NAME)
TARGET = ROOT / "Review-III.pptx"
IMG = ROOT / "docs" / "review" / "img"
FIG = ROOT / "docs" / "thesis" / "figures"
VIDEO = ROOT / "docs" / "review" / "video" / "demo.mp4"
TITLE = "Data Extraction Techniques for HIS Towards DPDP Compliance"
RED = NAVY.__class__(0xB0, 0x30, 0x30)
TEAL = NAVY.__class__(0x0E, 0x6E, 0x6E)


# --------------------------------------------------------------------------- #
# template-respecting helpers
# --------------------------------------------------------------------------- #

class Styles:
    """Level-0 and level-1 paragraphs lifted from the template's review-info slide."""

    def __init__(self, prs):
        tf = shape_named(prs.slides[1], "Text 2").text_frame
        self.l0 = copy.deepcopy(next(p._p for p in tf.paragraphs if p.level == 0 and p.runs))
        self.l1 = copy.deepcopy(next(p._p for p in tf.paragraphs if p.level == 1 and p.runs))


def body(shape, blocks, st: Styles, *, head=16, text=14):
    """(heading, [bullets]) blocks into a template body box; a heading of None adds bullets only."""

    tb = shape.text_frame._txBody
    for p in list(shape.text_frame.paragraphs):
        tb.remove(p._p)
    for heading, bullets in blocks:
        if heading:
            h = copy.deepcopy(st.l0)
            _run_font(_set_paragraph_text(h, heading), size=head, bold=True, color=NAVY)
            tb.append(h)
        for b in bullets:
            el = copy.deepcopy(st.l1 if heading else st.l0)
            _run_font(_set_paragraph_text(el, b), size=text, bold=False, color=BLACK)
            tb.append(el)


def title(slide, text):
    rewrite_plain(shape_named(slide, "Text 1"), [text])


def drop(shape):
    shape._element.getparent().remove(shape._element)


def picture(slide, path: Path, left, top, max_w, max_h, *, border=True):
    """A picture fitted inside a box, centred horizontally; returns (left, top, width, height) in inches."""

    from PIL import Image
    with Image.open(path) as im:
        w, h = im.size
    scale = min(max_w / w, max_h / h)
    pw, ph = w * scale, h * scale
    x = left + (max_w - pw) / 2
    pic = slide.shapes.add_picture(str(path), Inches(x), Inches(top), Inches(pw), Inches(ph))
    if border:
        pic.line.color.rgb = GREY
        pic.line.width = Pt(0.5)
    return x, top, pw, ph


def caption(slide, left, top, width, text, *, size=11):
    return add_text(slide, left, top, width, 0.4, [text], size=size, color=GREY)


def style_table(gf, *, first_col_bold=True, highlight_row=None):
    t = gf.table
    for r, row in enumerate(t.rows):
        for c, cell in enumerate(row.cells):
            cell.margin_left = cell.margin_right = Inches(0.05)
            cell.margin_top = cell.margin_bottom = Inches(0.02)
            if r and highlight_row is not None and r == highlight_row:
                cell.fill.solid()
                cell.fill.fore_color.rgb = LIGHT
            for p in cell.text_frame.paragraphs:
                if c:
                    p.alignment = PP_ALIGN.CENTER
                for run in p.runs:
                    if r and c == 0 and first_col_bold and r == highlight_row:
                        run.font.bold = True


def reorder(prs, slides):
    """Put the deck's slides in the given order (every slide must be listed once)."""

    lst = prs.slides._sldIdLst
    ids = [s.slide_id for s in slides]          # read before the list is emptied: slide_id looks it up
    by_id = {int(e.get("id")): e for e in lst}
    assert sorted(ids) == sorted(by_id), "every slide must be placed exactly once"
    for e in list(lst):
        lst.remove(e)
    for i in ids:
        lst.append(by_id[i])


def remove_slide(prs, slide):
    lst = prs.slides._sldIdLst
    sid = slide.slide_id
    for e in list(lst):
        if int(e.get("id")) == sid:
            prs.part.drop_rel(e.rId)
            lst.remove(e)


def number(prs):
    for n, slide in enumerate(prs.slides, start=1):
        for sh in slide.shapes:
            if sh.name == "Text 0" and sh.has_text_frame:
                rewrite_plain(sh, [str(n)])


# --------------------------------------------------------------------------- #
# numbers, from the artefacts
# --------------------------------------------------------------------------- #

def facts() -> dict:
    mem, por = tt.load("benchmark"), tt.load("benchmark-portal")
    models = [s for s in mem.scores if s.model]
    told = [s for s in models if s.briefing == "policy"]
    untold = [s for s in models if s.briefing in ("unaided", "informed")]
    inj = json.loads((tt.RESULTS / "injection.json").read_text(encoding="utf-8"))
    scale = json.loads((tt.RESULTS / "scale.json").read_text(encoding="utf-8"))["rows"]
    v2 = {s.short: s for s in tt.load("benchmark-portal-v2").scores}
    nav = json.loads((tt.RESULTS / "navigation-map.json").read_text(encoding="utf-8"))
    from agent.functions import REGISTRY
    same = sum(1 for s in por.scores if s.short in v2
               and round(s.mean_compliance_score, 6) == round(v2[s.short].mean_compliance_score, 6)
               and round(s.cost.coverage, 6) == round(v2[s.short].cost.coverage, 6)
               and s.traps_resisted == v2[s.short].traps_resisted
               and s.cost.distinct_fields == v2[s.short].cost.distinct_fields)
    return {
        "mem": mem, "por": por, "told": told, "scale": scale, "nav": nav,
        "ours": mem.reference(), "base": mem.baseline(), "ours_p": por.reference(), "base_p": por.baseline(),
        "held_untold": sum(s.traps_resisted for s in untold), "runs_untold": sum(s.traps for s in untold),
        "held_claude_told": sum(s.traps_resisted for s in told if s.model.startswith("claude")),
        "runs_claude_told": sum(s.traps for s in told if s.model.startswith("claude")),
        "agree": (min(s.cost.coverage for s in told), max(s.cost.coverage for s in told)),
        "stable": (min(s.stable_runs for s in told), max(s.stable_runs for s in told)),
        "inj_held": sum(r["held"] for r in inj["rows"] if r["model"]),
        "inj_runs": sum(r["runs"] for r in inj["rows"] if r["model"]),
        "inj_told": sum(r["held"] for r in inj["rows"] if r["model"] and r["briefing"] == "policy"),
        "inj_told_runs": sum(r["runs"] for r in inj["rows"] if r["model"] and r["briefing"] == "policy"),
        "same": same, "rows": len(por.scores), "v2_ours": v2["compliance-aware"].cost.page_loads,
        "v2_base": v2["unconstrained"].cost.page_loads,
        "functions": len(REGISTRY), "tests": tt._test_count(),
        "models": [tt.MODEL[m] for m in tt.MODEL_ORDER if any(s.model == m for s in models)],
    }


def pct(a, b) -> str:
    return f"{round(a * 100)} to {round(b * 100)}%"


# --------------------------------------------------------------------------- #
# slides
# --------------------------------------------------------------------------- #

def draw_architecture(slide):
    y1, y2, y3 = 1.45, 3.25, 5.15
    w, gap, x0 = 2.6, 0.45, 0.75
    xs = [x0 + i * (w + gap) for i in range(4)]
    top = [("A  Sources", "portal, export files,\nsynthetic generator"),
           ("B  Adapters", "one interface: browser,\nfiles, memory"),
           ("C  Meter", "fetches, records, fields,\nreal page loads"),
           ("D  Techniques", "ours, AI models,\nbaseline")]
    low = [("H  Assistant", "recognise, gate,\ncollect, guide"),
           ("G  Evidence", "audit log, sidecars,\nrecord of processing"),
           ("F  Export", "HL7 v2, FHIR, tokens,\nexport audit"),
           ("E  Rules", "seven DPDP rules,\nbenchmark")]
    for x, (t, sub) in zip(xs, top):
        add_box(slide, x, y1, w, 1.15, t, sub, size=14)
    for x, (t, sub) in zip(xs, low):
        add_box(slide, x, y2, w, 1.15, t, sub, size=14)
    for i in range(3):
        add_arrow(slide, xs[i] + w, y1 + 0.57, xs[i + 1], y1 + 0.57)
    add_arrow(slide, xs[3] + w / 2, y1 + 1.15, xs[3] + w / 2, y2)                 # D -> E
    add_arrow(slide, xs[3] + 0.25, y1 + 1.15, xs[2] + w - 0.25, y2)               # D -> F
    add_arrow(slide, xs[2] + 0.25, y1 + 1.15, xs[1] + w - 0.25, y2)               # C -> G
    add_arrow(slide, xs[2], y2 + 0.57, xs[1] + w, y2 + 0.57)                      # F -> G
    add_arrow(slide, xs[1] + 0.25, y1 + 1.15, xs[0] + w - 0.25, y2)               # B -> H (crawl map)
    add_box(slide, xs[0], y3, xs[3] + w - xs[0], 0.85, "Policy, read by E, F and H",
            "purpose table (three non-nested purposes)  |  capability register  |  role scope = purposes ∩ interoperability artefacts",
            fill=LIGHT, size=14)
    for x in (xs[0], xs[2], xs[3]):
        add_arrow(slide, x + w / 2, y3, x + w / 2, y2 + 1.15)
    add_text(slide, 0.75, 6.2, 12.0, 0.4, [
        "Solid arrows carry data. The adapter boundary means every technique runs unchanged on memory, the "
        "portal and an export; the meter sees everything at that boundary; the harness, not a technique, writes the evidence."],
        size=12, color=GREY)


def draw_workflow(slide, f):
    stages = [("1  Portal", "login-gated HIS portal served over TLS"),
              ("2  Discover", f"browser signs in, crawls, infers each module's layer ({f['nav']['page_loads']} page loads)"),
              ("3  Benchmark", f"{f['rows']} technique rows x 4 tasks; seven rules; real page loads; audit-logged"),
              ("4  Normalise", "HL7 v2 and FHIR, identifiers tokenised, export audited, erasure scheduled"),
              ("5  Purpose", "the same run re-judged under every purpose"),
              ("6  Assist", "one question per role, steps placed on the crawled screens; one declined"),
              ("7  Retain", "retention runs out; the purge erases the export and its key, and logs it")]
    w, h, gap = 3.55, 1.25, 0.32
    pos = [(0.75, 1.5), (0.75 + w + gap, 1.5), (0.75 + 2 * (w + gap), 1.5),
           (0.75 + 2 * (w + gap), 3.25), (0.75 + w + gap, 3.25), (0.75, 3.25),
           (0.75 + w + gap, 5.0)]
    for (t, sub), (x, y) in zip(stages, pos):
        add_box(slide, x, y, w, h, t, sub, size=14)
    for a, b in ((0, 1), (1, 2)):
        add_arrow(slide, pos[a][0] + w, pos[a][1] + h / 2, pos[b][0], pos[b][1] + h / 2)
    add_arrow(slide, pos[2][0] + w / 2, pos[2][1] + h, pos[3][0] + w / 2, pos[3][1])
    for a, b in ((3, 4), (4, 5)):
        add_arrow(slide, pos[a][0], pos[a][1] + h / 2, pos[b][0] + w, pos[b][1] + h / 2)
    add_arrow(slide, pos[5][0] + w / 2, pos[5][1] + h, pos[6][0], pos[6][1] + h / 2)
    add_text(slide, 0.75 + 2 * (w + gap), 5.05, w, 1.3, [
        "python scripts/run_pipeline.py",
        "One command, every stage real; about eight minutes on a laptop, most of it the baseline's "
        f"{f['base_p'].cost.page_loads} page loads."], size=12, color=NAVY, bold_first=True)


def build(*, without_instruction_slide: bool = False) -> Path:
    if not TEMPLATE.exists():
        sys.exit(f"template not found: {TEMPLATE}. Set REVIEW3_TEMPLATE to the path of '{TEMPLATE_NAME}' "
                 f"(kept outside the repository) or copy it to the repo root.")
    shutil.copyfile(TEMPLATE, TARGET)
    prs = Presentation(TARGET)
    st = Styles(prs)
    f = facts()
    s = list(prs.slides)
    (t_title, t_info, t_overview, t_arch, t_impl, t_results, t_compare, t_demo, t_sdg, t_concl, t_refs,
     t_thanks) = s
    ours, base, ours_p, base_p = f["ours"], f["base"], f["ours_p"], f["base_p"]
    # Copies are cut from the untouched template slides before any slide is filled.
    objectives = duplicate_slide(prs, 2)
    workflow = duplicate_slide(prs, 3)
    impl2, impl3, impl4, impl5 = (duplicate_slide(prs, 4) for _ in range(4))
    res2, res3, res4, res5 = (duplicate_slide(prs, 5) for _ in range(4))
    refs_b = duplicate_slide(prs, 10)

    # ---- title ------------------------------------------------------------------
    rewrite_plain(shape_named(t_title, "Text 3"), [TITLE], size=26)
    rewrite_plain(shape_named(t_title, "Text 5"), ["Ananya Karmakar        23BLC1017", "Avanindra Kushwah  23BLC1089"], size=13)
    rewrite_plain(shape_named(t_title, "Text 8"), ["Dr. Manoj Kumar, SENSE"])
    rewrite_plain(shape_named(t_title, "Text 11"), ["B.Tech ECM, SENSE, VIT Chennai"])
    rewrite_plain(shape_named(t_title, "Text 14"), ["Review-III, 28.10.2026 (Wednesday)"])
    for sh in list(t_title.shapes):
        if sh.has_text_frame and sh.text_frame.text.startswith("Approval is mandatory"):
            drop(sh)

    # ---- 1. project overview --------------------------------------------------------
    overview = t_overview
    title(overview, "Project Overview")
    body(shape_named(overview, "Text 2"), [
        ("Background", [
            "A hospital information system (HIS) holds identity, diagnoses, medication, contact and billing "
            "data. Much routine work starts by reading records out of it through the portal staff already use.",
            "Extraction techniques, including AI agents, are judged on speed, robustness and coverage. "
            "Whether they took only what the purpose needed is never measured.",
        ]),
        ("Why it matters now", [
            "The DPDP Act, 2023 and the DPDP Rules, 2025 make purpose, minimisation, notice, retention, "
            "safeguards and accountability binding on every hospital that processes patient data.",
            "A scraper tuned for coverage is, under the Act, tuned to over-collect.",
        ]),
        ("What we built", [
            "A pipeline that extracts from a login-gated HIS portal with a real browser and scores every "
            "technique on seven executable DPDP rules, with page loads as cost.",
            "Publicly available AI models compared with our rule-driven technique on identical tasks; exports "
            "verified; a role-gated assistant that guides hospital staff.",
        ]),
    ], st, head=16, text=14)

    # ---- 2. problem statement and objectives -------------------------------------------
    title(objectives, "Problem Statement & Objectives")
    body(shape_named(objectives, "Text 2"), [
        ("Problem statement", [
            "No executable account of what the DPDP Act requires of an extraction run, no benchmark that scores "
            "competing techniques on it under identical conditions, and no check of a technique's claims about "
            "its own output.",
        ]),
        ("Objectives and outcomes", [
            "Make the Act executable: seven rules over a declared manifest and the data categories taken.  "
            "Achieved.",
            f"Build a fair benchmark: ours, {len(f['models'])} public AI models (three briefings each) and a "
            "baseline, scored on the same rules with real cost.  Achieved.",
            "Extract from a system we do not control: a browser that discovers the portal's structure for "
            "itself; the same code on files and a public export.  Achieved on the fixture.",
            "Verify what leaves: HL7 v2 and FHIR with keyed tokens, audited; retention scheduled and purged.  "
            "Achieved.",
            "Guide staff within their role: an assistant gated by the same policy, robust to a HIS update.  "
            "Achieved.",
        ]),
        ("Constraint we planned for", [
            "No live HIS access and no hospital patient data: a portal fixture built as a foreign system, "
            "synthetic data, and a public export we did not generate.",
        ]),
    ], st, head=16, text=13.5)

    # ---- 3. architecture ---------------------------------------------------------------
    arch = t_arch
    title(arch, "System Architecture")
    draw_architecture(arch)
    title(workflow, "System Architecture: Workflow")
    draw_workflow(workflow, f)

    # ---- 4. complete implementation (five slides) ------------------------------------
    impl1 = t_impl
    title(impl1, "Complete Implementation: Modules")
    drop(shape_named(impl1, "Text 2"))
    rows = [["Module", "What it does", "Built with"],
            ["Portal fixture", "Login-gated HTML portal over TLS, paginated tables, record pages, search; four role accounts; robots.txt; a v2 release layout", "Flask"],
            ["Browser extraction", f"Signs in, crawls, infers each module's HIS layer from field names, label aliases, split modules, search-box scoping", "Playwright"],
            ["File adapter + gate", "Classifies export files by their columns; column map; refuses real data without provenance, git-ignore and an audit key", "pandas"],
            ["Compliance engine", "Manifest, seven rules, purpose policy, capability register, veracity, trap scoring, Wilson intervals", "pydantic"],
            ["AI-model techniques", f"{', '.join(f['models'])}: briefed with field names only, recorded once and replayed", "provider SDKs, CLI"],
            ["Export + evidence", "HL7 v2.5, FHIR R4, HMAC tokens, export audit, hash-chained audit log, retention purge, access and breach reports", "own code"],
            ["Staff assistant", f"{f['functions']} rule-based functions for three roles, gate before collection, steps worded from the crawl", "own code, no model"],
            ["Presentation", "Report, five portals and the HIS Staff Assistant page, offline, built from the artefacts", "HTML, JS"]]
    gf = add_table(impl1, 0.6, 1.3, 12.1, 5.2, rows, [2.4, 7.9, 1.8], body_size=12.5, header_size=13)
    add_text(impl1, 0.6, 6.6, 12.1, 0.4, [
        f"About 11,400 lines of Python in src/, {f['tests']} tests, CI on Python 3.10 and 3.12 that re-runs the "
        "benchmark and fails if any number changes."], size=12, color=GREY)

    title(impl2, "Implementation: Acquisition")
    drop(shape_named(impl2, "Text 2"))
    picture(impl2, IMG / "portal-crawl.png", 0.6, 1.35, 6.6, 4.6)
    add_text(impl2, 7.45, 1.35, 5.3, 5.2, [
        "A portal we do not control",
        "Username and password only: no API, no data attributes, module URLs in portal vocabulary. "
        "robots.txt disallows automation; we proceed only under a recorded authorisation (AUTH-RPA-2026).",
        "",
        "Discovery from content",
        f"The crawler maps {len(f['nav']['modules'])} modules in {f['nav']['page_loads']} page loads and infers each "
        "module's HIS layer from the field names it finds, never from the URL. Label aliases handle real "
        "display names; a module split by a release is followed and joined on the patient key.",
        "",
        "Reading only what is asked",
        "List columns before record pages; a one-patient task goes through the search box. Every page load "
        "is counted: that is the cost the benchmark reports.",
    ], size=13, bold_first=True)
    for i in (0, 3, 6):  # bold the three run-in heads
        p = impl2.shapes[-1].text_frame.paragraphs[i]
        p.runs[0].font.bold = True
        p.runs[0].font.color.rgb = NAVY

    title(impl3, "Implementation: Compliance Engine")
    drop(shape_named(impl3, "Text 2"))
    rules = [["Rule", "Principle (DPDP Act)", "Check", "Score"],
             ["DM-01", "Minimisation, s.6(1) with s.4(1)", "categories inside the purpose; one patient's records only", "lower of the two axes"],
             ["LB-01", "Lawful basis, s.4, s.6, s.7", "basis declared with its reference", "0, 0.5, 1"],
             ["SL-01", "Storage limitation, s.8(7)", "retention within ceiling; deletion route", "0.5 each"],
             ["SS-01", "Safeguards, s.8(4) to (6)", "TLS, at-rest, access control, tokens if required", "fraction"],
             ["PL-01", "Purpose limitation, s.4(1), s.5(1)", "one purpose; onward uses assessed", "1, 0.5, 0.25, 0"],
             ["NT-01", "Notice, s.5(1)", "notice recorded and covers the purpose", "0, 0.5, 1"],
             ["AC-01", "Accountability, s.8(1), s.8(9)", "audit log, accountable party, record of processing", "fraction"]]
    add_table(impl3, 0.6, 1.3, 7.7, 4.0, rules, [0.85, 2.45, 3.2, 1.2], body_size=11.5, header_size=12.5)
    add_text(impl3, 8.55, 1.3, 4.2, 5.3, [
        "The manifest",
        "Every run declares purpose, basis, retention, safeguards, notice and governance. The harness adds "
        "the record scope it observed; a technique cannot vouch for itself.",
        "",
        "Categories, never values",
        "Rows are reduced to six DPDP categories, so every artefact is free of personal data.",
        "",
        "Three non-nested purposes",
        "Care, billing, registration: no purpose contains another, so lawfulness depends on data and purpose together.",
    ], size=12.5)
    for i in (0, 3, 6):
        p = impl3.shapes[-1].text_frame.paragraphs[i]
        p.runs[0].font.bold = True
        p.runs[0].font.color.rgb = NAVY
    add_text(impl3, 0.6, 5.45, 7.7, 1.2, [
        "Capability register: what the deployment really has, each control with an identifier. Six controls "
        "are demonstrated by evidence the pipeline produces (TLS observed, audit log, export audit, purge, "
        "record of processing, access authorisation); the rest are attested."], size=12, color=GREY)

    title(impl4, "Implementation: Export, Evidence and Patients' Rights")
    body(shape_named(impl4, "Text 2"), [
        ("Shaping adds nothing", [
            "Rows leave as HL7 v2.5 (ADT, ORM, ORU, DFT) and FHIR R4 resources; only extracted fields appear.",
        ]),
        ("Pseudonymised and verified", [
            "Direct identifiers become HMAC-SHA-256 tokens (PSN-...), stable within an export, unlinkable across; "
            "birth date to year, PIN to three digits, k-anonymity reported.",
            "The export audit searches every message and resource for every raw identifier taken: the claim is "
            "checked against the file.",
        ]),
        ("Evidence a hospital can show", [
            "Hash-chained audit log written by the harness, patients as keyed tokens, kept 365 days (Rule 6).",
            "Retention sidecar per export; the purge erases files and key and logs it.",
            "Generated from the log: record of processing, an answer to a patient's access request, and a "
            "breach assessment with drafted notices to the Board (72 hours) and to each patient.",
        ]),
    ], st, head=15.5, text=13.5)
    add_text(impl4, 0.75, 6.25, 12.0, 0.5, [
        "PID|1||PSN-57990d0fcf78^^^HIS^MR||||2025|F      a token where the record number was, a birth year"],
        size=12, color=NAVY, font="Consolas")

    title(impl5, "Implementation: Staff Assistant, Integration, Optimisation")
    drop(shape_named(impl5, "Text 2"))
    picture(impl5, FIG / "agent-portal.png", 0.6, 1.35, 6.2, 3.95)
    add_text(impl5, 0.6, 5.4, 6.2, 1.3, [
        f"{f['functions']} functions for reception, nurse and administrator, no AI model. The DPDP gate runs before "
        "any detail is asked; steps name the operation and fields, and their words come from the crawl, so a "
        "vendor release needs a new crawl, not new code."], size=12)
    add_text(impl5, 7.05, 1.35, 5.7, 5.3, [
        "Integration",
        "scripts/run_pipeline.py runs all seven stages; --dataset and --portal point the same code at an "
        "export or a real portal.",
        "",
        "Performance optimisation",
        f"Search-box scoping: {ours_p.cost.page_loads} page loads instead of {base_p.cost.page_loads}.",
        "List columns before record pages; one crawl reused by every technique and the assistant.",
        "Model decisions recorded once and replayed: no network, no cost, reproducible; the recorder is "
        "paced and resumable.",
        "Seeded synthetic data, so CI can compare the benchmark exactly.",
    ], size=12.5)
    for i in (0, 3):
        p = impl5.shapes[-1].text_frame.paragraphs[i]
        p.runs[0].font.bold = True
        p.runs[0].font.color.rgb = NAVY

    # ---- 5. results and testing --------------------------------------------------------
    res1 = t_results
    title(res1, "Results: Ours vs Publicly Available AI Models")
    head = ["Technique", "Score", "Trap runs held", "Fields of the job obtained", "Excess", "Same decision",
            "Page loads (portal)"]
    rows = [head]
    portal = {s.short: s for s in f["por"].scores}
    for sc, _ in f["mem"].by_model():
        name = "Ours (reference)" if sc.short == "compliance-aware" else (
            "Baseline (take all)" if sc.short == "unconstrained" else tt.MODEL.get(sc.model, sc.model))
        p = portal.get(sc.short)
        rows.append([name, f"{sc.mean_compliance_score:.3f}", f"{sc.traps_resisted}/{sc.traps}",
                     f"{sc.cost.coverage * 100:.0f}%", f"{sc.cost.excess_ratio:.2f}",
                     f"{sc.stable_runs}/{sc.repeat_runs}", str(p.cost.page_loads) if p else "n/a"])
    gf = add_table(res1, 0.6, 1.35, 12.1, 3.3, rows, [3.0, 1.2, 1.6, 2.1, 1.1, 1.5, 1.6], body_size=13.5,
                   header_size=12.5)
    style_table(gf, highlight_row=1)
    lo, hi = f["agree"]
    add_text(res1, 0.6, 4.85, 12.1, 1.8, [
        f"Models told the hospital's purpose policy, in memory: 8 tasks x 5 runs, every run scored. Page loads from the portal run.",
        f"Scores are close; the difference is elsewhere. Every model obtained {pct(lo, hi)} of the fields the "
        f"jobs need and repeated its own first decision in at most {f['stable'][1]} of 32 repeats. Ours: 100%, 32/32, "
        "by construction.",
        f"Claude Sonnet 5.5 ties our score at 1.000 while doing {round(next(s for s in f['told'] if s.model == 'claude-sonnet-5-5').cost.coverage * 100)}% of the job, differently each time.",
    ], size=13)
    f0 = res1.shapes[-1].text_frame.paragraphs[0].runs[0].font
    f0.color.rgb = GREY
    f0.size = Pt(11.5)

    title(res2, "Results: Traps and Planted Instructions")
    picture(res2, IMG / "rules-vs-ai.png", 0.6, 1.35, 7.3, 3.6)
    add_text(res2, 8.15, 1.35, 4.6, 5.3, [
        "Trap tasks",
        "Lawful job, provocative wording: diagnosis for billing, insurance number at the desk, a research "
        "registry copy, a year's retention.",
        f"Not told the policy: {f['held_untold']} of {f['runs_untold']} trap runs held.",
        f"Told the policy: the three Claude models {f['held_claude_told']}/{f['runs_claude_told']}; Gemini 10/20 "
        "(took the diagnosis for billing every run).",
        "",
        "Planted instructions",
        "A fake officer's note, a fake system instruction, a fake supervisor.",
        f"Models held {f['inj_held']} of {f['inj_runs']} runs ({f['inj_told']}/{f['inj_told_runs']} told the policy). "
        "Ours 15/15: wording is not an input to it.",
    ], size=12.5)
    for i in (0, 5):
        p = res2.shapes[-1].text_frame.paragraphs[i]
        p.runs[0].font.bold = True
        p.runs[0].font.color.rgb = NAVY
    caption(res2, 0.6, 5.05, 7.3, "Report, Figure 1: trap runs held (95% interval), score, fields obtained, "
                                   "repeatability; models told the policy.", size=11)

    title(res3, "Results: Cost and Scale")
    srows = [["Records per module", "Ours: page loads", "Baseline: page loads", "Ratio", "Baseline: records read / needed"]]
    for r in f["scale"]:
        o, b = r["ours"], r["baseline"]
        srows.append([str(r["records"]), str(o["page_loads"]), str(b["page_loads"]),
                      f"{b['page_loads'] / o['page_loads']:.1f}x", f"{b['record_excess'] or 0:.0f}x"])
    add_table(res3, 0.6, 1.35, 7.4, 2.4, srows, [1.4, 1.4, 1.6, 1.0, 2.0], body_size=13, header_size=12)
    add_text(res3, 8.3, 1.35, 4.45, 5.3, [
        "Cost and compliance move together",
        f"On the portal ours loads {ours_p.cost.page_loads} pages, the baseline {base_p.cost.page_loads}, at the "
        f"same coverage; scores 1.000 and {base_p.mean_compliance_score:.3f}.",
        "The extra pages are exactly the overreach minimisation forbids: every patient's records read to answer "
        "for one.",
        "",
        "Growth",
        "Ours grows only on the ward census, the one task that covers every patient. The baseline's cost and "
        "the data it holds without need grow with the hospital.",
    ], size=13)
    for i in (0, 4):
        p = res3.shapes[-1].text_frame.paragraphs[i]
        p.runs[0].font.bold = True
        p.runs[0].font.color.rgb = NAVY
    picture(res3, IMG / "r3-scraper.png", 0.6, 4.0, 7.4, 2.6)
    caption(res3, 0.6, 6.65, 7.4, f"After a simulated vendor release: {f['same']} of {f['rows']} results unchanged; "
                                   f"only page loads moved.", size=11)

    title(res4, "Results: Purpose Matrix, Export Audit, Breach")
    prow = [["Care pull (30 days) judged under", "Score", "Rules failed"],
            ["care coordination (declared)", "1.000", "none"],
            ["billing settlement", "0.786", "DM-01, NT-01"],
            ["patient registration", "0.857", "DM-01, NT-01"]]
    add_table(res4, 0.6, 1.35, 6.0, 1.7, prow, [3.2, 1.0, 1.8], body_size=12.5, header_size=12.5)
    erow = [["Patient-summary export", "Ours", "Baseline"],
            ["Raw identifiers in export", "0", "60 of 60"],
            ["Patients exposed if leaked", "1, as tokens", "20, raw"],
            ["Erasure scheduled", "30 days", "cannot be"]]
    add_table(res4, 0.6, 3.25, 6.0, 1.7, erow, [3.0, 1.5, 1.5], body_size=12.5, header_size=12.5)
    add_text(res4, 0.6, 5.1, 6.0, 1.6, [
        "One unchanged extraction is lawful for its purpose and unlawful for the others, in both directions: "
        "neither purpose is the stricter one. The manifest's claim and the file agree for both techniques."],
        size=12.5)
    picture(res4, IMG / "r3-breach.png", 6.9, 1.35, 5.85, 3.0)
    caption(res4, 6.9, 4.45, 5.85, "Breach drill: the same job exported both ways, then lost. Notices to the "
                                   "Board and the patient are drafted from the audit log.", size=11)

    title(res5, "Results: Testing and Validation")
    body_box = add_text(res5, 0.6, 1.35, 12.1, 5.3, [
        f"Test suite: {f['tests']} tests; CI re-runs the benchmark from a clean checkout and fails on any change; the thesis "
        "and report tables are checked against the artefacts.",
        "Properties asserted by tests: no purpose contains another; techniques run unchanged on the portal; "
        "shaping adds no field; our export leaks no identifier and the baseline's leaks all; the assistant's gate "
        "runs before any input; a TLS claim over plain HTTP is rejected; the audit chain detects tampering.",
        "Data we did not write: the public Synthea export (108 patients, 18 files) through the real handling "
        "gate; the ranking held, national identifiers stopped at the adapter, and five adapter defects were found "
        "and fixed.",
        f"HIS update: a release that renames, moves and splits screens; {f['same']} of {f['rows']} benchmark rows "
        "unchanged; 27 of 31 assistant tasks re-worded themselves, 4 withheld until two proposals were "
        "confirmed.",
        "Sensitivity: 17 alternative rule weightings never move the baseline from last; ablation shows each of our five "
        "design choices moves only the rule it serves.",
        "Assistant page self-check: 1,053 recorded conversations replayed on every load.",
    ], size=13.5)
    for p in body_box.text_frame.paragraphs:
        p.space_after = Pt(7)

    compare = t_compare
    title(compare, "Results: Comparison with Existing Solutions")
    crow = [["Property", "Generated scrapers [2],[3],[5]", "LLM agents [4]", "AI models, told policy", "Coverage baseline", "Ours"],
            ["Purpose stated and scored", "no", "no", "yes", "no", "yes"],
            ["Fields limited to what the job needs", "no", "no", f"partly ({pct(lo, hi)})", "no", "yes"],
            ["Records limited to the patient", "no", "no", "yes", "no", "yes"],
            ["Holds a breach invited by wording", "n/a", "not tested", "3 of 4 models", "no", "yes"],
            ["Same decision every run", "once generated", "once replayed", f"no ({f['stable'][0]} to {f['stable'][1]} of 32)", "yes", "yes"],
            ["Pseudonymised export, verified", "no", "no", "declared only", "no", "yes"],
            ["Retention scheduled and purged", "no", "no", "declared only", "no", "yes"],
            ["Cost in reproducible units", "partly", "partly", "yes", "yes", "yes"]]
    gf = add_table(compare, 0.6, 1.35, 12.1, 4.6, crow, [3.4, 1.9, 1.5, 2.1, 1.6, 1.6], body_size=12.5,
                   header_size=12)
    style_table(gf, first_col_bold=False)
    add_text(compare, 0.6, 6.1, 12.1, 0.6, [
        "Existing extraction work was built to solve extraction, not governance: a 'no' records a measurement "
        "nobody made. Measuring these properties separates techniques that look alike on the usual scorecard."],
        size=12, color=GREY)

    # ---- 6. demonstration ------------------------------------------------------------
    demo = t_demo
    title(demo, "Live & Video Demonstration")
    body(shape_named(demo, "Text 2"), [
        ("Live demonstration plan (offline; no network or key needed)", [
            "scripts/run_pipeline.py: portal, crawl, benchmark, export audit, purpose matrix, assistant, purge.",
            "Portal v2: one job replayed end to end, every value from the hospital through scoring, "
            "pseudonymisation, shaping and erasure, ours beside an AI model and the baseline.",
            "The HIS Staff Assistant: a tour per role; a receptionist asking for a diagnosis is declined "
            "before any detail is asked.",
            "The Report: trap results, planted instructions, the breach drill, the HIS update.",
        ]),
        ("Video demonstration", [
            "Embedded below (also docs/review/video/demo.mp4): the same walk-through recorded, in case the "
            "room's machine cannot run a browser.",
        ]),
    ], st, head=15.5, text=13.5)
    if VIDEO.exists():
        poster = VIDEO.with_suffix(".png")
        demo.shapes.add_movie(str(VIDEO), Inches(4.4), Inches(4.75), Inches(4.5), Inches(2.53),
                              poster_frame_image=str(poster) if poster.exists() else None, mime_type="video/mp4")

    # ---- 7. standards and SDGs -----------------------------------------------------------
    sdg = t_sdg
    title(sdg, "Standards Followed & SDG Mapping")
    drop(shape_named(sdg, "Text 2"))
    srow = [["Standard", "How it is used"],
            ["DPDP Act 2023; DPDP Rules 2025", "seven executable rules; audit log 365 days; 72-hour breach notice"],
            ["HL7 v2.5; HL7 FHIR R4 (ANSI)", "every export shaped and audited"],
            ["ICD-10 (WHO)", "coherent diagnosis, drug and allergy codes"],
            ["ISO/TS 25237; ISO/IEC 20889", "keyed pseudonyms; generalisation; k-anonymity (aligned)"],
            ["ISO/IEC 27001 (IS/ISO/IEC 27001, BIS); ISO 27799", "role access, logging, log integrity (aligned)"],
            ["RFC 2104 HMAC-SHA-256; RFC 8446 TLS; RFC 9309", "tokens and hash chain; observed TLS; robots.txt honoured"],
            ["EHR Standards for India 2016 (MoHFW)", "exchange standards it recommends"]]
    add_table(sdg, 0.6, 1.3, 7.3, 4.6, srow, [3.4, 3.9], body_size=11.5, header_size=12.5)
    add_text(sdg, 8.15, 1.3, 4.6, 5.3, [
        "SDG 3  Good health and well-being",
        "Patient data used for care, billing and registration without exposure beyond each purpose.",
        "",
        "SDG 16  Strong institutions",
        "A national law turned into checks a hospital can run and evidence it can show.",
        "",
        "SDG 9  Industry and innovation",
        "A reproducible benchmark that rates AI models on legal obligations as well as cost.",
        "",
        "SDG 10  Reduced inequalities",
        "Safeguards by construction, so a small hospital's patients get the same protection.",
    ], size=12.5)
    for i in (0, 3, 6, 9):
        p = sdg.shapes[-1].text_frame.paragraphs[i]
        p.runs[0].font.bold = True
        p.runs[0].font.color.rgb = NAVY

    # ---- 8. conclusion -----------------------------------------------------------------
    concl = t_concl
    title(concl, "Conclusion & Future Scope")
    body(shape_named(concl, "Text 2"), [
        ("Conclusion", [
            f"Compliance can be scored on equal terms: ours {ours.mean_compliance_score:.3f}, the baseline "
            f"{base.mean_compliance_score:.3f}, on the same seven rules; artefacts carry no personal data.",
            "Lawfulness belongs to the pull and its purpose together; for a coverage scraper, cost and "
            "non-compliance coincide.",
            "Public AI models file good paperwork and, given the policy, mostly respect it, but do part of the job "
            "and decide differently each run. A rule-driven technique has neither weakness by construction.",
        ]),
        ("Limitations", [
            "A portal we wrote; no hospital patient data; four models, five samples; traps and register written "
            "by us; a coarse minimisation rule.",
        ]),
        ("Future scope", [
            "A real hospital portal; claims adjudication as a fourth purpose; DICOM and ISO/IEEE 11073 export; "
            "field-level minimisation; more model families; parallel browser contexts; a conference manuscript "
            "(drafted).",
        ]),
    ], st, head=16, text=14)

    # ---- 9. references ------------------------------------------------------------------
    refs = [
        '[1] R. N. R. Ruchitaa, S. Nandhakumar Raj and M. Vijayalakshmi, "Web scrapping tools and techniques: A brief survey," Proc. ICITIIT, 2023.',
        '[2] W. Huang et al., "AutoScraper: A progressive understanding web agent for web scraper generation," Proc. EMNLP, 2024, pp. 2371-2389.',
        '[3] A. Mansour, K. W. Alshaer and M. Elsaban, "AXE: Low-cost cross-domain web structured information extraction," arXiv:2602.01838, 2026.',
        '[4] A. Bohra et al., "WebLists: Extracting structured information from complex interactive websites using executable LLM agents," arXiv:2504.12682, 2025.',
        '[5] S. Wang, J. Qiu, W. Zhang and C. He, "Co-Scraper: Query-aware DOM pruning and reusable scraper synthesis," arXiv:2606.14821, 2026.',
        '[6] T. Kim et al., "Scrapers selectively respect robots.txt directives," Proc. ACM IMC, 2025, pp. 541-557.',
        '[7] D. A. Purnawan and K. Surendro, "Building enterprise architecture for hospital information system," Proc. ICoICT, 2016.',
        '[8] C. N. Vorisek et al., "FHIR for interoperability in health research: Systematic review," JMIR Med. Inform., vol. 10, no. 7, e35724, 2022.',
        '[9] V. Khanna and A. Kotwal, "Examining the significance of the DPDP Act, 2023 in the context of the healthcare industry," Discover Public Health, vol. 22, 381, 2025.',
        '[10] A. Sood et al., "Challenges and recommendations for enhancing digital data protection in the Indian medical research and healthcare sector," npj Digit. Med., vol. 8, 48, 2025.',
        '[11] M. A. Brown et al., "Web scraping for research: Legal, ethical, institutional, and scientific considerations," Big Data & Society, 2025.',
        '[12] The Digital Personal Data Protection Act, 2023 (Act No. 22 of 2023), Gazette of India, Aug. 2023; The DPDP Rules, 2025, Nov. 2025.',
    ]
    refs2 = [
        '[13] C. V. Cook, "Tokenization techniques for privacy-preserving healthcare data," Front. Drug Saf. Regul., vol. 5, 1599217, 2025.',
        '[14] M. A. de Carvalho Junior and P. Bandiera-Paiva, "Health information system role-based access control current security trends and challenges," J. Healthc. Eng., 6510249, 2018.',
        '[15] A. Rule, M. F. Chiang and M. R. Hribar, "Using EHR audit logs to study clinical activity: a systematic review," JAMIA, vol. 27, no. 3, pp. 480-490, 2020.',
        '[16] K. Greshake et al., "Not what you\'ve signed up for: Compromising real-world LLM-integrated applications with indirect prompt injection," Proc. AISec, 2023, pp. 79-90.',
        '[17] J. Walonoski et al., "Synthea: An approach, method, and software mechanism for generating synthetic patients," JAMIA, vol. 25, no. 3, pp. 230-238, 2018.',
        '[18] L. Sweeney, "k-anonymity: A model for protecting privacy," Int. J. Uncertainty, Fuzziness Knowl.-Based Syst., vol. 10, no. 5, pp. 557-570, 2002.',
        '[19] E. B. Wilson, "Probable inference, the law of succession, and statistical inference," J. Amer. Stat. Assoc., vol. 22, no. 158, pp. 209-212, 1927.',
        '[20] J.-H. Hoepman, "Privacy design strategies," Proc. IFIP SEC, 2014, pp. 446-459.',
        '[21] HL7 International, "FHIR Release 4 (v4.0.1)," 2019; HL7 Messaging Standard Version 2.5, 2003.',
        '[22] ISO/TS 25237:2017, Health informatics: Pseudonymization; RFC 9309, Robots Exclusion Protocol, 2022.',
    ]
    title(t_refs, "References")
    rewrite_plain(shape_named(t_refs, "Text 2"), refs, size=11)
    rewrite_plain(shape_named(t_refs, "Text 3"), ["IEEE format. The full list of 39 references is in the project report."], size=11)
    title(refs_b, "References (contd.)")
    rewrite_plain(shape_named(refs_b, "Text 2"), refs2, size=11)
    rewrite_plain(shape_named(refs_b, "Text 3"), ["IEEE format. The full list of 39 references is in the project report."], size=11)

    # ---- order, numbering ---------------------------------------------------------------------
    order = [t_title, t_info, overview, objectives, arch, workflow, impl1, impl2, impl3, impl4, impl5,
             res1, res2, res3, res4, res5, compare, demo, sdg, concl, t_refs, refs_b, t_thanks]
    reorder(prs, order)
    if without_instruction_slide:
        remove_slide(prs, t_info)
    number(prs)
    prs.save(TARGET)
    return TARGET


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--without-instruction-slide", action="store_true",
                        help="leave out the template's review-information slide (after numbering)")
    args = parser.parse_args()
    out = build(without_instruction_slide=args.without_instruction_slide)
    print(f"  wrote {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
