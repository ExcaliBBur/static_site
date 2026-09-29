"""Генерирует синтетический набор данных эксперимента (запускается один раз).

Результат фиксируется в git: data/dataset.csv и data/dataset.meta.json.
Версия набора данных меняется вручную при изменении параметров генерации.
"""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
DATASET_VERSION = "1.0"
SEED = 42
N = 200


def main() -> None:
    rng = np.random.default_rng(SEED)
    x = rng.uniform(0.0, 2.0, N)
    y = 3.0 * x + 2.0 + rng.normal(0.0, 0.5, N)

    DATA.mkdir(exist_ok=True)
    csv_path = DATA / "dataset.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["x", "y"])
        w.writerows([f"{a:.6f}", f"{b:.6f}"] for a, b in zip(x, y))

    meta = {
        "version": DATASET_VERSION,
        "seed": SEED,
        "rows": N,
        "generator": "y = 3x + 2 + N(0, 0.5^2), x ~ U(0, 2)",
        "sha256": hashlib.sha256(csv_path.read_bytes()).hexdigest(),
    }
    (DATA / "dataset.meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(meta, ensure_ascii=False))


if __name__ == "__main__":
    main()
