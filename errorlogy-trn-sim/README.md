# errorlogy-trn-sim — TRN research layer

**Label:** RESEARCH (not part of the 14-agent MAS pipeline)

Synthetic agent-based simulation of TRN-like information fields: polarization, echo chambers, anticonsensus thresholds. Used to strengthen theory and math before any optional bridge to [errorlogy-mas](../errorlogy-mas/) EGD diagnostics.

## Scope and safety

Read [docs/SAFETY_AND_SCOPE.md](docs/SAFETY_AND_SCOPE.md) before running experiments. TRN here is an abstract information environment for defensive / theoretical analysis only — no real platforms, PII, or targeting.

Relation to MAS:

| Layer | Path | Role |
|-------|------|------|
| Production analysis | `errorlogy-mas/` | 14-agent pipeline, EGD echo-room metrics |
| Research simulation | `errorlogy-trn-sim/` | Synthetic TRN dynamics, sweeps, theory validation |

Future mapping stub (not wired): [bridge/egd_stub.py](bridge/egd_stub.py).

## Setup

```powershell
cd c:\Users\Public\ERRORLOGY_MVP\errorlogy-trn-sim
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## CLI — run experiments

From project root (adds `src/` to path automatically):

```powershell
# Baseline single run
python run_experiments.py --config configs/default_config.json --out outputs

# Parameter sweeps (lambda, q/r grid, chi/h)
python run_experiments.py --config configs/sweep_config.json --out outputs --sweep

# Stress scenario (bipolar field, low q/r)
python run_experiments.py --config configs/stress_config.json --out outputs/stress --sweep
```

Outputs: CSV tables under `--out`, plots under `--out/plots/`.

## CLI — validate outputs

Check CSV columns and value ranges against [data/output_schema.json](data/output_schema.json):

```powershell
python scripts/validate_outputs.py outputs/lambda_sweep.csv
python scripts/validate_outputs.py outputs --recursive
```

## Docs

| File | Content |
|------|---------|
| [docs/THEORY.md](docs/THEORY.md) | Conceptual overview |
| [docs/MATHEMATICAL_MODEL.md](docs/MATHEMATICAL_MODEL.md) | Rigorous equations, stability, empirical thresholds |
| [docs/PHASE_DIAGRAM.md](docs/PHASE_DIAGRAM.md) | Phase map from stress sweeps (\(\lambda_{\mathrm{crit}}\approx 0.35\)) |
| [docs/EXPERIMENT_PROTOCOL.md](docs/EXPERIMENT_PROTOCOL.md) | Sweep design and reporting |
| [docs/PROMPT_FOR_AGENT.md](docs/PROMPT_FOR_AGENT.md) | Agent research checklist |

Anticonsensus flag (code): `consensus < 0.45`, `polarization > 0.44`, `extreme_share > 0.35`.

Analytic risk index: `R_TRN = λ·m̄·(1−r̄)·(1−q̄)·χ / (h̄ + ε)` — see `trn_sim.metrics.trn_risk_index`.
