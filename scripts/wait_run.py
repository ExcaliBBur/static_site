"""Ожидание завершения последнего запуска workflow по публичной веб-странице.

API GitHub без токена ограничен 60 запросами в час; веб-страница — нет.
Статус берётся из aria-label значка запуска («completed successfully»,
«failed», «in progress»), а не из заголовка: у workflow_run заголовок
сам содержит слово «completed».

python scripts/wait_run.py <workflow.yml> [таймаут, с]
"""
import re
import sys
import time

from playwright.sync_api import sync_playwright

wf = sys.argv[1]
deadline = time.time() + int(sys.argv[2] if len(sys.argv) > 2 else 900)
url = f"https://github.com/ExcaliBBur/static_site/actions/workflows/{wf}"
with sync_playwright() as p:
    b = p.chromium.launch(channel="chrome")
    pg = b.new_page(locale="en-US")
    while True:
        pg.goto(url, wait_until="domcontentloaded")
        pg.wait_for_timeout(3000)
        row = pg.locator("[id^='check_suite_']").first
        label = row.locator("svg[aria-label]").first.get_attribute("aria-label") or ""
        link = row.locator("a[href*='/actions/runs/']").first.get_attribute("href")
        done = not re.search(r"progress|running|queued|pending|waiting", label, re.I)
        if done or time.time() > deadline:
            print(label or "timeout", "https://github.com" + (link or ""))
            break
        time.sleep(30)
    b.close()
