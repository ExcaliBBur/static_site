"""Подготовка контента перед сборкой обоих сайтов.

1. Читает data/dataset.csv, обучает линейную регрессию градиентным спуском
   с тремя скоростями обучения и находит аналитическое решение МНК.
2. Строит статический (matplotlib) и интерактивный (Plotly) графики.
3. Формирует таблицу результатов с объединёнными ячейками в двух вариантах:
   HTML (MkDocs) и grid table reStructuredText (Sphinx).
4. Пишет метку версии: хеш коммита, дату сборки, версию набора данных.
5. Копирует локальную копию MathJax и общий текст отчёта (report/) в оба сайта.

Запуск: python scripts/prepare.py
"""
from __future__ import annotations

import datetime as dt
import json
import os
import shutil
import subprocess
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import plotly.graph_objects as go  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
MK = ROOT / "site-mkdocs"
SX = ROOT / "site-sphinx"

EPOCHS = 60
LEARNING_RATES = [0.01, 0.05, 0.2]
TOL = 1e-4
# Первые три слота валидированной категориальной палитры (CVD-safe попарно).
COLORS = ["#2a78d6", "#eb6834", "#1baf7a"]
OLS_COLOR = "#52514e"


def load_dataset() -> tuple[np.ndarray, np.ndarray, dict]:
    raw = np.loadtxt(DATA / "dataset.csv", delimiter=",", skiprows=1)
    meta = json.loads((DATA / "dataset.meta.json").read_text(encoding="utf-8"))
    return raw[:, 0], raw[:, 1], meta


def mse(y: np.ndarray, y_hat: np.ndarray) -> float:
    return float(np.mean((y - y_hat) ** 2))


def gradient_descent(x, y, xv, yv, lr):
    w = b = 0.0
    train, val = [], []
    for _ in range(EPOCHS):
        err = w * x + b - y
        w -= lr * 2 * np.mean(err * x)
        b -= lr * 2 * np.mean(err)
        train.append(mse(y, w * x + b))
        val.append(mse(yv, w * xv + b))
    converged = next(
        (i + 1 for i in range(1, EPOCHS) if abs(train[i - 1] - train[i]) < TOL), None
    )
    return {"lr": lr, "w": w, "b": b, "train": train, "val": val, "epochs": converged}


def run_experiment():
    x, y, meta = load_dataset()
    x_tr, y_tr, x_v, y_v = x[:160], y[:160], x[160:], y[160:]
    runs = [gradient_descent(x_tr, y_tr, x_v, y_v, lr) for lr in LEARNING_RATES]
    w, b = np.polyfit(x_tr, y_tr, 1)
    ols = {
        "w": float(w),
        "b": float(b),
        "train": mse(y_tr, w * x_tr + b),
        "val": mse(y_v, w * x_v + b),
    }
    return runs, ols, meta


def fmt(v: float) -> str:
    return f"{v:.4f}".replace(".", ",")


def plot_static(runs, ols, out: Path) -> None:
    epochs = np.arange(1, EPOCHS + 1)
    fig, ax = plt.subplots(figsize=(8, 4.5), dpi=150)
    for run, color in zip(runs, COLORS):
        ax.plot(epochs, run["val"], color=color, linewidth=2, label=f"η = {run['lr']}")
    ax.axhline(ols["val"], color=OLS_COLOR, linewidth=1.5, linestyle="--", label="МНК")
    ax.set_yscale("log")
    ax.set_xlim(1, EPOCHS)
    ax.set_xlabel("Эпоха")
    ax.set_ylabel("MSE на контрольной выборке (лог. шкала)")
    ax.set_title("Сходимость градиентного спуска", loc="left", fontsize=12)
    ax.grid(True, which="major", color="#e4e3df", linewidth=0.8)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.legend(frameon=False, loc="upper right")
    fig.tight_layout()
    fig.savefig(out)
    plt.close(fig)


