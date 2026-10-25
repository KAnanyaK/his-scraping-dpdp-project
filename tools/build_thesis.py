"""Build the project report (the thesis) from docs/thesis/ on the School's template.

    python tools/build_thesis.py              # the common copy (PDF + LaTeX zip) and each student's PDF
    python tools/build_thesis.py --common     # the common copy only
    python tools/build_thesis.py --no-pdf     # only the LaTeX zip (no TeX engine needed)

Everything is written to ``final-thesis/``: ``thesis_common.pdf``, ``thesis_common.zip``
(LaTeX) and, beside them, ``thesis_ananya.pdf`` and ``thesis_avanindra.pdf``. A student's
own copy names both students on its title page and that student alone inside: the Declaration
is made by that student ("I ... submitted by me", one signature block), and the Certificate and
the Biodata name that student, as the School's individual copies require. The Word copy, ``thesis_common.docx``, is built from the same sources by
tools/thesis_docx/build_thesis_docx.py.

The School's class file and logo (``Thesis-1.cls``, ``logo.png``) are its
files, not project output, and are kept out of the repository like the review
deck templates (team decision 2026-09-17). Point ``THESIS_TEMPLATE`` at the
folder that holds them, or unpack the template into ``thesis-template/`` at the
repository root (git-ignored).

The build copies ``docs/thesis/`` and the two template files into
``build/thesis/``, regenerates the tables and plot data from the artefacts
(``tools/thesis_tables.py``), and compiles with Tectonic when it is installed
(``TECTONIC`` names the executable if it is not on the path). The zip,
``final-thesis/thesis_common.zip``, holds everything Overleaf needs,
including the School's two files and a ``latexmkrc`` that selects XeLaTeX (the
engine Tectonic uses, so the PDF and an Overleaf build agree): upload it as a
new project and compile.
"""

from __future__ import annotations

import argparse
import ast
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tokenize
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import thesis_tables  # noqa: E402

SOURCE = ROOT / "docs" / "thesis"
BUILD = ROOT / "build" / "thesis"
FINAL = ROOT / "final-thesis"
ZIP = FINAL / "thesis_common.zip"
PDF = FINAL / "thesis_common.pdf"
# Each student's own copy: the file name and the "Name & Reg. No." of its Declaration.
# Each student's own copy: file name -> (biodata position, name, registration number). The title page
# names both students; inside, the Declaration, the Certificate and the Biodata name this student alone.
COPIES = {"ananya": (1, "Ananya Karmakar", "23BLC1017"), "avanindra": (2, "Avanindra Kushwah", "23BLC1089")}
TEMPLATE_FILES = ("Thesis-1.cls", "logo.png")
# Source files the appendix lists verbatim (\lstinputlisting{code/...}), copied at build time.
CODE = {
    "base.py": "src/extraction/base.py",
    "rules_base.py": "src/compliance/rules/base.py",
    "checkers.py": "src/compliance/checkers.py",
    "minimisation.py": "src/compliance/rules/minimisation.py",
    "compliant.py": "src/extraction/techniques/compliant.py",
    "pseudonymise.py": "src/compliance/pseudonymise.py",
}


def template_dir() -> Path:
    here = Path(os.environ.get("THESIS_TEMPLATE") or ROOT / "thesis-template")
    missing = [f for f in TEMPLATE_FILES if not (here / f).exists()]
    if missing:
        sys.exit(f"The School's template files are not in {here} ({', '.join(missing)} missing).\n"
                 "Set THESIS_TEMPLATE to the folder holding Thesis-1.cls and logo.png, or unpack the\n"
                 "template zip into thesis-template/ at the repository root.")
    return here


def tectonic() -> str | None:
    for candidate in (os.environ.get("TECTONIC"), shutil.which("tectonic"),
                      str(Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "tectonic" / "tectonic.exe")):
        if candidate and Path(candidate).exists():
            return candidate
    return None


def code_only(text: str) -> str:
    """The source without its documentation strings, comment-only lines or repeated blank lines."""

    tree = ast.parse(text)
    drop: set[int] = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)) and node.body:
            first = node.body[0]
            if isinstance(first, ast.Expr) and isinstance(first.value, ast.Constant) \
                    and isinstance(first.value.value, str):
                drop.update(range(first.lineno, first.end_lineno + 1))
    lines = text.splitlines()
    for tok in tokenize.generate_tokens(io.StringIO(text).readline):
        if tok.type == tokenize.COMMENT and lines[tok.start[0] - 1].lstrip().startswith("#"):
            drop.add(tok.start[0])
    kept: list[str] = []
    for i, line in enumerate(lines, 1):
        # A blank line is dropped at the start, after another blank, and straight after a block opener
        # (where the documentation string used to be).
        if i in drop or (not line.strip() and (not kept or not kept[-1].strip()
                                                 or kept[-1].rstrip().endswith(":"))):
            continue
        kept.append(line)
    return "\n".join(kept).rstrip() + "\n"


def biodata() -> list[dict] | None:
    """The students' details for the Biodata page, from the git-ignored private folder, if present."""

    path = SOURCE / "private" / "biodata.json"
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))["students"]


