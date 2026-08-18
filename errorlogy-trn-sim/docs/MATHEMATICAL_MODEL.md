# Математическая модель TRN-симуляции

Документ согласован с реализацией в `src/trn_sim/` (`model.py`, `metrics.py`, `graph.py`, `config.py`). Обозначения: дискретное время \(t=0,1,\ldots,T\), шаг \(\Delta t\) (`dt`).

---

## 1. Пространство состояний

### 1.1. Множество агентов и граф

\[
\mathcal{A}=\{a_1,\ldots,a_N\},\quad G=(V,E),\quad V=\mathcal{A},\quad |V|=N.
\]

Матрица влияния \(W=[w_{ij}]_{N\times N}\):

\[
w_{ij}\ge 0,\quad \sum_{j=1}^N w_{ij}=1\quad \forall i.
\]

Строки \(W\) нормируются в `graph.normalize_rows`; изолированным узлам добавляется петля \(w_{ii}=1\).

Типы графа (`graph_type`): `ring_lattice`, `watts_strogatz`, `erdos_renyi` — см. `graph.py`.

### 1.2. Вектор состояния агента

\[
x_i(t)=
\begin{bmatrix}
b_i(t) \\
e_i(t) \\
q_i(t) \\
r_i(t) \\
m_i(t) \\
\alpha_i \\
h_i \\
z_i
\end{bmatrix}.
\]

| Компонента | Домен (код) | Роль |
|---|---|---|
| \(b_i\) | \([-1,1]\) | мнение / позиция |
| \(e_i\) | \([0,1]\) | эмоциональная активация |
| \(q_i\) | \([0,1]\) | критическая фильтрация (L4) |
| \(r_i\) | \([0,1]\) | устойчивость (L5) |
| \(m_i\) | \([0,1]\) | меметическая восприимчивость (L2–L3) |
| \(\alpha_i\) | \([0,1]\) | социальная податливость |
| \(h_i\) | \([0.05,1.2]\) | ширина окна bounded confidence |
| \(z_i\) | \([0,1)\) | фиксированная метка для бipolar-поля |

Параметры \(q,r,m,\alpha,h\) инициализируются из нормальных/Beta-распределений с центрами `q_mean`, `r_mean`, `m_mean`, `alpha_mean`, `confidence_h_mean` (`TRNSimulation.__init__`).

### 1.3. Глобальное состояние

\[
\mathbf{x}(t)=\bigl(x_1(t),\ldots,x_N(t)\bigr)\in\mathcal{X}\subseteq [-1,1]^N\times[0,1]^{4N}\times[0,1]^N\times[0.05,1.2]^N.
\]

Скрытые константы запуска: \(\theta=(N,T,\Delta t,\texttt{graph\_type},\ldots)\in\Theta\) — см. `TRNParams`.

---

## 2. Нарративное поле \(P_i(t)\)

Функция `narrative_pole()`; режим `narrative_mode`:

### 2.1. Константное поле

\[
P_i(t)=p_0=\texttt{constant\_pole}\in[-1,1].
\]

### 2.2. Бipolar-поле

\[
P_i(t)=
\begin{cases}
-1, & z_i<0.5,\\
+1, & z_i\ge 0.5.
\end{cases}
\]

Метки \(z_i\) фиксированы на всём горизонте \(T\). Половина агентов «назначена» левому полюсу, половина — правому.

### 2.3. Эхо-поле

\[
\bar b_i(t)=\sum_j w_{ij}b_j(t),\qquad
P_i(t)=\tanh\!\bigl(\chi\,\bar b_i(t)\bigr),\quad \chi=\texttt{echo\_chi}\ge 0.
\]

**Замечание:** при `narrative_mode='bipolar'` параметр \(\chi\) **не входит** в динамику; sweep по \(\chi\) в `stress_config` не меняет траекторию (подтверждено `outputs/stress/chi_h_sweep.csv`).

---

## 3. Социальное влияние (bounded confidence)

\[
S_i(t)=\alpha_i\sum_{j=1}^N w_{ij}\,\kappa_{ij}(t)\,\bigl(b_j(t)-b_i(t)\bigr),
\]

\[
\kappa_{ij}(t)=\exp\!\left(-\frac{\bigl(b_j(t)-b_i(t)\bigr)^2}{2h_i^2}\right).
\]

Реализация: `social_term()` — матричная форма с `diff[i,j]=b_j-b_i`.

