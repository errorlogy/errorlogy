# Taxonomy vs Engine — formalization gap

> **Status:** architectural question · **Criticality:** high for v2+

## Core question

Taxonomy v16 — **381 mode universe**, **217 atomic** (189 CB biases). Most entries are **ontology + operational_signal**, not a formula.

Engine v1-math — thin formal layer on top of μ and aggregates.

**Do not conflate:** "CB-001 μ=0.72" ≠ experimentally measured confirmation bias.

## Two layers

| Layer | Share of v16 |
|-------|--------------|
| Semantic (definitions, cues) | ~80–90% |
| Formal (α, WMS, PNO, ACC) | ~10–20% |

## What the engine uses

- **fuzzy** — TF-IDF/heuristics, not per-bias equations
- **alpha** — NetworkX graph ✅
- **wms/CEP, fpd** — formulas ✅
- **189 CB biases** — shared text-matcher

## Not in v1 code

METHODS, LCC, LAC (Shapley), GT, LΩ — 0% implementation.

## v2+ strategy

1. Corpus calibration for μ
2. Embeddings per operational_signal
3. METHODS as plugins
4. α confidence damping
5. Hybrid: engine numbers + LLM narrative

## Maturity ladder

L0 catalog → L1 heuristic+graph (v1 ✅) → L2 CEP persist → L3 calibrated μ → L4 METHODS → L5 ensemble validation
