# About this repository

A final-year research project at VIT (School of Electronics Engineering, SENSE), by Avanindra (23BLC1089) and Ananya (23BLC1017), guided by Dr. Manoj Kumar.

**What is delivered.** The code, the committed artefacts under `docs/benchmark_results/` and the Report `docs/review/report.html`. Every number in them is regenerated from the repository (see `README.md`, "Run it"). CI reruns the suite and checks that the committed benchmark and the weight sweep reproduce to the number.

**How it was built.** Development was AI-assisted: an AI coding assistant wrote and revised much of the code and documentation under the team's direction and review, and commits carry a `Co-Authored-By` trailer where it did. Separately, AI models are also the *object of study*: the benchmark compares our rule-driven reference technique with publicly available language models given the same job. Their decisions are recorded once and replayed, so nothing in the demos calls a model.

**Working files.** `CLAUDE.md` (the assistant's standing project instructions), `PLAN.md` (the team's completion ledger), `PRODUCT.md` / `DESIGN.md` and `.impeccable/` (design notes and design-tool state) are internal working material. They are kept for transparency and are not part of the deliverable's argument.

**Data.** No real patient data is in this repository. The evaluation runs on generated synthetic records, a locally served fixture portal, and Synthea's public synthetic export. `data/` is git-ignored, and a real export cannot be read unless it passes the handling gate in `src/compliance/handling.py`.

**Licence.** Code: MIT (`LICENSE`). Documentation and artefacts: CC BY 4.0. How to cite: `CITATION.cff`.
