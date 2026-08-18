"""Validate TRN experiment CSV outputs against data/*_schema.json."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

RUN_SCHEMA = DATA / "output_schema.json"
AGG_SCHEMAS = {
    "lambda_sweep.csv": DATA / "aggregated_lambda_schema.json",
    "qr_grid.csv": DATA / "aggregated_qr_schema.json",
    "chi_h_sweep.csv": DATA / "aggregated_chi_h_schema.json",
}

NUMERIC_FIELDS = {
    "lambda_trn",
    "q_mean",
    "r_mean",
    "echo_chi",
    "confidence_h_mean",
    "consensus_final",
    "polarization_final",
    "extreme_share_final",
    "entropy_final",
    "trn_risk_index",
    "consensus_mean",
    "polarization_mean",
    "extreme_share_mean",
    "entropy_mean",
    "risk_index_mean",
    "anticonsensus_rate",
}

UNIT_INTERVAL = {
    "consensus_final",
    "polarization_final",
    "extreme_share_final",
    "anticonsensus_final",
    "consensus_mean",
    "polarization_mean",
    "extreme_share_mean",
    "anticonsensus_rate",
}


def load_schema(path: Path) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def schema_for(path: Path) -> Path | None:
    name = path.name
    if name.endswith("_raw.csv") or name == "sample_metrics.csv":
        return RUN_SCHEMA
    if name in AGG_SCHEMAS:
        return AGG_SCHEMAS[name]
    return None


def validate_dataframe(df: pd.DataFrame, schema: dict, source: Path) -> list[str]:
    errors: list[str] = []
    required = set(schema.keys())
    missing = required - set(df.columns)
    if missing:
        errors.append(f"{source}: missing columns {sorted(missing)}")
        return errors

    for col in NUMERIC_FIELDS & required:
        if not pd.api.types.is_numeric_dtype(df[col]):
            errors.append(f"{source}: column {col} must be numeric")

    for col in UNIT_INTERVAL & required:
        if col in df.columns and pd.api.types.is_numeric_dtype(df[col]):
            lo, hi = float(df[col].min()), float(df[col].max())
            if lo < 0.0 or hi > 1.0:
                errors.append(f"{source}: {col} out of [0,1] range ({lo:.4f}, {hi:.4f})")

    if "anticonsensus_final" in df.columns:
        bad = df[~df["anticonsensus_final"].isin([0, 1])]
        if not bad.empty:
            errors.append(f"{source}: anticonsensus_final must be 0 or 1 ({len(bad)} bad rows)")

    return errors


def collect_csv_paths(target: Path, recursive: bool) -> list[Path]:
    if target.is_file():
        return [target]
    pattern = "**/*.csv" if recursive else "*.csv"
    return sorted(target.glob(pattern))


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate TRN experiment CSV outputs.")
    parser.add_argument("path", type=Path, help="CSV file or directory")
    parser.add_argument("--recursive", action="store_true", help="Scan subdirectories for CSV")
    args = parser.parse_args()

    paths = collect_csv_paths(args.path, args.recursive)
    if not paths:
        print(f"No CSV files under {args.path}", file=sys.stderr)
        return 1

    all_errors: list[str] = []
    validated = 0
    skipped = 0
    for path in paths:
        schema_path = schema_for(path)
        if schema_path is None:
            skipped += 1
            continue
        df = pd.read_csv(path)
        schema = load_schema(schema_path)
        all_errors.extend(validate_dataframe(df, schema, path))
        validated += 1

    if all_errors:
        for err in all_errors:
            print(f"FAIL: {err}", file=sys.stderr)
        return 1

    print(f"OK: validated {validated} file(s), skipped {skipped} (timeseries / unknown)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
