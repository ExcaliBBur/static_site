"""Ожидание завершения N-го запуска workflow по публичной веб-странице Actions.

API GitHub без токена ограничен 60 запросами в час; страница Actions — нет.
python scripts/wait_run.py <workflow.yml> <номер запуска> [таймаут, с]
"""
import re
import sys
import time

from playwright.sync_api import sync_playwright

wf, num = sys.argv[1], sys.argv[2]
deadline = time.time() + int(sys.argv[3] if len(sys.argv) > 3 else 900)
url = f"https://github.com/ExcaliBBur/static_site/actions/workflows/{wf}"
with sync_playwright() as p:
    b = p.chromium.launch(channel="chrome")
    pg = b.new_page(locale="en-US")
    while True:
        pg.goto(url, wait_until="domcontentloaded")
        pg.wait_for_timeout(3000)
        text = pg.inner_text("main")
        m = re.search(rf"#{num}: (Completed|completed|Failed|failed|Cancelled|cancelled)[^\n]*", text)
        if m or time.time() > deadline:
            print(m.group(0) if m else "timeout")
            links = pg.eval_on_selector_all("a[href*='/actions/runs/']", "els => els.map(e => e.href)")
            print(sorted({l for l in links if re.search(r"/runs/\d+$", l)}, reverse=True)[0])
            break
        time.sleep(30)
    b.close()