**Интерпретация:** при малом \(h_i\) агент «не слышит» далёкие мнения → фрагментация; при большом \(h_i\) — классическое усреднение по соседям (Deffuant–Hegselmann–Krause в непрерывной аппроксимации).

**Важно:** \(q_i,r_i\) **не** входят в \(S_i\); защитный эффект \(q,r\) проявляется только через TRN-член \(I_i\).

---

## 4. TRN-воздействие

\[
I_i(t)=\lambda\,m_i(1-r_i)(1-q_i)\,A_i(t)\,\bigl(P_i(t)-b_i(t)\bigr),
\]

\[
A_i(t)=\sigma\!\bigl(\beta_0+\beta_1 e_i(t)+\beta_2|P_i(t)-b_i(t)|\bigr),\qquad
\sigma(z)=\frac{1}{1+e^{-z}}.
\]

Параметры: \(\lambda=\texttt{lambda\_trn}\ge 0\), \(\beta_0,\beta_1,\beta_2\) — см. `TRNParams`.

**Структура susceptibility:** \(\phi_i=m_i(1-r_i)(1-q_i)\in[0,1]\) — эффективная «открытость» внешнему полю. Высокие \(r_i,q_i\) подавляют TRN; высокие \(m_i\) усиливают.

---

## 5. Динамика мнений и эмоций

### 5.1. Обновление мнения

\[
b_i(t+1)=\mathrm{clip}_{[-1,1]}\!\Bigl[b_i(t)+\Delta t\,\bigl(S_i(t)+I_i(t)+\eta_i(t)\bigr)\Bigr],
\]

\[
\eta_i(t)\sim\mathcal{N}(0,\sigma_b^2),\quad \sigma_b=\texttt{opinion\_noise}.
\]

### 5.2. Обновление эмоции

\[
e_i(t+1)=\mathrm{clip}_{[0,1]}\!\Bigl[e_i(t)+\Delta t\,\bigl(\rho|P_i-b_i|-\delta e_i+\xi_i(t)\bigr)\Bigr],
\]

\[
\xi_i(t)\sim\mathcal{N}(0,\sigma_e^2),\quad \sigma_e=\texttt{emotion\_noise}.
\]

Конфликт \(|P_i-b_i|\) повышает \(e_i\); затухание \(\delta e_i\) стабилизирует эмоцию. Рост \(e_i\) через \(\beta_1\) увеличивает внимание \(A_i\) → положительная обратная связь «конфликт → внимание → TRN».

### 5.3. Порядок шага (`step()`)

1. Вычислить \(P(t)\).
2. \(S(t)\), \(I(t)\); обновить \(b(t+1)\).
3. Обновить \(e(t+1)\) (используется тот же \(P(t)\)).
4. Записать метрики (`record()`).

Начальная запись метрик — до первого `step()` (`run()` вызывает `record()` при \(t=0\)).

### 5.4. Численная схема

- Явный метод Эйлера с фиксированным \(\Delta t=0.08\).
- Проекция (`clip`) после шага — не симplectic; для исследовательских горизонтов \(T\le 200\) достаточно.
- Стохастичность: гауссов шум на \(b,e\); RNG — `numpy.random.Generator(seed)`.
- **Семантика времени:** один вызов `step()` = один такт \(t\to t+1\); физическая длительность \(\Delta t\) безразмерна.

---

## 6. Метрики

Реализация: `metrics.calculate_metrics(b, params)`.

### 6.1. Поляризация и консенсус

\[
\mathrm{Pol}(t)=\mathrm{std}\bigl(b_1(t),\ldots,b_N(t)\bigr),
\]

\[
C(t)=\max\bigl(0,\,1-\mathrm{Pol}(t)\bigr).
\]

### 6.2. Доля крайних мнений

\[
\mathrm{Ext}(t)=\frac{1}{N}\sum_{i=1}^N \mathbf{1}\bigl(|b_i(t)|>\theta_{\mathrm{ext}}\bigr),\quad
\theta_{\mathrm{ext}}=0.65\ \text{(код)}.
\]

### 6.3. Энтропия распределения мнений

Гистограмма \(b\) на 20 бинах \([-1,1]\), \(p_k\) — нормированные частоты:

\[
H(t)=-\sum_{k:\,p_k>0} p_k\log p_k.
\]

### 6.4. Индекс риска TRN

\[
R_{\mathrm{TRN}}=\frac{\lambda\,\bar m\,(1-\bar r)\,(1-\bar q)\,\chi}{\bar h+\varepsilon},\quad
\varepsilon=10^{-6},
\]

