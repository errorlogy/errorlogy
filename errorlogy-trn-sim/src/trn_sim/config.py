from dataclasses import dataclass, asdict
from typing import Any, Dict
import json


@dataclass
class TRNParams:
    N: int = 800
    T: int = 160
    dt: float = 0.08

    graph_type: str = "watts_strogatz"
    k_neighbors: int = 8
    rewiring_p: float = 0.08

    alpha_mean: float = 0.55
    alpha_std: float = 0.12
    confidence_h_mean: float = 0.45
    confidence_h_std: float = 0.10

    lambda_trn: float = 0.0
    narrative_mode: str = "echo"
    constant_pole: float = 0.8
    echo_chi: float = 2.0

    beta0: float = -0.6
    beta1: float = 1.7
    beta2: float = 1.5

    rho: float = 0.45
    delta: float = 0.25

    opinion_noise: float = 0.015
    emotion_noise: float = 0.02

    q_mean: float = 0.45
    q_std: float = 0.18
    r_mean: float = 0.45
    r_std: float = 0.18
    m_mean: float = 0.55
    m_std: float = 0.18

    seed: int = 42

    @classmethod
    def from_json(cls, path: str) -> "TRNParams":
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if "base" in data:
            data = data["base"]
        return cls(**data)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
