"""Build a Word copy of the thesis (Thesis.docx) from the same LaTeX sources as Thesis.pdf.

    python build_thesis_docx.py                  # writes Thesis.docx and a PDF of it to check against
    python build_thesis_docx.py --no-word        # skip Word: page numbers in the contents stay unset

The page set-up, type and layout follow the School's Word template (A4, Times New Roman 12 pt,
1.5 line spacing, justified text, centred chapter openings, italic centred captions, roman page
numbers for the front matter and arabic from Chapter 1). The text, tables, numbering,
cross-references and bibliography are read from docs/thesis/ and docs/thesis/generated/, so the
Word copy says what the PDF says. Figures drawn in TikZ or pgfplots are compiled one by one with
Tectonic and placed as images; equations become editable Word equations.

Environment:
    THESIS_DOCX_OUT  where to write Thesis.docx (default: the repository root, beside Thesis.pdf)
    THESIS_TEMPLATE  the folder with the School's logo.png (as tools/build_thesis.py)
"""

from __future__ import annotations

import argparse
import html
import os
import re
import shutil
import subprocess
import sys
import zipfile
from dataclasses import dataclass, field
from pathlib import Path

from PIL import Image, ImageChops

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import build_thesis  # noqa: E402

SOURCE = ROOT / "docs" / "thesis"
WORK = HERE / "work"
OUT = Path(os.environ.get("THESIS_DOCX_OUT", ROOT / "Thesis.docx"))
CHECK_PDF = WORK / "Thesis-docx.pdf"

# The official title, as submitted at the start of the project (user, 2026-10-18).
TITLE = "Data Extraction Techniques for HIS Towards DPDP Compliance"
TITLE_LINES = ("Data Extraction Techniques for HIS", "Towards DPDP Compliance")
# The working title used in the sources until then; replaced wherever it is still found.
OLD_TITLE = re.compile(r"AI-Driven\s+HIS\s+Management\s+Agent(?:\s*\\\\)?\s+with\s+DPDP-Compliant\s+Web\s+Scraping")
STUDENTS = (("Ananya Karmakar", "23BLC1017"), ("Avanindra Kushwah", "23BLC1089"))

# ---------------------------------------------------------------- page geometry (twips)
PAGE_W, PAGE_H = 11906, 16838                  # A4, as the School's template
MARGIN_L, MARGIN_R, MARGIN_T, MARGIN_B = 1800, 1440, 1440, 1440
TEXT_W = PAGE_W - MARGIN_L - MARGIN_R          # 8666 twips = 15.29 cm
LATEX_TEXTWIDTH_CM = 14.65                     # the LaTeX template's text block
CM = 567                                       # twips per cm
EMU_PER_TWIP = 635

LINK_COLOR = "1F4E9A"
RULE_COLOR = "000000"

# ---------------------------------------------------------------- the document model


@dataclass
class Run:
    text: str = ""
    b: bool = False
    i: bool = False
    mono: bool = False
    sf: bool = False
    sc: bool = False
    size: float | None = None          # points
    sup: bool = False
    sub: bool = False
    kind: str = "text"                 # text | br | ref | cite | url | tab
    key: str = ""                      # label for ref, comma keys for cite, target for url
    prefix: str = ""                   # "auto" for \sref-style references


@dataclass
class Para:
    runs: list[Run]
    style: str = "Body"
    align: str | None = None
    size: float | None = None


@dataclass
class Heading:
    level: int                          # 1 chapter, 2 section, 3 subsection
    runs: list[Run]
    numbered: bool = True
    label: str | None = None
    number: str = ""
    bookmark: str = ""
    ref_number: str = ""                # what \aref prints for an unnumbered appendix part


@dataclass
class ListBlock:
    ordered: bool
    items: list[list]                    # each item: a list of blocks
    level: int = 0
    compact: bool = False                # set in a \small group: 10 pt, single spacing (the standards page)


@dataclass
class Cell:
    runs: list[Run]
    span: int = 1
    vmerge: str | None = None           # restart | continue
    align: str = "left"


@dataclass
class Row:
    cells: list[Cell]
    header: bool = False
    top: str | None = None              # rule above: thick | thin
    bottom: str | None = None
    cline: list[tuple[int, int]] = field(default_factory=list)
    shade: str | None = None


@dataclass
class Table:
    widths: list[int]
    aligns: list[str]
    vbars: list[bool]                    # a bar before column i (len = ncols + 1)
    rows: list[Row]
    caption: list[Run] | None = None
    short: list[Run] | None = None
    label: str | None = None
    size: float = 9.0
    notes: list[Para] = field(default_factory=list)
    number: str = ""
    bookmark: str = ""
    long: bool = False                   # a longtable may break across pages; a float is kept whole


@dataclass
class Image_:
    path: Path
    width_twips: int


@dataclass
class Code:
    lines: list[str]
    numbered: bool = False
    caption: list[Run] | None = None
    label: str | None = None
    number: str = ""
    bookmark: str = ""


@dataclass
class Figure:
    rows: list[list[Image_]]
    code: Code | None = None
    caption: list[Run] | None = None
    short: list[Run] | None = None
    label: str | None = None
    number: str = ""
    bookmark: str = ""


@dataclass
class Equation:
    tex: str
    label: str | None = None
    number: str = ""
    bookmark: str = ""


# ---------------------------------------------------------------- reading the LaTeX


def braced(s: str, i: int) -> tuple[str, int]:
    """The contents of the {...} group at s[i] (after spaces), and the index after it."""
    while i < len(s) and s[i] in " \t\n":
        i += 1
    if i >= len(s) or s[i] != "{":
        if i < len(s) and s[i] == "\\":
            m = re.match(r"\\([A-Za-z@]+|.)", s[i:], flags=re.S)
            return m.group(0), i + len(m.group(0))
        return (s[i] if i < len(s) else ""), i + 1
    depth, j = 0, i
    while j < len(s):
        c = s[j]
        if c == "\\":
            j += 2
            continue
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return s[i + 1:j], j + 1
        j += 1
    raise ValueError(f"unbalanced braces near: {s[i:i + 80]!r}")


def bracketed(s: str, i: int) -> tuple[str | None, int]:
    """An optional [...] argument at s[i], if there is one."""
    j = i
    while j < len(s) and s[j] in " \t":
        j += 1
    if j >= len(s) or s[j] != "[":
        return None, i
    depth, k = 0, j
    while k < len(s):
        c = s[k]
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
        elif c == "]" and depth == 0:
            return s[j + 1:k], k + 1
        k += 1
    return None, i


def env_body(s: str, i: int, name: str) -> tuple[str, int]:
    """Body of the environment `name` whose \\begin{...} ended at i, honouring nesting."""
    begin, end = f"\\begin{{{name}}}", f"\\end{{{name}}}"
    depth, j = 1, i
    while True:
        a, b = s.find(begin, j), s.find(end, j)
        if b < 0:
            raise ValueError(f"no \\end{{{name}}}")
        if 0 <= a < b:
            depth += 1
            j = a + len(begin)
            continue
        depth -= 1
        if depth == 0:
            return s[i:b], b + len(end)
        j = b + len(end)


def split_top(s: str, sep: str) -> list[str]:
    """Split on `sep` outside braces: '&' between cells, '\\\\' between rows."""
    out, depth, cur, i = [], 0, [], 0
    while i < len(s):
        c = s[i]
        if sep == "\\\\" and depth == 0 and s.startswith("\\\\", i):
            out.append("".join(cur))
            cur = []
            i += 2
            _, i = bracketed(s, i)
            continue
        if c == "\\":
            cur.append(s[i:i + 2])
            i += 2
            continue
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
        if c == sep and depth == 0:
            out.append("".join(cur))
            cur = []
            i += 1
            continue
        cur.append(c)
        i += 1
    out.append("".join(cur))
    return out


def split_items(body: str) -> list[str]:
    """The \\item bodies of a list, ignoring the items of lists nested inside it."""
    items, depth, start = [], 0, None
    for m in re.finditer(r"\\begin\{[^}]+\}|\\end\{[^}]+\}|\\item\b", body):
        tok = m.group(0)
        if tok.startswith("\\begin"):
            depth += 1
        elif tok.startswith("\\end"):
            depth -= 1
        elif depth == 0:
            if start is not None:
                items.append(body[start:m.start()])
            start = m.end()
    if start is not None:
        items.append(body[start:])
    return items


def strip_comments(s: str) -> str:
    return re.sub(r"(?<!\\)%[^\n]*", "", s)


class Source:
    """Expands \\input and keeps verbatim listings away from everything else."""

    def __init__(self):
        self.verbatim: list[str] = []
        self.old_title: set[str] = set()

    def read(self, rel: str) -> str:
        path = SOURCE / (rel if rel.endswith(".tex") else rel + ".tex")
        s = path.read_text(encoding="utf-8")
        s = self._protect(s)
        s = strip_comments(s)
        if OLD_TITLE.search(s):                 # the sources may still carry the working title
            self.old_title.add(path.name)
            s = OLD_TITLE.sub(TITLE, s)
        return re.sub(r"\\input\{([^}]+)\}", lambda m: self.read(m.group(1)), s)

    def _protect(self, s: str) -> str:
        def keep(m):
            self.verbatim.append(m.group(2))
            return f"\\begin{{lstlisting}}{m.group(1) or ''}\\VERBATIM{{{len(self.verbatim) - 1}}}\\end{{lstlisting}}"
        return re.sub(r"\\begin\{lstlisting\}(\[[^\]]*\])?\n?(.*?)\\end\{lstlisting\}", keep, s, flags=re.S)


# ---------------------------------------------------------------- inline text

SYMBOLS = {
    "%": "%", "&": "&", "_": "_", "#": "#", "$": "$", "{": "{", "}": "}", " ": " ",
    ",": "\u202f", ";": " ", ":": " ", "!": "", "-": "", "@": "", "/": "", "\n": " ",
}
WORDS = {
    "ldots": "\u2026", "dots": "\u2026", "textbackslash": "\\", "textendash": "\u2013", "textemdash": "\u2014",
    "quad": "\u2003", "qquad": "\u2003\u2003", "S": "\u00a7", "times": "\u00d7", "cap": "\u2229",
    "cdot": "\u00b7", "setminus": "\u2216", "le": "\u2264", "ge": "\u2265", "leq": "\u2264", "geq": "\u2265",
    "to": "\u2192", "rightarrow": "\u2192", "approx": "\u2248", "pm": "\u00b1", "neq": "\u2260",
    "subseteq": "\u2286", "in": "\u2208", "cup": "\u222a", "infty": "\u221e",
    "textregistered": "\u00ae", "textdegree": "\u00b0", "min": "min", "max": "max",
}
SIZES = {"tiny": 6.0, "scriptsize": 8.0, "footnotesize": 9.0, "small": 10.0, "normalsize": None,
         "large": 14.0, "Large": 16.0, "LARGE": 18.0, "huge": 20.0, "Huge": 24.0}
IGNORE = {"centering", "noindent", "smallskip", "medskip", "bigskip", "sloppy", "fussy", "par", "relax",
          "raggedright", "raggedleft", "hfill", "vfill", "null", "linebreak", "nolinebreak", "clearpage",
          "newpage", "arraybackslash", "protect", "displaystyle", "left", "right", "big", "Big",
          "nobreak", "allowbreak", "strut", "unskip", "xspace", "and", "phantomsection", "begingroup",
          "endgroup", "toprule", "midrule", "bottomrule", "hline"}


@dataclass
class Fmt:
    b: bool = False
    i: bool = False
    mono: bool = False
    sf: bool = False
    sc: bool = False
    size: float | None = None
    sup: bool = False
    sub: bool = False

    def copy(self, **kw) -> "Fmt":
        d = dict(self.__dict__)
        d.update(kw)
        return Fmt(**d)