где \(\bar m,\bar r,\bar q,\bar h\) — **параметры запуска** (`m_mean`, `r_mean`, `q_mean`, `confidence_h_mean`), не выборочные средние по агентам.

**Смысл:** безразмерный скаляр «давления среды»; не вероятность и не \(\mu\) из таксономии Errorlogy.

### 6.5. Флаг антиконсенсуса

\[
\mathcal{A}(t)=\mathbf{1}\Bigl[C(t)<0.45\ \land\ \mathrm{Pol}(t)>0.44\ \land\ \mathrm{Ext}(t)>0.35\Bigr]\in\{0,1\}.
\]

**Логическое упрощение:** при определении \(C=1-\mathrm{Pol}\) условие \(C<0.45\) эквивалентно \(\mathrm{Pol}>0.55\), откуда \(\mathrm{Pol}>0.44\) следует автоматически. Связующие пороги:

\[
\mathcal{A}(t)=1 \iff C(t)<0.45\ \land\ \mathrm{Ext}(t)>0.35.
\]

Порог \(\mathrm{Pol}>0.44\) сохранён в коде для явной читаемости и возможного расширения определения \(C\).

**Происхождение порогов:** эвристическая калибровка под бipolar stress-сценарий (см. §10). Порог \(\theta_{\mathrm{ext}}=0.65\) отсекает «умеренных» (\(|b|\le 0.65\)) при \(\mathrm{Pol}\approx 0.55\).

**Не реализовано в коде:** расширенное условие \(K_{\mathrm{clusters}}\ge 3\) из ранних черновиков — требует отдельной кластеризации по \(b\).

---

## 7. Неподвижные точки и устойчивость

### 7.1. Режим без TRN (\(\lambda=0\))

Динамика:

\[
b_i(t+1)\approx b_i(t)+\Delta t\,S_i(t)+\eta_i.
\]

При \(h_i\) достаточно большом и связном графе классический аргумент Deffuant: все \(b_i\) сходятся к общему значению \(b^\*\) (консенсус). Линейзация около \(b^\*\):

\[
\Delta b_i \leftarrow \Delta t\,\alpha_i\sum_j w_{ij}(b_j-b_i).
\]

В матричной форме \(\dot{\mathbf{b}}=-L_W\mathbf{b}\) (упрощённо), где \(L_W\) — laplacian-подобный оператор. Спектр на связном графе: нулевое собственное значение (единый консенсус) устойчиво при \(\Delta t\,\alpha_{\max}<2/\lambda_{\max}(L)\).

**Эмпирика (`stress`, \(\lambda=0\)):** \(C_{\mathrm{final}}\approx 0.97\), \(\mathrm{Pol}\approx 0.03\), \(\mathcal{A}=0\).

### 7.2. Режим с TRN и bipolar-полем

Неподвижные точки (формально, без шума):

\[
S_i+I_i=0\quad \text{или}\quad b_i\in\{-1,+1\}\ \text{(граница clip)}.
\]

При сильном \(\lambda\) и низких \(q,r\): притяжение к **двум кластерам** \(b\approx -1\) и \(b\approx +1\) согласно знаку \(P_i\). Это не антиконсенсус в социологическом смысле «много лагерей», а **бipolar lock-in**.

**Lyapunov-эскиз:** функция

\[
V(\mathbf{b})=\frac{1}{N}\sum_i (b_i-P_i)^2
\]

убывает вдоль чистого TRN-потока \(\dot b_i=\lambda\phi_i A_i(P_i-b_i)\). Социальный член может увеличивать \(V\). Конкуренция задаёт баланс; при \(\lambda>\lambda_{\mathrm{crit}}\) доминирует TRN → \(V\to 0\) внутри каждой половины.

### 7.3. Условие бифуркации (mean-field)

Оценка порядка величины для bipolar-режима. Пусть \(b_i\approx 0\) (начальное распределение \(\mathcal{N}(0,0.18)\)). Линейизация TRN:

\[
I_i\approx \lambda\,\bar\phi\,\bar A\,P_i,\quad
\bar\phi=\bar m(1-\bar r)(1-\bar q),\quad
\bar A\approx\sigma(\beta_0+\beta_1\bar e+\beta_2).
\]

Социальное «восстановление» к локальному среднему масштаба \(\sim \bar\alpha\,\mathrm{Pol}/\bar h\). Критическое \(\lambda\) из баланса:

\[
\lambda_{\mathrm{crit}}^{\mathrm{MF}}\sim\frac{\bar\alpha\,\bar h}{\bar\phi\,\bar A\,|P|}
\approx\frac{0.55\times 0.35}{0.75^3\times 0.92\times 1}\approx 0.49.
\]

