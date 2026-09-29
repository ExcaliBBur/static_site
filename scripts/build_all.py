"""Полная сборка: prepare -> MkDocs -> Sphinx -> public/.

public/          — MkDocs + Material (основной сайт)
public/sphinx/   — Sphinx + MyST (тот же контент)

Строгий режим обязателен: mkdocs build --strict и sphinx-build -W
превращают предупреждения (битые ссылки, якоря) в ошибку сборки.

Переменные окружения:
  SITE_URL        — канонический адрес сайта (со слешем в конце)
  SKIP_PREPARE=1  — не перезапускать scripts/prepare.py
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"


def run(cmd: list[str], cwd: Path, env: dict | None = None) -> float:
    print("$", " ".join(cmd), flush=True)
    t0 = time.perf_counter()
    subprocess.run(cmd, cwd=cwd, check=True, env=env)
    return time.perf_counter() - t0


def main() -> None:
    py = sys.executable
    site_url = os.environ.get("SITE_URL", "http://127.0.0.1:8000/")
    env = dict(os.environ, SITE_URL=site_url, SPHINX_BASEURL=site_url + "sphinx/")

    timings = {}
    if os.environ.get("SKIP_PREPARE") != "1":
        timings["prepare"] = run([py, "scripts/prepare.py"], ROOT, env)
    timings["mkdocs"] = run(
        [py, "-m", "mkdocs", "build", "--strict", "--clean", "-d", "site"],
        ROOT / "site-mkdocs",
        env,
    )
    shutil.rmtree(ROOT / "site-sphinx" / "_build", ignore_errors=True)
    timings["sphinx"] = run(
        [py, "-m", "sphinx", "-W", "--keep-going", "-q", "-b", "html", ".", "_build/html"],
        ROOT / "site-sphinx",
        env,
    )

    if PUBLIC.exists():
        shutil.rmtree(PUBLIC)
    shutil.copytree(ROOT / "site-mkdocs" / "site", PUBLIC)
    shutil.copytree(ROOT / "site-sphinx" / "_build" / "html", PUBLIC / "sphinx")
    # .nojekyll: GitHub Pages не должен обрабатывать каталоги с '_' (_static Sphinx)
    (PUBLIC / ".nojekyll").touch()

    for k, v in timings.items():
        print(f"{k:8s} {v:6.2f} s")


if __name__ == "__main__":
    main()
