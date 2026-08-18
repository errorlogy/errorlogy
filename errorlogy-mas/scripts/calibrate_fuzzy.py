"""
Calibrate fuzzy weights against structure_only (Scout+engine) reference runs.

1. Run LightweightScout on seed cases → save targets
2. scipy.optimize weights to maximize top-5 Jaccard vs reference
3. Write data/fuzzy_weights.json
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
from scipy.optimize import minimize

sys.path.insert(0, str(Path(__file__).parent.parent))

from mas.engine import fuzzy
from mas.engine.alpha import propagate
from mas.engine.wms import detect as wms_detect
from mas.engine.types import FuzzyContext, EngineWarnings
from mas.orchestrator import Orchestrator
from mas.schemas.case import GovernanceCase

from seed_corpus import SEED_CASES

TARGETS_PATH = Path(__file__).parent.parent / "data" / "calibration_targets.json"
WEIGHT_KEYS = ("dimension", "keyword", "signal", "layer", "boost")


def _top5_ids(case: GovernanceCase) -> list[str]:
    warnings = EngineWarnings()
    wms = wms_detect(case)
    ctx = FuzzyContext(wms_msi=wms.msi)
    modes = fuzzy.score_candidates(case, top_n=20, ctx=ctx, warnings=warnings)
    alpha = propagate(modes, warnings=warnings)
    return [m.mode_id for m in alpha.top_modes[:5]]


def _jaccard(a: set[str], b: set[str]) -> float:
    if not a and not b:
        return 1.0
    u = a | b
    return len(a & b) / len(u) if u else 0.0


def build_reference_targets(*, use_llm: bool = True) -> dict:
    """structure_only runs → top-5 mode ids + weak_signals per case."""
    targets: dict = {}
    orch = Orchestrator(init_llm=use_llm)

    for seed in SEED_CASES:
        cid = seed["case_id"]
        print(f"  reference: {cid} ...", end=" ", flush=True)
        if use_llm:
            case = orch.scout.run(
                cid, seed["text"], seed["title"], seed["country"], seed["year"],
            )
            ids = _top5_ids(case)
            signals = [s.model_dump() for s in case.weak_signals]
        else:
            case = GovernanceCase(
                case_id=cid,
                title=seed["title"],
                description=seed["text"][:500],
                country=seed["country"],
                domain="governance",
                year=seed["year"],
                source_text=seed["text"],
                weak_signals=[],
            )
            ids = _top5_ids(case)
            signals = []
        targets[cid] = {"top5": ids, "weak_signals": signals}
        print(ids[:3], "...")

    TARGETS_PATH.write_text(json.dumps(targets, indent=2), encoding="utf-8")
    print(f"Saved targets -> {TARGETS_PATH}")
    return targets


def load_targets() -> dict:
    if TARGETS_PATH.exists():
        return json.loads(TARGETS_PATH.read_text(encoding="utf-8"))
    return build_reference_targets(use_llm=True)


def _cases_from_seeds() -> list[tuple[str, GovernanceCase, set[str]]]:
    targets = load_targets()
    out = []
    for seed in SEED_CASES:
        cid = seed["case_id"]
        entry = targets.get(cid, {})
        if isinstance(entry, list):
            entry = {"top5": entry, "weak_signals": []}
        from mas.schemas.case import WeakSignal
        signals = [WeakSignal(**s) for s in entry.get("weak_signals", [])]
        case = GovernanceCase(
            case_id=cid,
            title=seed["title"],
            description=seed["text"][:500],
            country=seed["country"],
            domain="governance",
            year=seed["year"],
            source_text=seed["text"],
            weak_signals=signals,
        )
        ref = set(entry.get("top5", []))
        out.append((cid, case, ref))
    return out


def _loss_from_vector(x: np.ndarray) -> float:
    weights = {k: float(v) for k, v in zip(WEIGHT_KEYS, x)}
    fuzzy.set_weights(weights)
    cases = _cases_from_seeds()
    scores = []
    for _, case, ref in cases:
        if not ref:
            continue
        pred = set(_top5_ids(case))
        scores.append(1.0 - _jaccard(pred, ref))
    return float(np.mean(scores)) if scores else 1.0


def calibrate() -> dict[str, float]:
    print("Calibrating fuzzy weights...")
    x0 = np.array([fuzzy.get_weights()[k] for k in WEIGHT_KEYS])
    bounds = [(0.05, 0.55)] * len(WEIGHT_KEYS)

    result = minimize(
        _loss_from_vector,
        x0,
        method="L-BFGS-B",
        bounds=bounds,
        options={"maxiter": 80},
    )

    optimal = {k: float(v) for k, v in zip(WEIGHT_KEYS, result.x)}
    fuzzy.set_weights(optimal)
    fuzzy.save_weights(version="calibrated-v1")

    print(f"  loss: {result.fun:.4f}")
    print(f"  weights: {fuzzy.get_weights()}")
    return fuzzy.get_weights()


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--rebuild-targets", action="store_true", help="Re-run Scout reference")
    parser.add_argument("--no-llm", action="store_true", help="Skip LLM for reference (engine only)")
    args = parser.parse_args()

    if args.rebuild_targets or not TARGETS_PATH.exists():
        build_reference_targets(use_llm=not args.no_llm)

    w = calibrate()
    print("\nDone. Weights saved to data/fuzzy_weights.json")
    for k, v in w.items():
        print(f"  {k}: {v:.4f}")


if __name__ == "__main__":
    main()
