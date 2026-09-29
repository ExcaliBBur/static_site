# Публикация результатов экспериментов: MkDocs vs Sphinx

[![pages](https://github.com/ExcaliBBur/static_site/actions/workflows/pages.yml/badge.svg)](https://github.com/ExcaliBBur/static_site/actions/workflows/pages.yml)
[![helios](https://github.com/ExcaliBBur/static_site/actions/workflows/helios.yml/badge.svg)](https://github.com/ExcaliBBur/static_site/actions/workflows/helios.yml)
[![Content: CC BY 4.0](https://img.shields.io/badge/content-CC%20BY%204.0-lightgrey.svg)](LICENSE-CONTENT)
[![Code: MIT](https://img.shields.io/badge/code-MIT-blue.svg)](LICENSE)

Лабораторная работа «Генераторы статических сайтов на Python»:
исследовательское задание **T5** (публикуемость и цитируемость) и практическое
задание **P2** (стресс-тест научного контента на двух генераторах).

| Площадка | Адрес |
|---|---|
| GitHub Pages, MkDocs + Material | https://excalibbur.github.io/static_site/ |
| GitHub Pages, Sphinx + MyST | https://excalibbur.github.io/static_site/sphinx/ |
| Helios ИТМО (зеркало) | https://se.ifmo.ru/~s335989/p2/ |

## Структура

```
data/                 набор данных эксперимента + метаданные (sha256, версия)
report/               текст отчёта (общий Markdown для обоих генераторов)
scripts/prepare.py    расчёт → графики, таблица, метка версии; раскладка по сайтам
scripts/build_all.py  prepare → mkdocs --strict → sphinx -W → public/
scripts/check_site.py healthcheck: HTTP 200, контрольная строка, поиск, отсутствие CDN
scripts/measure.py    замеры P2 (время сборки, вес, запросы, мобильная вёрстка)
scripts/build_docx.py отчёт в Word
site-mkdocs/          MkDocs + Material (основной сайт)
site-sphinx/          Sphinx + MyST + Furo
vendor/mathjax/       локальная копия MathJax 3.2.2 (работа без CDN)
.github/workflows/    pages.yml (GitHub Pages), helios.yml (rsync на Helios)
```

## Локальная сборка

```bash
python -m virtualenv .venv
.venv/Scripts/activate          # Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
python scripts/build_all.py     # результат в public/
python -m http.server 8000 --directory public
python scripts/check_site.py http://127.0.0.1:8000/
```

Предпросмотр одного генератора с автообновлением:
`python scripts/prepare.py && cd site-mkdocs && mkdocs serve`.

## Лицензии

Текст и рисунки — [CC BY 4.0](LICENSE-CONTENT), код — [MIT](LICENSE),
данные — [CC0 1.0](data/LICENSE). Как цитировать — [CITATION.cff](CITATION.cff).
