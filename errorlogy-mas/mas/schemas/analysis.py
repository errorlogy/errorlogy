from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Literal, Any

_CONFIDENCE_MAP = {"low": 0.25, "medium": 0.5, "moderate": 0.5, "high": 0.75, "very high": 0.9}
_GRADE_MAP = {
    "a": "strong", "b": "moderate", "c": "weak",
    "high": "strong", "medium": "moderate", "low": "weak",
    "strong": "strong", "moderate": "moderate", "weak": "weak",
}


class ModeScore(BaseModel):
    mode_id: str
    name: str
    mu: float = Field(ge=0.0, le=1.0, description="Fuzzy membership, not probability")
    confidence: float = Field(ge=0.0, le=1.0, default=0.5)
    evidence_grade: Literal["weak", "moderate", "strong"] = "weak"
    contributing_signals: list[str] = Field(default_factory=list)

    @field_validator("confidence", mode="before")
    @classmethod
    def coerce_confidence(cls, v):
        if isinstance(v, str):
            return _CONFIDENCE_MAP.get(v.lower().strip(), 0.5)
        return v

    @field_validator("evidence_grade", mode="before")
    @classmethod
    def coerce_grade(cls, v):
        if isinstance(v, str):
            return _GRADE_MAP.get(v.lower().strip(), "weak")
        return v

    @field_validator("mu", mode="before")
    @classmethod
    def coerce_mu(cls, v):
        if isinstance(v, str):
            return _CONFIDENCE_MAP.get(v.lower().strip(), 0.5)
        return max(0.0, min(1.0, float(v)))


class AlphaEdgeActivated(BaseModel):
    from_id: str
    to_id: str
    weight: float
    delta_mu: float


class AlphaResult(BaseModel):
    initial_mu: dict[str, float]
    propagated_mu: dict[str, float]
    activated_edges: list[AlphaEdgeActivated]
    top_modes: list[ModeScore]


class WMSResult(BaseModel):
    msi: float = Field(description="Multisource Signal Index")
    cep: float = Field(description="Cumulative Error Pressure")
    active_signals: list[str]
    early_warning_hypothesis: str


class PNOResult(BaseModel):
    dominant_pno: str
    scores: dict[str, float]
    explanation: str


class ClusterResult(BaseModel):
    cluster_id: str
    name: str
    score: float = Field(ge=0.0, le=1.0)
    signature_modes: list[str]
    explanation: str


class ACCResult(BaseModel):
    max_contribution_cluster: ClusterResult
    clusters: list[ClusterResult]


class EGDResult(BaseModel):
    echo_room_pressure: float = Field(ge=0.0, le=1.0)
    hidden_signal_prior: float = Field(ge=0.0, le=1.0)
    likely_egd_modes: list[ModeScore]


class ErrorWorldlinePoint(BaseModel):
    t: str
    stage: Literal["weak_signal", "ignored_warning", "escalation", "failure", "inquiry"]
    modes: list[str]
    description: str


class T4DResult(BaseModel):
    worldline: list[ErrorWorldlinePoint]
    warning_to_action_latency_risk: float = Field(ge=0.0, le=1.0)
    intervention_window_loss: float = Field(ge=0.0, le=1.0)
    irreversibility_threshold_risk: float = Field(ge=0.0, le=1.0)


class CATResult(BaseModel):
    catastrophe_hypothesis: str
    bifurcation_risk: float = Field(ge=0.0, le=1.0)
    hysteresis_risk: float = Field(ge=0.0, le=1.0)
    explanation: str


def _coerce_float(v) -> float:
    if isinstance(v, str):
        return _CONFIDENCE_MAP.get(v.lower().strip(), 0.5)
    return max(0.0, min(1.0, float(v)))


def _coerce_grade(v) -> str:
    if isinstance(v, str):
        return _GRADE_MAP.get(v.lower().strip(), "weak")
    return v


class ModeForecast(BaseModel):
    mode_id: str
    mu_forecast: float = Field(ge=0.0, le=1.0, default=0.5)
    scenario_probability: float = Field(ge=0.0, le=1.0, default=0.5)
    confidence: float = Field(ge=0.0, le=1.0, default=0.5)
    evidence_grade: Literal["weak", "moderate", "strong"] = "weak"

    @field_validator("mu_forecast", "scenario_probability", "confidence", mode="before")
    @classmethod
    def coerce_floats(cls, v): return _coerce_float(v)

    @field_validator("evidence_grade", mode="before")
    @classmethod
    def coerce_grade(cls, v): return _coerce_grade(v)


class EarlyWarning(BaseModel):
    signal: str
    urgency: Literal["low", "medium", "high"]
    description: str


class FPDResult(BaseModel):
    horizon: Literal["near", "short", "medium", "long"]
    mode_forecasts: list[ModeForecast]
    pno_transition_forecast: str
    early_warnings: list[EarlyWarning]
    confidence: float = Field(ge=0.0, le=1.0)


class BettermentAlternative(BaseModel):
    alternative_id: str
    title: str
    target_modes: list[str]
    expected_reduction: float = Field(ge=0.0, le=1.0)
    feasibility: float = Field(ge=0.0, le=1.0)
    risk_of_new_errors: list[str]
    explanation: str


class LBIResult(BaseModel):
    alternatives: list[BettermentAlternative]


class CaseAnalysis(BaseModel):
    case_id: str
    top_modes: list[ModeScore]
    wms: WMSResult
    alpha: AlphaResult
    pno: PNOResult
    acc: ACCResult
    egd: EGDResult
    t4d: T4DResult
    cat: CATResult
    fpd: FPDResult
    lbi: LBIResult
    public_explanation: str
    red_team_notes: list[str] = Field(default_factory=list)
    neutrality_flags: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