class Inline:
    def __init__(self, macros: dict[str, str], warn):
        self.macros = macros
        self.warn = warn

    def runs(self, s: str, fmt: Fmt | None = None) -> list[Run]:
        out: list[Run] = []
        self._walk(s, fmt or Fmt(), out)
        return merge_runs(out)

    def plain(self, s: str) -> str:
        return "".join(r.text if r.kind in ("text", "url") else " " for r in self.runs(s))

    def _emit(self, out, text, fmt: Fmt):
        if text:
            out.append(Run(text=text, b=fmt.b, i=fmt.i, mono=fmt.mono, sf=fmt.sf, sc=fmt.sc, size=fmt.size,
                           sup=fmt.sup, sub=fmt.sub))

    def _walk(self, s: str, fmt: Fmt, out: list[Run]):
        i, n = 0, len(s)
        buf: list[str] = []

        def flush():
            if buf:
                self._emit(out, "".join(buf), fmt)
                buf.clear()

        while i < n:
            c = s[i]
            if c == "\\":
                m = re.match(r"\\([A-Za-z@]+)\*?|\\(.)", s[i:], flags=re.S)
                name = m.group(1) or m.group(2)
                i += len(m.group(0))
                if m.group(2) is not None:
                    if name == "\\":
                        flush()
                        _, i = bracketed(s, i)
                        out.append(Run(kind="br"))
                    elif name in SYMBOLS:
                        buf.append(SYMBOLS[name])
                    elif name in "'`^\"~":
                        arg, i = braced(s, i)
                        buf.append(accent(name, arg))
                    else:
                        buf.append(name)
                    continue
                if name in ("textbf", "textit", "emph", "texttt", "textsf", "textsc", "underline", "file",
                            "field", "ruleid", "textsuperscript", "textsubscript", "mathrm", "mathit",
                            "mathbf", "text", "mbox", "textrm", "textnormal", "textup", "url", "nolinkurl"):
                    arg, i = braced(s, i)
                    flush()
                    if name in ("url", "nolinkurl"):
                        out.append(Run(kind="url", key=arg, text=arg))
                        continue
                    sub_fmt = {
                        "textbf": fmt.copy(b=True), "textit": fmt.copy(i=True), "emph": fmt.copy(i=not fmt.i),
                        "texttt": fmt.copy(mono=True), "field": fmt.copy(mono=True),
                        "file": fmt.copy(mono=True),
                        "textsf": fmt.copy(sf=True), "ruleid": fmt.copy(sf=True), "textsc": fmt.copy(sc=True),
                        "textsuperscript": fmt.copy(sup=True), "textsubscript": fmt.copy(sub=True),
                        "mathrm": fmt.copy(i=False), "mathit": fmt.copy(i=True), "mathbf": fmt.copy(b=True),
                    }.get(name, fmt)
                    self._walk(arg, sub_fmt, out)
                    continue
                if name in ("ref", "pageref"):
                    arg, i = braced(s, i)
                    flush()
                    out.append(Run(kind="ref", key=arg, b=fmt.b, i=fmt.i, size=fmt.size))
                    continue
                if name in ("fref", "tref", "sref", "cref", "aref", "eref"):
                    arg, i = braced(s, i)
                    flush()
                    out.append(Run(kind="ref", key=arg, b=fmt.b, i=fmt.i, size=fmt.size, prefix="auto"))
                    continue
                if name in ("cite", "citep", "citet", "citealp"):
                    _, i = bracketed(s, i)
                    arg, i = braced(s, i)
                    flush()
                    out.append(Run(kind="cite", key=arg.replace(" ", ""), b=fmt.b, i=fmt.i, size=fmt.size))
                    continue
                if name == "href":
                    url, i = braced(s, i)
                    arg, i = braced(s, i)
                    flush()
                    out.append(Run(kind="url", key=url, text=self.plain(arg)))
                    continue
                if name == "newline":
                    flush()
                    out.append(Run(kind="br"))
                    continue
                if name == "frac":
                    a, i = braced(s, i)
                    b2, i = braced(s, i)
                    buf.append(f"{self.plain(a)}/{self.plain(b2)}")
                    continue
                if name in ("multicolumn", "multirow"):
                    _, i = braced(s, i)
                    _, i = braced(s, i)
                    arg, i = braced(s, i)
                    flush()
                    self._walk(arg, fmt, out)
                    continue
                if name == "raisebox":
                    _, i = braced(s, i)
                    arg, i = braced(s, i)
                    flush()
                    self._walk(arg, fmt, out)
                    continue
                if name in ("bf", "bfseries"):
                    flush()
                    fmt = fmt.copy(b=True)
                    continue
                if name in ("it", "itshape", "em", "sl", "slshape"):
                    flush()
                    fmt = fmt.copy(i=True)
                    continue
                if name in ("tt", "ttfamily"):
                    flush()
                    fmt = fmt.copy(mono=True)
                    continue
                if name in ("sffamily", "sf"):
                    flush()
                    fmt = fmt.copy(sf=True)
                    continue
                if name == "scshape":
                    flush()
                    fmt = fmt.copy(sc=True)
                    continue
                if name in ("upshape", "normalfont", "rm", "rmfamily", "mdseries"):
                    flush()
                    fmt = fmt.copy(i=False) if name == "upshape" else fmt.copy(b=False, i=False, mono=False)
                    continue
                if name in SIZES:
                    flush()
                    fmt = fmt.copy(size=SIZES[name])
                    continue
                if name in WORDS:
                    buf.append(WORDS[name])
                    continue
                if name in self.macros:
                    buf.append(self.macros[name])
                    if s.startswith("{}", i):
                        i += 2
                    continue
                if name in ("label", "vspace", "hspace", "setstretch", "thispagestyle", "pagestyle"):
                    _, i = bracketed(s, i)
                    _, i = braced(s, i)
                    continue
                if name in ("rowcolor", "cellcolor"):
                    _, i = bracketed(s, i)
                    _, i = braced(s, i)
                    continue
                if name in ("addlinespace", "cline"):
                    _, i = bracketed(s, i)
                    if name == "cline":
                        _, i = braced(s, i)
                    continue
                if name in IGNORE:
                    continue
                if name == "dotfill":
                    flush()
                    out.append(Run(kind="tab"))
                    continue
                self.warn(f"inline: unknown \\{name}")
                continue
            if c == "{":
                arg, i = braced(s, i)
                flush()
                self._walk(arg, fmt, out)
                continue
            if c == "}":
                i += 1
                continue
            if c == "$":
                j = s.index("$", i + 1)
                flush()
                self._math(s[i + 1:j], fmt, out)
                i = j + 1
                continue
            if c == "~":
                buf.append("\u00a0")
                i += 1
                continue
            if c == "`":
                if s.startswith("``", i):
                    buf.append("\u201c")
                    i += 2
                else:
                    buf.append("\u2018")
                    i += 1
                continue
            if c == "'":
                if s.startswith("''", i):
                    buf.append("\u201d")
                    i += 2
                else:
                    buf.append("\u2019")
                    i += 1
                continue
            if c == "-":
                if s.startswith("---", i):
                    buf.append("\u2014")
                    i += 3
                elif s.startswith("--", i):
                    buf.append("\u2013")
                    i += 2
                else:
                    buf.append("-")
                    i += 1
                continue
            if c in "\n\t\r":
                buf.append(" ")
                i += 1
                continue
            if c == '"':
                prev = buf[-1][-1:] if buf else (out[-1].text[-1:] if out and out[-1].kind == "text" else "")
                buf.append("“" if prev in ("", " ", "(", "[", " ") else "”")
                i += 1
                continue
            buf.append(c)
            i += 1
        flush()

    def _math(self, s: str, fmt: Fmt, out: list[Run]):
        """Inline maths as text: letters italic, operators upright, _ and ^ as sub- and superscripts."""
        i, n = 0, len(s)
        while i < n:
            c = s[i]
            if c == "\\":
                m = re.match(r"\\([A-Za-z]+|.)", s[i:])
                name = m.group(1)
                i += len(m.group(0))
                if name in ("mathrm", "text", "textrm", "mathit"):
                    arg, i = braced(s, i)
                    self._emit(out, self.plain(arg), fmt.copy(i=name == "mathit"))
                elif name in WORDS:
                    self._emit(out, WORDS[name], fmt.copy(i=False))
                elif name in SYMBOLS:
                    self._emit(out, SYMBOLS[name], fmt.copy(i=False))
                elif name == "frac":
                    a, i = braced(s, i)
                    b2, i = braced(s, i)
                    self._emit(out, f"{self.plain(a)}/{self.plain(b2)}", fmt)
                elif name in IGNORE:
                    pass
                else:
                    self.warn(f"math: unknown \\{name}")
                continue
            if c in "_^":
                arg, i = braced(s, i + 1)
                self._math(arg, fmt.copy(sub=c == "_", sup=c == "^"), out)
                continue
            if c in "{}":
                i += 1
                continue
            if c.isalpha():
                self._emit(out, c, fmt.copy(i=True))
            elif c == "-":
                self._emit(out, "\u2212", fmt.copy(i=False))
            elif c != " ":
                self._emit(out, c, fmt.copy(i=False))
            i += 1


def accent(mark: str, letter: str) -> str:
    table = {('"', "u"): "\u00fc", ('"', "a"): "\u00e4", ('"', "o"): "\u00f6", ("'", "e"): "\u00e9",
             ("`", "e"): "\u00e8", ("^", "o"): "\u00f4", ("~", "n"): "\u00f1", ('"', "U"): "\u00dc"}
    letter = letter.strip("{}")
    if not letter:                     # \^{} and \~{} print the mark itself
        return mark
    return table.get((mark, letter), letter)


def same_fmt(a: Run, b: Run) -> bool:
    return (a.b, a.i, a.mono, a.sf, a.sc, a.size, a.sup, a.sub) == (b.b, b.i, b.mono, b.sf, b.sc, b.size, b.sup, b.sub)


def merge_runs(runs: list[Run]) -> list[Run]:
    out: list[Run] = []
    for r in runs:
        if out and r.kind == "text" and out[-1].kind == "text" and same_fmt(r, out[-1]):
            out[-1].text += r.text
        else:
            out.append(r)
    for r in out:
        if r.kind == "text":
            r.text = re.sub(r" {2,}", " ", r.text)
    # no space after a line break, none at either end
    for k in range(1, len(out)):
        if out[k].kind == "text" and out[k - 1].kind == "br":
            out[k].text = out[k].text.lstrip(" ")
        if out[k].kind == "br" and out[k - 1].kind == "text":
            out[k - 1].text = out[k - 1].text.rstrip(" ")
    while out and out[0].kind == "text" and not out[0].text.strip(" "):
        out.pop(0)
    if out and out[0].kind == "text":
        out[0].text = out[0].text.lstrip(" ")
    while out and out[-1].kind in ("text", "br") and not out[-1].text.strip(" "):
        out.pop()
    if out and out[-1].kind == "text":
        out[-1].text = out[-1].text.rstrip(" ")
    return [r for r in out if r.kind != "text" or r.text]


# ---------------------------------------------------------------- blocks