def plot_interactive(runs, ols, out_dir: Path) -> None:
    epochs = list(range(1, EPOCHS + 1))
    fig = go.Figure()
    for run, color in zip(runs, COLORS):
        fig.add_trace(
            go.Scatter(
                x=epochs,
                y=run["val"],
                name=f"η = {run['lr']}",
                mode="lines",
                line={"color": color, "width": 2},
                hovertemplate="%{y:.4f}",
            )
        )
    fig.add_trace(
        go.Scatter(
            x=[1, EPOCHS],
            y=[ols["val"]] * 2,
            name="МНК",
            mode="lines",
            line={"color": OLS_COLOR, "width": 1.5, "dash": "dash"},
            hovertemplate="%{y:.4f}",
        )
    )
    fig.update_layout(
        template="simple_white",
        hovermode="x unified",
        yaxis_type="log",
        yaxis_dtick=1,  # подписи только на степенях 10
        xaxis_title="Эпоха",
        yaxis_title="MSE (контрольная выборка)",
        margin={"l": 60, "r": 20, "t": 20, "b": 50},
        legend={"orientation": "h", "y": 1.08},
        autosize=True,
    )
    fig.update_xaxes(showspikes=True, spikemode="across", spikethickness=1)
    fig.write_html(
        out_dir / "mse_interactive.html",
        include_plotlyjs="directory",  # plotly.min.js рядом, без CDN
        full_html=True,
        config={"responsive": True, "displaylogo": False},
        default_height="420px",
    )


def table_html(runs, ols) -> str:
    rows = []
    for i, r in enumerate(runs):
        method = '<td rowspan="3">Градиентный спуск</td>' if i == 0 else ""
        rows.append(
            f"<tr>{method}<td>{fmt(r['lr'])}</td><td>{fmt(r['train'][-1])}</td>"
            f"<td>{fmt(r['val'][-1])}</td><td>{r['epochs'] or '&gt; ' + str(EPOCHS)}</td></tr>"
        )
    rows.append(
        f"<tr><td>МНК (аналитически)</td><td>—</td><td>{fmt(ols['train'])}</td>"
        f"<td>{fmt(ols['val'])}</td><td>—</td></tr>"
    )
    return (
        '<div class="table-wrap">\n<table class="results-table" id="tab-results">\n<thead>\n'
        '<tr><th rowspan="2">Метод</th><th rowspan="2">η</th>'
        '<th colspan="2">Итоговая MSE</th><th rowspan="2">Эпох до сходимости</th></tr>\n'
        "<tr><th>обучающая</th><th>контрольная</th></tr>\n</thead>\n<tbody>\n"
        + "\n".join(rows)
        + "\n</tbody>\n</table>\n</div>\n"
    )


def table_rst(runs, ols) -> str:
    """Grid table: единственный способ получить rowspan/colspan в Sphinx без HTML."""
    W = [22, 8, 12, 12, 12]

    def cell(text, width):
        return " " + str(text).ljust(width - 1)

    def line(parts, fill="-"):
        return "+" + "+".join(fill * w for w in parts) + "+"

    out = [
        line(W),
        "|" + cell("Метод", W[0]) + "|" + cell("η", W[1]) + "|"
        + cell("Итоговая MSE", W[2] + W[3] + 1) + "|" + cell("Эпох до", W[4]) + "|",
        "|" + cell("", W[0]) + "|" + cell("", W[1]) + "+" + "-" * W[2] + "+" + "-" * W[3]
        + "+" + cell("сходимости", W[4]) + "|",
        "|" + cell("", W[0]) + "|" + cell("", W[1]) + "|" + cell("обучающая", W[2]) + "|"
        + cell("контрольная", W[3]) + "|" + cell("", W[4]) + "|",
        line(W, "="),
    ]
    for i, r in enumerate(runs):
        label = "Градиентный спуск" if i == 0 else ""
        out.append(
            "|" + cell(label, W[0]) + "|" + cell(fmt(r["lr"]), W[1]) + "|"
            + cell(fmt(r["train"][-1]), W[2]) + "|" + cell(fmt(r["val"][-1]), W[3]) + "|"
            + cell(r["epochs"] or f"> {EPOCHS}", W[4]) + "|"
        )
        if i < len(runs) - 1:
            out.append("|" + " " * W[0] + "+" + "+".join("-" * w for w in W[1:]) + "+")
        else:
            out.append(line(W))
    out.append(
        "|" + cell("МНК (аналитически)", W[0]) + "|" + cell("—", W[1]) + "|"
        + cell(fmt(ols["train"]), W[2]) + "|" + cell(fmt(ols["val"]), W[3]) + "|"
        + cell("—", W[4]) + "|"
    )
    out.append(line(W))
    header = [
        ".. table:: Итоговая ошибка после 60 эпох (объединённые ячейки в grid table)",
        "   :name: tab-results",
        "   :class: results-table",
        "",
    ]
    return "\n".join(header + ["   " + row for row in out]) + "\n"


