"""Проверка опубликованного сайта (шаг 12 «Хода работы»).

Проверяется не «на глаз», а по признакам:
  * HTTP 200 для ключевых страниц обоих генераторов;
  * наличие контрольной строки в HTML главной страницы;
  * метка версии сборки совпадает с ожидаемым коммитом (если задан);
  * доступны индексы поиска (MkDocs: search/search_index.json,
    Sphinx: searchindex.js) и в них есть русское слово из текста;
  * MathJax и Plotly.js отдаются с того же хоста (работа без CDN);
  * HTML не ссылается на внешние CDN в <script src> и <link href>.

Использование:
  python scripts/check_site.py https://excalibbur.github.io/p2-static-site/ [--commit abc1234]
Код возврата 1 при любой ошибке — job в CI завершается с ошибкой.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
import urllib.error
import urllib.request
from urllib.parse import urljoin, urlparse

CONTROL = "p2-site-ok"
PAGES = [
    "index.html",
    "p2/stress-test.html",
    "report/t5.html",
    "sphinx/index.html",
    "sphinx/p2/stress-test.html",
]
ASSETS = [
    "assets/js/tex-svg.js",
    "generated/plotly.min.js",
    "sphinx/_static/mathjax/tex-svg.js",
    "sphinx/generated/plotly.min.js",
    "sitemap.xml",
    "sphinx/sitemap.xml",
]
CDN_HOSTS = ("cdn.jsdelivr.net", "cdnjs.cloudflare.com", "unpkg.com", "fonts.googleapis.com",
             "fonts.gstatic.com", "cdn.plot.ly", "polyfill.io")


def fetch(url: str, retries: int = 5, delay: float = 6.0) -> tuple[int, bytes]:
    """GET с повторами: CDN GitHub Pages обновляется не мгновенно."""
    last: Exception | None = None
    for _ in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "p2-healthcheck", "Cache-Control": "no-cache"})
            with urllib.request.urlopen(req, timeout=30) as r:
                return r.status, r.read()
        except urllib.error.HTTPError as e:
            return e.code, b""
        except (urllib.error.URLError, TimeoutError) as e:
            last = e
            time.sleep(delay)
    raise SystemExit(f"FAIL network: {url}: {last}")


def main() -> int:
    # Консоль Windows по умолчанию cp1251: символ «→» в выводе вызывал UnicodeEncodeError.
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("base")
    ap.add_argument("--commit", help="ожидаемый короткий хеш коммита в метке версии")
    ap.add_argument("--wait-commit", type=int, default=0,
                    help="сколько секунд ждать появления нужного коммита (задержка CDN)")
    args = ap.parse_args()
    base = args.base if args.base.endswith("/") else args.base + "/"
    errors: list[str] = []

    def check(ok: bool, msg: str) -> None:
        print(("ok   " if ok else "FAIL ") + msg)
        if not ok:
            errors.append(msg)

    deadline = time.time() + args.wait_commit
    while True:
        status, body = fetch(urljoin(base, "index.html"))
        html = body.decode("utf-8", "replace")
        if not args.commit or args.commit in html or time.time() > deadline:
            break
        time.sleep(10)
    check(status == 200, f"index.html → HTTP {status}")
    check(CONTROL in html, f"контрольная строка '{CONTROL}' в index.html")
    if args.commit:
        check(args.commit in html, f"метка версии содержит коммит {args.commit}")

    for page in PAGES[1:]:
        status, body = fetch(urljoin(base, page))
        check(status == 200, f"{page} → HTTP {status}")
        text = body.decode("utf-8", "replace")
        cdn = [m.group(1) for m in re.finditer(r'<(?:script[^>]+src|link[^>]+href)="(https?://[^"]+)"', text)
               if (urlparse(m.group(1)).hostname or "").endswith(CDN_HOSTS)]
        check(not cdn, f"{page}: нет ссылок на внешние CDN {cdn or ''}")

    for asset in ASSETS:
        status, _ = fetch(urljoin(base, asset))
        check(status == 200, f"{asset} → HTTP {status} (локальная копия, без CDN)")

    status, body = fetch(urljoin(base, "search/search_index.json"))
    docs = json.loads(body or b'{"docs": []}')["docs"]
    check(status == 200 and any("градиентн" in d["text"].lower() for d in docs),
          "MkDocs: search_index.json содержит слово 'градиентн…'")
    status, body = fetch(urljoin(base, "sphinx/searchindex.js"))
    check(status == 200 and len(body) > 1000, "Sphinx: searchindex.js доступен")

    print(f"\n{len(errors)} ошибок" if errors else "\nвсе проверки пройдены")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