class Reader:
    """Turns chapter LaTeX into blocks. Numbering happens later, over the whole document."""

    def __init__(self, src: Source, inline: Inline, figures: "FigureMaker", warn):
        self.src, self.inline, self.figures, self.warn = src, inline, figures, warn
        self.appx = 0

    def blocks(self, s: str) -> list:
        out: list = []
        para: list[str] = []
        size = {"v": None}

        def flush():
            text = "".join(para).strip()
            para.clear()
            if text:
                runs = self.inline.runs(text)
                if runs:
                    out.append(Para(runs=runs, size=size["v"]))

        i, n = 0, len(s)
        while i < n:
            if s[i] == "\n":
                m = re.match(r"\n[ \t]*\n", s[i:])
                if m:
                    flush()
                    i += m.end() - 1
                    continue
            if s[i] != "\\":
                para.append(s[i])
                i += 1
                continue
            m = re.match(r"\\([A-Za-z@]+)(\*?)", s[i:])
            if not m:
                para.append(s[i:i + 2])
                i += 2
                continue
            name, star = m.group(1), m.group(2)
            j = i + len(m.group(0))
            if name in ("chapter", "section", "subsection", "subsubsection"):
                flush()
                _, j = bracketed(s, j)
                title, j = braced(s, j)
                level = {"chapter": 1, "section": 2, "subsection": 3, "subsubsection": 3}[name]
                out.append(Heading(level=level, runs=self.inline.runs(title), numbered=not star))
                i = j
                continue
            if name == "appendixpart":
                flush()
                title, j = braced(s, j)
                label, j = braced(s, j)
                self.appx += 1
                runs = [Run(text=f"Appendix {self.appx}: ")] + self.inline.runs(title)
                out.append(Heading(level=2, runs=runs, numbered=False, label=label, ref_number=str(self.appx)))
                i = j
                continue
            if name == "makeatletter":
                end = s.find("\\makeatother", j)
                i = len(s) if end < 0 else end + len("\\makeatother")
                continue
            if name in ("markboth", "setcounter", "renewcommand", "setlength", "setlist"):
                flush()
                _, j = bracketed(s, j)
                _, j = braced(s, j)
                _, j = braced(s, j)
                i = j
                continue
            if name == "paragraph":
                flush()
                title, j = braced(s, j)
                para.append(f"\\textbf{{{title}}} ")
                i = j
                continue
            if name == "label":
                arg, j = braced(s, j)
                target = next((b for b in reversed(out) if isinstance(b, Heading)), None)
                if target is not None and target.label is None and not "".join(para).strip():
                    target.label = arg
                else:
                    self.warn(f"label {arg} has nothing to attach to")
                i = j
                continue
            if name == "begin":
                env, j = braced(s, j)
                flush()
                body, j = env_body(s, j, env)
                found = self.environment(env, body)
                for x in found:
                    if isinstance(x, ListBlock) and size["v"]:
                        mark_compact(x)
                    if isinstance(x, Table) and env in ("tabular", "tabularx", "longtable", "xltabular"):
                        x.size = size["v"] or 11.0          # a table outside a float is set at text size
                out.extend(found)
                i = j
                continue
            if name == "lstinputlisting":
                flush()
                opts, j = bracketed(s, j)
                path, j = braced(s, j)
                out.append(self.listing_file(opts or "", path))
                i = j
                continue
            if name == "appendix":
                flush()
                out.append("APPENDIX")
                i = j
                continue
            if name == "addcontentsline":
                for _ in range(3):
                    _, j = braced(s, j)
                i = j
                continue
            if name == "par":
                flush()
                i = j
                continue
            if name in ("footnotesize", "small", "scriptsize") and not "".join(para).strip():
                size["v"] = SIZES[name]
                i = j
                continue
            if name in ("setstretch", "thispagestyle", "vspace", "definecolor"):
                flush()
                if name == "definecolor":
                    _, j = braced(s, j)
                    _, j = braced(s, j)
                _, j = braced(s, j)
                i = j
                continue
            if name in ("begingroup", "endgroup", "centering", "sloppy", "fussy", "clearpage", "medskip",
                        "smallskip", "bigskip", "phantomsection", "newpage", "noindent"):
                i = j
                continue
            para.append(m.group(0))
            i = j
        flush()
        return out

    def environment(self, env: str, body: str) -> list:
        if env in ("figure", "figure*", "table", "table*"):
            body = re.sub(r"^\s*\[[^\]]*\]", "", body)        # the float placement, [htbp]
        if env in ("itemize", "enumerate"):
            _, k = bracketed(body, 0)
            items = split_items(body[k:])
            blocks = []
            for item in items:
                _, k = bracketed(item, 0)
                blocks.append(self.blocks(item[k:]))
            return [ListBlock(ordered=env == "enumerate", items=blocks)]
        if env in ("table", "table*"):
            return [self.table_float(body)]
        if env in ("figure", "figure*"):
            if body.count("\\caption") > 1:
                return [self.figure(part) for part in re.split(r"\\bigskip", body) if "\\caption" in part]
            return [self.figure(body)]
        if env in ("tabularx", "tabular", "longtable", "xltabular"):
            return [self.tabular(env, body)]
        if env == "lstlisting":
            return [self.listing(body)]
        if env == "equation":
            m = re.search(r"\\label\{([^}]+)\}", body)
            tex = re.sub(r"\\label\{[^}]+\}", "", body).strip()
            return [Equation(tex=tex, label=m.group(1) if m else None)]
        if env == "acronym":
            return [self.acronyms(body)]
        if env in ("center", "flushleft", "flushright", "minipage"):
            if env == "minipage":
                _, k = bracketed(body, 0)
                _, k = braced(body, k)
                body = body[k:]
            inner = self.blocks(body)
            for b in inner:
                if isinstance(b, Para):
                    b.align = {"center": "center", "flushright": "right"}.get(env, b.align)
            return inner
        self.warn(f"environment {env} not handled")
        return []

    # -- tables
    def table_float(self, body: str) -> Table:
        head = body.split("\\begin{tabular")[0]
        size = next((pts for name, pts in SIZES.items() if pts and re.search(rf"\\{name}\b", head)), 9.0)
        short, cap, label = self.caption(body)
        m = re.search(r"\\begin\{(tabularx|tabular)\}", body)
        tbody, end = env_body(body, m.end(), m.group(1))
        table = self.tabular(m.group(1), tbody)
        table.caption, table.short, table.label, table.size = cap, short, label, size
        for b in self.blocks(body[end:]):
            if isinstance(b, Para):
                b.style, b.size = "Note", b.size or 9.0
                table.notes.append(b)
        return table

    def caption(self, body: str):
        m = re.search(r"\\caption", body)
        if not m:
            return None, None, None
        short, k = bracketed(body, m.end())
        cap, k = braced(body, k)
        lab = re.search(r"\\label\{([^}]+)\}", body)
        return (self.inline.runs(short) if short else None, self.inline.runs(cap),
                lab.group(1) if lab else None)

    def colspec(self, spec: str) -> tuple[list[tuple[str, float | None]], list[bool]]:
        """[(kind, width_cm)] with kind w?/X?/l/c/r (? = l c r alignment); bars before each column."""
        spec = re.sub(r"@\{[^}]*\}", "", spec)
        spec = re.sub(r"\*\{(\d+)\}\{((?:[^{}]|\{(?:[^{}]|\{[^{}]*\})*\})*)\}",
                      lambda m: m.group(2) * int(m.group(1)), spec)
        cols: list[tuple[str, float | None]] = []
        bars: list[bool] = [False]
        i, pending = 0, None
        while i < len(spec):
            c = spec[i]
            if c == "|":
                bars[-1] = True
                i += 1
                continue
            if c == ">":
                arg, i = braced(spec, i + 1)
                pending = "c" if "centering" in arg else ("r" if "raggedleft" in arg else "l")
                continue
            if c in "pmbCL":
                arg, j = braced(spec, i + 1)
                kind = {"C": "c", "L": "l"}.get(c, pending or "l")
                cols.append(("w" + kind, cm_of(arg)))
                bars.append(False)
                pending = None
                i = j
                continue
            if c in "XY":
                cols.append(("X" + (pending or "l"), None))
                bars.append(False)
                pending = None
                i += 1
                continue
            if c in "lcr":
                cols.append((c, None))
                bars.append(False)
                i += 1
                continue
            i += 1
        return cols, bars

    def tabular(self, env: str, body: str) -> Table:
        k = 0
        if env in ("tabularx", "xltabular"):
            _, k = braced(body, 0)
        _, k = bracketed(body, k)
        spec, k = braced(body, k)
        rows_src = body[k:]
        cols, bars = self.colspec(spec)
        short, cap, label = None, None, None
        if env in ("longtable", "xltabular"):
            if "\\caption" in rows_src.split("\\endfirsthead")[0]:
                short, cap, label = self.caption(rows_src)
                rows_src = re.sub(r"\\caption(\[[^\]]*\])?\{(?:[^{}]|\{[^{}]*\})*\}\s*(\\label\{[^}]+\})?\s*\\\\",
                                  "", rows_src, count=1)
            if "\\endfirsthead" in rows_src:
                first, rest = rows_src.split("\\endfirsthead", 1)
                if "\\endhead" in rest:
                    rest = rest.split("\\endhead", 1)[1]
                if "\\endfoot" in rest:
                    rest = rest.split("\\endfoot", 1)[1]
                lastfoot = ""
                if "\\endlastfoot" in rest:
                    lastfoot, rest = rest.split("\\endlastfoot", 1)
                rows_src = first + "\\HEADEND" + rest + lastfoot
        table = self.rows(rows_src, cols, bars)
        table.caption, table.short, table.label = cap, short, label
        table.long = env in ("longtable", "xltabular")
        return table

    def rows(self, src: str, cols, bars) -> Table:
        widths = self.widths(cols, src)
        aligns = [{"c": "center", "r": "right"}.get(kind[-1], "left") for kind, _ in cols]
        rows: list[Row] = []
        pending_top, pending_shade, header_done = None, None, False
        rule = re.compile(r"\\(toprule|midrule|bottomrule|hline|cline\{(\d+)-(\d+)\}|HEADEND|"
                          r"addlinespace(?:\[[^\]]*\])?|rowcolor(?:\[[^\]]*\])?\{[^}]*\}|endfirsthead|endhead|"
                          r"endfoot|endlastfoot)")
        for chunk in split_top(src, "\\\\"):
            text = chunk
            while True:
                text = text.lstrip()
                m = rule.match(text)
                if not m:
                    break
                tok = m.group(1)
                if tok.startswith("cline"):
                    if rows:
                        rows[-1].cline.append((int(m.group(2)), int(m.group(3))))
                elif tok == "HEADEND":
                    for r in rows:
                        r.header = True
                    header_done = True
                elif tok.startswith("rowcolor"):
                    pending_shade = "C0C0C0"
                elif tok.startswith("addlinespace") or tok.startswith("end"):
                    pass
                else:
                    weight = "thick" if tok in ("toprule", "bottomrule") else "thin"
                    if tok == "midrule" and not header_done and rows:
                        for r in rows:
                            r.header = True
                        header_done = True
                    if rows:
                        rows[-1].bottom = rows[-1].bottom or weight
                    else:
                        pending_top = weight
                text = text[m.end():]
            if not text.strip():
                continue
            cells: list[Cell] = []
            col = 0
            for c in split_top(text, "&"):
                c = c.strip()
                span, align = 1, None
                mm = re.match(r"\\multicolumn\{(\d+)\}\{([^}]*)\}", c)
                if mm:
                    span = int(mm.group(1))
                    align = {"c": "center", "r": "right"}.get(mm.group(2).strip("|")[:1], "left")
                vmerge = "restart" if c.startswith("\\multirow") else None
                cells.append(Cell(runs=self.inline.runs(c), span=span, vmerge=vmerge,
                                  align=align or (aligns[col] if col < len(aligns) else "left")))
                col += span
            rows.append(Row(cells=cells, top=pending_top, shade=pending_shade))
            pending_top, pending_shade = None, None
        # cells under a \multirow are empty in the source: continue the merge
        for ri, row in enumerate(rows):
            for ci, cell in enumerate(row.cells):
                if cell.vmerge == "restart":
                    k = ri + 1
                    while k < len(rows) and ci < len(rows[k].cells) and not rows[k].cells[ci].runs:
                        rows[k].cells[ci].vmerge = "continue"
                        k += 1
        return Table(widths=widths, aligns=aligns, vbars=bars, rows=rows)

    def widths(self, cols, src: str) -> list[int]:
        # p{w} is the text width of a column; LaTeX adds \tabcolsep (6 pt) either side
        scale = TEXT_W / (LATEX_TEXTWIDTH_CM * CM)
        fixed: list[int | None] = [int((w + 0.42) * CM * scale) if w else None for _, w in cols]
        flex = [i for i, (kind, _) in enumerate(cols) if kind.startswith("X")]
        natural = [i for i, (kind, w) in enumerate(cols) if not kind.startswith("X") and w is None]
        if natural:
            longest = {i: 4 for i in natural}
            for chunk in split_top(src.replace("\\HEADEND", ""), "\\\\"):
                for ci, c in enumerate(split_top(chunk, "&")):
                    if ci in longest and "\\multicolumn" not in c and "\\caption" not in c:
                        longest[ci] = max(longest[ci], len(self.inline.plain(c)))
            for i in natural:
                fixed[i] = int(min(longest[i] * 110 + 240, TEXT_W * 0.5))
        used = sum(w for w in fixed if w)
        if flex:
            each = max(int((TEXT_W - used) / len(flex)), 900)
            for i in flex:
                fixed[i] = each
        total = sum(fixed)
        if total > TEXT_W or flex:
            fixed = [int(w * TEXT_W / total) for w in fixed]
        return fixed

    # -- figures and listings
    def figure(self, body: str) -> Figure:
        short, cap, label = self.caption(body)
        fig = Figure(rows=[], caption=cap, short=short, label=label)
        if "\\begin{tikzpicture}" in body:
            # everything before the caption: a table read with \pgfplotstableread, then the picture
            code = re.sub(r"\\centering\b", "", body.split("\\caption")[0])
            fig.rows = [[self.figures.tikz(code.strip(), label)]]
            return fig
        if "\\begin{lstlisting}" in body:
            m = re.search(r"\\begin\{lstlisting\}", body)
            inner, _ = env_body(body, m.end(), "lstlisting")
            fig.code = self.listing(inner)
            return fig
        rows: list[list[Image_]] = [[]]
        for m in re.finditer(r"\\includegraphics(\[[^\]]*\])?\{([^}]+)\}(\s*\\\\(\[[^\]]*\])?)?", body):
            rows[-1].append(self.figures.image(m.group(2), (m.group(1) or "")[1:-1]))
            if m.group(3):
                rows.append([])
        fig.rows = [r for r in rows if r]
        return fig

    def listing(self, body: str) -> Code:
        opts, _ = bracketed(body, 0)
        m = re.search(r"\\VERBATIM\{(\d+)\}", body)
        text = self.src.verbatim[int(m.group(1))]
        numbered = "style=py" in (opts or "") and "numbers=none" not in (opts or "")
        return Code(lines=text.rstrip("\n").split("\n"), numbered=numbered)

    def listing_file(self, opts: str, path: str) -> Code:
        src = ROOT / build_thesis.CODE[Path(path).name]
        cap = re.search(r"caption=\{((?:[^{}]|\{[^{}]*\})*)\}", opts)
        text = build_thesis.code_only(src.read_text(encoding="utf-8"))
        return Code(lines=text.rstrip("\n").split("\n"),
                    numbered="numbers=none" not in opts, caption=self.inline.runs(cap.group(1)) if cap else None)

    def acronyms(self, body: str) -> Table:
        rows = [Row(cells=[Cell(runs=[Run(text="Acronym", b=True)]), Cell(runs=[Run(text="Full form", b=True)])],
                    header=True, top="thick", bottom="thin")]
        for m in re.finditer(r"\\acro\{([^}]+)\}\s*\{((?:[^{}]|\{[^{}]*\})*)\}", body):
            rows.append(Row(cells=[Cell(runs=[Run(text=m.group(1), b=True)]),
                                   Cell(runs=self.inline.runs(m.group(2)))]))
        rows[-1].bottom = "thick"
        return Table(widths=[int(TEXT_W * 0.2), TEXT_W - int(TEXT_W * 0.2)], aligns=["left", "left"],
                     vbars=[False] * 3, rows=rows, size=11.0)


def cm_of(arg: str) -> float:
    m = re.match(r"\s*([\d.]+)\s*(cm|mm|in|pt)", arg)
    if m:
        v = float(m.group(1))
        return {"cm": v, "mm": v / 10, "in": v * 2.54, "pt": v / 28.45}[m.group(2)]
    m = re.match(r"\s*([\d.]*)\s*\\(textwidth|linewidth)", arg)
    if m:
        return float(m.group(1) or 1) * LATEX_TEXTWIDTH_CM
    return 3.0