def build_info(meta: dict) -> dict:
    sha = os.environ.get("GITHUB_SHA")
    if not sha:
        try:
            sha = subprocess.run(
                ["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True, check=True
            ).stdout.strip()
        except (OSError, subprocess.CalledProcessError):
            sha = "unknown"
    return {
        "commit": sha[:7],
        "built": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "dataset": f"{meta['version']} (sha256 {meta['sha256'][:12]})",
    }


def build_info_md(info: dict) -> str:
    return (
        f"Коммит `{info['commit']}` · сборка {info['built']} · "
        f"набор данных v{info['dataset']}\n"
    )


def reset(path: Path) -> Path:
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True)
    return path


def copy_fonts(dst: Path) -> None:
    """Локальные шрифты (woff2 + fonts.css) — сайт не обращается к Google Fonts."""
    dst.mkdir(parents=True, exist_ok=True)
    for f in (ROOT / "vendor" / "fonts").iterdir():
        if f.suffix in (".woff2", ".css"):
            shutil.copy2(f, dst)


def copy_tree(src: Path, dst: Path) -> None:
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst)


def main() -> None:
    runs, ols, meta = run_experiment()
    info = build_info(meta)

    # --- MkDocs ---
    mk_gen = reset(MK / "docs" / "generated")
    plot_static(runs, ols, mk_gen / "mse_curve.png")
    plot_interactive(runs, ols, mk_gen)
    mk_snip = reset(MK / "snippets")
    (mk_snip / "results_table.html").write_text(table_html(runs, ols), encoding="utf-8")
    (mk_snip / "build_info.md").write_text(build_info_md(info), encoding="utf-8")
    (MK / "docs" / "assets" / "js").mkdir(parents=True, exist_ok=True)
    shutil.copy2(ROOT / "vendor" / "mathjax" / "tex-svg.js", MK / "docs" / "assets" / "js")
    copy_fonts(MK / "docs" / "assets" / "fonts")
    copy_tree(ROOT / "report", MK / "docs" / "report")

    # --- Sphinx ---
    sx_gen = reset(SX / "generated")
    shutil.copy2(mk_gen / "mse_curve.png", sx_gen)
    sx_extra = reset(SX / "_extra" / "generated")
    for name in ("mse_interactive.html", "plotly.min.js"):
        shutil.copy2(mk_gen / name, sx_extra)
    sx_inc = reset(SX / "_generated")
    (sx_inc / "results_table.rst").write_text(table_rst(runs, ols), encoding="utf-8")
    (sx_inc / "build_info.md").write_text(build_info_md(info), encoding="utf-8")
    (SX / "_static" / "mathjax").mkdir(parents=True, exist_ok=True)
    shutil.copy2(ROOT / "vendor" / "mathjax" / "tex-svg.js", SX / "_static" / "mathjax")
    copy_fonts(SX / "_static" / "fonts")
    copy_tree(ROOT / "report", SX / "report")

    summary = {
        "build": info,
        "runs": [
            {"lr": r["lr"], "train": r["train"][-1], "val": r["val"][-1], "epochs": r["epochs"]}
            for r in runs
        ],
        "ols": ols,
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
