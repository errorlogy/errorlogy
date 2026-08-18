from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def plot_time_series(sim, out_path=None):
    df = sim.time_series_frame()
    plt.figure(figsize=(10, 5))
    plt.plot(df["t"], df["consensus"], label="Consensus")
    plt.plot(df["t"], df["polarization"], label="Polarization")
    plt.plot(df["t"], df["extreme_share"], label="Extreme share")
    plt.xlabel("Time")
    plt.ylabel("Metric")
    plt.title("TRN synthetic simulation metrics")
    plt.legend()
    plt.grid(True)
    if out_path:
        Path(out_path).parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(out_path, dpi=160, bbox_inches="tight")
        plt.close()
    else:
        plt.show()


def plot_belief_distribution(sim, out_path=None):
    steps = [0, len(sim.history["b"]) // 2, -1]
    plt.figure(figsize=(10, 5))
    for s in steps:
        b = sim.history["b"][s]
        label = f"step {s if s >= 0 else len(sim.history['b']) - 1}"
        plt.hist(b, bins=30, range=(-1, 1), alpha=0.35, label=label)
    plt.xlabel("Belief b")
    plt.ylabel("Agents")
    plt.title("Belief distribution over simulation")
    plt.legend()
    plt.grid(True)
    if out_path:
        Path(out_path).parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(out_path, dpi=160, bbox_inches="tight")
        plt.close()
    else:
        plt.show()


def plot_lambda_sweep(grouped: pd.DataFrame, out_path=None):
    plt.figure(figsize=(10, 5))
    plt.plot(grouped["lambda_trn"], grouped["consensus_mean"], marker="o", label="Consensus")
    plt.plot(grouped["lambda_trn"], grouped["polarization_mean"], marker="o", label="Polarization")
    plt.plot(grouped["lambda_trn"], grouped["extreme_share_mean"], marker="o", label="Extreme share")
    plt.plot(grouped["lambda_trn"], grouped["anticonsensus_rate"], marker="o", label="Anticonsensus rate")
    plt.xlabel("TRN intensity lambda")
    plt.ylabel("Mean metric")
    plt.title("Lambda sweep")
    plt.legend()
    plt.grid(True)
    if out_path:
        Path(out_path).parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(out_path, dpi=160, bbox_inches="tight")
        plt.close()
    else:
        plt.show()


def plot_qr_heatmap(grouped: pd.DataFrame, out_path=None):
    pivot = grouped.pivot(index="q_mean", columns="r_mean", values="anticonsensus_rate")
    plt.figure(figsize=(7, 5))
    plt.imshow(pivot.values, origin="lower", aspect="auto")
    plt.xticks(range(len(pivot.columns)), [str(x) for x in pivot.columns])
    plt.yticks(range(len(pivot.index)), [str(x) for x in pivot.index])
    plt.xlabel("Resistance mean r")
    plt.ylabel("Filtering mean q")
    plt.title("Anticonsensus rate heatmap")
    plt.colorbar(label="Anticonsensus rate")
    if out_path:
        Path(out_path).parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(out_path, dpi=160, bbox_inches="tight")
        plt.close()
    else:
        plt.show()
