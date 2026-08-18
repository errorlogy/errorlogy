from dataclasses import replace
import pandas as pd
from .config import TRNParams
from .model import TRNSimulation


def run_once(params: TRNParams, experiment_id: str = "single", repeat: int = 0) -> tuple[TRNSimulation, dict]:
    sim = TRNSimulation(params)
    report = sim.run()
    report["experiment_id"] = experiment_id
    report["repeat"] = repeat
    return sim, report


def lambda_sweep(base_params: TRNParams, lambdas, repeats: int = 10, base_seed: int = 100) -> pd.DataFrame:
    rows = []
    for lam in lambdas:
        for rep in range(repeats):
            params = replace(base_params, lambda_trn=float(lam), seed=base_seed + rep)
            _sim, report = run_once(params, experiment_id="lambda_sweep", repeat=rep)
            rows.append(report)
    return pd.DataFrame(rows)


def qr_grid(base_params: TRNParams, q_means, r_means, repeats: int = 10, base_seed: int = 500) -> pd.DataFrame:
    rows = []
    for q in q_means:
        for r in r_means:
            for rep in range(repeats):
                params = replace(base_params, q_mean=float(q), r_mean=float(r), seed=base_seed + rep)
                _sim, report = run_once(params, experiment_id="qr_grid", repeat=rep)
                rows.append(report)
    return pd.DataFrame(rows)


def chi_h_sweep(base_params: TRNParams, echo_chis, confidence_h_means, repeats: int = 10, base_seed: int = 900) -> pd.DataFrame:
    rows = []
    for chi in echo_chis:
        for h in confidence_h_means:
            for rep in range(repeats):
                params = replace(base_params, echo_chi=float(chi), confidence_h_mean=float(h), seed=base_seed + rep)
                _sim, report = run_once(params, experiment_id="chi_h_sweep", repeat=rep)
                rows.append(report)
    return pd.DataFrame(rows)


def aggregate(df: pd.DataFrame, by) -> pd.DataFrame:
    return df.groupby(by).agg(
        consensus_mean=("consensus_final", "mean"),
        polarization_mean=("polarization_final", "mean"),
        extreme_share_mean=("extreme_share_final", "mean"),
        entropy_mean=("entropy_final", "mean"),
        risk_index_mean=("trn_risk_index", "mean"),
        anticonsensus_rate=("anticonsensus_final", "mean"),
    ).reset_index()
