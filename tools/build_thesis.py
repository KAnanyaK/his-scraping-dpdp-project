"""Build the project report (the thesis) from docs/thesis/ on the School's template.

    python tools/build_thesis.py              # writes Thesis.pdf and build/thesis-overleaf.zip
    python tools/build_thesis.py --no-pdf     # only the Overleaf zip (no TeX engine needed)

The School's class file and logo (``Thesis-1.cls``, ``logo.png``) are its
files, not project output, and are kept out of the repository like the review
deck templates (team decision 2026-09-17). Point ``THESIS_TEMPLATE`` at the
folder that holds them, or unpack the template into ``thesis-template/`` at the
repository root (git-ignored).

The build copies ``docs/thesis/`` and the two template files into
``build/thesis/``, regenerates the tables and plot data from the artefacts
(``tools/thesis_tables.py``), and compiles with Tectonic when it is installed
(``TECTONIC`` names the executable if it is not on the path). The zip holds
everything Overleaf needs: upload it as a new project and compile with
pdfLaTeX and BibTeX.
"""

from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import thesis_tables  # noqa: E402

SOURCE = ROOT / "docs" / "thesis"
BUILD = ROOT / "build" / "thesis"
ZIP = ROOT / "build" / "thesis-overleaf.zip"
PDF = ROOT / "Thesis.pdf"
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


def stage() -> None:
    if BUILD.exists():
        shutil.rmtree(BUILD)
    shutil.copytree(SOURCE, BUILD, ignore=shutil.ignore_patterns("*.pdf", "*.aux", "*.log"))
    here = template_dir()
    for f in TEMPLATE_FILES:
        shutil.copy2(here / f, BUILD / f)
    (BUILD / "code").mkdir(exist_ok=True)
    for name, src in CODE.items():
        shutil.copy2(ROOT / src, BUILD / "code" / name)


def compile_pdf(engine: str) -> Path:
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
    out = BUILD / "main.pdf"
    shutil.copy2(out, PDF)
    return PDF


def make_zip() -> Path:
    ZIP.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(ZIP, "w", zipfile.ZIP_DEFLATED) as z:
        for path in sorted(BUILD.rglob("*")):
            if path.is_file() and path.suffix not in {".pdf", ".log", ".aux", ".blg", ".bbl", ".out", ".toc",
                                                      ".lof", ".lot"}:
                z.write(path, path.relative_to(BUILD).as_posix())
    return ZIP


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-pdf", action="store_true", help="stage and zip only; do not compile")
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
    return 0


if __name__ == "__main__":
    sys.exit(main())
