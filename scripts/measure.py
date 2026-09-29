"""Измерения для P2: время сборки, вес страницы, внешние запросы, мобильная вёрстка.

1. Время сборки: 3 холодные сборки (каталог результата удалён) и 3
   инкрементальные (повторный запуск без изменений) для каждого генератора.
2. Страница стресс-теста открывается в Chrome (Playwright) из public/:
   суммарный вес всех загруженных ресурсов (включая iframe с Plotly),
   число запросов, число внешних запросов (к хостам кроме localhost).
3. Проверка без внешних CDN: все запросы к внешним хостам блокируются,
   проверяется, что формулы отрисованы MathJax и график Plotly построен.
4. Мобильное разрешение 390×844: нет горизонтальной прокрутки страницы,
   двухколоночный блок складывается в одну колонку. Скриншоты — report/img/.

Результат: report/measurements.json (читается отчётом и build_docx.py).
Запуск: python scripts/measure.py  (после python scripts/build_all.py)
"""
from __future__ import annotations

import functools
import http.server
import json
import os
import shutil
import statistics
import subprocess
import sys
import threading
import time
from pathlib import Path
from urllib.parse import urlparse

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
IMG = ROOT / "report" / "img"
PORT = 8799
RUNS = 3

GENERATORS = {
    "mkdocs": {
        "title": "MkDocs + Material",
        "cwd": ROOT / "site-mkdocs",
        "out": ROOT / "site-mkdocs" / "site",
        "cmd": [sys.executable, "-m", "mkdocs", "build", "--strict", "-q", "-d", "site"],
        "page": "p2/stress-test.html",
        "columns": ".grid.two-col",
    },
    "sphinx": {
        "title": "Sphinx + MyST",
        "cwd": ROOT / "site-sphinx",
        "out": ROOT / "site-sphinx" / "_build",
        "cmd": [sys.executable, "-m", "sphinx", "-W", "-q", "-b", "html", ".", "_build/html"],
        "page": "sphinx/p2/stress-test.html",
        "columns": ".sd-row",
    },
}


def dir_size(path: Path) -> int:
    return sum(p.stat().st_size for p in path.rglob("*") if p.is_file())


def time_builds(name: str, g: dict) -> dict:
    env = dict(os.environ, SITE_URL="http://127.0.0.1:8000/", SPHINX_BASEURL="http://127.0.0.1:8000/sphinx/")
    cold, incr = [], []
    for _ in range(RUNS):
        shutil.rmtree(g["out"], ignore_errors=True)
        t0 = time.perf_counter()
        subprocess.run(g["cmd"], cwd=g["cwd"], check=True, env=env, capture_output=True)
        cold.append(time.perf_counter() - t0)
    for _ in range(RUNS):
        t0 = time.perf_counter()
        subprocess.run(g["cmd"], cwd=g["cwd"], check=True, env=env, capture_output=True)
        incr.append(time.perf_counter() - t0)
    html_dir = g["out"] / "html" if name == "sphinx" else g["out"]
    return {
        "cold": cold,
        "cold_mean": statistics.mean(cold),
        "incremental": incr,
        "incremental_mean": statistics.mean(incr),
        "output_bytes": dir_size(html_dir),
        "output_files": sum(1 for p in html_dir.rglob("*") if p.is_file()),
    }


def serve() -> http.server.ThreadingHTTPServer:
    handler = functools.partial(QuietHandler, directory=str(PUBLIC))
    httpd = http.server.ThreadingHTTPServer(("127.0.0.1", PORT), handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return httpd


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):  # noqa: D401
        pass


