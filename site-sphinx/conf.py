"""Конфигурация Sphinx + MyST для того же контента, что и в MkDocs."""
import os

project = "Публикация результатов экспериментов"
author = "Павлов Александр Сергеевич"
copyright = "2026, Павлов Александр Сергеевич. Текст — CC BY 4.0, код — MIT"
language = "ru"

extensions = [
    "myst_parser",
    "sphinx.ext.mathjax",
    "sphinxcontrib.bibtex",
    "sphinx_design",
    "sphinx_sitemap",
    "sphinxext.opengraph",
]

source_suffix = {".md": "markdown", ".rst": "restructuredtext"}
root_doc = "index"
exclude_patterns = ["_build", "_generated", "Thumbs.db", ".DS_Store"]
templates_path = ["_templates"]

# --- MyST ---
myst_enable_extensions = ["dollarmath", "amsmath", "colon_fence", "attrs_block", "attrs_inline"]
myst_heading_anchors = 3
myst_footnote_transition = False

# --- Нумерация рисунков, таблиц, листингов и формул ---
numfig = True
math_numfig = True
math_eqref_format = "({number})"
numfig_format = {"figure": "Рисунок %s", "table": "Таблица %s", "code-block": "Листинг %s"}

# --- Формулы: локальная копия MathJax вместо CDN ---
mathjax_path = "mathjax/tex-svg.js"

# --- Библиография ---
bibtex_bibfiles = ["../references.bib"]
bibtex_default_style = "unsrt"
bibtex_reference_style = "author_year"

# --- HTML ---
html_theme = "furo"
html_title = project
html_static_path = ["_static"]
html_extra_path = ["_extra"]
html_css_files = ["extra.css"]
html_last_updated_fmt = "%Y-%m-%d"
# Базовый URL задаётся из окружения (GitHub Pages / Helios), нужен sitemap и og:url.
html_baseurl = os.environ.get("SPHINX_BASEURL", "http://127.0.0.1:8001/")
sitemap_url_scheme = "{link}"
ogp_site_url = html_baseurl
ogp_type = "article"
ogp_enable_meta_description = True
ogp_social_cards = {"enable": False}

html_context = {
    "citation": {
        "title": "Сравнение генераторов статических сайтов для публикации результатов экспериментов",
        "authors": ["Павлов, Александр Сергеевич"],
        "orcid": "https://orcid.org/0000-0000-0000-0000",
        "date": "2026-09-29",
        "license": "https://creativecommons.org/licenses/by/4.0/",
    }
}
