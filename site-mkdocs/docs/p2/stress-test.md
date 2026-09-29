# Стресс-тест научного контента (MkDocs + Material)

<div class="build-info" markdown>

--8<-- "build_info.md"

</div>

Страница публикует результаты небольшого вычислительного эксперимента:
обучение линейной регрессии градиентным спуском с разными скоростями обучения
и сравнение с аналитическим решением методом наименьших квадратов (МНК).
Графики и таблица формируются скриптом `scripts/prepare.py` из файла
`data/dataset.csv` на этапе сборки, т. е. числа на странице всегда
соответствуют текущей версии данных и кода [@peng2011].

## Постановка эксперимента {#setup}

Качество модели $\hat y = wx + b$ оценивается среднеквадратичной ошибкой:

$$
\begin{equation}
\operatorname{MSE}(w, b) = \frac{1}{n}\sum_{i=1}^{n}\left(y_i - w x_i - b\right)^2
\label{eq:mse}
\end{equation}
$$

Параметры обновляются по правилу градиентного спуска со скоростью обучения $\eta$:

$$
\begin{equation}
\begin{aligned}
w &\leftarrow w - \eta\,\frac{\partial\,\mathrm{MSE}}{\partial w}, &
b &\leftarrow b - \eta\,\frac{\partial\,\mathrm{MSE}}{\partial b}.
\end{aligned}
\label{eq:gd}
\end{equation}
$$

Минимизируемый функционал — формула $\eqref{eq:mse}$, шаг обновления —
формула $\eqref{eq:gd}$. Подробное обоснование выбора метрики приведено
в учебнике [@goodfellow2016].

## Результаты {#results}

/// table-caption
    attrs: {id: tab-results}
Итоговая ошибка после 60 эпох (объединённые ячейки: `rowspan`, `colspan`)
///

--8<-- "results_table.html"

Кривые обучения на контрольной выборке показаны на рисунке 1; график построен
библиотекой Matplotlib [@hunter2007].

![Кривые MSE для трёх скоростей обучения и уровень МНК](../generated/mse_curve.png)
/// figure-caption
    attrs: {id: fig-static}
Сходимость градиентного спуска (статический PNG, Matplotlib)
///

<div class="plot-wrap">
<iframe class="plot-frame" src="../generated/mse_interactive.html"
        title="Интерактивный график MSE" loading="lazy"></iframe>
</div>
/// figure-caption
    attrs: {id: fig-interactive}
Тот же результат в Plotly: наведение показывает значения всех серий на эпохе
///

## Реализация {#code}

Ядро эксперимента — функция одного прогона градиентного спуска (листинг 1).

/// listing-caption
    attrs: {id: lst-gd}
Градиентный спуск для парной линейной регрессии
///

```python linenums="1" title="scripts/prepare.py"
def gradient_descent(x, y, xv, yv, lr):
    w = b = 0.0
    train, val = [], []
    for _ in range(EPOCHS):
        err = w * x + b - y
        w -= lr * 2 * np.mean(err * x)
        b -= lr * 2 * np.mean(err)
        train.append(mse(y, w * x + b))
        val.append(mse(yv, w * xv + b))
    return train, val
```

Строки 6–7 реализуют формулу $\eqref{eq:gd}$.

## Интерпретация {#discussion}

<div class="grid two-col" markdown>

<div markdown>

При $\eta = 0{,}2$ градиентный спуск за 39 эпох достигает ошибки
аналитического решения (см. [таблицу 1](#tab-results)), тогда как при
$\eta = 0{,}01$ за 60 эпох ошибка остаётся почти вдвое выше.
Малый шаг гарантирует устойчивость, но требует больше итераций[^lr].
Вопросы публикации и цитирования таких результатов разобраны в разделе
[«Постоянные ссылки»](../report/t5.md#1-постоянные-ссылки-и-стабильность-url)
отчёта по T5, а принципы FAIR — в работе [@wilkinson2016].

</div>

<div markdown>

![Кривые MSE](../generated/mse_curve.png)

</div>

</div>

[^lr]: При $\eta > 1/\lambda_{\max}$, где $\lambda_{\max}$ — наибольшее
    собственное значение гессиана, итерации расходятся.

## Литература

\bibliography
