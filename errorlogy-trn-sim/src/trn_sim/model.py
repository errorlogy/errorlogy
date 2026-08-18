import numpy as np
from .config import TRNParams
from .graph import make_graph_matrix
from .metrics import calculate_metrics


def sigmoid(x):
    return 1.0 / (1.0 + np.exp(-x))


def clip01(x):
    return np.clip(x, 0.0, 1.0)


def clip11(x):
    return np.clip(x, -1.0, 1.0)


class TRNSimulation:
    """
    Synthetic agent-based model of a TRN-like information field.

    This class does not connect to real platforms and does not use real user data.
    It is intended for defensive / research simulations only.
    """

    def __init__(self, params: TRNParams):
        self.p = params
        self.rng = np.random.default_rng(params.seed)
        self.N = params.N
        self.W = make_graph_matrix(
            graph_type=params.graph_type,
            N=params.N,
            k_neighbors=params.k_neighbors,
            rewiring_p=params.rewiring_p,
            rng=self.rng,
        )

        self.b = clip11(self.rng.normal(0.0, 0.18, self.N))
        self.e = clip01(self.rng.beta(2.0, 5.0, self.N))
        self.q = clip01(self.rng.normal(params.q_mean, params.q_std, self.N))
        self.r = clip01(self.rng.normal(params.r_mean, params.r_std, self.N))
        self.m = clip01(self.rng.normal(params.m_mean, params.m_std, self.N))
        self.alpha = clip01(self.rng.normal(params.alpha_mean, params.alpha_std, self.N))
        self.h = np.clip(
            self.rng.normal(params.confidence_h_mean, params.confidence_h_std, self.N),
            0.05,
            1.2,
        )
        self.z = self.rng.random(self.N)

        self.history = {
            "b": [],
            "e": [],
            "consensus": [],
            "polarization": [],
            "extreme_share": [],
            "entropy": [],
            "trn_risk_index": [],
            "anticonsensus": [],
        }

    def narrative_pole(self) -> np.ndarray:
        mode = self.p.narrative_mode
        if mode == "constant":
            return np.full(self.N, self.p.constant_pole)
        if mode == "bipolar":
            return np.where(self.z < 0.5, -1.0, 1.0)
        if mode == "echo":
            local_mean = self.W @ self.b
            return np.tanh(self.p.echo_chi * local_mean)
        raise ValueError(f"Unknown narrative_mode: {mode}")

    def social_term(self) -> np.ndarray:
        diff = self.b[None, :] - self.b[:, None]
        h2 = self.h[:, None] ** 2
        K = np.exp(-(diff ** 2) / (2.0 * h2))
        weighted_diff = self.W * K * diff
        return self.alpha * weighted_diff.sum(axis=1)

    def trn_term(self, P: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        # I_i = λ·m_i·(1−r_i)·(1−q_i)·A_i·(P_i−b_i); q,r only affect TRN, not social_term.
        conflict = np.abs(P - self.b)
        attention = sigmoid(self.p.beta0 + self.p.beta1 * self.e + self.p.beta2 * conflict)
        I = self.p.lambda_trn * self.m * (1.0 - self.r) * (1.0 - self.q) * attention * (P - self.b)
        return I, attention

    def update_emotion(self, P: np.ndarray) -> None:
        conflict = np.abs(P - self.b)
        noise = self.rng.normal(0.0, self.p.emotion_noise, self.N)
        de = self.p.rho * conflict - self.p.delta * self.e + noise
        self.e = clip01(self.e + self.p.dt * de)

    def step(self) -> None:
        P = self.narrative_pole()
        S = self.social_term()
        I, _attention = self.trn_term(P)
        noise = self.rng.normal(0.0, self.p.opinion_noise, self.N)
        db = S + I + noise
        self.b = clip11(self.b + self.p.dt * db)
        self.update_emotion(P)
        self.record()

    def record(self) -> None:
        self.history["b"].append(self.b.copy())
        self.history["e"].append(self.e.copy())
        m = calculate_metrics(self.b, self.p)
        for k in ["consensus", "polarization", "extreme_share", "entropy", "trn_risk_index", "anticonsensus"]:
            self.history[k].append(m[k])

    def run(self) -> dict:
        self.record()
        for _ in range(self.p.T):
            self.step()
        return self.final_report()

    def final_report(self) -> dict:
        m = calculate_metrics(self.b, self.p)
        return {
            "lambda_trn": self.p.lambda_trn,
            "narrative_mode": self.p.narrative_mode,
            "echo_chi": self.p.echo_chi,
            "q_mean": self.p.q_mean,
            "r_mean": self.p.r_mean,
            "m_mean": self.p.m_mean,
            "confidence_h_mean": self.p.confidence_h_mean,
            "consensus_final": m["consensus"],
            "polarization_final": m["polarization"],
            "extreme_share_final": m["extreme_share"],
            "entropy_final": m["entropy"],
            "trn_risk_index": m["trn_risk_index"],
            "anticonsensus_final": m["anticonsensus"],
        }

    def time_series_frame(self):
        import pandas as pd
        return pd.DataFrame({
            "t": np.arange(len(self.history["consensus"])),
            "consensus": self.history["consensus"],
            "polarization": self.history["polarization"],
            "extreme_share": self.history["extreme_share"],
            "entropy": self.history["entropy"],
            "trn_risk_index": self.history["trn_risk_index"],
            "anticonsensus": self.history["anticonsensus"],
        })
