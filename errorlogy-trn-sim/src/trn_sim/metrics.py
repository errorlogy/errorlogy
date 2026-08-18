import numpy as np


def entropy(values: np.ndarray, bins: int = 20) -> float:
    hist, _ = np.histogram(values, bins=bins, range=(-1, 1), density=False)
    p = hist / max(1, hist.sum())
    p = p[p > 0]
    return float(-(p * np.log(p)).sum())


def trn_risk_index(lambda_trn: float, m_mean: float, r_mean: float, q_mean: float, echo_chi: float, h_mean: float, eps: float = 1e-6) -> float:
    """R_TRN = λ·m̄·(1−r̄)·(1−q̄)·χ / (h̄+ε); uses run-level means, not agent samples."""
    return float((lambda_trn * m_mean * (1 - r_mean) * (1 - q_mean) * echo_chi) / (h_mean + eps))


def calculate_metrics(b: np.ndarray, params) -> dict:
    pol = float(np.std(b))
    consensus = float(max(0.0, 1.0 - pol))
    extreme_share = float(np.mean(np.abs(b) > 0.65))
    ent = entropy(b)
    # Pol>0.44 is redundant when consensus=1-pol and C<0.45 => Pol>0.55; kept for explicit spec.
    anticonsensus = int((consensus < 0.45) and (pol > 0.44) and (extreme_share > 0.35))
    risk = trn_risk_index(
        lambda_trn=params.lambda_trn,
        m_mean=params.m_mean,
        r_mean=params.r_mean,
        q_mean=params.q_mean,
        echo_chi=params.echo_chi,
        h_mean=params.confidence_h_mean,
    )
    return {
        "consensus": consensus,
        "polarization": pol,
        "extreme_share": extreme_share,
        "entropy": ent,
        "trn_risk_index": risk,
        "anticonsensus": anticonsensus,
    }
