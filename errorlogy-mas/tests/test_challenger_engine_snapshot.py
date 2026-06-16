"""Golden snapshot for Challenger engine-only analytics.

Deterministic fields (MSI, CEP, dominant PNO, top-5 mode IDs and μ) are compared
against tests/fixtures/challenger_engine_baseline.json.

If the baseline file is missing, this test writes it on first run and skips so the
file can be reviewed and committed. Re-run after committing to enforce the snapshot.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from mas.orchestrator import Orchestrator
from mas.schemas.analysis import CaseAnalysis

BASELINE_PATH = Path(__file__).parent / "fixtures" / "challenger_engine_baseline.json"
FLOAT_TOL = 1e-3
MU_TOL = 1e-2


@pytest.fixture(autouse=True)
def deterministic_engine(monkeypatch):
    """Keyless CI: skip HuggingFace embeddings (network-dependent scores)."""
    monkeypatch.setenv("ERRORLOGY_USE_EMBEDDINGS", "0")


def _extract_snapshot(analysis: CaseAnalysis) -> dict:
    return {
        "case_id": analysis.case_id,
        "wms": {
            "msi": round(analysis.wms.msi, 4),
            "cep": round(analysis.wms.cep, 4),
        },
        "pno": {"dominant_pno": analysis.pno.dominant_pno},
        "top_modes_ids": [m.mode_id for m in analysis.top_modes[:5]],
        "top_modes_mu": [round(m.mu, 4) for m in analysis.top_modes[:5]],
    }


def _assert_close(actual: float, expected: float, *, tol: float, label: str) -> None:
    assert abs(actual - expected) <= tol, (
        f"{label}: expected {expected}, got {actual} (tol={tol})"
    )


def test_challenger_engine_snapshot(challenger_case):
    orch = Orchestrator(init_llm=False)
    result = orch.run_engine_from_case(challenger_case)
    validated = CaseAnalysis.model_validate(result.model_dump())

    assert validated.case_id == challenger_case.case_id
    assert validated.metadata.get("engine_only") is True

    snapshot = _extract_snapshot(validated)

    if not BASELINE_PATH.exists():
        BASELINE_PATH.parent.mkdir(parents=True, exist_ok=True)
        BASELINE_PATH.write_text(json.dumps(snapshot, indent=2) + "\n", encoding="utf-8")
        pytest.skip(
            "Baseline generated at tests/fixtures/challenger_engine_baseline.json; "
            "review and commit, then re-run."
        )

    baseline = json.loads(BASELINE_PATH.read_text(encoding="utf-8"))

    assert snapshot["case_id"] == baseline["case_id"]
    assert snapshot["pno"]["dominant_pno"] == baseline["pno"]["dominant_pno"]
    assert snapshot["top_modes_ids"] == baseline["top_modes_ids"]

    _assert_close(
        snapshot["wms"]["msi"],
        baseline["wms"]["msi"],
        tol=FLOAT_TOL,
        label="wms.msi",
    )
    _assert_close(
        snapshot["wms"]["cep"],
        baseline["wms"]["cep"],
        tol=FLOAT_TOL,
        label="wms.cep",
    )

    for i, (actual_mu, expected_mu) in enumerate(
        zip(snapshot["top_modes_mu"], baseline["top_modes_mu"], strict=True)
    ):
        _assert_close(actual_mu, expected_mu, tol=MU_TOL, label=f"top_modes[{i}].mu")
