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
html_css_files = ["fonts/fonts.css", "extra.css"]

# Та же палитра, что у MkDocs («подсолнух + малина»), через CSS-переменные Furo.
_HEADINGS = '"Unbounded", "Golos Text", -apple-system, "Segoe UI", sans-serif'
_BODY = '"Golos Text", -apple-system, "Segoe UI", Roboto, sans-serif'
html_theme_options = {
    "light_css_variables": {
        "font-stack": _BODY,
        "font-stack--headings": _HEADINGS,
        "color-brand-primary": "#221a33",
        "color-brand-content": "#c2255c",
        "color-brand-visited": "#8f1a44",
        "color-sidebar-background": "#ffd23f",
        "color-header-background": "#ffd23f",
        "color-header-text": "#221a33",
        "color-header-border": "#f0b400",
        "color-sidebar-background-border": "#f0b400",
        "color-sidebar-link-text": "#221a33",
        "color-sidebar-link-text--top-level": "#221a33",
        "color-sidebar-caption-text": "#5f3dc4",
        "color-sidebar-item-background--hover": "#ffe27f",
        "color-sidebar-search-background": "#fff4c7",
        "color-sidebar-search-border": "#f0b400",
        "color-code-background": "#fff4c7",
        "color-inline-code-background": "#fff4c7",
        "color-table-header-background": "#fff4c7",
        "color-highlighted-background": "#ffe27f",
        "color-admonition-title-background--note": "#fff4c7",
    },
    "dark_css_variables": {
        "font-stack": _BODY,
        "font-stack--headings": _HEADINGS,
        "color-brand-primary": "#ffd23f",
        "color-brand-content": "#ff8fb3",
        "color-brand-visited": "#ffc2d6",
        "color-background-primary": "#1b1528",
        "color-background-secondary": "#221a33",
        "color-sidebar-background": "#2b2146",
        "color-header-background": "#2b2146",
        "color-header-text": "#ffd23f",
        "color-header-border": "#3a2d5c",
        "color-sidebar-background-border": "#3a2d5c",
        "color-sidebar-link-text": "#f1ecfa",
        "color-sidebar-link-text--top-level": "#ffd23f",
        "color-sidebar-caption-text": "#b69cff",
        "color-sidebar-item-background--hover": "#3a2d5c",
        "color-sidebar-search-background": "#1b1528",
        "color-sidebar-search-border": "#3a2d5c",
        "color-sidebar-search-foreground": "#f1ecfa",
        "color-code-background": "#2e2645",
        "color-inline-code-background": "#2e2645",
        "color-table-header-background": "#2e2645",
        "color-highlighted-background": "#4a3a12",
    },
}
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