def load_page(browser, url: str, *, mobile: bool = False, block_external: bool = False, shot: Path | None = None) -> dict:
    ctx = browser.new_context(
        viewport={"width": 390, "height": 844} if mobile else {"width": 1280, "height": 900},
        device_scale_factor=2 if mobile else 1,
        is_mobile=mobile,
        has_touch=mobile,
        color_scheme="light",
    )
    page = ctx.new_page()
    records, blocked = [], []

    if block_external:
        def route(r):
            host = urlparse(r.request.url).hostname
            if host not in ("127.0.0.1", "localhost"):
                blocked.append(r.request.url)
                return r.abort()
            return r.continue_()

        page.route("**/*", route)

    def on_finished(req):
        try:
            sizes = req.sizes()
            body = sizes["responseBodySize"]
        except Exception:  # noqa: BLE001
            body = 0
        records.append({"url": req.url, "type": req.resource_type, "bytes": body})

    page.on("requestfinished", on_finished)
    t0 = time.perf_counter()
    page.goto(url, wait_until="networkidle")
    load_s = time.perf_counter() - t0
    # Дожидаемся MathJax и Plotly во фрейме
    page.wait_for_timeout(1500)
    math = page.evaluate("document.querySelectorAll('mjx-container svg').length")
    raw_tex = page.evaluate(
        "[...document.querySelectorAll('.arithmatex, .math')].filter(e => !e.querySelector('mjx-container')).length"
    )
    plot = 0
    for fr in page.frames:
        if fr.url.endswith("mse_interactive.html"):
            plot = fr.evaluate("document.querySelectorAll('.main-svg').length")
    overflow = page.evaluate("document.documentElement.scrollWidth - window.innerWidth")
    loc = page.locator(".sd-row, .grid.two-col").last
    columns = None
    if loc.count():
        loc.scroll_into_view_if_needed()
        columns = page.evaluate(
            """sel => { const el = document.querySelectorAll(sel);
                        const g = el[el.length - 1];
                        const kids = [...g.children].filter(c => c.offsetParent);
                        return new Set(kids.map(c => Math.round(c.getBoundingClientRect().top))).size === kids.length
                               ? 1 : kids.length; }""",
            ".sd-row, .grid.two-col",
        )
        page.evaluate("window.scrollTo(0, 0)")
    if shot:
        page.screenshot(path=str(shot), full_page=True)
    ctx.close()

    external = [r for r in records if urlparse(r["url"]).hostname not in ("127.0.0.1", "localhost")]
    by_type: dict[str, int] = {}
    for r in records:
        by_type[r["type"]] = by_type.get(r["type"], 0) + r["bytes"]
    return {
        "requests": len(records),
        "bytes": sum(r["bytes"] for r in records),
        "bytes_by_type": by_type,
        "external_requests": len(external),
        "external_hosts": sorted({urlparse(r["url"]).hostname for r in external}),
        "blocked": len(blocked),
        "load_s": load_s,
        "math_rendered": math,
        "math_unrendered": raw_tex,
        "plotly_svg": plot,
        "horizontal_overflow_px": overflow,
        "stacked_columns": columns,
    }


def main() -> None:
    IMG.mkdir(parents=True, exist_ok=True)
    results: dict = {"builds": {}, "pages": {}}
    for name, g in GENERATORS.items():
        print("build timing:", name, flush=True)
        results["builds"][name] = time_builds(name, g)

    # public/ собирается заново, чтобы измерялась ровно текущая версия
    subprocess.run([sys.executable, "scripts/build_all.py"], cwd=ROOT, check=True,
                   env=dict(os.environ, SKIP_PREPARE="1"), capture_output=True)

    httpd = serve()
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(channel="chrome")
            for name, g in GENERATORS.items():
                url = f"http://127.0.0.1:{PORT}/{g['page']}"
                print("page:", url, flush=True)
                results["pages"][name] = {
                    "desktop": load_page(browser, url, shot=IMG / f"p2_{name}_desktop.png"),
                    "mobile": load_page(browser, url, mobile=True, shot=IMG / f"p2_{name}_mobile.png"),
                    "offline_cdn": load_page(browser, url, block_external=True),
                }
            browser.close()
    finally:
        httpd.shutdown()

    out = ROOT / "report" / "measurements.json"
    out.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