# ---------------------------------------------------------------- figures


class FigureMaker:
    """Photographs placed as they are; TikZ and pgfplots compiled one by one and rendered at 300 dpi."""

    def __init__(self, macros_tex: str):
        self.macros_tex = macros_tex
        (WORK / "fig").mkdir(parents=True, exist_ok=True)
        self.n = 0

    def image(self, name: str, opts: str) -> Image_:
        src = SOURCE / "figures" / (name if Path(name).suffix else name + ".png")
        width = re.search(r"width=([\d.]*)\\(textwidth|linewidth)", opts)
        frac = float(width.group(1) or 1) if width else 1.0
        trim = re.search(r"trim=([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)", opts)
        path = src
        if trim and "clip" in opts:
            left, bottom, right, top = (float(x) for x in trim.groups())
            im = Image.open(src)
            k = (im.info.get("dpi") or (72, 72))[0] / 72.0
            path = WORK / "fig" / f"{src.stem}-trim.png"
            im.crop((int(left * k), int(top * k), im.width - int(right * k), im.height - int(bottom * k))).save(path)
        return Image_(path=path, width_twips=int(TEXT_W * frac))

    def tikz(self, code: str, label: str | None) -> Image_:
        self.n += 1
        stem = (label or f"tikz{self.n}").replace(":", "-")
        tex = WORK / "fig" / f"{stem}.tex"
        png = tex.with_suffix(".png")
        doc = ("\\documentclass[border=2pt]{standalone}\n"
               "\\usepackage{amsmath,amssymb}\\usepackage{newtxtext}\\usepackage{newtxmath}\n"
               "\\usepackage{array}\\usepackage{xcolor}\\usepackage{tikz}\\usepackage{pgfplots}\n"
               "\\usetikzlibrary{positioning, arrows.meta, calc, fit, backgrounds, shapes.geometric, patterns}\n"
               "\\usepackage{pgfplotstable}\\pgfplotsset{compat=1.18}\\usepackage{listings}\n"
               f"\\setlength{{\\textwidth}}{{{LATEX_TEXTWIDTH_CM}cm}}\\setlength{{\\linewidth}}{{\\textwidth}}\n"
               f"{self.macros_tex}\n"
               "\\begin{document}\n\\footnotesize\n" + code + "\n\\end{document}\n")
        if not (png.exists() and tex.exists() and tex.read_text(encoding="utf-8") == doc):
            tex.write_text(doc, encoding="utf-8")
            engine = build_thesis.tectonic()
            if engine is None:
                sys.exit("Tectonic is needed to draw the TikZ figures (set TECTONIC).")
            proc = subprocess.run([engine, "-X", "compile", tex.name], cwd=tex.parent, capture_output=True,
                                  text=True, encoding="utf-8", errors="replace")
            if proc.returncode != 0:
                print(proc.stdout[-3000:], proc.stderr[-3000:])
                sys.exit(f"Tectonic could not draw {tex.name}")
            render_pdf(tex.with_suffix(".pdf"), png, dpi=300)
        im = Image.open(png)
        width_cm = im.width / 300 * 2.54
        return Image_(path=png, width_twips=min(int(width_cm * CM * TEXT_W / (LATEX_TEXTWIDTH_CM * CM)), TEXT_W))


def render_pdf(pdf: Path, png: Path, dpi: int = 300) -> None:
    """First page of a PDF to a PNG with the Windows PDF renderer, trimmed of its white margin."""
    from pypdf import PdfReader
    width_pt = float(PdfReader(str(pdf)).pages[0].mediabox.width)
    outdir = png.parent / (png.stem + "-pages")
    subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File",
                    str(HERE / "render_pdf_page.ps1"), "-Pdf", str(pdf), "-OutDir", str(outdir), "-Pages", "1",
                    "-Width", str(int(width_pt / 72 * dpi))], check=True, capture_output=True)
    im = Image.open(outdir / "page-001.png").convert("RGB")
    shutil.rmtree(outdir, ignore_errors=True)
    box = ImageChops.difference(im, Image.new("RGB", im.size, (255, 255, 255))).getbbox()
    if box:
        pad = 6
        im = im.crop((max(box[0] - pad, 0), max(box[1] - pad, 0), min(box[2] + pad, im.width),
                      min(box[3] + pad, im.height)))
    im.save(png, dpi=(dpi, dpi))


# ---------------------------------------------------------------- numbering and citations


class Numberer:
    def __init__(self):
        self.labels: dict[str, tuple[str, str, str]] = {}    # label -> (kind, number, bookmark)
        self.toc: list[tuple[int, str, str, str]] = []       # (level, number, text, bookmark)
        self.lof: list[tuple[str, list[Run], str]] = []
        self.lot: list[tuple[str, list[Run], str]] = []
        self.cites: list[str] = []
        self.n_bm = 0
        self.chapter, self.section, self.sub = 0, 0, 0
        self.appendix = False
        self.counters = {"fig": 0, "tab": 0, "eq": 0, "lst": 0}

    def bookmark(self) -> str:
        self.n_bm += 1
        return f"_Ref{self.n_bm:05d}"

    def cur(self) -> str:
        return chr(64 + self.chapter) if self.appendix else str(self.chapter)

    def walk(self, blocks: list, *, numbered_floats: bool = True):
        for b in flatten(blocks):
            if b == "APPENDIX":
                self.appendix, self.chapter = True, 0
                continue
            if isinstance(b, Heading):
                b.bookmark = self.bookmark()
                if b.level == 1:
                    if b.numbered:
                        self.chapter += 1
                        b.number = self.cur()
                    elif self.appendix:
                        self.chapter += 1          # the Appendix: floats inside it are numbered A.n
                    self.section = self.sub = 0
                    self.counters = {k: 0 for k in self.counters}
                    kind = "appendix" if self.appendix else "chapter"
                elif b.level == 2:
                    self.section += 1
                    self.sub = 0
                    b.number = f"{self.cur()}.{self.section}" if b.numbered else ""
                    kind = "section"
                else:
                    self.sub += 1
                    b.number = f"{self.cur()}.{self.section}.{self.sub}" if b.numbered else ""
                    kind = "section"
                if b.ref_number:
                    kind = "appendix"
                if b.label:
                    self.labels[b.label] = (kind, b.ref_number or b.number, b.bookmark)
                if b.level < 3 or b.numbered:       # an unnumbered sub-heading stays out of the contents
                    self.toc.append((b.level, b.number, plain(b.runs), b.bookmark))
            elif isinstance(b, (Table, Figure, Equation, Code)) and numbered_floats:
                if isinstance(b, Code) and b.caption is None:
                    continue
                if isinstance(b, Table) and b.caption is None:
                    continue
                key = {Table: "tab", Figure: "fig", Equation: "eq", Code: "lst"}[type(b)]
                self.counters[key] += 1
                b.number = f"{self.cur()}.{self.counters[key]}"
                b.bookmark = self.bookmark()
                if b.label:
                    self.labels[b.label] = (key, b.number, b.bookmark)
                if isinstance(b, Table):
                    self.lot.append((b.number, b.short or b.caption, b.bookmark))
                if isinstance(b, Figure) and b.caption:
                    self.lof.append((b.number, b.short or b.caption, b.bookmark))
            for r in runs_of(b):
                if r.kind == "cite":
                    for k in r.key.split(","):
                        if k not in self.cites:
                            self.cites.append(k)


def mark_compact(b: "ListBlock") -> None:
    b.compact = True
    for item in b.items:
        for blk in item:
            if isinstance(blk, ListBlock):
                mark_compact(blk)


def flatten(blocks):
    for b in blocks:
        yield b
        if isinstance(b, ListBlock):
            for item in b.items:
                yield from flatten(item)


def runs_of(b) -> list[Run]:
    if isinstance(b, (Para, Heading)):
        return b.runs
    if isinstance(b, Table):
        out = list(b.caption or [])
        for row in b.rows:
            for c in row.cells:
                out += c.runs
        for p in b.notes:
            out += p.runs
        return out
    if isinstance(b, (Figure, Code)):
        return list(b.caption or [])
    return []


def plain(runs: list[Run]) -> str:
    return "".join(r.text if r.kind in ("text", "url") else " " for r in runs).strip()


# ---------------------------------------------------------------- the bibliography (IEEEtran's order and form)

MONTHS = {"jan": "Jan.", "feb": "Feb.", "mar": "Mar.", "apr": "Apr.", "may": "May", "jun": "Jun.", "jul": "Jul.",
          "aug": "Aug.", "sep": "Sep.", "oct": "Oct.", "nov": "Nov.", "dec": "Dec."}


def read_bib(path: Path) -> dict[str, dict[str, str]]:
    s = strip_comments(path.read_text(encoding="utf-8"))
    out: dict[str, dict[str, str]] = {}
    for m in re.finditer(r"@(\w+)\s*\{\s*([^,\s]+)\s*,", s):
        body, _ = braced(s, s.index("{", m.start()))
        fields: dict[str, str] = {"_type": m.group(1).lower()}
        i = body.index(",") + 1
        while i < len(body):
            fm = re.match(r"\s*(\w+)\s*=\s*", body[i:])
            if not fm:
                break
            name = fm.group(1).lower()
            i += fm.end()
            if body[i] == "{":
                val, i = braced(body, i)
            else:
                vm = re.match(r"[^,]+", body[i:])
                val = vm.group(0).strip()
                i += vm.end()
            fields[name] = val.strip()
            cm = re.match(r"\s*,", body[i:])
            i += cm.end() if cm else 0
        out[m.group(2)] = fields
    return out


def sentence_case(title: str) -> str:
    """BibTeX's change.case "t": the first letter, a letter after a colon and braced groups keep their
    case; every other letter is lower-cased."""
    out, depth, keep = [], 0, True
    k = 0
    while k < len(title):
        c = title[k]
        if c == "\\":                               # a control sequence passes through untouched
            m = re.match(r"\\([A-Za-z]+|.)", title[k:])
            out.append(m.group(0))
            k += len(m.group(0))
            continue
        if c in "{}":
            depth += 1 if c == "{" else -1
            out.append(c)
            keep = False
            k += 1
            continue
        if depth > 0 or not c.isalpha():
            out.append(c)
            if c == ":" and depth == 0:
                keep = True
            elif c.isalpha():
                keep = False
        else:
            out.append(c if keep else c.lower())
            keep = False
        k += 1
    return "".join(out)


def bib_entry(e: dict[str, str], inline: Inline) -> list[Run]:
    """One entry in IEEEtran's form, written as LaTeX and read once so the spacing survives."""
    def authors(s: str) -> str:
        names = [a.strip() for a in re.split(r"\s+and\s+", s)]
        etal = bool(names) and names[-1] == "others"
        names = [n for n in names if n != "others"]
        if etal:
            return f"{names[0]} \\emph{{et~al.}}"
        if len(names) <= 2:
            return " and ".join(names)
        return ", ".join(names[:-1]) + ", and " + names[-1]

    t = e["_type"]
    head = authors(e["author"]) + ", " if e.get("author") else ""
    title, pages, year = e.get("title", ""), e.get("pages", ""), e.get("year", "")
    pp = (f"pp.~{pages}" if "--" in pages else f"p.~{pages}") if pages else ""
    when = f"{MONTHS.get(e.get('month', '').lower(), '')} {year}".strip()
    if t == "book":
        ed = f", {e['edition']} ed." if e.get("edition") else "."
        place, pub = e.get("address", ""), e.get("publisher", "")
        s = f"{head}\\textit{{{title}}}{ed} " + (f"{place}: {pub}, {year}." if place else f"{pub}, {year}.")
        return inline.runs(s)
    s = head + "``" + sentence_case(title) + ",'' "
    if t == "article":
        rest = [x for x in (f"vol.~{e['volume']}" if e.get("volume") else "",
                            f"no.~{e['number']}" if e.get("number") else "", pp, when) if x]
        s += f"\\textit{{{e.get('journal', '')}}}, " + ", ".join(rest) + "."
    elif t == "inproceedings":
        s += f"in \\textit{{{e.get('booktitle', '')}}}"
        if e.get("series"):
            s += f", ser. {e['series']}" + (f", vol.~{e['volume']}" if e.get("volume") else "") + ". "
            s += ", ".join(x for x in (e.get("publisher", ""), when, pp) if x) + "."
        else:
            s += ", " + ", ".join(x for x in (e.get("address", ""), when, pp) if x) + "."
    else:
        s += ", ".join(x for x in (e.get("howpublished", ""), when) if x) + "."
    return inline.runs(s)


# ---------------------------------------------------------------- OOXML writing


def esc(s: str) -> str:
    return html.escape(s, quote=True)


