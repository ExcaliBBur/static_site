# Стресс-тест научного контента (Sphinx + MyST)

```{include} ../_generated/build_info.md
```

Страница публикует результаты небольшого вычислительного эксперимента:
обучение линейной регрессии градиентным спуском с разными скоростями обучения
и сравнение с аналитическим решением методом наименьших квадратов (МНК).
Графики и таблица формируются скриптом `scripts/prepare.py` из файла
`data/dataset.csv` на этапе сборки, т. е. числа на странице всегда
соответствуют текущей версии данных и кода {cite:p}`peng2011`.

(setup)=
## Постановка эксперимента

Качество модели $\hat y = wx + b$ оценивается среднеквадратичной ошибкой:

```{math}
:label: eq-mse
\operatorname{MSE}(w, b) = \frac{1}{n}\sum_{i=1}^{n}\left(y_i - w x_i - b\right)^2
```

Параметры обновляются по правилу градиентного спуска со скоростью обучения $\eta$:

```{math}
:label: eq-gd
\begin{aligned}
w &\leftarrow w - \eta\,\frac{\partial\,\mathrm{MSE}}{\partial w}, &
b &\leftarrow b - \eta\,\frac{\partial\,\mathrm{MSE}}{\partial b}.
\end{aligned}
```

Минимизируемый функционал — формула {eq}`eq-mse`, шаг обновления —
формула {eq}`eq-gd`. Подробное обоснование выбора метрики приведено
в учебнике {cite:p}`goodfellow2016`.

(results)=
## Результаты

```{eval-rst}
.. include:: ../_generated/results_table.rst
```

Кривые обучения на контрольной выборке показаны на {numref}`fig-static`;
график построен библиотекой Matplotlib {cite:p}`hunter2007`.

```{figure} ../generated/mse_curve.png
:name: fig-static
:alt: Кривые MSE для трёх скоростей обучения и уровень МНК
:width: 100%

Сходимость градиентного спуска (статический PNG, Matplotlib)
```

```{raw} html
<iframe class="plot-frame" src="../generated/mse_interactive.html"
        title="Интерактивный график MSE" loading="lazy"></iframe>
```

*Тот же результат в Plotly: наведение показывает значения всех серий на эпохе
(подпись не нумеруется: директива `figure` в Sphinx принимает только изображение).*

(code)=
## Реализация

Ядро эксперимента — функция одного прогона градиентного спуска ({numref}`lst-gd`).

```{code-block} python
:caption: Градиентный спуск для парной линейной регрессии (scripts/prepare.py)
:name: lst-gd
:linenos:
:emphasize-lines: 6,7

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

Строки 6–7 реализуют формулу {eq}`eq-gd`.

(discussion)=
## Интерпретация

::::{grid} 1 1 2 2
:gutter: 3

:::{grid-item}
При $\eta = 0{,}2$ градиентный спуск за 39 эпох достигает ошибки
аналитического решения (см. {numref}`tab-results`), тогда как при
$\eta = 0{,}01$ за 60 эпох ошибка остаётся почти вдвое выше.
Малый шаг гарантирует устойчивость, но требует больше итераций[^lr].
Вопросы публикации и цитирования таких результатов разобраны в разделе
[«Постоянные ссылки»](../report/t5.md#1-постоянные-ссылки-и-стабильность-url) отчёта по T5, а принципы FAIR — в работе
{cite:p}`wilkinson2016`.
:::

:::{grid-item}
```{image} ../generated/mse_curve.png
:alt: Кривые MSE
```
:::
::::

[^lr]: При $\eta > 1/\lambda_{\max}$, где $\lambda_{\max}$ — наибольшее
    собственное значение гессиана, итерации расходятся.

## Литература

```{bibliography}
```
