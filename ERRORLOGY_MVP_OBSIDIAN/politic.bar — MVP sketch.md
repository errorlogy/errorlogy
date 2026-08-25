# politic.bar - MVP sketch

> **OLD SKETCH** - `ERRORLOGY/errorlogy_old_version/Windows_old_MVP/Politic Bar (pre errorlogy)/`

## What is this

The first applied implementation of Errorlogy: a multi-agent pipeline builds an **error card** according to the protocol (without accusatory language).

## Pipeline (v0.6)

```text
Scout → Framer → Chain-Mapper → Failure-Mode Classifier →
Red-Team → Verifier → Neutrality Auditor → Card Compiler
```

Code: `politic_bar/pipeline.py`, `agents.py`, `prompts.py`

## Seed cases (v0.1)

| ID | Event |
|----|---------|
| US-NASA-1986-CHALLENGER-01 | STS-51L |
| SU-USSR-1986-CHERNOBYL-01 | Nuclear Power Plant |
| US-IC-2002-IRAQ-WMD-01 | NIE Iraq WMD |
| GB-POL-1999-HORIZON-01 | Post Office/Horizon |
| US-MMS-2010-DEEPWATER-01 | MMS surveillance |

Plus v0.6 run: `US-NASA-1986-CHALLENGER-V06-01` with full `_pipeline/`.

## Taxonomy in sketch (v0.6)

- `taxonomy/cognitive_biases.json` - 189 (L1–L3)
- `taxonomy/strategic_failure_modes.json` - 14 (L4)
- `taxonomy/mechanism_pathologies.json` - 14 (L5)

Methodology in README: v0.6 (actors §7a, attractors §7b, L4/L5, chain-mapper).  
**Implementation in code lags** behind the methodology (Chain-Mapper, L4, profiles - next pass according to README).

## UI sketch

`dashboard.html` - one-page directory view in the browser.

## Launch the pipeline (if you need a reference)

```bash
pip install anthropic
export ANTHROPIC_API_KEY=...
python run.py MY-CASE-ID path/to/source_bundle.txt
```

→ [[Artifact map]] · [[Errorlogy - concept]]

#political-bar #old-sketch