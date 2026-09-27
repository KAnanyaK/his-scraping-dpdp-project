# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

- **The review panel and later readers.** Dr. Manoj Kumar and the VIT SENSE review panel (Review-II 30.09.2026, Review-III 28.10.2026) see the pipeline demonstrated with a presenter driving. Afterwards the guide, examiners and paper readers open the same material on their own, with nobody to explain it. Viewing is mostly on **laptop screens**; projection is the exception.
- **The watcher of the crawl.** For the mock portal the relevant person is someone watching a real browser log in and crawl it (`python scripts/run_pipeline.py --show`), or looking at captures of it. Their job is to follow what the browser is doing: which module, which page of how many, which record, signed in or not.
- **The scraper.** The portal's other reader is the Tier 2 Playwright code (`src/extraction/tier2/`), which reads it exactly as it would a real hospital portal. Any design change is judged by both readers.
- Inside the fiction the portal serves hospital front-desk staff (account `frontdesk`). That is scenery for the fixture, not a user whose job we are designing for.

## Product Purpose

A final-year research project (VIT, SENSE; team Avanindra 23BLC1089 and Ananya 23BLC1017; guide Dr. Manoj Kumar) that extracts data from Hospital Information System portals and scores every extraction technique against seven DPDP Act 2023 rules, with real page loads as cost. The comparison is our compliance-aware technique against publicly available AI agents and a coverage-optimised baseline. A rule-based staff assistant gives role-appropriate steps, gated by the same purpose-limitation check.

The mock portal (`tools/mock_portal/`, Flask, login-gated, served over TLS on loopback) exists so the browser code scrapes something **for real**: real authentication, real DOM traversal, real pagination, real latency. Success for the portal: a watcher can follow the crawl at a glance, and the scraper's results stay unchanged.

## Positioning

The contribution is the compliance work: extraction designed and benchmarked against DPDP from the start, not a wrapper added later. The portal backs up that claim because it is built on one rule: **assume we do not control it.** The scraper holds a username and password and nothing else. If the adapter can read the portal, it is because the adapter does what it would do against a real portal.

## Operating Context

- `python -m tools.mock_portal --records 500 --seed 42 --port 8765` (account `frontdesk` / `letmein`) serves it by hand. `scripts/run_pipeline.py` serves it in a background thread (`serve.BackgroundPortal`) and crawls it: about 2 minutes at the default size, mostly the baseline's page loads. `--show` makes the browser visible and `--records 200` makes the crawl longer.
- Modules use portal vocabulary, not our layer names: Patient Registration `/m/registration/`, Clinical Records `/m/clinical/`, Departmental Orders `/m/departments/`, Billing & Accounts `/m/billing/`, Audit Log `/m/integration/`.
- The portal serves any `HISDataSource` unchanged: synthetic data, the public Synthea export, and a hospital export if one is ever released. It has to hold up at `--records 5000`, where pagination runs for a while.
- `labels=` renders column headers as display text (for example `mrn` → "Patient ID"), so that the adapter's label-to-field aliases get exercised.

## Capabilities and Constraints

**The DOM contract.** The scraper uses generic selectors and text, never ids or data attributes. A redesign must keep all of these true (`src/extraction/tier2/browser.py`, `navigation.py`):

- **Login.** `input[name='username']`, `input[name='password']`, and a `button[type='submit']` or `input[type='submit']`. A rejected login is detected by landing back on `/login` or by a password input still being present.
- **Home.** Every link inside `main` that does not go to `/`, `/login` or `/logout` is treated as a module candidate and gets loaded. A new link inside `main` on the home page costs a page load and changes the crawl and `navigation-map.json`. Site navigation belongs outside `main`.
- **List pages.** The scraper reads the *first* `table` on the page: `thead th` for headers, `tbody tr` / `td` for rows. A blank last header marks the actions column, and the first link in that column's cell is the record's detail link. The text of `main` must still match `page N of M` and `N record(s)`. The pager is the first link in `main` whose text starts with "Next", so no other link in `main` may start with "next".
- **Detail pages.** Name/value rows as `table tbody tr`, with a `th` holding the name and a `td` holding the value.
- **Search.** A GET form with a `q` parameter. Single-patient tasks go through the search box.
- **No hooks for the scraper.** No JSON endpoints, no data attributes, no ids added for the scraper's benefit. URLs stay in portal vocabulary.

**The numbers must not move.** Page loads are the cost metric. `benchmark-portal.{json,md}` and `navigation-map.json` are committed, and CI diffs the regenerated benchmark. A design change is presentation only: after any portal change, the portal tests (`tests/tools/test_mock_portal.py`, `tests/extraction/test_portal_*.py`) and the page-load counts must come out identical.

**Stack.** Jinja templates in `tools/mock_portal/templates/`, with inline CSS in `base.html`. Flask is the only dependency. Any new dependency needs team confirmation first.

**Out of scope for design work.** The review pages (`docs/review/*.html`, built from `tools/*_page.html` + `page_base.css/js`) are **frozen for now**: they were refreshed 2026-09-26 and are touched only on request. The Review deck is locked to the mandatory VIT/SENSE Project-I 2026 template. The staff assistant is kept deliberately small.

## Brand Commitments

- **The portal is not ours and not anyone's.** It stands in for a third-party system, so it carries no project branding, scores, DPDP language or project colours. It uses no real vendor's name or look, to stay consistent with the no-vendor-names convention across code, slides and the report. Its name stays generic ("HIS Portal").
- Copy in the portal speaks the hospital's language ("Authorised staff only. Access is logged."), never the scraper's or the benchmark's.
- Report-facing text uses the group voice ("we"), never first-person singular.

## Evidence on Hand

- Synthetic records (Faker generator; `scripts/generate_dataset.py` → `data/`, git-ignored) and the public Synthea sample (`scripts/fetch_public_dataset.py` → `data/public_synthea/`).
- Committed artefacts: `docs/benchmark_results/benchmark-portal.{json,md}`, `navigation-map.json`, and page captures in `docs/review/img/` (`tools/capture_demo_pages.py`).
- **Absent, and not to be fabricated:** any real hospital portal, real vendor UI, real hospital name or logo, or real patient data. We have no live HIS access and plan as if a hospital dataset never arrives.

## Product Principles

1. **A stranger's portal.** Every change is one a real hospital portal could plausibly have. Nothing is added for the scraper's convenience.
2. **Followable at a glance.** Someone watching the crawl on a laptop can tell where the browser is: which module, page N of M, which record, and whether it is signed in. The demo's claim is a count of page loads, so each load should be visibly distinct.
3. **Presentation only.** Design never changes what the scraper reads or how many pages it loads. The committed numbers are the test.
4. **Holds at scale and on any data.** It works at 5000 records and on whatever fields a source exposes, with no layout that assumes the synthetic columns.

## Accessibility & Inclusion

Viewed mostly on laptop screens, sometimes projected. No formal standard has been set. Watchers read it from a distance and in motion, so legible contrast and readable type are the practical floor.
