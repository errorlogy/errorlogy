# Harness engineering → Errorlogy mapping

---

## errorlogy-mas (ACTIVE)

### Agent harness (production)

| Component | Path | Harness role |
|-----------|------|----------------|
| Orchestrator | `mas/orchestrator.py` | 14-agent loop, `engine_only`, `structure_only`, dual-run |
| Engine | `mas/engine/*` | Deterministic layer — **core**, not LLM |
| Agents | `mas/agents/*` | Prompts, LANGUAGE_RULES, narrative after engine |
| Guards | `mas/engine/guards.py` | Weak-evidence μ cap, warnings → Red Team |
| Schemas | `mas/schemas/analysis.py` | Contract for graders |
| Dual-run | `tests/test_dual_run.py`, orchestrator flags | Drift detection between runs |
| Neutrality | `agents/neutrality*.py` | Language compliance — LLM-rubric eval candidate |

### Eval harness (today)

| Artifact | Type | CI |
|----------|-----|-----|
| `pytest tests/` | L1 unit + integration | ✅ every PR |
| `run_challenger.py --engine-only` | L2 smoke eval | ✅ every PR |
| `run_challenger.py` (full) | L4 live E2E | local, keys required |
| `examples/run_challenger.py` Challenger case | Golden seed case | fixed STS-51L text |

### Gaps (targets for harness spec)

- Per-agent eval YAML (Scout extraction, Neutrality violations)
- Recorded outputs / cassettes for regression without live LLM
- API-level eval (`POST /analyze`) with schema assertions
- Per-agent step latency metrics (SSE in GUI — source for eval)

---

## errorlogy-gui / errorlogy-gui-v2 (ACTIVE)

| Zone | Harness link |
|------|----------------|
| `errorlogy-gui` Analyze | UI for full / `engine_only` / LightweightScout / dual-run |
| `src/lib/api.ts` | Contract client — eval on breaking API changes |
| `errorlogy-gui-v2` | Browser forecast UI — smoke `npm run build` in CI |
| SSE step progress | Observability surface for manual + future automated trace compare |

GUI evals — **contract + build**, not LLM quality (quality — on MAS).

---

## errorlogy-trn-sim (RESEARCH)

| Rule | Detail |
|---------|--------|
| Separate harness | `run_experiments.py`, CSV outputs, `validate_outputs.py` |
| Bridge | `bridge/egd_stub.py` — only MAS engine touchpoint |
| Eval focus | Polarization / anticonsensus metrics, not 14-agent narrative |

Do not move trn-sim eval patterns into `mas/agents/` without explicit migration.

---

## OSS integration funnel

| Stage | Harness activity |
|--------|-------------------|
| Discover | Record eval-tool in `research/oss-candidates.yaml`, `target_area: mas` or `infra` |
| Screen | Axes `test_safety`, `engine_llm_fit` — critical for harness tools |
| Spike | POC: one agent + `templates/harness-spec.yaml` |
| Pilot | Opt-in flag, default off; CI green required |
| Adopt | Documentation in this handbook, tests in `errorlogy-mas/tests/` |

See [05-next-steps.md](05-next-steps.md) for specific candidates.

---

## CI pipeline (current = minimal eval harness)

```text
push/PR → pytest (MAS) → run_challenger --engine-only → npm run build (GUI)
```

This is the **quality gate** for Pilot→Adopt from [`oss-integration-funnel.md`](../../oss-integration-funnel.md).
