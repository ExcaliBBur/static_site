"""Сводка JSON-отчётов Lighthouse: аннотации ::notice в stdout и Markdown-таблица в файл.

Файлы вида <генератор>_<профиль>_<прогон>.json группируются по
<генератор>_<профиль>; в сводку идут оценки всех прогонов и метрики
медианного по Performance прогона (оценка на мобильном профиле «шумит»).

python scripts/lighthouse_summary.py <каталог с *.json> <файл для Markdown-таблицы>
"""
import json
import sys
from collections import defaultdict
from pathlib import Path

CATS = ["performance", "accessibility", "best-practices", "seo"]
METRICS = ["first-contentful-paint", "largest-contentful-paint", "total-blocking-time",
           "cumulative-layout-shift", "speed-index"]

groups = defaultdict(list)
version = ""
for f in sorted(Path(sys.argv[1]).glob("*.json")):
    d = json.loads(f.read_text(encoding="utf-8"))
    version = d["lighthouseVersion"]
    key = f.stem.rsplit("_", 1)[0] if f.stem.count("_") >= 2 else f.stem
    groups[key].append({
        "cats": {c: round(d["categories"][c]["score"] * 100) for c in CATS},
        "met": {m: d["audits"][m]["displayValue"] for m in METRICS},
        "kib": round(d["audits"]["total-byte-weight"]["numericValue"] / 1024),
    })

out = ["| Страница | Perf (прогоны) | Perf, медиана | A11y | BP | SEO | FCP | LCP | TBT | CLS | SI | Передано, КиБ |",
       "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
for key, runs in groups.items():
    runs.sort(key=lambda r: r["cats"]["performance"])
    med = runs[len(runs) // 2]
    perfs = " / ".join(str(r["cats"]["performance"]) for r in runs)
    c, m = med["cats"], med["met"]
    # Аннотация видна на странице запуска без входа в GitHub
    print(f"::notice title=lighthouse {key}::perf_runs={perfs} median: "
          + " ".join(f"{k}={v}" for k, v in c.items()) + " "
          + " ".join(f"{k}={v}" for k, v in m.items()) + f" transfer_kib={med['kib']}")
    out.append(f"| {key} | {perfs} | {c['performance']} | {c['accessibility']} | {c['best-practices']} | "
               f"{c['seo']} | " + " | ".join(m[x] for x in METRICS) + f" | {med['kib']} |")
if groups:
    out.append(f"\nLighthouse {version}; метрики — медианного по Performance прогона.")
with open(sys.argv[2], "a", encoding="utf-8") as fh:
    fh.write("\n".join(out) + "\n")
