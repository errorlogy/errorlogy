# ТЗ для Cursor / Codex / Claude: Errorlogy → politic.bar MVP

**Проект:** Errorlogy  
**Первый продукт:** politic.bar  
**Назначение ТЗ:** дать Cursor Agent / ChatGPT Codex / Claude Code единое техническое задание для сборки MVP, который использует JSON-ядро Errorlogy как машинно-читаемую онтологию ошибок госменеджмента.

---

## 0. Режим работы AI-агентов

В проекте могут работать несколько AI-агентов:

- **Cursor Agent** — основной IDE-агент для навигации по репозиторию, правок, рефакторинга, ревью изменений.
- **ChatGPT / Codex** — агент для реализации кода, тестов, генерации модулей, CLI/пайплайнов, симуляций.
- **Claude / Claude Code** — агент для архитектурного анализа, long-context reasoning, документации, альтернативных реализаций и ревью.

### Правило координации

Агенты не должны спорить с методологией Errorlogy.  
Главный источник истины по предметной модели:

```txt
/data/errorlogy_unified_taxonomy_v16_max_catastrophe.json
/data/errorlogy_retrospective_200_case_seed_v3.json
```

Если агент видит противоречие:

1. не переписывать методологию произвольно;
2. создать issue / TODO;
3. предложить минимальное изменение;
4. не менять ID режимов без отдельного решения.

---

## 1. Цель MVP

Создать прототип web-системы politic.bar, которая:

1. загружает JSON-онтологию Errorlogy;
2. загружает ретроспективный корпус кейсов;
3. позволяет анализировать governance-case;
4. выявляет слабые мультисредные сигналы;
5. оценивает fuzzy-membership `μ` по режимам ошибок;
6. строит α-связи / цепочки ошибок;
7. определяет PNO-режим;
8. показывает временную 4D-траекторию ошибки;
9. выделяет кластеры максимального вклада;
10. делает прогноз FPD;
11. показывает CAT / bifurcation hypothesis;
12. предлагает LBI — как можно было сделать лучше;
13. формирует публичную карточку politic.bar без юридического обвинения.

---

## 2. Ключевая формула продукта

```txt
DATA
→ WMS
→ μ(CB/SF/MP/GT/HM/LCJ/LCC/EGD/T4D/CAT)
→ α propagation
→ ACC contribution clusters
→ PNO regime
→ FPD forecast
→ LBI betterment
→ public explanation
```

Коротко:

```txt
данные → слабые сигналы → ошибки → связи → режим → прогноз → как лучше
```

---

## 3. Обязательные ограничения языка

### Нельзя

- писать “виновен”, “преступник”, “доказана вина”, “коррупционер” без отдельного legal evidence layer;
- представлять fuzzy-оценку как факт;
- представлять weak signals как доказательство;
- утверждать намерение агента без доказательств;
- использовать закон как финальную истину управленческой оптимальности.

### Нужно

Использовать формулировки:

```txt
аналитический вклад
вероятный вклад стратегии
кластер максимального вклада
fuzzy-membership
confidence / uncertainty
early-warning hypothesis
legal contour may have contributed
capacity mismatch
possible hidden weak signals
```

---

## 4. Главные файлы данных

### 4.1 Errorlogy ontology

```txt
/data/errorlogy_unified_taxonomy_v16_max_catastrophe.json
```

Содержит:

```txt
381 режим в max_mode_universe
85 alpha seed edges
CB / SF / MP / MP_EXT
GT / GT_EXT
HM
LCJ
LBI
LAC
LCC
WMS
ACC
EGD
FPD
T4D
CAT
PNO
LΩ
```

### 4.2 Retrospective seed corpus

```txt
/data/errorlogy_retrospective_200_case_seed_v3.json
```

Содержит:

```txt
200 retrospective seed-cases
expected_modes
weak_multisource_signals
t4d_modes
betterment_hypothesis
dimension_load
```

---

## 5. MVP-архитектура

Предпочтительный стек:

```txt
Frontend: Next.js + React + TypeScript
UI: TailwindCSS + shadcn/ui
Backend: Next.js API routes или FastAPI
Data processing: Python
Storage MVP: JSON files + SQLite
Future storage: Postgres + pgvector
Charts: Recharts / Plotly
Testing: pytest + vitest
```

---

## 6. Структура репозитория

Создать структуру:

```txt
/errorlogy-politicbar/
  README.md
  AGENTS.md
  /data/
    errorlogy_unified_taxonomy_v16_max_catastrophe.json
    errorlogy_retrospective_200_case_seed_v3.json
  /docs/
    methodology.md
    ontology_layers.md
    public_language_rules.md
    case_card_spec.md
    validation_plan.md
  /src/
    /app/
      page.tsx
      cases/page.tsx
      cases/[caseId]/page.tsx
      taxonomy/page.tsx
      simulation/page.tsx
      forecast/page.tsx
    /components/
      CaseCard.tsx
      ModeBadge.tsx
      PNOChart.tsx
      AlphaGraph.tsx
      Timeline4D.tsx
      ContributionClusterCard.tsx
      BettermentPanel.tsx
      CatastrophePanel.tsx
    /lib/
      taxonomy.ts
      case-loader.ts
      fuzzy.ts
      alpha.ts
      pno.ts
      wms.ts
      acc.ts
      egd.ts
      fpd.ts
      t4d.ts
      cat.ts
      lbi.ts
      validation.ts
  /python/
    simulate_case.py
    simulate_corpus.py
    validate_retro.py
    export_results.py
  /tests/
    test_taxonomy_loader.py
    test_alpha_propagation.py
    test_pno_scoring.py
    test_case_schema.py
```

---

## 7. AGENTS.md

Создать файл `AGENTS.md`:

```md
# Agent Instructions for Errorlogy / politic.bar

## Mission
Build an MVP for Errorlogy, a governance-error analysis framework. politic.bar is the first product.

## Source of Truth
Use:
- /data/errorlogy_unified_taxonomy_v16_max_catastrophe.json
- /data/errorlogy_retrospective_200_case_seed_v3.json

Do not rename IDs such as CB-113, WMS-003, T4D-017, CAT-002, PNO-4.

## Language Rules
Use "analytical contribution", not "legal guilt".
Use "maximum contribution cluster", not "guilty cluster".
Use "weak signal hypothesis", not "proof".
Use "fuzzy membership μ", not binary truth.

## Build Order
1. Load taxonomy.
2. Load retrospective cases.
3. Render taxonomy explorer.
4. Render case cards.
5. Implement fuzzy scoring.
6. Implement alpha propagation.
7. Implement PNO scoring.
8. Implement T4D timeline.
9. Implement CAT hypothesis.
10. Implement LBI betterment panel.
11. Implement public explanation export.

## Never
- Do not invent new taxonomy IDs without creating a candidate under LΩ.
- Do not remove anti-overclaim disclaimers.
- Do not convert fuzzy scores into legal claims.
```

---

## 8. Cursor Rules

Создать `.cursor/rules/errorlogy.mdc`:

```md
---
description: Errorlogy project rules
alwaysApply: true
---

You are working on Errorlogy / politic.bar.

The project analyzes government-management errors using a fuzzy multi-layer ontology.

Always preserve:
- mode IDs
- layer names
- anti-overclaim rules
- distinction between contribution and guilt
- μ ≠ probability ≠ confidence ≠ evidence_grade

All public explanations must be written in careful non-accusatory language.
```

---

## 9. Основные модули

### 9.1 Taxonomy Loader

Файл:

```txt
/src/lib/taxonomy.ts
```

Функции:

```ts
loadTaxonomy(): Taxonomy
getModeById(id: string): Mode
getModesByFamily(family: string): Mode[]
getAlphaEdges(): AlphaEdge[]
getLayer(name: string): Layer
```

Проверки:

```txt
- max_mode_universe существует
- alpha_matrix_max_seed существует
- все mode_id уникальны
- все alpha edges ссылаются на существующие mode_id или PNO
```

---

### 9.2 Case Loader

Файл:

```txt
/src/lib/case-loader.ts
```

Функции:

