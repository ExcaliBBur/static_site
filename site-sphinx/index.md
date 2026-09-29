# Публикация результатов экспериментов

Учебный сайт по теме «Генераторы статических сайтов на Python».
Это версия, собранная **Sphinx + MyST** (тема Furo); основная версия на
MkDocs + Material расположена <a href="../index.html">уровнем выше</a>.

::::{grid} 1 1 3 3
:gutter: 2

:::{grid-item-card} P2. Стресс-тест
:link: p2/stress-test
:link-type: doc

Формулы, таблица с объединёнными ячейками, графики Matplotlib и Plotly,
листинг, библиография из `.bib`, колонки и сноски на одной странице.
:::

:::{grid-item-card} T5. Публикуемость
:link: report/t5
:link-type: doc

Постоянные ссылки, версии, DOI, ORCID, метаданные, лицензии и FAIR.
:::

:::{grid-item-card} Отчёт
:link: report/index
:link-type: doc

Ход работы, измерения, отладка и выводы.
:::
::::

```{include} _generated/build_info.md
```

Контрольная строка: `p2-site-ok`

```{toctree}
:hidden:
:caption: P2

p2/stress-test
```

```{toctree}
:hidden:
:caption: Отчёт

report/index
report/t5
report/p2
report/debugging
report/conclusion
```

```{toctree}
:hidden:

license
```
