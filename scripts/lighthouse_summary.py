"""Сводка JSON-отчётов Lighthouse: аннотации ::notice в stdout и Markdown-таблица в файл.

python scripts/lighthouse_summary.py <каталог с *.json> <файл для Markdown-таблицы>
"""
import json
import sys
from pathlib import Path

CATS = ["performance", "accessibility", "best-practices", "seo"]
METRICS = ["first-contentful-paint", "largest-contentful-paint", "total-blocking-time",
           "cumulative-layout-shift", "speed-index"]

rows = []
for f in sorted(Path(sys.argv[1]).glob("*.json")):
    d = json.loads(f.read_text(encoding="utf-8"))
    cats = {c: round(d["categories"][c]["score"] * 100) for c in CATS}
    met = {m: d["audits"][m]["displayValue"] for m in METRICS}
    kib = round(d["audits"]["total-byte-weight"]["numericValue"] / 1024)
    rows.append((f.stem, cats, met, kib, d["lighthouseVersion"]))
    # Аннотация видна на странице запуска без входа в GitHub
    print(f"::notice title=lighthouse {f.stem}::" + " ".join(f"{c}={v}" for c, v in cats.items())
          + " " + " ".join(f"{m}={v}" for m, v in met.items()) + f" transfer_kib={kib}")

out = ["| Страница | Perf | A11y | BP | SEO | FCP | LCP | TBT | CLS | SI | Передано, КиБ |",
       "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
for name, c, m, kib, _ in rows:
    out.append(f"| {name} | {c['performance']} | {c['accessibility']} | {c['best-practices']} | {c['seo']} | "
          + " | ".join(m[x] for x in METRICS) + f" | {kib} |")
if rows:
    out.append(f"\nLighthouse {rows[0][4]}")
with open(sys.argv[2], "a", encoding="utf-8") as fh:
    fh.write("\n".join(out) + "\n")