class Writer:
    def __init__(self, num: Numberer, bib_numbers: dict[str, int]):
        self.num = num
        self.bib = bib_numbers
        self.images: list[Path] = []
        self.urls: list[str] = []
        self.ordered: list[int] = []
        self.docpr = 0
        self.bm_id = 0

    # -- runs
    def rpr(self, r: Run, base: dict | None = None) -> str:
        base = base or {}
        p = []
        if r.mono:
            p.append('<w:rFonts w:ascii="Courier New" w:hAnsi="Courier New" w:cs="Courier New"/>')
        elif r.sf:
            p.append('<w:rFonts w:ascii="Arial" w:hAnsi="Arial" w:cs="Arial"/>')
        if r.b or base.get("b"):
            p.append("<w:b/><w:bCs/>")
        if r.i or base.get("i"):
            p.append("<w:i/><w:iCs/>")
        if r.sc:
            p.append("<w:smallCaps/>")
        if base.get("color"):
            p.append(f'<w:color w:val="{base["color"]}"/>')
        size = r.size or base.get("size")
        if (r.sf or r.mono) and not r.size:
            size = (size or 12) - 1
        if size:
            hp = int(round(size * 2))
            p.append(f'<w:sz w:val="{hp}"/><w:szCs w:val="{hp}"/>')
        if r.sup:
            p.append('<w:vertAlign w:val="superscript"/>')
        if r.sub:
            p.append('<w:vertAlign w:val="subscript"/>')
        return f"<w:rPr>{''.join(p)}</w:rPr>" if p else ""

    def text_run(self, text: str, rpr: str = "") -> str:
        xml = []
        for k, part in enumerate(text.split("\t")):
            if k:
                xml.append(f"<w:r>{rpr}<w:tab/></w:r>")
            if part:
                xml.append(f'<w:r>{rpr}<w:t xml:space="preserve">{esc(part)}</w:t></w:r>')
        return "".join(xml)

    def runs(self, runs: list[Run], base: dict | None = None) -> str:
        base = base or {}
        link = dict(base, color=LINK_COLOR)
        xml = []
        for r in runs:
            if r.kind == "text":
                xml.append(self.text_run(r.text, self.rpr(r, base)))
            elif r.kind == "br":
                xml.append("<w:r><w:br/></w:r>")
            elif r.kind == "tab":
                xml.append(f"<w:r>{self.rpr(r, base)}<w:tab/></w:r>")
            elif r.kind == "url":
                if r.key not in self.urls:
                    self.urls.append(r.key)
                xml.append(f'<w:hyperlink w:history="1" r:id="rIdUrl{self.urls.index(r.key) + 1}">'
                           + self.text_run(r.text, self.rpr(Run(), link)) + "</w:hyperlink>")
            elif r.kind == "ref":
                kind, number, bm = self.num.labels.get(r.key, ("?", "??", ""))
                if r.prefix == "auto":
                    word = {"fig": "Figure", "tab": "Table", "eq": "Equation", "lst": "Listing",
                            "chapter": "Chapter", "appendix": "Appendix", "section": "Section"}.get(kind, "")
                    xml.append(self.text_run(word + "\u00a0", self.rpr(r, base)))
                    if kind == "eq":
                        number = f"({number})"
                xml.append(f'<w:hyperlink w:anchor="{bm}" w:history="1">{self.text_run(number, self.rpr(r, link))}'
                           f'</w:hyperlink>' if bm else self.text_run(number, self.rpr(r, base)))
            elif r.kind == "cite":
                nums = sorted(self.bib[k] for k in r.key.split(",") if k in self.bib)
                xml.append(self.text_run("[", self.rpr(r, base)))
                for gi, (a, b) in enumerate(compress(nums)):
                    if gi:
                        xml.append(self.text_run(", ", self.rpr(r, base)))
                    label = f"{a}" if a == b else (f"{a}, {b}" if b == a + 1 else f"{a}\u2013{b}")
                    xml.append(f'<w:hyperlink w:anchor="_Bib{a:03d}" w:history="1">'
                               f'{self.text_run(label, self.rpr(r, link))}</w:hyperlink>')
                xml.append(self.text_run("]", self.rpr(r, base)))
        return "".join(xml)

    # -- paragraphs
    def para(self, runs_xml: str, *, style: str = "Body", align: str | None = None, keep_next: bool = False,
             before: int | None = None, after: int | None = None, page_break: bool = False,
             bookmark: str | None = None, extra: str = "", sect: str = "", ind: str = "") -> str:
        ppr = [f'<w:pStyle w:val="{style}"/>']
        if keep_next:
            ppr.append("<w:keepNext/>")
        if page_break:
            ppr.append("<w:pageBreakBefore/>")
        ppr.append(extra)
        if before is not None or after is not None:
            ppr.append("<w:spacing" + (f' w:before="{before}"' if before is not None else "")
                       + (f' w:after="{after}"' if after is not None else "") + "/>")
        ppr.append(ind)
        if align:
            ppr.append(f'<w:jc w:val="{"both" if align == "justify" else align}"/>')
        ppr.append(sect)
        bm = bm_end = ""
        if bookmark:
            self.bm_id += 1
            bm = f'<w:bookmarkStart w:id="{self.bm_id}" w:name="{bookmark}"/>'
            bm_end = f'<w:bookmarkEnd w:id="{self.bm_id}"/>'
        return f"<w:p><w:pPr>{''.join(ppr)}</w:pPr>{bm}{runs_xml}{bm_end}</w:p>"

    def block(self, b, ctx: dict) -> str:
        if isinstance(b, Para):
            return self.para(self.runs(b.runs, {"size": b.size} if b.size else None), style=b.style, align=b.align,
                             keep_next=getattr(b, "keep", False))
        if isinstance(b, Heading):
            return self.heading(b, ctx)
        if isinstance(b, ListBlock):
            return self.list_block(b, 0)
        if isinstance(b, Table):
            return self.table(b)
        if isinstance(b, Figure):
            return self.figure(b)
        if isinstance(b, Code):
            return self.code(b)
        if isinstance(b, Equation):
            return self.equation(b)
        if b == "APPENDIX":
            ctx["appendix"] = True
            return ""
        raise TypeError(b)

    def heading(self, h: Heading, ctx: dict) -> str:
        if h.level == 1:
            if h.numbered:
                label = ("APPENDIX " if ctx.get("appendix") else "CHAPTER ") + h.number
                return (self.para(self.text_run(label), style="ChapterLabel", page_break=True)
                        + self.para(self.runs(h.runs), style="Heading1", bookmark=h.bookmark))
            return self.para(self.runs(h.runs), style="Heading1", page_break=True, bookmark=h.bookmark)
        style = "Heading2" if h.level == 2 else "Heading3"
        number = self.text_run(h.number + "\t") if h.number else ""
        return self.para(number + self.runs(h.runs), style=style, bookmark=h.bookmark)

    def list_block(self, b: ListBlock, level: int, bullet_level: int = 0) -> str:
        # As in LaTeX, a bullet list takes its symbol from how many bullet lists enclose it (a bullet list
        # inside a numbered list gets the first symbol), and its indent from the whole nesting.
        if b.ordered:
            num_id = 100 + len(self.ordered) + 1
            self.ordered.append(num_id)
        else:
            num_id = 1
        level = min(level, 2)
        ilvl = level if b.ordered else min(bullet_level, 2)
        hang = f'<w:ind w:left="{720 * (level + 1)}" w:hanging="360"/>' if ilvl != level else ""
        xml = []
        for item in b.items:
            first = True
            for blk in item:
                if isinstance(blk, Para):
                    numpr = (f'<w:numPr><w:ilvl w:val="{ilvl}"/><w:numId w:val="{num_id}"/></w:numPr>'
                             if first else "")
                    ind = hang if first else f'<w:ind w:left="{720 * (level + 1)}"/>'
                    size = 10.0 if b.compact else blk.size
                    if b.compact:
                        numpr += '<w:spacing w:before="0" w:after="20" w:line="240" w:lineRule="auto"/>'
                    xml.append(self.para(self.runs(blk.runs, {"size": size} if size else None),
                                         style="ListBody", extra=numpr, ind=ind))
                    first = False
                elif isinstance(blk, ListBlock):
                    xml.append(self.list_block(blk, level + 1, bullet_level + (0 if b.ordered else 1)))
                else:
                    xml.append(self.block(blk, {}))
        return "".join(xml)

    # -- tables
    @staticmethod
    def border(kind: str | None, side: str) -> str:
        if not kind:
            return ""
        sz = {"thick": 12, "thin": 4, "bar": 4}[kind]
        return f'<w:{side} w:val="single" w:sz="{sz}" w:space="0" w:color="{RULE_COLOR}"/>'

    def caption_para(self, label: str, number: str, caption: list[Run], bookmark: str, *, above: bool) -> str:
        runs = self.text_run(f"{label} {number}: ") + self.runs(caption)
        return self.para(runs, style="Caption", keep_next=above, bookmark=bookmark,
                         before=240 if above else None, after=120 if above else None)

    def table(self, t: Table) -> str:
        xml = []
        if t.caption:
            xml.append(self.caption_para("Table", t.number, t.caption, t.bookmark, above=True))
        ncols = len(t.widths)
        grid = "".join(f'<w:gridCol w:w="{w}"/>' for w in t.widths)
        xml.append(f'<w:tbl><w:tblPr><w:tblW w:w="{sum(t.widths)}" w:type="dxa"/><w:jc w:val="center"/>'
                   f'<w:tblLayout w:type="fixed"/><w:tblCellMar><w:top w:w="30" w:type="dxa"/>'
                   f'<w:left w:w="85" w:type="dxa"/><w:bottom w:w="30" w:type="dxa"/><w:right w:w="85" w:type="dxa"/>'
                   f'</w:tblCellMar><w:tblLook w:val="0000"/></w:tblPr><w:tblGrid>{grid}</w:tblGrid>')
        last = len(t.rows) - 1
        for ri, row in enumerate(t.rows):
            xml.append(f"<w:tr><w:trPr><w:cantSplit/>{'<w:tblHeader/>' if row.header else ''}</w:trPr>")
            col = 0
            for cell in row.cells:
                if col >= ncols:
                    break
                span = min(cell.span, ncols - col)
                bottom = row.bottom or ("thin" if any(a - 1 <= col < b for a, b in row.cline) else None)
                borders = self.border(row.top, "top") + self.border(bottom, "bottom")
                if t.vbars[col]:
                    borders += self.border("bar", "left")
                if col + span < len(t.vbars) and t.vbars[col + span]:
                    borders += self.border("bar", "right")
                tcpr = f'<w:tcW w:w="{sum(t.widths[col:col + span])}" w:type="dxa"/>'
                if span > 1:
                    tcpr += f'<w:gridSpan w:val="{span}"/>'
                if cell.vmerge == "restart":
                    tcpr += '<w:vMerge w:val="restart"/>'
                elif cell.vmerge == "continue":
                    tcpr += "<w:vMerge/>"
                tcpr += f"<w:tcBorders>{borders}</w:tcBorders>"
                if row.shade:
                    tcpr += f'<w:shd w:val="clear" w:color="auto" w:fill="{row.shade}"/>'
                # a float table stays on one page, as LaTeX keeps it; a long table may break between rows
                hold = (not t.long and ri < last) or (t.long and row.header)
                body = self.para(self.runs(cell.runs, {"size": t.size}), style="TableText", align=cell.align,
                                 keep_next=hold)
                xml.append(f"<w:tc><w:tcPr>{tcpr}</w:tcPr>{body}</w:tc>")
                col += span
            while col < ncols:
                xml.append(f'<w:tc><w:tcPr><w:tcW w:w="{t.widths[col]}" w:type="dxa"/><w:tcBorders>'
                           f'{self.border(row.top, "top")}{self.border(row.bottom, "bottom")}</w:tcBorders></w:tcPr>'
                           f'{self.para("", style="TableText")}</w:tc>')
                col += 1
            xml.append("</w:tr>")
        xml.append("</w:tbl>")
        for p in t.notes:
            xml.append(self.para(self.runs(p.runs, {"size": p.size or 9.0}), style="Note"))
        if not t.notes:
            xml.append(self.para("", style="AfterTable"))
        return "".join(xml)

    # -- figures, code, equations
    def image_run(self, img: Image_, max_w: int | None = None) -> str:
        self.images.append(img.path)
        rid = f"rIdImg{len(self.images)}"
        im = Image.open(img.path)
        w = min(img.width_twips, max_w or img.width_twips)
        h = int(w * im.height / im.width)
        cx, cy = w * EMU_PER_TWIP, h * EMU_PER_TWIP
        self.docpr += 1
        n = self.docpr
        a = "http://schemas.openxmlformats.org/drawingml/2006/main"
        return (f'<w:r><w:drawing><wp:inline distT="0" distB="0" distL="0" distR="0"><wp:extent cx="{cx}" cy="{cy}"/>'
                f'<wp:docPr id="{n}" name="Picture {n}"/><wp:cNvGraphicFramePr><a:graphicFrameLocks xmlns:a="{a}" '
                f'noChangeAspect="1"/></wp:cNvGraphicFramePr><a:graphic xmlns:a="{a}">'
                f'<a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture">'
                f'<pic:pic xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture"><pic:nvPicPr>'
                f'<pic:cNvPr id="{n}" name="{esc(img.path.name)}"/><pic:cNvPicPr/></pic:nvPicPr><pic:blipFill>'
                f'<a:blip r:embed="{rid}"/><a:stretch><a:fillRect/></a:stretch></pic:blipFill><pic:spPr>'
                f'<a:xfrm><a:off x="0" y="0"/><a:ext cx="{cx}" cy="{cy}"/></a:xfrm><a:prstGeom prst="rect">'
                f'<a:avLst/></a:prstGeom></pic:spPr></pic:pic></a:graphicData></a:graphic></wp:inline></w:drawing></w:r>')

    def figure(self, f: Figure) -> str:
        xml = []
        if f.code:
            xml.append(self.code(f.code, keep=True))
        for row in f.rows:
            if len(row) == 1:
                xml.append(self.para(self.image_run(row[0]), style="FigureBody", keep_next=True))
            else:
                gap = 120
                cw = (TEXT_W - gap * (len(row) - 1)) // len(row)
                cells = "".join(f'<w:tc><w:tcPr><w:tcW w:w="{cw}" w:type="dxa"/></w:tcPr>'
                                f'{self.para(self.image_run(img, cw - 80), style="FigureBody")}</w:tc>' for img in row)
                xml.append(f'<w:tbl><w:tblPr><w:tblW w:w="{cw * len(row)}" w:type="dxa"/><w:jc w:val="center"/>'
                           f'<w:tblLayout w:type="fixed"/><w:tblCellMar><w:left w:w="40" w:type="dxa"/>'
                           f'<w:right w:w="40" w:type="dxa"/></w:tblCellMar></w:tblPr><w:tblGrid>'
                           + "".join(f'<w:gridCol w:w="{cw}"/>' for _ in row)
                           + f"</w:tblGrid><w:tr><w:trPr><w:cantSplit/></w:trPr>{cells}</w:tr></w:tbl>")
        if f.caption:
            xml.append(self.caption_para("Figure", f.number, f.caption, f.bookmark, above=False))
        return "".join(xml)

    def code(self, c: Code, keep: bool = False) -> str:
        xml = []
        side = '<w:{0} w:val="single" w:sz="4" w:space="4" w:color="7F7F7F"/>'
        border = "<w:pBdr>" + "".join(side.format(s) for s in ("top", "left", "bottom", "right")) + "</w:pBdr>"
        width = len(str(len(c.lines)))
        for k, line in enumerate(c.lines, 1):
            line = line.replace("\t", "    ")
            num = ""
            if c.numbered:
                num = (f'<w:r><w:rPr><w:color w:val="7F7F7F"/><w:sz w:val="14"/><w:szCs w:val="14"/></w:rPr>'
                       f'<w:t xml:space="preserve">{str(k).rjust(width)}  </w:t></w:r>')
            body = f'<w:r><w:t xml:space="preserve">{esc(line)}</w:t></w:r>' if line else ""
            hold = keep or k <= 2 or k >= len(c.lines) - 1
            xml.append(self.para(num + body, style="Code", extra=border, keep_next=hold and k < len(c.lines) or
                                 (keep and k == len(c.lines))))
        if c.caption:
            xml.append(self.caption_para("Listing", c.number, c.caption, c.bookmark, above=False))
        elif not keep:
            xml.append(self.para("", style="AfterTable"))
        return "".join(xml)

    def equation(self, e: Equation) -> str:
        """A display equation centred in a borderless row, its number at the right margin."""
        gap = ('<m:r><m:rPr><m:sty m:val="p"/></m:rPr><w:rPr><w:rFonts w:ascii="Cambria Math" '
               'w:hAnsi="Cambria Math"/></w:rPr><m:t xml:space="preserve">\u2003\u2003</m:t></m:r>')
        parts = [p.strip() for p in re.split(r"\\qquad", e.tex) if p.strip()]
        math = gap.join(omml_of(p) for p in parts)
        side, mid = 560, TEXT_W - 1120
        none = ('<w:tblBorders><w:top w:val="nil"/><w:left w:val="nil"/><w:bottom w:val="nil"/>'
                '<w:right w:val="nil"/><w:insideH w:val="nil"/><w:insideV w:val="nil"/></w:tblBorders>')
        center = (f'<w:p><w:pPr><w:pStyle w:val="Equation"/></w:pPr><m:oMathPara><m:oMathParaPr>'
                  f'<m:jc m:val="center"/></m:oMathParaPr><m:oMath>{math}</m:oMath></m:oMathPara></w:p>')
        number = self.para(self.text_run(f"({e.number})"), style="Equation", align="right", bookmark=e.bookmark)
        cell = '<w:tc><w:tcPr><w:tcW w:w="{w}" w:type="dxa"/><w:vAlign w:val="center"/></w:tcPr>{body}</w:tc>'
        return (f'<w:tbl><w:tblPr><w:tblW w:w="{TEXT_W}" w:type="dxa"/><w:tblLayout w:type="fixed"/>{none}'
                f'<w:tblCellMar><w:left w:w="0" w:type="dxa"/><w:right w:w="0" w:type="dxa"/></w:tblCellMar>'
                f'</w:tblPr><w:tblGrid><w:gridCol w:w="{side}"/><w:gridCol w:w="{mid}"/><w:gridCol w:w="{side}"/>'
                f'</w:tblGrid><w:tr><w:trPr><w:cantSplit/></w:trPr>'
                + cell.format(w=side, body=self.para("", style="Equation"))
                + cell.format(w=mid, body=center) + cell.format(w=side, body=number)
                + "</w:tr></w:tbl>" + self.para("", style="AfterTable"))