```ts
loadCases(): GovernanceCase[]
getCaseById(caseId: string): GovernanceCase
getCasesByRegion(region: string): GovernanceCase[]
getCasesByDomain(domain: string): GovernanceCase[]
```

---

### 9.3 Fuzzy Scoring

Файл:

```txt
/src/lib/fuzzy.ts
```

Назначение:

Оценить `μ(mode)` для кейса.

В MVP можно использовать heuristic scoring:

```txt
μ(mode) =
0.35 * dimension_match
+ 0.25 * keyword_match
+ 0.20 * expected_or_detected_signal
+ 0.10 * layer_prior
+ 0.10 * WMS/T4D/CAT boost
```

Важно:

```txt
μ is degree of membership, not probability.
```

---

### 9.4 Alpha Propagation

Файл:

```txt
/src/lib/alpha.ts
```

Формула:

```txt
μ_i(t+1) =
clip(
  μ_i(t) + Σ_j α_{j→i} * μ_j(t) * (1 - μ_i(t)),
  0,
  1
)
```

Параметры:

```ts
steps: number
damping?: number
threshold?: number
```

Выход:

```ts
{
  initialMu: Record<string, number>,
  propagatedMu: Record<string, number>,
  activatedEdges: ActivatedEdge[],
  topModes: ModeScore[]
}
```

---

### 9.5 PNO Scoring

Файл:

```txt
/src/lib/pno.ts
```

Рассчитать системный режим:

```txt
PNO-1 informational
PNO-2 incentive/Nash
PNO-3 coordination
PNO-4 temporal
PNO-5 anti-consensus
PNO-6 inter-system
PNO-7 persistent non-optimality
```

Выход:

```ts
{
  dominantPNO: string,
  scores: Record<string, number>,
  explanation: string
}
```

---

### 9.6 WMS Detector

Файл:

```txt
/src/lib/wms.ts
```

Рассчитать:

```txt
MSI — Multisource Signal Index
CEP — Cumulative Error Pressure
```

Формула MVP:

```txt
MSI = Σ reliability * strength * independence * diversity * temporal_relevance

CEP(t) = decay * CEP(t-1) + MSI(t)
```

---

### 9.7 ACC Cluster Detection

Файл:

```txt
/src/lib/acc.ts
```

Задача:

Найти кластеры максимального вклада:

```txt
ACC-001 Capacity-veto cluster
ACC-002 Legal-delay cluster
ACC-003 Procurement-rent cluster
ACC-004 Narrative-amplification cluster
ACC-005 Expert-exclusion cluster
ACC-006 Data-silo / measurement cluster
ACC-007 Interagency churn cluster
ACC-008 Externality-displacement cluster
ACC-009 Technical-debt dependency cluster
ACC-010 Crisis-compression cluster
```

Выход:

```ts
{
  maxContributionCluster: ClusterResult,
  clusters: ClusterResult[]
}
```

Формула:

```txt
cluster_score =
mean(μ(signature_modes))
* evidence_confidence
* environment_diversity
```

---

### 9.8 EGD Analysis

Файл:

```txt
/src/lib/egd.ts
```

Задача:

Оценить echo-room / small-group dynamics:

```txt
EGD-001 Closed-room echo reinforcement
EGD-002 Hidden dissent suppression
EGD-009 Informal veto norm
EGD-011 Weak-signal normalization in small groups
```

Выход:

```ts
{
  echoRoomPressure: number,
  hiddenSignalPrior: number,
  likelyEGDModes: ModeScore[]
}
```

---

### 9.9 T4D Temporal Topology

Файл:

```txt
/src/lib/t4d.ts
```

Задача:

Построить 3D+1D worldline ошибки:

```txt
γ_error(t)
```

MVP-объекты:

```ts
type ErrorWorldlinePoint = {
  t: string
  stage: "weak_signal" | "ignored_warning" | "escalation" | "failure" | "inquiry"
  modes: string[]
  description: string
}
```

Рассчитать:

```txt
warning_to_action_latency_risk
intervention_window_loss
irreversibility_threshold_risk
```

---

### 9.10 CAT Catastrophe Theory

