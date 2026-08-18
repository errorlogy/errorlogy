# Agent Instructions — Errorlogy MAS

## Mission

Build and operate the Errorlogy MAS: a multi-agent AI system for analytical monitoring of
government management errors. politic.bar is the first public product.

## Source of truth

- Ontology: `data/errorlogy_unified_taxonomy_v16.json`
- Pipeline spec: `ERRORLOGY_MVP/ERRORLOGY/errorlogy_old_version/Cursor_Project/TZ_Cursor_Errorlogy_politicbar_FULL.md`
- Analytics formulas: TZ §9.3–9.11 → implemented in `mas/engine/`

Do NOT rename or invent mode IDs (CB-xxx, SF-xxx, MP-xxx, PNO-x, ACC-xxx, EGD-xxx, CAT-xxx).

## Engine vs LLM split (v1-math)

**Engine (`mas/engine/`)** — all numeric outputs. Deterministic, repeatable, unit-tested.

| Module | Responsibility |
|--------|----------------|
| `fuzzy.py` | μ scoring over full atomic universe + keyword pre-filter |
| `alpha.py` | α-propagation via NetworkX graph |
| `wms.py` | MSI, CEP |
| `pno.py` | PNO-1..7 scores |
| `acc.py` | ACC cluster scores from JSON archetypes |
| `egd.py` | echo_room_pressure, hidden_signal_prior |
| `t4d.py` | worldline + ruptures changepoints |
| `cat.py` | catastrophe rule engine + sympy forms |
| `fpd.py` | fuzzy trajectory forecasts |
| `guards.py` | name resolution, weak-evidence μ cap (0.65), warnings |

**LLM agents (`mas/agents/`)** — interpretation and public output only:

| Agent | LLM role |
|-------|----------|
| Scout | extract `GovernanceCase` + weak signals |
| WMS, PNO, ACC, T4D, CAT, FPD | optional narrative / explanation after engine numbers |
| Classifier | optional `contributing_signals` labels (μ from engine) |
| Alpha, EGD | no LLM |
| LBI | betterment alternatives |
| Red Team | adversarial review (receives engine warning flags) |
| Card Compiler | public explanation card |
| Neutrality | language compliance |

Use `orchestrator.run_from_text(..., engine_only=True)` or `run_engine_from_case()` for tests without LLM.

## Language rules (mandatory for all agents)

| Use | Never use |
|-----|-----------|
| analytical contribution | guilty, criminal |
| fuzzy membership μ | proven guilt |
| confidence / evidence_grade | intentionally caused |
| early-warning hypothesis | corrupt (without legal evidence layer) |
| capacity mismatch | "this proves" |
| possible / consistent with | "is responsible for" |

μ is degree of membership. NOT probability. NOT evidence grade.
Always separate: `mu_forecast` / `scenario_probability` / `confidence` / `evidence_grade`

Weak evidence (`evidence_grade=weak`) → μ capped at 0.65 by `engine/guards.py` after fuzzy + alpha.

## Agent pipeline

```
Scout → WMS → Classifier → Alpha → PNO → ACC → EGD → T4D → CAT → FPD → LBI → RedTeam → CardCompiler → NeutralityAudit
         └────────────── engine (deterministic) ──────────────┘
```

## Do

- Put new numeric logic in `mas/engine/`, not in agent prompts
- Ask where new code should live before adding modules outside `mas/`
- Treat taxonomy v16 as the ontology source, not a frozen API — propose changes as LΩ candidates
- Keep `schemas/analysis.py` as the single definition of output types
- Run `pytest tests/` before merging analytics changes
- Run `examples/run_challenger.py --engine-only` for quick smoke without API keys

## Do not

- Ask LLM to compute μ, MSI, CEP, PNO scores, cluster scores, or FPD trajectories
- Convert μ scores to legal claims or probability statements
- Remove `LANGUAGE_RULES` from `agents/base.py`
- Slice classifier candidates to `atomic[:80]` — use full universe via engine
- Merge politic.bar v0.6 pipeline code with this MAS without explicit migration task
- Commit `ANTHROPIC_API_KEY` or any secrets