def compress(nums: list[int]) -> list[tuple[int, int]]:
    out: list[tuple[int, int]] = []
    for n in nums:
        if out and n == out[-1][1] + 1:
            out[-1] = (out[-1][0], n)
        elif not out or n != out[-1][1]:
            out.append((n, n))
    return out


# ---------------------------------------------------------------- equations as Word maths


def omml_of(tex: str) -> str:
    toks = [t for t in re.findall(r"\\[A-Za-z]+|\\.|[{}_^()|,.=+\-]|[A-Za-z]|\d+|\s+|.", tex)]
    pos = [0]

    def peek():
        return toks[pos[0]] if pos[0] < len(toks) else None

    def take():
        pos[0] += 1
        return toks[pos[0] - 1]

    def run(text: str, upright: bool) -> str:
        sty = '<m:rPr><m:sty m:val="p"/></m:rPr>' if upright else ""
        return (f'<m:r>{sty}<w:rPr><w:rFonts w:ascii="Cambria Math" w:hAnsi="Cambria Math"/></w:rPr>'
                f'<m:t xml:space="preserve">{esc(text)}</m:t></m:r>')

    def skip_space():
        while peek() is not None and peek().isspace():
            take()

    def group() -> str:
        skip_space()
        if peek() == "{":
            take()
            out = seq(stop="}")
            take()
            return out
        return atom()

    def atom() -> str:
        t = take()
        if t.startswith("\\"):
            name = t[1:]
            if name in ("mathrm", "text"):
                take()
                words = []
                while peek() != "}":
                    w = take()
                    words.append(" " if w == "\\ " else w)
                take()
                return run("".join(words), True)
            if name == "frac":
                num, den = group(), group()
                return f"<m:f><m:num>{num}</m:num><m:den>{den}</m:den></m:f>"
            if name == "left":
                opener = take()
                inner = seq(stop="\\right")
                take()
                closer = take()
                return (f'<m:d><m:dPr><m:begChr m:val="{esc(opener)}"/><m:endChr m:val="{esc(closer)}"/></m:dPr>'
                        f"<m:e>{inner}</m:e></m:d>")
            if name in WORDS:
                return run(WORDS[name], True)
            if name in ("!", ","):
                return ""
            if name == " ":
                return run(" ", True)
            return run(name, True)
        if t.isspace():
            return ""
        if t == "-":
            return run("\u2212", True)
        if t.isalpha():
            return run(t, False)
        return run(t, True)

    def seq(stop: str | None = None) -> str:
        out = []
        while peek() is not None and peek() != stop:
            if stop is None and peek() == "}":
                take()
                continue
            base = atom()
            skip_space()
            if peek() == "_":
                take()
                base = f"<m:sSub><m:e>{base}</m:e><m:sub>{group()}</m:sub></m:sSub>"
            elif peek() == "^":
                take()
                base = f"<m:sSup><m:e>{base}</m:e><m:sup>{group()}</m:sup></m:sSup>"
            out.append(base)
        return "".join(out)

    return seq()


# ---------------------------------------------------------------- the package

NS = ('xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" '
      'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" '
      'xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing" '
      'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
      'xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture" '
      'xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math"')


def styles_xml() -> str:
    def pstyle(sid, name, ppr="", rpr="", based="Normal", ui=None):
        u = f'<w:uiPriority w:val="{ui}"/>' if ui else ""
        return (f'<w:style w:type="paragraph" w:customStyle="1" w:styleId="{sid}"><w:name w:val="{name}"/>'
                f'<w:basedOn w:val="{based}"/>{u}<w:qFormat/><w:pPr>{ppr}</w:pPr><w:rPr>{rpr}</w:rPr></w:style>')

    def builtin(sid, name, ppr, rpr, nxt="Body", ui=9):
        return (f'<w:style w:type="paragraph" w:styleId="{sid}"><w:name w:val="{name}"/><w:basedOn w:val="Normal"/>'
                f'<w:next w:val="{nxt}"/><w:uiPriority w:val="{ui}"/><w:qFormat/><w:pPr>{ppr}</w:pPr>'
                f'<w:rPr>{rpr}</w:rPr></w:style>')

    bold16 = '<w:b/><w:bCs/><w:sz w:val="32"/><w:szCs w:val="32"/>'
    toc_tab = f'<w:tabs><w:tab w:val="right" w:leader="dot" w:pos="{TEXT_W}"/></w:tabs>'
    body = '<w:spacing w:after="160" w:line="360" w:lineRule="auto"/><w:jc w:val="both"/>'
    styles = [
        '<w:docDefaults><w:rPrDefault><w:rPr><w:rFonts w:ascii="Times New Roman" w:eastAsia="Times New Roman" '
        'w:hAnsi="Times New Roman" w:cs="Times New Roman"/><w:color w:val="000000"/><w:sz w:val="24"/>'
        '<w:szCs w:val="24"/><w:lang w:val="en-IN" w:eastAsia="en-GB" w:bidi="ar-SA"/></w:rPr></w:rPrDefault>'
        '<w:pPrDefault><w:pPr><w:spacing w:after="0" w:line="240" w:lineRule="auto"/></w:pPr></w:pPrDefault>'
        '</w:docDefaults>',
        '<w:style w:type="paragraph" w:default="1" w:styleId="Normal"><w:name w:val="Normal"/><w:qFormat/></w:style>',
        '<w:style w:type="character" w:default="1" w:styleId="DefaultParagraphFont">'
        '<w:name w:val="Default Paragraph Font"/><w:uiPriority w:val="1"/><w:semiHidden/></w:style>',
        '<w:style w:type="table" w:default="1" w:styleId="TableNormal"><w:name w:val="Normal Table"/><w:semiHidden/>'
        '<w:tblPr><w:tblInd w:w="0" w:type="dxa"/><w:tblCellMar><w:top w:w="0" w:type="dxa"/>'
        '<w:left w:w="108" w:type="dxa"/><w:bottom w:w="0" w:type="dxa"/><w:right w:w="108" w:type="dxa"/>'
        '</w:tblCellMar></w:tblPr></w:style>',
        '<w:style w:type="numbering" w:default="1" w:styleId="NoList"><w:name w:val="No List"/><w:semiHidden/></w:style>',
        pstyle("Body", "Thesis Body", body),
        pstyle("ListBody", "Thesis List", '<w:spacing w:after="80" w:line="360" w:lineRule="auto"/><w:jc w:val="both"/>'),
        pstyle("ChapterLabel", "Chapter Label", '<w:keepNext/><w:spacing w:before="0" w:after="80"/><w:jc w:val="center"/>',
               bold16),
        builtin("Heading1", "heading 1", '<w:keepNext/><w:keepLines/><w:spacing w:before="40" w:after="480"/>'
                '<w:jc w:val="center"/><w:outlineLvl w:val="0"/>', bold16),
        builtin("Heading2", "heading 2", f'<w:keepNext/><w:keepLines/><w:tabs><w:tab w:val="left" w:pos="720"/></w:tabs>'
                '<w:spacing w:before="360" w:after="160"/><w:ind w:left="720" w:hanging="720"/><w:outlineLvl w:val="1"/>',
                '<w:b/><w:bCs/><w:sz w:val="28"/><w:szCs w:val="28"/>'),
        builtin("Heading3", "heading 3", '<w:keepNext/><w:keepLines/><w:tabs><w:tab w:val="left" w:pos="720"/></w:tabs>'
                '<w:spacing w:before="280" w:after="120"/><w:ind w:left="720" w:hanging="720"/><w:outlineLvl w:val="2"/>',
                '<w:b/><w:bCs/>'),
        builtin("Caption", "caption", '<w:spacing w:before="120" w:after="280"/><w:ind w:left="400" w:right="400"/>'
                '<w:jc w:val="center"/>', '<w:i/><w:iCs/><w:sz w:val="22"/><w:szCs w:val="22"/>', ui=35),
        pstyle("TableText", "Table Text", '<w:spacing w:before="10" w:after="10"/>', '<w:sz w:val="18"/><w:szCs w:val="18"/>'),
        pstyle("Note", "Table Note", '<w:spacing w:before="80" w:after="280"/><w:ind w:left="200" w:right="200"/>'
               '<w:jc w:val="both"/>', '<w:sz w:val="18"/><w:szCs w:val="18"/>'),
        pstyle("AfterTable", "After Table", '<w:spacing w:after="160"/>', '<w:sz w:val="12"/><w:szCs w:val="12"/>'),
        pstyle("FigureBody", "Figure", '<w:spacing w:before="200" w:after="0"/><w:jc w:val="center"/>'),
        pstyle("Code", "Code", '<w:spacing w:before="0" w:after="0"/><w:ind w:left="120" w:right="120"/>',
               '<w:rFonts w:ascii="Courier New" w:hAnsi="Courier New" w:cs="Courier New"/><w:sz w:val="18"/>'
               '<w:szCs w:val="17"/>'),
        pstyle("Equation", "Equation", '<w:spacing w:before="160" w:after="240"/>'),
        pstyle("FrontCenter", "Front Matter Centred", '<w:spacing w:after="0" w:line="360" w:lineRule="auto"/>'
               '<w:jc w:val="center"/>'),
        pstyle("TOCHeading", "Contents Heading", '<w:pageBreakBefore/><w:spacing w:after="480"/><w:jc w:val="center"/>',
               bold16),
        builtin("TOC1", "toc 1", f'{toc_tab}<w:spacing w:before="160" w:after="40"/><w:ind w:left="480" w:hanging="480"/>',
                "", ui=39),
        builtin("TOC2", "toc 2", f'{toc_tab}<w:spacing w:before="0" w:after="40"/>'
                '<w:ind w:left="1060" w:right="500" w:hanging="580"/>', "", ui=39),
        builtin("TOC3", "toc 3", f'{toc_tab}<w:spacing w:before="0" w:after="40"/>'
                '<w:ind w:left="1800" w:right="500" w:hanging="740"/>', "", ui=39),
        builtin("TOF", "table of figures", f'{toc_tab}<w:spacing w:before="0" w:after="100"/>'
                '<w:ind w:left="700" w:right="500" w:hanging="700"/>', "", ui=99),
        pstyle("Bib", "Bibliography Entry", '<w:spacing w:after="140" w:line="300" w:lineRule="auto"/>'
               '<w:ind w:left="600" w:hanging="600"/><w:jc w:val="both"/>'),
        '<w:style w:type="paragraph" w:styleId="Footer"><w:name w:val="footer"/><w:basedOn w:val="Normal"/>'
        '<w:pPr><w:jc w:val="center"/></w:pPr></w:style>',
    ]
    return '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>' + f'<w:styles {NS}>' + "".join(styles) + "</w:styles>"


