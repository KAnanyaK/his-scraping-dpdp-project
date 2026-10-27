"""A timed trial run on the portal: how long each technique takes to access the records and to process them.

    python scripts/time_portal_trial.py         # writes docs/benchmark_results/portal-trial-timing.json

One pass of every job by every technique (an AI model replays its first recorded sample, as the Portal pages
replay it), through a real browser against the locally served fixture portal the Portal v2 replays: 20 records
a module, 10 a page, seed 42, no added latency. Two clocks per run:

  access   the technique's extraction through the browser: the page loads, reading the tables, the search box;
  process  what the pipeline then does with what was read: the seven rules, pseudonymisation, HL7 v2 / FHIR
           shaping and the export audit.

The sign-in and the crawl that finds the modules are timed once, before any job. Wall-clock on this machine:
hardware-dependent, reported beside the recorded figures, never relied on by any score. Each run's page loads
are written too, so a reader can check the trial made the same visits the recorded run made.
"""

from __future__ import annotations

import json
import platform
import sys
import time
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for p in (ROOT, ROOT / "src", ROOT / "scripts"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from compliance.benchmark import bind_subject, necessary_records          # noqa: E402
from compliance.checkers import run_all                                     # noqa: E402
from compliance.models import RecordScope                                   # noqa: E402
from extraction.adapters.mock_his import MockHISDataSource                  # noqa: E402
from extraction.adapters.portal_his import PortalHISDataSource              # noqa: E402
from extraction.metering import MeteredSource                               # noqa: E402
from extraction.techniques import default_techniques                        # noqa: E402
from interop.normalise import audit, normalise                              # noqa: E402
from tools import build_portal_app as v1                                     # noqa: E402
from tools.mock_portal.serve import BackgroundPortal                        # noqa: E402

OUT = ROOT / "docs" / "benchmark_results" / "portal-trial-timing.json"
RECORDS, PAGE_SIZE, SEED = 20, 10, 42


def main() -> int:
    from run_pipeline import TASKS

    source = MockHISDataSource(records_per_layer=RECORDS, seed=SEED)
    runs: dict[str, dict[str, dict]] = {}
    with BackgroundPortal(source, page_size=PAGE_SIZE, latency_ms=0) as portal:
        t0 = time.perf_counter()
        scraper = PortalHISDataSource(portal.url, portal.username, portal.password, authorisation=portal.authorisation)
        crawl_ms = (time.perf_counter() - t0) * 1000
        crawl_pages = scraper.page_loads
        tasks = bind_subject(TASKS, scraper)
        necessary = {t.task_id: necessary_records(t, scraper) for t in tasks}
        techniques = default_techniques(tasks, scraper)
        for n, technique in enumerate(techniques, 1):
            tid = v1._tech_id(technique.name)[0]
            print(f"  [{n:2}/{len(techniques)}] {technique.name}", flush=True)
            for task in tasks:
                for attempt in (1, 2):
                    # A browser that dies mid-run (a detached page on a machine short of memory) is reopened, signed
                    # in again outside the clock, and the run is timed afresh; a second failure stops the trial.
                    try:
                        metered = MeteredSource(scraper)
                        t0 = time.perf_counter()
                        out = technique.extract(metered, task)
                        access_ms = (time.perf_counter() - t0) * 1000
                        break
                    except Exception as exc:                                  # noqa: BLE001 - any browser failure
                        if attempt == 2:
                            raise
                        print(f"      browser failed ({type(exc).__name__}); reopening and timing the run again", flush=True)
                        try:
                            scraper.close()
                        except Exception:                                     # noqa: BLE001
                            pass
                        scraper = PortalHISDataSource(portal.url, portal.username, portal.password,
                                                      authorisation=portal.authorisation)
                pages = metered.cost(set(), 0.0).page_loads
                if necessary[task.task_id] is not None:
                    out.run.scope = RecordScope(records_pulled=metered.records, records_necessary=necessary[task.task_id])
                t0 = time.perf_counter()
                run_all(out.run, out.records)
                shaped = normalise(out)
                audit(out, shaped)
                process_ms = (time.perf_counter() - t0) * 1000
                runs.setdefault(tid, {})[task.task_id] = {
                    "access_ms": round(access_ms, 1), "process_ms": round(process_ms, 1),
                    "pages": pages, "records": metered.records,
                }
        scraper.close()

    data = {
        "generated": date.today().isoformat(),
        "machine": f"{platform.system()} {platform.release()}, {platform.processor() or platform.machine()}",
        "portal": {"records": RECORDS, "page_size": PAGE_SIZE, "seed": SEED, "latency_ms": 0},
        "crawl": {"ms": round(crawl_ms, 1), "pages": crawl_pages},
        "runs": runs,
    }
    OUT.write_text(json.dumps(data, indent=1) + "\n", encoding="utf-8")
    print(f"  wrote {OUT.relative_to(ROOT)}  (crawl {crawl_ms / 1000:.1f} s, {sum(len(v) for v in runs.values())} runs)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
