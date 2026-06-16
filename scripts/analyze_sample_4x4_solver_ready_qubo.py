"""
Analyze solver-ready metadata for merged sample_4x4 sparse QUBO.

Purpose
-------
The sample_4x4 sparse QUBO has already been:

1. streamed to CSV without building a dense matrix
2. validated by streamed energy evaluation
3. merged by duplicate (i,j) pairs
4. validated again after merging

This script reads the merged sparse QUBO CSV in chunks and computes solver-ready
metadata:

- number of variables
- number of linear terms
- number of quadratic terms
- coefficient min/max/mean
- absolute coefficient max
- density estimates
- constant offset
- file schema
- recommended scaling notes

The merged coefficient CSV is large and is usually ignored by Git.
This script commits only metadata and summary files.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


def main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--merged-csv",
        type=str,
        default="results/tables/sample_4x4_sparse_qubo_coefficients_merged.csv",
    )

    parser.add_argument(
        "--streaming-summary",
        type=str,
        default="results/tables/sample_4x4_sparse_qubo_streaming_summary.json",
    )

    parser.add_argument(
        "--merge-summary",
        type=str,
        default="results/tables/sample_4x4_sparse_qubo_merge_summary.json",
    )

    parser.add_argument(
        "--metadata-out",
        type=str,
        default="results/tables/sample_4x4_sparse_qubo_solver_ready_metadata.json",
    )

    parser.add_argument(
        "--summary-out",
        type=str,
        default="results/tables/sample_4x4_sparse_qubo_solver_ready_summary.csv",
    )

    parser.add_argument("--chunksize", type=int, default=500000)

    args = parser.parse_args()

    merged_csv = Path(args.merged_csv)

    if not merged_csv.exists():
        raise FileNotFoundError(
            f"Merged QUBO CSV not found: {merged_csv}. "
            "Run scripts/merge_sample_4x4_streamed_qubo_coefficients.py first."
        )

    streaming_summary = json.loads(Path(args.streaming_summary).read_text())
    merge_summary = json.loads(Path(args.merge_summary).read_text())

    num_variables = int(streaming_summary["num_variables"])
    constant = float(streaming_summary["constant"])

    total_terms = 0
    linear_terms = 0
    quadratic_terms = 0

    coeff_sum = 0.0
    coeff_abs_sum = 0.0
    coeff_min = None
    coeff_max = None
    coeff_abs_max = 0.0

    positive_terms = 0
    negative_terms = 0
    zero_terms = 0

    max_i = 0
    max_j = 0

    print("=== Analyzing merged sample_4x4 sparse QUBO ===")
    print(f"Merged CSV: {merged_csv}")
    print(f"Chunksize: {args.chunksize}")

    for chunk_id, chunk in enumerate(
        pd.read_csv(merged_csv, chunksize=args.chunksize)
    ):
        if chunk_id % 5 == 0:
            print(f"Processing chunk {chunk_id}")

        total_terms += len(chunk)

        i_values = chunk["i"]
        j_values = chunk["j"]
        coeff = chunk["coefficient"]

        linear_terms += int((i_values == j_values).sum())
        quadratic_terms += int((i_values != j_values).sum())

        coeff_sum += float(coeff.sum())
        coeff_abs_sum += float(coeff.abs().sum())

        c_min = float(coeff.min())
        c_max = float(coeff.max())
        c_abs_max = float(coeff.abs().max())

        coeff_min = c_min if coeff_min is None else min(coeff_min, c_min)
        coeff_max = c_max if coeff_max is None else max(coeff_max, c_max)
        coeff_abs_max = max(coeff_abs_max, c_abs_max)

        positive_terms += int((coeff > 0).sum())
        negative_terms += int((coeff < 0).sum())
        zero_terms += int((coeff == 0).sum())

        max_i = max(max_i, int(i_values.max()))
        max_j = max(max_j, int(j_values.max()))

    coeff_mean = coeff_sum / total_terms if total_terms else None
    coeff_abs_mean = coeff_abs_sum / total_terms if total_terms else None

    possible_upper_triangular_terms = num_variables * (num_variables + 1) // 2
    possible_quadratic_terms = num_variables * (num_variables - 1) // 2

    sparse_density_upper_triangular = (
        total_terms / possible_upper_triangular_terms
        if possible_upper_triangular_terms
        else None
    )

    quadratic_density = (
        quadratic_terms / possible_quadratic_terms
        if possible_quadratic_terms
        else None
    )

    # A simple conservative scaling recommendation for solvers that prefer
    # coefficients in roughly [-1, 1].
    scale_to_unit_abs_max = (
        1.0 / coeff_abs_max if coeff_abs_max and coeff_abs_max > 0 else None
    )

    metadata = {
        "experiment": "sample_4x4_sparse_qubo_solver_ready_metadata",
        "merged_csv": str(merged_csv),
        "merged_csv_is_local_artifact": True,
        "num_variables": num_variables,
        "constant_offset": constant,
        "total_terms": total_terms,
        "linear_terms": linear_terms,
        "quadratic_terms": quadratic_terms,
        "possible_upper_triangular_terms": possible_upper_triangular_terms,
        "possible_quadratic_terms": possible_quadratic_terms,
        "sparse_density_upper_triangular": sparse_density_upper_triangular,
        "quadratic_density": quadratic_density,
        "coefficient_min": coeff_min,
        "coefficient_max": coeff_max,
        "coefficient_mean": coeff_mean,
        "coefficient_abs_mean": coeff_abs_mean,
        "coefficient_abs_max": coeff_abs_max,
        "positive_terms": positive_terms,
        "negative_terms": negative_terms,
        "zero_terms": zero_terms,
        "max_i": max_i,
        "max_j": max_j,
        "scale_to_unit_abs_max": scale_to_unit_abs_max,
        "schema": {
            "i": "integer variable index, 0-based",
            "j": "integer variable index, 0-based, with i <= j",
            "coefficient": "merged QUBO coefficient for x_i x_j",
        },
        "qubo_energy_convention": (
            "E(x) = constant_offset + sum_{i<=j} coefficient(i,j) * x_i * x_j"
        ),
        "streaming_summary_reference": str(args.streaming_summary),
        "merge_summary_reference": str(args.merge_summary),
        "merge_total_input_rows": merge_summary.get("total_input_rows"),
        "merge_unique_pairs_after_drop": merge_summary.get("unique_pairs_after_drop"),
        "merge_reduction_ratio_after_drop": merge_summary.get(
            "reduction_ratio_after_drop"
        ),
        "solver_notes": [
            "The merged CSV is solver-ready as an upper-triangular sparse QUBO coefficient list.",
            "The constant offset should be added back when comparing absolute energies.",
            "Some solvers ignore constant offsets during optimization; this is acceptable because constants do not affect argmin.",
            "For hardware annealers or solvers with coefficient ranges, coefficients may need scaling.",
            "The large merged CSV should usually remain a local artifact or be stored externally.",
        ],
    }

    metadata_out = Path(args.metadata_out)
    metadata_out.parent.mkdir(parents=True, exist_ok=True)
    metadata_out.write_text(json.dumps(metadata, indent=2))

    summary_rows = [
        {"metric": "num_variables", "value": num_variables},
        {"metric": "constant_offset", "value": constant},
        {"metric": "total_terms", "value": total_terms},
        {"metric": "linear_terms", "value": linear_terms},
        {"metric": "quadratic_terms", "value": quadratic_terms},
        {
            "metric": "sparse_density_upper_triangular",
            "value": sparse_density_upper_triangular,
        },
        {"metric": "quadratic_density", "value": quadratic_density},
        {"metric": "coefficient_min", "value": coeff_min},
        {"metric": "coefficient_max", "value": coeff_max},
        {"metric": "coefficient_abs_max", "value": coeff_abs_max},
        {"metric": "coefficient_mean", "value": coeff_mean},
        {"metric": "coefficient_abs_mean", "value": coeff_abs_mean},
        {"metric": "positive_terms", "value": positive_terms},
        {"metric": "negative_terms", "value": negative_terms},
        {"metric": "zero_terms", "value": zero_terms},
        {"metric": "scale_to_unit_abs_max", "value": scale_to_unit_abs_max},
    ]

    summary_df = pd.DataFrame(summary_rows)
    summary_out = Path(args.summary_out)
    summary_out.parent.mkdir(parents=True, exist_ok=True)
    summary_df.to_csv(summary_out, index=False)

    print("=== Solver-ready metadata complete ===")
    print(f"num_variables = {num_variables}")
    print(f"constant_offset = {constant}")
    print(f"total_terms = {total_terms}")
    print(f"linear_terms = {linear_terms}")
    print(f"quadratic_terms = {quadratic_terms}")
    print(f"coefficient_min = {coeff_min}")
    print(f"coefficient_max = {coeff_max}")
    print(f"coefficient_abs_max = {coeff_abs_max}")
    print(f"sparse_density_upper_triangular = {sparse_density_upper_triangular}")
    print(f"quadratic_density = {quadratic_density}")
    print(f"scale_to_unit_abs_max = {scale_to_unit_abs_max}")
    print(f"saved metadata = {metadata_out}")
    print(f"saved summary = {summary_out}")


if __name__ == "__main__":
    main()
