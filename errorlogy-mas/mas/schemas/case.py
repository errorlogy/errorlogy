from pydantic import BaseModel, Field
from typing import Any


class WeakSignal(BaseModel):
    signal_type: str
    description: str
    source_environment: str
    strength: float = Field(ge=0.0, le=1.0)
    reliability: float = Field(ge=0.0, le=1.0)
    temporal_relevance: float = Field(ge=0.0, le=1.0)


class GovernanceCase(BaseModel):
    case_id: str
    title: str
    description: str
    country: str
    domain: str
    year: int
    source_text: str
    weak_signals: list[WeakSignal] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