def numbering_xml(ordered: list[int]) -> str:
    def lvl(i, fmt, text, left):
        return (f'<w:lvl w:ilvl="{i}"><w:start w:val="1"/><w:numFmt w:val="{fmt}"/><w:lvlText w:val="{text}"/>'
                f'<w:lvlJc w:val="left"/><w:pPr><w:ind w:left="{left}" w:hanging="360"/></w:pPr></w:lvl>')

    bullets = lvl(0, "bullet", "\u2022", 720) + lvl(1, "bullet", "\u2013", 1440) + lvl(2, "bullet", "\u2219", 2160)
    numbers = lvl(0, "decimal", "%1.", 720) + lvl(1, "lowerLetter", "(%2)", 1440) + lvl(2, "lowerRoman", "%3.", 2160)
    nums = ['<w:num w:numId="1"><w:abstractNumId w:val="1"/></w:num>']
    for num_id in ordered:
        nums.append(f'<w:num w:numId="{num_id}"><w:abstractNumId w:val="2"/>'
                    f'<w:lvlOverride w:ilvl="0"><w:startOverride w:val="1"/></w:lvlOverride></w:num>')
    return ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>' f'<w:numbering {NS}>'
            f'<w:abstractNum w:abstractNumId="1"><w:multiLevelType w:val="hybridMultilevel"/>{bullets}</w:abstractNum>'
            f'<w:abstractNum w:abstractNumId="2"><w:multiLevelType w:val="hybridMultilevel"/>{numbers}</w:abstractNum>'
            + "".join(nums) + "</w:numbering>")


FOOTER = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
          f'<w:ftr {NS}><w:p><w:pPr><w:pStyle w:val="Footer"/></w:pPr>'
          '<w:r><w:fldChar w:fldCharType="begin"/></w:r><w:r><w:instrText xml:space="preserve"> PAGE </w:instrText></w:r>'
          '<w:r><w:fldChar w:fldCharType="separate"/></w:r><w:r><w:t>1</w:t></w:r>'
          '<w:r><w:fldChar w:fldCharType="end"/></w:r></w:p></w:ftr>')

SETTINGS = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            f'<w:settings {NS}><w:zoom w:percent="100"/><w:autoHyphenation/><w:consecutiveHyphenLimit w:val="2"/>'
            '<w:hyphenationZone w:val="284"/><w:defaultTabStop w:val="720"/>'
            '<w:characterSpacingControl w:val="doNotCompress"/><w:compat><w:doNotExpandShiftReturn/>'
            '<w:compatSetting w:name="compatibilityMode" w:uri="http://schemas.microsoft.com/office/word" w:val="15"/>'
            '</w:compat><m:mathPr><m:mathFont m:val="Cambria Math"/></m:mathPr></w:settings>')


def sect(kind: str) -> str:
    """Section properties: title (no number), front (roman from i) or main (arabic from 1)."""
    footer = '<w:footerReference w:type="default" r:id="rIdFooter"/>' if kind != "title" else ""
    num = {"front": '<w:pgNumType w:fmt="lowerRoman" w:start="1"/>',
           "main": '<w:pgNumType w:fmt="decimal" w:start="1"/>'}.get(kind, "")
    return (f'<w:sectPr>{footer}<w:type w:val="nextPage"/><w:pgSz w:w="{PAGE_W}" w:h="{PAGE_H}"/>'
            f'<w:pgMar w:top="{MARGIN_T}" w:right="{MARGIN_R}" w:bottom="{MARGIN_B}" w:left="{MARGIN_L}" '
            f'w:header="708" w:footer="708" w:gutter="0"/>{num}<w:cols w:space="720"/></w:sectPr>')


def pageref(bm: str) -> str:
    return (f'<w:r><w:fldChar w:fldCharType="begin"/></w:r><w:r><w:instrText xml:space="preserve"> PAGEREF {bm} \\h '
            f'</w:instrText></w:r><w:r><w:fldChar w:fldCharType="separate"/></w:r><w:r><w:t>#</w:t></w:r>'
            f'<w:r><w:fldChar w:fldCharType="end"/></w:r>')


def package(body: str, w: Writer, out: Path) -> None:
    rel = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
    rels = [f'<Relationship Id="rIdStyles" Type="{rel}/styles" Target="styles.xml"/>',
            f'<Relationship Id="rIdNumbering" Type="{rel}/numbering" Target="numbering.xml"/>',
            f'<Relationship Id="rIdSettings" Type="{rel}/settings" Target="settings.xml"/>',
            f'<Relationship Id="rIdFooter" Type="{rel}/footer" Target="footer1.xml"/>']
    media = {}
    for k, p in enumerate(w.images, 1):
        name = f"media/image{k}{p.suffix.lower()}"
        media[name] = p
        rels.append(f'<Relationship Id="rIdImg{k}" Type="{rel}/image" Target="{name}"/>')
    for k, url in enumerate(w.urls, 1):
        rels.append(f'<Relationship Id="rIdUrl{k}" Type="{rel}/hyperlink" Target="{esc(url)}" TargetMode="External"/>')
    ct = "application/vnd.openxmlformats-officedocument.wordprocessingml"
    content_types = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Default Extension="xml" ContentType="application/xml"/><Default Extension="png" ContentType="image/png"/>'
        f'<Override PartName="/word/document.xml" ContentType="{ct}.document.main+xml"/>'
        f'<Override PartName="/word/styles.xml" ContentType="{ct}.styles+xml"/>'
        f'<Override PartName="/word/numbering.xml" ContentType="{ct}.numbering+xml"/>'
        f'<Override PartName="/word/settings.xml" ContentType="{ct}.settings+xml"/>'
        f'<Override PartName="/word/footer1.xml" ContentType="{ct}.footer+xml"/>'
        '<Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>'
        '</Types>')
    root_rels = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                 '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                 f'<Relationship Id="rId1" Type="{rel}/officeDocument" Target="word/document.xml"/>'
                 '<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/'
                 'metadata/core-properties" Target="docProps/core.xml"/></Relationships>')
    core = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" '
            'xmlns:dc="http://purl.org/dc/elements/1.1/">'
            f'<dc:title>{esc(TITLE)}</dc:title><dc:creator>{esc(", ".join(s for s, _ in STUDENTS))}</dc:creator>'
            '<dc:subject>Data protection compliance of data extraction from hospital information systems</dc:subject>'
            '<cp:keywords>DPDP Act 2023, hospital information systems, web scraping, compliance benchmarking, HL7, FHIR'
            '</cp:keywords></cp:coreProperties>')
    document = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                f'<w:document {NS}><w:body>{body}</w:body></w:document>')
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", content_types)
        z.writestr("_rels/.rels", root_rels)
        z.writestr("docProps/core.xml", core)
        z.writestr("word/document.xml", document)
        z.writestr("word/styles.xml", styles_xml())
        z.writestr("word/numbering.xml", numbering_xml(w.ordered))
        z.writestr("word/settings.xml", SETTINGS)
        z.writestr("word/footer1.xml", FOOTER)
        z.writestr("word/_rels/document.xml.rels",
                   '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                   '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                   + "".join(rels) + "</Relationships>")
        for name, p in media.items():
            z.write(p, "word/" + name)


# ---------------------------------------------------------------- the front and back matter


