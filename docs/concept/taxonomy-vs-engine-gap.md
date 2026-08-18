# Таксономия vs Engine — formalization gap

> **Статус:** архитектурный вопрос · **Критичность:** высокая для v2+

## Суть вопроса

Таксономия v16 — **381 mode universe**, **217 atomic** (189 CB biases). Большая часть — **онтология + operational_signal**, не формула.

Engine v1-math — тонкий формальный слой поверх μ и агрегатов.

**Нельзя путать:** «CB-001 μ=0.72» ≠ экспериментально измеренный confirmation bias.

## Два слоя

| Слой | Доля v16 |
|------|----------|
| Семантический (definitions, cues) | ~80–90% |
| Формальный (α, WMS, PNO, ACC) | ~10–20% |

## Что engine использует

- **fuzzy** — TF-IDF/heuristics, не per-bias equations
- **alpha** — NetworkX graph ✅
- **wms/CEP, fpd** — формулы ✅
- **189 CB biases** — общий text-matcher

## Не в коде v1

METHODS, LCC, LAC (Shapley), GT, LΩ — 0% implementation.

## Стратегия v2+

1. Corpus calibration для μ
2. Embeddings per operational_signal
3. METHODS как plugins
4. α confidence damping
5. Hybrid: engine numbers + LLM narrative

## Зрелость

L0 catalog → L1 heuristic+graph (v1 ✅) → L2 CEP persist → L3 calibrated μ → L4 METHODS → L5 ensemble validation
