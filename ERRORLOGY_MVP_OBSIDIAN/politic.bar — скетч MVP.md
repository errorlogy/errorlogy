# politic.bar — скетч MVP

> **OLD SKETCH** — `ERRORLOGY/errorlogy_old_version/Windows_old_MVP/Politic Bar (pre errorlogy)/`

## Что это

Первое прикладное воплощение Errorlogy: мультиагентный пайплайн строит **error card** по протоколу (без обвинительного языка).

## Пайплайн (v0.6)

```text
Scout → Framer → Chain-Mapper → Failure-Mode Classifier →
Red-Team → Verifier → Neutrality Auditor → Card Compiler
```

Код: `politic_bar/pipeline.py`, `agents.py`, `prompts.py`

## Seed-кейсы (v0.1)

| ID | Событие |
|----|---------|
| US-NASA-1986-CHALLENGER-01 | STS-51L |
| SU-USSR-1986-CHERNOBYL-01 | АЭС |
| US-IC-2002-IRAQ-WMD-01 | NIE Iraq WMD |
| GB-POL-1999-HORIZON-01 | Post Office / Horizon |
| US-MMS-2010-DEEPWATER-01 | MMS oversight |

Плюс прогон v0.6: `US-NASA-1986-CHALLENGER-V06-01` с полным `_pipeline/`.

## Таксономия в скетче (v0.6)

- `taxonomy/cognitive_biases.json` — 189 (L1–L3)
- `taxonomy/strategic_failure_modes.json` — 14 (L4)
- `taxonomy/mechanism_pathologies.json` — 14 (L5)

Методология в README: v0.6 (акторы §7a, attractors §7b, L4/L5, chain-mapper).  
**Реализация в коде отстаёт** от методологии (Chain-Mapper, L4, профили — следующий pass по README).

## UI скетч

`dashboard.html` — одностраничный просмотр каталога в браузере.

## Запуск пайплайна (если нужен референс)

```bash
pip install anthropic
export ANTHROPIC_API_KEY=...
python run.py MY-CASE-ID path/to/source_bundle.txt
```

→ [[Карта артефактов]] · [[Errorlogy — концепция]]

#politic-bar #old-sketch
