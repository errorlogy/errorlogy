"""
Placeholder: map errorlogy-mas EGD outputs to TRN simulation parameters.

NOT wired to MAS orchestrator. Research-only stub for future calibration experiments.

MAS EGD (see errorlogy-mas/mas/schemas/analysis.py):
  - echo_room_pressure ∈ [0, 1]
  - hidden_signal_prior ∈ [0, 1]

TRN params (see trn_sim.config.TRNParams):
  - lambda_trn — external field intensity
  - echo_chi — echo-chamber sharpness (narrative_mode='echo')
  - confidence_h_mean — bounded-confidence window width
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class EGDStubInput:
    """Minimal stand-in for MAS EGDResult fields (no MAS import)."""

    echo_room_pressure: float
    hidden_signal_prior: float


@dataclass(frozen=True)
class TRNStubParams:
    lambda_trn: float
    echo_chi: float
    confidence_h_mean: float


def egd_to_trn_stub(egd: EGDStubInput) -> TRNStubParams:
    """
    Heuristic mapping for synthetic replay — not calibrated on real cases.

    Higher echo_room_pressure → stronger TRN field and sharper local echo.
    Higher hidden_signal_prior → narrower trust window (more fragmentation risk).
    """
    lam = min(1.2, 0.15 + 0.85 * egd.echo_room_pressure)
    chi = 0.5 + 3.5 * egd.echo_room_pressure
    h = max(0.15, 0.55 - 0.35 * egd.hidden_signal_prior)
    return TRNStubParams(lambda_trn=lam, echo_chi=chi, confidence_h_mean=h)


def example() -> TRNStubParams:
    return egd_to_trn_stub(EGDStubInput(echo_room_pressure=0.72, hidden_signal_prior=0.41))
