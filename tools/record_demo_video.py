"""Record the demonstration video for Review-III: docs/review/video/demo.mp4.

    python tools/record_demo_video.py        # needs Chromium; ffmpeg to convert (FFMPEG, or imageio-ffmpeg)

A silent walk-through recorded by headless Chromium from the offline pages the
review uses, in the order the live demonstration follows: Portal v2 (one job
from the hospital to erasure, ours beside an AI model and the baseline, then
the trap job), the HIS Staff Assistant (a tour per role and a request the
reception desk may not make), and the Report's key figures. Short title cards
separate the parts. Every page shows synthetic data only.

Playwright records WebM; the deck needs MP4 (H.264), so the recording is
converted with ffmpeg when one is available (``FFMPEG`` names the executable;
otherwise the ``imageio-ffmpeg`` package's bundled binary is used). A poster
frame is written beside the video for the deck.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
REVIEW = ROOT / "docs" / "review"
OUT = REVIEW / "video"
SIZE = {"width": 1366, "height": 768}

CARD = """<!doctype html><meta charset="utf-8"><body style="margin:0;height:100vh;display:flex;align-items:center;
justify-content:center;background:#1d2f82;color:#fff;font-family:Calibri,Segoe UI,sans-serif">
<div style="text-align:center;max-width:1000px;padding:0 40px"><div style="font-size:22px;opacity:.75;
letter-spacing:.06em;text-transform:uppercase">{kicker}</div><div style="font-size:46px;font-weight:700;margin-top:14px">
{title}</div><div style="font-size:24px;opacity:.85;margin-top:18px;line-height:1.4">{sub}</div></div></body>"""


def card(page, kicker, title, sub, seconds=4.0):
    page.set_content(CARD.format(kicker=kicker, title=title, sub=sub))
    page.wait_for_timeout(int(seconds * 1000))


def open_page(page, name):
    page.goto((REVIEW / name).resolve().as_uri())
    page.wait_for_load_state("load")
    page.wait_for_timeout(1500)
    page.evaluate("document.activeElement && document.activeElement.blur()")


def keys(page, seq, wait):
    for k in seq:
        page.keyboard.press(k)
        page.wait_for_timeout(int(wait * 1000))


def show_figure(page, fig, seconds):
    page.evaluate(f"document.getElementById('{fig}').scrollIntoView({{behavior: 'smooth', block: 'start'}})")
    page.wait_for_timeout(int(seconds * 1000))


def record(raw_dir: Path) -> Path:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(viewport=SIZE, record_video_dir=str(raw_dir), record_video_size=SIZE,
                                  color_scheme="light")
        page = ctx.new_page()
        card(page, "Review-III  |  SENSE, VIT Chennai", "AI-Driven HIS Management Agent with DPDP-Compliant Web Scraping",
             "Ananya Karmakar (23BLC1017)  &middot;  Avanindra Kushwah (23BLC1089)<br>Guide: Dr. Manoj Kumar", 5)
        card(page, "Part 1", "One job through the whole pipeline",
             "Ours, an AI model told the hospital's policy, and the baseline, replayed from the recorded run:"
             " acquire, extract, score, pseudonymise, shape, export, erase.")
        open_page(page, "portal-v2.html")
        keys(page, ["Space"] * 9, 3.6)
        card(page, "Part 1, continued", "The trap job: a request worded to invite a breach",
             "Claim reconciliation asks to cross-check the invoice against the diagnosis, which billing may not see.", 4)
        open_page(page, "portal-v2.html")
        keys(page, ["j", "j", "j"], 1.0)
        keys(page, ["Space"] * 5, 3.4)
        card(page, "Part 2", "The HIS Staff Assistant",
             "Rule-based, no AI model. Steps are placed on the screens the crawler found; the DPDP gate runs before any detail is asked.")
        open_page(page, "agent-portal.html")
        keys(page, ["t"], 1.5)
        keys(page, ["Space"] * 8, 2.6)
        keys(page, ["Escape", "2", "t"], 1.5)
        keys(page, ["Space"] * 7, 2.6)
        keys(page, ["Escape", "1"], 1.0)
        page.keyboard.press("/")
        page.wait_for_timeout(600)
        page.keyboard.type("what is the patient's diagnosis", delay=70)
        page.keyboard.press("Enter")
        page.wait_for_timeout(6000)
        card(page, "Part 3", "The evidence",
             "Trap runs held, planted instructions, a leaked export assessed, and the HIS update.")
        open_page(page, "report.html")
        for fig, secs in (("fig-forest", 7), ("fig-traps", 6), ("fig-injection", 6), ("fig-breach", 6),
                          ("fig-release", 6), ("fig-scraper", 6), ("fig-assistant", 6)):
            show_figure(page, fig, secs)
        card(page, "Reproduce it", "python scripts/run_pipeline.py",
             "Every number is regenerated from the repository; the AI models replay committed recordings, offline.", 5)
        video = page.video
        ctx.close()
        browser.close()
        return Path(video.path())


def ffmpeg() -> str | None:
    if os.environ.get("FFMPEG"):
        return os.environ["FFMPEG"]
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError:
        return shutil.which("ffmpeg")


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        webm = record(Path(tmp))
        target_webm = OUT / "demo.webm"
        shutil.copy2(webm, target_webm)
    exe = ffmpeg()
    if exe is None:
        print(f"  wrote {target_webm.relative_to(ROOT)} (no ffmpeg found: not converted to MP4)")
        return 0
    mp4 = OUT / "demo.mp4"
    subprocess.run([exe, "-y", "-loglevel", "error", "-i", str(target_webm), "-c:v", "libx264", "-pix_fmt", "yuv420p",
                    "-preset", "slow", "-crf", "26", "-movflags", "+faststart", str(mp4)], check=True)
    subprocess.run([exe, "-y", "-loglevel", "error", "-ss", "2", "-i", str(mp4), "-frames:v", "1",
                    str(OUT / "demo.png")], check=True)
    target_webm.unlink()
    print(f"  wrote {mp4.relative_to(ROOT)} ({mp4.stat().st_size / 1e6:.1f} MB) and demo.png")
    return 0


if __name__ == "__main__":
    sys.exit(main())