class Front:
    def __init__(self, w: Writer, inline: Inline, logo: Path):
        self.w, self.inline, self.logo = w, inline, logo

    def c(self, text: str, size: float | None = None, bold=False, before=None, after=None) -> str:
        runs = self.inline.runs(text, Fmt(b=bold))
        return self.w.para(self.w.runs(runs, {"size": size} if size else None), style="FrontCenter",
                           before=before, after=after)

    def title_page(self) -> str:
        w = self.w
        big = w.rpr(Run(b=True, size=20))
        x = [w.para("", style="FrontCenter", before=600),
             w.para(w.text_run(TITLE_LINES[0], big) + "<w:r><w:br/></w:r>" + w.text_run(TITLE_LINES[1], big),
                    style="FrontCenter", after=600)]
        for line, size in (("A project report submitted in partial fulfilment", 12),
                           ("of the requirements for the degree of", 12), ("Bachelor of Technology", 14),
                           ("in", 12), ("Electronics and Computer Engineering", 14)):
            x.append(self.c(line, size))
        x.append(self.c("by", 16, before=360, after=120))
        x.append(self.names_table())
        x.append(w.para(w.image_run(Image_(path=self.logo, width_twips=int(8 * CM))), style="FrontCenter",
                        before=600, after=600))
        for line in ("School of Electronics Engineering,", "Vellore Institute of Technology, Chennai,",
                     "Vandalur\u2013Kelambakkam Road,", "Chennai \u2013 600127, India."):
            x.append(self.c(line, 12))
        x.append(self.c("October 2026", 14, before=480))
        return "".join(x)

    def names_table(self) -> str:
        w = self.w
        cw = int(TEXT_W * 0.42)
        cells = "".join(f'<w:tc><w:tcPr><w:tcW w:w="{cw}" w:type="dxa"/></w:tcPr>'
                        + w.para(w.text_run(name, w.rpr(Run(size=16))), style="FrontCenter")
                        + w.para(w.text_run(reg, w.rpr(Run(size=12))), style="FrontCenter") + "</w:tc>"
                        for name, reg in STUDENTS)
        return (f'<w:tbl><w:tblPr><w:tblW w:w="{cw * 2}" w:type="dxa"/><w:jc w:val="center"/>'
                f'<w:tblLayout w:type="fixed"/></w:tblPr><w:tblGrid><w:gridCol w:w="{cw}"/><w:gridCol w:w="{cw}"/>'
                f'</w:tblGrid><w:tr>{cells}</w:tr></w:tbl>')

    def school_head(self, title: str, bookmark: str) -> str:
        w = self.w
        return (w.para(w.image_run(Image_(path=self.logo, width_twips=int(6.5 * CM))), style="FrontCenter",
                       before=120, after=200, page_break=True)
                + self.c("School of Electronics Engineering", 14, bold=True, after=240)
                + w.para(w.text_run(title), style="Heading1", bookmark=bookmark))

    def sign_table(self, rows: list[tuple[str, str]], head: tuple[str, str] | None = None) -> str:
        w = self.w
        cw = TEXT_W // 2
        tab = f'<w:tabs><w:tab w:val="right" w:leader="dot" w:pos="{cw - 360}"/></w:tabs>'
        trs = []
        if head:
            trs.append("<w:tr>" + "".join(f'<w:tc><w:tcPr><w:tcW w:w="{cw}" w:type="dxa"/></w:tcPr>'
                                          + w.para(w.text_run(h, w.rpr(Run(b=True))), style="Normal", after=400)
                                          + "</w:tc>" for h in head) + "</w:tr>")
        for left, right in rows:
            trs.append("<w:tr>" + "".join(f'<w:tc><w:tcPr><w:tcW w:w="{cw}" w:type="dxa"/></w:tcPr>'
                                          + w.para(w.runs(self.inline.runs(t)), style="Normal", extra=tab, after=240)
                                          + "</w:tc>" for t in (left, right)) + "</w:tr>")
        return (f'<w:tbl><w:tblPr><w:tblW w:w="{TEXT_W}" w:type="dxa"/><w:tblLayout w:type="fixed"/></w:tblPr>'
                f'<w:tblGrid><w:gridCol w:w="{cw}"/><w:gridCol w:w="{cw}"/></w:tblGrid>{"".join(trs)}</w:tbl>')

    def declaration(self, bm: str) -> str:
        t = "\\textbf{\\textit{" + TITLE + "}}"
        body = [
            f"We hereby declare that the report titled {t} submitted by us to the School of Electronics "
            "Engineering, Vellore Institute of Technology, Chennai, in partial fulfilment of the requirements for "
            "the award of \\textbf{Bachelor of Technology} in \\textbf{Electronics and Computer Engineering}, is a "
            "bonafide record of the work carried out by us under the supervision of "
            "\\textbf{\\textit{Dr.~Manoj Kumar}}.",
            "We further declare that the work reported in this report has not been submitted and will not be "
            "submitted, either in part or in full, for the award of any other degree or diploma of this institute "
            "or of any other institute or University.",
        ]
        x = [self.school_head("Declaration", bm)]
        x += [self.w.para(self.w.runs(self.inline.runs(p)), style="Body") for p in body]
        x.append(self.w.para("", style="Normal", after=600))
        x.append(self.sign_table([
            ("Signature of the Student: \\dotfill", "Signature of the Student: \\dotfill"),
            ("Name \\& Reg.\\ No.: Ananya Karmakar, 23BLC1017", "Name \\& Reg.\\ No.: Avanindra Kushwah, 23BLC1089"),
            ("Date: \\dotfill", "Date: \\dotfill")]))
        return "".join(x)

    def certificate(self, bm: str) -> str:
        p = ("This is to certify that the project report titled \\textbf{\\textit{" + TITLE + "}} submitted by "
             "\\textbf{\\textit{Ananya Karmakar} (23BLC1017)} and \\textbf{\\textit{Avanindra Kushwah} (23BLC1089)} "
             "to Vellore Institute of Technology, Chennai, in partial fulfilment of the requirement for the award "
             "of the degree of \\textbf{Bachelor of Technology} in \\textbf{Electronics and Computer Engineering} "
             "is a bonafide work carried out under my supervision. The project report fulfils the requirements as "
             "per the regulations of this University and, in my opinion, meets the necessary standards for "
             "submission. The contents of this report have not been submitted and will not be submitted either in "
             "part or in full, for the award of any other degree or diploma and the same is certified.")
        x = [self.school_head("Certificate", bm), self.w.para(self.w.runs(self.inline.runs(p)), style="Body"),
             self.w.para("", style="Normal", after=240),
             self.sign_table([("Signature: \\dotfill", "Signature: \\dotfill"),
                              ("Name: Dr.~Manoj Kumar", "Name: Dr.~Vijayakumar P"),
                              ("Date: \\dotfill", "Date: \\dotfill")], head=("Supervisor", "Head of the Department")),
             self.w.para("", style="Normal", after=240),
             self.sign_table([("Signature: \\dotfill", "Signature: \\dotfill"), ("Name: \\dotfill", "Name: \\dotfill"),
                              ("Date: \\dotfill", "Date: \\dotfill")], head=("Examiner 1", "Examiner 2")),
             self.w.para(self.w.text_run("(Seal of the School)"), style="Normal", align="right", before=240)]
        return "".join(x)

    def biodata(self, bm: str) -> str:
        w = self.w
        x = [w.para(w.text_run("Biodata"), style="Heading1", page_break=True, bookmark=bm)]
        photo_w = int(3.8 * CM)
        rest_w = TEXT_W - photo_w
        line = '<w:pBdr><w:bottom w:val="single" w:sz="4" w:space="1" w:color="000000"/></w:pBdr>'
        box = ("<w:tcBorders>" + "".join(f'<w:{s} w:val="single" w:sz="6" w:space="0" w:color="000000"/>'
                                         for s in ("top", "left", "bottom", "right")) + "</w:tcBorders>")
        bold = w.rpr(Run(b=True))
        for k, (name, reg) in enumerate(STUDENTS, 1):
            x.append(w.para(w.text_run(f"Student {k}", bold), style="Normal", before=480, after=200, keep_next=True))
            fields = [w.para(w.text_run("Name: ", bold) + w.text_run(name), style="Normal", after=240)]
            # Word joins the borders of neighbouring paragraphs that are formatted alike and draws only the
            # last line; a right indent one twip different on each keeps every line its own rule.
            for k, label in enumerate(("Mobile No.:", "E-mail:"), 1):
                fields.append(w.para(w.text_run(label, bold), style="Normal", after=240, extra=line,
                                     ind=f'<w:ind w:right="{k}"/>'))
            fields.append(w.para(w.text_run("Permanent Address:", bold), style="Normal", after=240))
            for k in range(3):
                fields.append(w.para("", style="Normal", after=240, extra=line,
                                     ind=f'<w:ind w:right="{k + 3}"/>'))
            x.append(f'<w:tbl><w:tblPr><w:tblW w:w="{TEXT_W}" w:type="dxa"/><w:tblLayout w:type="fixed"/></w:tblPr>'
                     f'<w:tblGrid><w:gridCol w:w="{photo_w}"/><w:gridCol w:w="{rest_w}"/></w:tblGrid>'
                     f'<w:tr><w:trPr><w:cantSplit/></w:trPr>'
                     f'<w:tc><w:tcPr><w:tcW w:w="{photo_w}" w:type="dxa"/>{box}<w:vAlign w:val="center"/></w:tcPr>'
                     + w.para(w.text_run("Photo", bold), style="FrontCenter")
                     + f'</w:tc><w:tc><w:tcPr><w:tcW w:w="{rest_w}" w:type="dxa"/><w:tcMar><w:left w:w="400" '
                       f'w:type="dxa"/></w:tcMar></w:tcPr>' + "".join(fields) + "</w:tc></w:tr></w:tbl>")
        return "".join(x)


# ---------------------------------------------------------------- assembling the thesis


def load_macros() -> tuple[dict[str, str], str]:
    commit = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, capture_output=True,
                            text=True).stdout.strip() or "unknown"
    raw: dict[str, str] = {"Act": "DPDP Act", "BuildCommit": commit}
    numbers = (SOURCE / "generated" / "numbers.tex").read_text(encoding="utf-8")
    for m in re.finditer(r"\\newcommand\{\\(\w+)\}\{((?:[^{}]|\{[^{}]*\})*)\}", numbers):
        raw[m.group(1)] = m.group(2)
    plain_inline = Inline({}, lambda *_: None)
    macros = {k: plain_inline.plain(v) if ("\\" in v or "~" in v) else v for k, v in raw.items()}
    tex_macros = (SOURCE / "macros.tex").read_text(encoding="utf-8") + "\n" + numbers
    return macros, tex_macros


def build(out: Path) -> Path:
    warnings: list[str] = []

    def warn(msg: str):
        if msg not in warnings:
            warnings.append(msg)

    macros, tex_macros = load_macros()
    src = Source()
    inline = Inline(macros, warn)
    reader = Reader(src, inline, FigureMaker(tex_macros), warn)

    def chapter(name: str) -> list:
        return reader.blocks(src.read(f"chapters/{name}"))

    def unnumbered(title: str) -> Heading:
        return Heading(level=1, runs=[Run(text=title)], numbered=False)

    abstract = [unnumbered("Abstract")] + chapter("abstract")
    thanks = [unnumbered("Acknowledgements")] + chapter("acknowledgements")
    standards, sdg = chapter("standards"), chapter("sdg")
    acronyms = [unnumbered("List of Acronyms")] + chapter("acronyms")
    main = []
    for name in ("ch1-introduction", "ch2-literature", "ch3-methodology", "ch4-implementation", "ch5-results",
                 "ch6-conclusion", "appendix"):
        if name == "appendix":
            main.append("APPENDIX")             # main.tex says \appendix before it
        main += chapter(name)

    num = Numberer()
    decl_bm, cert_bm, lof_bm, lot_bm, toc_bm, bib_bm, bio_bm = (num.bookmark() for _ in range(7))
    num.toc += [(1, "", "Declaration", decl_bm), (1, "", "Certificate", cert_bm)]
    num.walk(abstract + thanks + standards + sdg, numbered_floats=False)
    num.toc += [(1, "", "List of Figures", lof_bm), (1, "", "List of Tables", lot_bm)]
    num.walk(acronyms, numbered_floats=False)
    num.chapter = 0
    num.walk(main)
    num.toc += [(1, "", "Bibliography", bib_bm), (1, "", "Biodata", bio_bm)]

    bib = read_bib(SOURCE / "refs.bib")
    missing = [k for k in num.cites if k not in bib]
    if missing:
        warn("citations without a bibliography entry: " + ", ".join(missing))
    bib_numbers = {k: n for n, k in enumerate((k for k in num.cites if k in bib), 1)}

    w = Writer(num, bib_numbers)
    fm = Front(w, inline, build_thesis.template_dir() / "logo.png")
    ctx: dict = {}
    body: list[str] = [fm.title_page(), w.para("", style="Normal", sect=sect("title")),
                       fm.declaration(decl_bm), fm.certificate(cert_bm)]
    for b in abstract + thanks + standards + sdg:
        body.append(w.block(b, ctx))

    # contents and the two lists, with page numbers Word fills in
    body.append(w.para(w.text_run("Contents"), style="TOCHeading", bookmark=toc_bm))
    for level, number, text, bm in num.toc:
        rpr = w.rpr(Run(b=level == 1 and bool(number)))
        runs = w.text_run((number + "\t" if number else "") + text + "\t", rpr) + pageref(bm)
        ind = '<w:ind w:left="0" w:firstLine="0"/>' if level == 1 and not number else ""
        body.append(w.para(f'<w:hyperlink w:anchor="{bm}" w:history="1">{runs}</w:hyperlink>',
                           style=f"TOC{min(level, 3)}", ind=ind))
    for title, entries, bm in (("List of Figures", num.lof, lof_bm), ("List of Tables", num.lot, lot_bm)):
        body.append(w.para(w.text_run(title), style="TOCHeading", bookmark=bm))
        for number, cap, ebm in entries:
            runs = w.text_run(number + "\t") + w.runs(cap) + w.text_run("\t") + pageref(ebm)
            body.append(w.para(f'<w:hyperlink w:anchor="{ebm}" w:history="1">{runs}</w:hyperlink>', style="TOF"))
    for b in acronyms:
        body.append(w.block(b, ctx))
    body.append(w.para("", style="Normal", sect=sect("front")))

    for k, b in enumerate(main):
        if isinstance(b, Para) and k + 1 < len(main) and isinstance(main[k + 1], Equation):
            b.keep = True                   # the sentence that introduces an equation stays with it
        body.append(w.block(b, ctx))

    body.append(w.para(w.text_run("Bibliography"), style="Heading1", page_break=True, bookmark=bib_bm))
    for key, n in bib_numbers.items():
        runs = w.text_run(f"[{n}]\t") + w.runs(bib_entry(bib[key], inline))
        body.append(w.para(runs, style="Bib", bookmark=f"_Bib{n:03d}",
                           extra='<w:tabs><w:tab w:val="left" w:pos="600"/></w:tabs>'))
    body.append(fm.biodata(bio_bm))
    body.append(sect("main"))

    out.parent.mkdir(parents=True, exist_ok=True)
    package("".join(body), w, out)
    print(f"  wrote {out}: {len(num.toc)} contents entries, {len(num.lof)} figures, {len(num.lot)} tables, "
          f"{sum(1 for b in flatten(main) if isinstance(b, Code) and b.caption)} listings, "
          f"{len(bib_numbers)} references")
    unresolved = sorted({r.key for b in flatten(main) for r in runs_of(b) if r.kind == "ref"
                         and r.key not in num.labels})
    if unresolved:
        print("  unresolved references: " + ", ".join(unresolved))
    for msg in warnings:
        print("  note: " + msg)
    if src.old_title:
        print("  note: the old working title is still in " + ", ".join(sorted(src.old_title))
              + f"; the Word copy uses the official title, \"{TITLE}\"")
    return out


def word_finish(docx: Path, pdf: Path) -> None:
    """Word lays the copy out, fills in the page numbers of the contents and lists, and writes a PDF."""
    proc = subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File",
                           str(HERE / "word_update_fields.ps1"), "-Docx", str(docx), "-Pdf", str(pdf)],
                          capture_output=True, text=True)
    if proc.returncode != 0:
        print(proc.stdout, proc.stderr)
        sys.exit("Word could not update the document")
    print("  " + proc.stdout.strip())


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-word", action="store_true", help="do not open Word to fill in page numbers")
    parser.add_argument("--out", default=str(OUT))
    args = parser.parse_args()
    out = build(Path(args.out))
    if not args.no_word and os.name == "nt":
        WORK.mkdir(parents=True, exist_ok=True)
        word_finish(out, CHECK_PDF)
    return 0


if __name__ == "__main__":
    sys.exit(main())