def write_biodata() -> None:
    """generated/biodata.tex in the build only: the details are personal data and stay out of git."""

    students = biodata()
    if not students:
        return
    blocks = []
    for macro, s in zip(("BiodataOne", "BiodataTwo"), students):
        address = r" \\[0.4em] ".join(thesis_tables.tex(line) for line in s.get("address", []))
        photo = f"private/{s['photo']}" if s.get("photo") and (SOURCE / "private" / s["photo"]).exists() else ""
        # \BiodataOne{heading}: chapters/biodata.tex shows one block in a student's own copy, both otherwise.
        blocks.append(rf"\newcommand{{\{macro}}}[1]{{\biodatablock{{#1}}{{{thesis_tables.tex(s['name'])}}}"
                      rf"{{{thesis_tables.tex(s.get('mobile', ''))}}}{{{thesis_tables.tex(s.get('email', ''))}}}"
                      rf"{{{address}}}{{{photo}}}}}")
    (BUILD / "generated" / "biodata.tex").write_text("\n".join(blocks) + "\n", encoding="utf-8", newline="\n")


def stage() -> None:
    if BUILD.exists():
        shutil.rmtree(BUILD)
    shutil.copytree(SOURCE, BUILD, ignore=shutil.ignore_patterns("*.pdf", "*.aux", "*.log"))
    here = template_dir()
    for f in TEMPLATE_FILES:
        shutil.copy2(here / f, BUILD / f)
    (BUILD / "code").mkdir(exist_ok=True)
    for name, src in CODE.items():
        # The documentation strings and comments restate what the chapters say; the listing shows the code.
        text = (ROOT / src).read_text(encoding="utf-8")
        (BUILD / "code" / name).write_text(code_only(text), encoding="utf-8", newline="\n")
    commit = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, capture_output=True,
                            text=True).stdout.strip() or "unknown"
    (BUILD / "generated" / "version.tex").write_text(
        f"\\newcommand{{\\BuildCommit}}{{{commit}}}\n", encoding="utf-8", newline="\n")
    write_biodata()
    # Overleaf reads latexmkrc: compile with XeLaTeX, as Tectonic does here.
    (BUILD / "latexmkrc").write_text("$pdf_mode = 5;\n", encoding="utf-8", newline="\n")


def compile_pdf(engine: str, target: Path = PDF) -> Path:
    proc = subprocess.run([engine, "-X", "compile", "--keep-logs", "main.tex"], cwd=BUILD,
                          capture_output=True, text=True, encoding="utf-8", errors="replace")
    log = (BUILD / "main.log").read_text(encoding="utf-8", errors="replace") if (BUILD / "main.log").exists() else ""
    if proc.returncode != 0:
        print(proc.stdout[-4000:], proc.stderr[-4000:], sep="\n")
        sys.exit("Tectonic failed; the log is build/thesis/main.log")
    over = re.findall(r"Overfull \\hbox \(([\d.]+)pt too wide\)", log)
    wide = [float(x) for x in over if float(x) > 2.0]
    undefined = sorted(set(re.findall(r"(?:Reference|Citation) `([^']+)' .*undefined", log)))
    print(f"  compiled: {len(wide)} overfull boxes over 2pt" + (f" (widest {max(wide):.1f}pt)" if wide else ""))
    if undefined:
        print("  undefined references or citations: " + ", ".join(undefined))
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(BUILD / "main.pdf", target)
    return target


def compile_copy(engine: str, key: str) -> Path:
    """A student's own copy: the same build naming that student alone inside (generated/copy.tex)."""

    index, name, reg = COPIES[key]
    switch = BUILD / "generated" / "copy.tex"
    switch.write_text(f"\\newcommand{{\\CopyIndex}}{{{index}}}\n\\newcommand{{\\CopyName}}{{{name}}}\n"
                      f"\\newcommand{{\\CopyReg}}{{{reg}}}\n", encoding="utf-8", newline="\n")
    try:
        return compile_pdf(engine, FINAL / f"thesis_{key}.pdf")
    finally:
        switch.unlink()


def make_zip() -> Path:
    ZIP.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(ZIP, "w", zipfile.ZIP_DEFLATED) as z:
        for path in sorted(BUILD.rglob("*")):
            # the private JSON is the build's input; generated/biodata.tex already carries the page
            if path.is_file() and path.name != "biodata.json" and path.suffix not in {
                    ".pdf", ".log", ".aux", ".blg", ".bbl", ".out", ".toc", ".lof", ".lot"}:
                z.write(path, path.relative_to(BUILD).as_posix())
    return ZIP


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-pdf", action="store_true", help="stage and zip only; do not compile")
    parser.add_argument("--common", action="store_true", help="the common copy only, not the students' own")
    args = parser.parse_args()

    changed = thesis_tables.write()
    print("  tables: " + (", ".join(changed) if changed else "already current"))
    stage()
    if not args.no_pdf:
        engine = tectonic()
        if engine is None:
            print("  Tectonic not found: skipped the PDF (set TECTONIC, or use the Overleaf zip)")
        else:
            print(f"  wrote {compile_pdf(engine).relative_to(ROOT)}")
    print(f"  wrote {make_zip().relative_to(ROOT)}")
    if not args.no_pdf and engine is not None and not args.common:
        for key in COPIES:
            print(f"  wrote {compile_copy(engine, key).relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