Файл:

```txt
/src/lib/cat.ts
```

Задача:

Определить гипотезу порогового перехода:

```txt
CAT-001 Fold
CAT-002 Cusp
CAT-003 Swallowtail
CAT-008 Hysteresis
CAT-010 Critical slowing
CAT-015 Catastrophic loss of optionality
```

MVP-скоринг:

```txt
if WMS_CEP high + T4D-017 high → CAT-001
if blocker_power high + capacity_gap high → CAT-002
if path_dependence high + implementation_decay high → CAT-003
if backlog / meeting_churn high → CAT-010
if delay + contract/legal lock-in high → CAT-015
```

Выход:

```ts
{
  catastropheHypothesis: string,
  bifurcationRisk: number,
  hysteresisRisk: number,
  explanation: string
}
```

---

### 9.11 FPD Forecast

Файл:

```txt
/src/lib/fpd.ts
```

Назначение:

Прогноз fuzzy trajectory:

```txt
μ(t+1) =
F(μ(t), α, WMS, ACC, EGD, LCC, LCJ, T4D, CAT, LBI)
```

Выход:

```ts
{
  horizon: "near" | "short" | "medium" | "long",
  modeForecasts: ModeForecast[],
  pnoTransitionForecast: PNOTransitionForecast,
  earlyWarnings: EarlyWarning[],
  confidence: number
}
```

Обязательно разделять:

```txt
mu_forecast
scenario_probability
confidence
evidence_grade
```

---

### 9.12 LBI Betterment

Файл:

```txt
/src/lib/lbi.ts
```

Задача:

Сгенерировать “как лучше”:

```txt
information betterment
coordination betterment
legal-contour betterment
competence-routing betterment
temporal betterment
catastrophe-prevention betterment
```

Формат:

```ts
{
  alternativeId: string,
  title: string,
  targetModes: string[],
  expectedReduction: number,
  feasibility: number,
  riskOfNewErrors: string[],
  explanation: string
}
```

---

## 10. UI MVP

### 10.1 Главная страница

Показать:

```txt
Errorlogy / politic.bar
Ontology: 381 modes
Retrospective cases: 200
Alpha edges: 85
Main pipeline visualization
```

### 10.2 Taxonomy Explorer

Функции:

```txt
- поиск mode_id
- фильтр по family/layer
- карточка режима
- linked modes
- alpha in/out
```

### 10.3 Case Explorer

Функции:

```txt
- список 200 кейсов
- фильтр region/domain/evidence_grade
- открыть case page
```

### 10.4 Case Page

Показать:

```txt
case metadata
weak signals
top activated modes
PNO scores
T4D timeline
ACC clusters
EGD echo-room hypothesis
CAT catastrophe hypothesis
FPD forecast
LBI betterment
public explanation
```

### 10.5 Public Card

Карточка должна быть понятна обществу:

```txt
Что произошло?
Какая ошибка вероятна?
Почему она могла возникнуть?
Какие слабые сигналы были?
Когда окно вмешательства было потеряно?
Какой кластер внес максимальный вклад?
Как можно было сделать лучше?
Что неизвестно?
```

---

## 11. API endpoints

Если используется Next.js API:

```txt
GET /api/taxonomy
GET /api/taxonomy/mode/:id
GET /api/cases
GET /api/cases/:caseId
POST /api/analyze
POST /api/simulate
POST /api/forecast
POST /api/export-card
```

### POST /api/analyze

Input:

```json
{
  "caseId": "US-FLINT-2014",
  "options": {
    "alphaSteps": 5,
    "includeForecast": true,
    "includeBetterment": true
  }
}
```

Output:

```json
{
  "caseId": "US-FLINT-2014",
  "topModes": [],
  "pno": {},
  "wms": {},
  "acc": {},
  "egd": {},
  "t4d": {},
  "cat": {},
  "fpd": {},
  "lbi": {},
  "publicExplanation": ""
}
```

---

## 12. Python simulation tools

Создать Python-скрипты:

```txt
/python/simulate_case.py
/python/simulate_corpus.py
/python/validate_retro.py
/python/export_results.py
```

