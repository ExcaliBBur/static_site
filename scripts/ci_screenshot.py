"""Скриншот страницы запуска GitHub Actions (публичный репозиторий, без входа).

python scripts/ci_screenshot.py <run_id> <имя_файла> [<job_id>]
"""
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

REPO = "ExcaliBBur/static_site"
run_id, name = sys.argv[1], sys.argv[2]
job = sys.argv[3] if len(sys.argv) > 3 else None
url = f"https://github.com/{REPO}/actions/runs/{run_id}" + (f"/job/{job}" if job else "")
out = Path(__file__).resolve().parents[1] / "report" / "img" / f"{name}.png"
with sync_playwright() as p:
    b = p.chromium.launch(channel="chrome")
    pg = b.new_page(viewport={"width": 1400, "height": 1000}, color_scheme="light", locale="en-US")
    pg.goto(url, wait_until="networkidle")
    pg.wait_for_timeout(2000)
    pg.screenshot(path=str(out), full_page=False)
    b.close()
print(out)