Stress-параметры: \(\bar m=0.75\), \(\bar q=\bar r=0.25\), \(\bar h=0.35\), `narrative_mode=bipolar`.

---

## 8. Фазовый переход по \(\lambda\)

### 8.1. Эмпирические данные (`configs/stress_config.json`, `outputs/stress/lambda_sweep.csv`, \(R=3\) повтора)

| \(\lambda\) | \(C_{\mathrm{mean}}\) | \(\mathrm{Pol}_{\mathrm{mean}}\) | \(\mathrm{Ext}_{\mathrm{mean}}\) | \(R_{\mathrm{TRN}}\) | \(\mathcal{A}\)-rate |
|---:|---:|---:|---:|---:|---:|
| 0.0 | 0.970 | 0.030 | 0.000 | 0.00 | 0.0 |
| 0.2 | 0.650 | 0.350 | 0.021 | 0.60 | 0.0 |
| **0.4** | **0.223** | **0.777** | **0.923** | **1.21** | **1.0** |
| 0.6 | 0.103 | 0.897 | 0.991 | 1.81 | 1.0 |
| 1.0 | 0.035 | 0.965 | 1.000 | 3.01 | 1.0 |
| 2.0 | 0.009 | 0.991 | 1.000 | 6.03 | 1.0 |

**Вывод:** резкий переход между \(\lambda=0.2\) и \(\lambda=0.4\):

\[
\lambda_{\mathrm{crit}}^{\mathrm{emp}}\in(0.2,\,0.4),\quad \text{оценка}\ \lambda_{\mathrm{crit}}\approx 0.35\pm 0.05.
\]

При \(\lambda=0.2\) высокая поляризация (\(\mathrm{Pol}=0.35\)), но \(\mathrm{Ext}<0.35\) → \(\mathcal{A}=0\). При \(\lambda=0.4\) все три метрики пересекают пороги → \(\mathcal{A}=1\).

Согласование с \(R_{\mathrm{TRN}}\): переход при \(R_{\mathrm{TRN}}\approx 1.2\); эвристическое правило

\[
R_{\mathrm{TRN}}\gtrsim 1 \quad\Rightarrow\quad \text{высокий риск антиконсенсуса (bipolar stress)}.
\]

### 8.2. Контрольный sweep (`echo`-режим, `outputs/lambda_sweep.csv`)

При `narrative_mode='echo'`, \(\bar q=\bar r=0.45\), \(\bar m=0.55\): даже при \(\lambda=1.2\) — \(C\approx 0.90\), \(\mathcal{A}=0\). Переход **не универсален по \(\lambda\)**; зависит от режима поля и susceptibility.

### 8.3. Grid \(q,r\) при \(\lambda=0\)

`outputs/stress/qr_grid.csv`: все комбинации дают \(C\approx 0.978\), \(\mathcal{A}=0\). Параметры \(q,r\) не влияют на динамику при \(\lambda=0\) (ожидаемо из §4). Для оценки защиты \(q,r\) sweep нужно проводить при \(\lambda\ge\lambda_{\mathrm{crit}}^{\mathrm{emp}}\).

---

## 9. Таксономия параметров (L1–L5)

| Слой | Параметры агента | Гиперпараметры `TRNParams` | Влияние на метрики |
|---|---|---|---|
| L1 Reactive | \(e_i\), \(\rho,\delta\) | `rho`, `delta`, `emotion_noise` | Косвенно через \(A_i\) → \(I_i\); при большом \(\rho\) усиливает TRN-петлю |
| L2 Mimetic | \(m_i\), \(\alpha_i\) | `m_mean`, `m_std`, `alpha_mean` | \(m\) — прямой множитель \(I\); \(\alpha\) — скорость социального консенсуса |
| L3 Narrative | \(P_i\), \(\chi\) | `narrative_mode`, `echo_chi`, `constant_pole` | Задаёт направление поля; \(\chi\) активен только в `echo` |
| L4 Reflective | \(q_i\) | `q_mean`, `q_std` | Подавляет \(I_i\) через \((1-q_i)\) |
| L5 Strategic | \(r_i\) | `r_mean`, `r_std` | Подавляет \(I_i\) через \((1-r_i)\) |
| Социальная топология | \(w_{ij}\) | `graph_type`, `k_neighbors`, `rewiring_p` | Фрагментация при малом \(h\) + низкая связность |
| Bounded confidence | \(h_i\) | `confidence_h_mean`, `confidence_h_std` | Малый \(\bar h\) → слабее \(S_i\) между кластерами; делитель \(R_{\mathrm{TRN}}\) |
| TRN-среда | \(\lambda\) | `lambda_trn` | Основной рычаг фазового перехода |
| Внимание | \(\beta_0,\beta_1,\beta_2\) | одноимённые | Порог и усиление \(A_i\) |

