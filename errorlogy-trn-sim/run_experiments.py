import argparse
import json
import sys
from pathlib import Path

# Allow running from repository root without installation.
ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import pandas as pd
from trn_sim.config import TRNParams
from trn_sim.experiments import run_once, lambda_sweep, qr_grid, chi_h_sweep, aggregate
from trn_sim.plots import plot_time_series, plot_belief_distribution, plot_lambda_sweep, plot_qr_heatmap


def load_config(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    parser.add_argument("--out", default="outputs")
    parser.add_argument("--sweep", action="store_true")
    args = parser.parse_args()

    config = load_config(args.config)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "plots").mkdir(parents=True, exist_ok=True)

    if args.sweep:
        base = TRNParams(**config["base"])
        repeats = int(config.get("repeats", 3))

        raw_lambda = lambda_sweep(base, config["lambdas"], repeats=repeats)
        agg_lambda = aggregate(raw_lambda, ["lambda_trn"])
        raw_lambda.to_csv(out / "lambda_sweep_raw.csv", index=False)
        agg_lambda.to_csv(out / "lambda_sweep.csv", index=False)
        plot_lambda_sweep(agg_lambda, out / "plots" / "lambda_sweep.png")

        raw_qr = qr_grid(base, config["q_means"], config["r_means"], repeats=repeats)
        agg_qr = aggregate(raw_qr, ["q_mean", "r_mean"])
        raw_qr.to_csv(out / "qr_grid_raw.csv", index=False)
        agg_qr.to_csv(out / "qr_grid.csv", index=False)
        plot_qr_heatmap(agg_qr, out / "plots" / "qr_heatmap.png")

        raw_ch = chi_h_sweep(base, config["echo_chis"], config["confidence_h_means"], repeats=repeats)
        agg_ch = aggregate(raw_ch, ["echo_chi", "confidence_h_mean"])
        raw_ch.to_csv(out / "chi_h_sweep_raw.csv", index=False)
        agg_ch.to_csv(out / "chi_h_sweep.csv", index=False)

        print("Sweep completed.")
        print(agg_lambda)
        return

    params = TRNParams.from_json(args.config)
    sim, report = run_once(params)
    pd.DataFrame([report]).to_csv(out / "sample_metrics.csv", index=False)
    sim.time_series_frame().to_csv(out / "sample_timeseries.csv", index=False)
    plot_time_series(sim, out / "plots" / "sample_timeseries.png")
    plot_belief_distribution(sim, out / "plots" / "sample_belief_distribution.png")

    print("Single simulation completed.")
    for k, v in report.items():
        print(f"{k}: {v}")


if __name__ == "__main__":
    main()