### simulate_case.py

CLI:

```bash
python python/simulate_case.py --case-id US-FLINT-2014 --alpha-steps 5
```

### simulate_corpus.py

CLI:

```bash
python python/simulate_corpus.py --input data/errorlogy_retrospective_200_case_seed_v3.json
```

### validate_retro.py

Считать:

```txt
Recall@20
Recall@40
mean expected μ
PNO distribution
T4D mean μ
CAT activation
alpha candidate support
```

---

## 13. Testing

Минимальные тесты:

```txt
test_taxonomy_loads
test_mode_ids_unique
test_alpha_edges_valid
test_cases_load
test_case_expected_modes_exist
test_fuzzy_scores_range_0_1
test_alpha_propagation_range_0_1
test_pno_scores_range_0_1
test_public_language_no_legal_guilt
test_lbi_returns_at_least_one_betterment
```

---

## 14. Acceptance Criteria

MVP считается готовым, если:

```txt
1. JSON v16 загружается без ошибок.
2. 200 кейсов загружаются без ошибок.
3. По каждому кейсу строится top modes.
4. По каждому кейсу строится PNO.
5. По каждому кейсу строится хотя бы 1 WMS summary.
6. По каждому кейсу строится T4D summary.
7. По каждому кейсу строится CAT hypothesis или “not enough data”.
8. По каждому кейсу строится LBI betterment.
9. Public Card не содержит юридических обвинений.
10. Есть README с запуском.
11. Есть AGENTS.md.
12. Есть тесты.
```

---

## 15. Команды запуска

Предложить:

```bash
npm install
npm run dev
npm run test
python -m pytest
python python/simulate_corpus.py
```

---

## 16. README.md

README должен объяснять:

```txt
Что такое Errorlogy
Что такое politic.bar
Как устроена онтология
Как запустить MVP
Как добавить новый кейс
Как добавить новый mode candidate через LΩ
Как читать μ / PNO / CAT / T4D
Почему contribution ≠ guilt
```

---

## 17. Первый sprint plan

### Sprint 1 — Foundation

```txt
- repo setup
- data folder
- taxonomy loader
- case loader
- README
- AGENTS.md
- basic tests
```

### Sprint 2 — Analysis Core

```txt
- fuzzy scoring
- alpha propagation
- PNO scoring
- WMS scoring
- top modes
```

### Sprint 3 — Case UI

```txt
- case explorer
- case page
- mode badges
- PNO chart
- public explanation draft
```

### Sprint 4 — Advanced Layers

```txt
- ACC clusters
- EGD echo-room
- T4D timeline
- CAT hypothesis
- LBI betterment
```

### Sprint 5 — Forecast / Export

```txt
- FPD forecast
- public card export
- validation dashboard
- polish
```

---

## 18. Master Prompt for Cursor Agent

```txt
You are building Errorlogy / politic.bar MVP.

Use the project JSON files as the source of truth:
- data/errorlogy_unified_taxonomy_v16_max_catastrophe.json
- data/errorlogy_retrospective_200_case_seed_v3.json

Build a Next.js + TypeScript MVP that loads the ontology and retrospective cases, analyzes cases through fuzzy mode scoring, alpha propagation, PNO scoring, WMS, ACC, EGD, T4D, CAT, FPD and LBI, and renders a public non-accusatory case card.

Critical rules:
- contribution is not legal guilt
- weak signals are not proof
- μ is not probability
- law is a governance contour, not final truth
- always include betterment: how it could have been done better
- preserve all IDs
- do not invent new IDs unless under LΩ candidate flow

Start by creating repo structure, AGENTS.md, taxonomy loader, case loader, tests, and a basic case explorer.
```

---

## 19. Definition of Done

```txt
The MVP can open a case, run Errorlogy analysis, show:
- top activated errors
- PNO regime
- weak signals
- contribution clusters
- temporal topology
- catastrophe hypothesis
- forecast
- betterment
- public explanation

And the explanation is safe:
- no unsupported accusations
- no legal guilt claims
- all outputs have confidence / uncertainty language
```