---

## 10. Связь с Errorlogy (EGD)

Исследовательский мост: `bridge/egd_stub.py` (не подключён к MAS).

| MAS EGD (концепт) | TRN-параметр | Замечание |
|---|---|---|
| `echo_room_pressure` \(\in[0,1]\) | \(\lambda\), \(\chi\) | Эвристика: \(\lambda=0.15+0.85\cdot\)pressure, \(\chi=0.5+3.5\cdot\)pressure |
| `hidden_signal_prior` \(\in[0,1]\) | \(\bar h\) | Узкое окно доверия: \(h=\max(0.15,\,0.55-0.35\cdot\)prior\()\) |

**Не смешивать:** \(R_{\mathrm{TRN}}\), \(\mu\) из таксономии v16 и вероятностные оценки MAS — разные величины. TRN-симуляция не выдаёт юридических или каузальных выводов.

---

## 11. Выходные таблицы CLI

1. **Покомponentный отчёт** — `sample_metrics.csv`, `*_raw.csv`; поля `data/output_schema.json`; `TRNSimulation.final_report()`.
2. **Агрегаты sweep** — `lambda_sweep.csv`, `qr_grid.csv`, `chi_h_sweep.csv`; `experiments.aggregate()`.

Валидация: `python scripts/validate_outputs.py outputs --recursive`.

---

## 12. Открытые проблемы и фalsifiable гипотезы

| # | Гипотеза | Эксперимент, опровергающий |
|---|---|---|
| H1 | \(\lambda_{\mathrm{crit}}\) монотонно убывает при росте \(\bar m(1-\bar r)(1-\bar q)\) | Grid по \(q,r\) **при фиксированном** \(\lambda=0.5\); ожидание: высокие \(q,r\) восстанавливают консенсус |
| H2 | \(R_{\mathrm{TRN}}>1\) достаточен для \(\mathcal{A}=1\) в bipolar stress | Найти counterexample: \(\lambda,\bar m,\bar q,\bar r,\chi,\bar h\) с \(R_{\mathrm{TRN}}>1\) но \(\mathcal{A}=0\) |
| H3 | Echo-режим даёт переход при \(\chi\uparrow\) при \(\lambda>0\) | Sweep \(\chi\) с `narrative_mode='echo'`, \(\lambda\in\{0.4,0.6\}\) |
| H4 | Пороги 0.45/0.44/0.35 универсальны | Калибровка ROC на разметке «поляризация/нет» для других \(N,T,\theta_{\mathrm{ext}}\) |
| H5 | Устойчивость консенсуса при \(\lambda=0\) сохраняется при \(h\to 0.05\) | Sweep \(\bar h\) при \(\lambda=0\); ожидание: рост \(\mathrm{Pol}\) без TRN |

**Следующие шаги модели:** (1) кластерная метрика \(K_{\mathrm{clusters}}\); (2) sweep \(q,r\) при \(\lambda>0\); (3) калибровка `egd_stub` на синтетических кейсах; (4) увеличение \(R\) до 30 для доверительных интервалов (см. `EXPERIMENT_PROTOCOL.md`).

---

## Приложение A. Сводка уравнений (код = документ)

\[
\boxed{
\begin{aligned}
b_i^+ &= \mathrm{clip}_{[-1,1]}\Bigl[b_i+\Delta t\bigl(\alpha_i\sum_j w_{ij}e^{-(b_j-b_i)^2/(2h_i^2)}(b_j-b_i)+\lambda m_i(1-r_i)(1-q_i)A_i(P_i-b_i)+\eta_i\bigr)\Bigr],\\
e_i^+ &= \mathrm{clip}_{[0,1]}\Bigl[e_i+\Delta t\bigl(\rho|P_i-b_i|-\delta e_i+\xi_i\bigr)\Bigr],\\
A_i &= \sigma(\beta_0+\beta_1 e_i+\beta_2|P_i-b_i|).
\end{aligned}
}
\]

Файлы: `model.py` (динамика), `metrics.py` (метрики), `graph.py` (\(W\)), `config.py` (домены параметров).
