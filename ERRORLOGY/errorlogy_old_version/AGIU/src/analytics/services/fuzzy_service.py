"""Fuzzy Predictive Dynamics (FPD) demonstrations."""

import numpy as np
from pydantic import BaseModel


def sigmoid_membership(x: np.ndarray, center: float, width: float) -> np.ndarray:
    """Smooth fuzzy membership via sigmoid."""
    return 1.0 / (1.0 + np.exp(-(x - center) / width))


def gaussian_membership(x: np.ndarray, center: float, sigma: float) -> np.ndarray:
    """Gaussian fuzzy membership."""
    return np.exp(-0.5 * ((x - center) / sigma) ** 2)


class FuzzyTrajectoryRequest(BaseModel):
    start: float = 0.0
    end: float = 10.0
    steps: int = 200
    center: float = 5.0
    width: float = 1.0
    mode: str = "sigmoid"  # sigmoid | gaussian


class FuzzyTrajectoryResponse(BaseModel):
    x: list[float]
    mu: list[float]
    mode: str
    center: float
    width: float


def compute_trajectory(req: FuzzyTrajectoryRequest) -> FuzzyTrajectoryResponse:
    x = np.linspace(req.start, req.end, req.steps)
    if req.mode == "gaussian":
        mu = gaussian_membership(x, req.center, req.width)
    else:
        mu = sigmoid_membership(x, req.center, req.width)
    return FuzzyTrajectoryResponse(
        x=x.tolist(),
        mu=mu.tolist(),
        mode=req.mode,
        center=req.center,
        width=req.width,
    )
