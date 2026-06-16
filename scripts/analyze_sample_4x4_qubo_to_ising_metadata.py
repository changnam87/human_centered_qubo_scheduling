"""Analyze QUBO-to-Ising conversion metadata for sample_4x4 merged sparse QUBO."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--merged-csv", type=str, default="results/tables/sample_4x4_sparse_qubo_coefficients_merged.csv")
    parser.add_argument("--solver-ready-metadata", type=str, default="results/tables/sample_4x4_sparse_qubo_solver_ready_metadata.json")
    parser.add_argument("--chunksize", type=int, default=500000)
    parser.add_argument("--ising-linear-out", type=str, default="results/tables/sample_4x4_ising_linear_fields.csv")
    parser.add_argument("--ising-quadratic-out", type=str, default="results/tables/sample_4x4_ising_couplers.csv")
    parser.add_argument("--summary-out", type=str, default="results/tables/sample_4x4_qubo_to_ising_metadata_summary.json")
    parser.add_argument("--compact-summary-out", type=str, default="results/tables/sample_4x4_qubo_to_ising_metadata_summary.csv")
    args = parser.parse_args()

    merged_csv = Path(args.merged_csv)
    metadata_path = Path(args.solver_ready_metadata)

    if not merged_csv.exists():
        raise FileNotFoundError(f"Merged QUBO CSV not found: {merged_csv}")
    if not metadata_path.exists():
        raise FileNotFoundError(f"Solver-ready metadata not found: {metadata_path}")

    metadata = json.loads(metadata_path.read_text())
    num_variables = int(metadata["num_variables"])
    qubo_constant = float(metadata["constant_offset"])

    h = [0.0 for _ in range(num_variables)]
    ising_offset = qubo_constant

    total_qubo_terms = 0
    linear_qubo_terms = 0
    quadratic_qubo_terms = 0
    total_ising_couplers = 0

    j_min = None
    j_max = None
    j_abs_max = 0.0

    q_min = None
    q_max = None
    q_abs_max = 0.0

    coupler_out = Path(args.ising_quadratic_out)
    coupler_out.parent.mkdir(parents=True, exist_ok=True)

    with coupler_out.open("w") as jf:
        jf.write("i,j,J_ij\\n")

        for chunk_id, chunk in enumerate(pd.read_csv(merged_csv, chunksize=args.chunksize)):
            if chunk_id % 5 == 0:
                print(f"Processing chunk {chunk_id}")

            total_qubo_terms += len(chunk)

            for row in chunk.itertuples(index=False):
                i = int(row.i)
                j = int(row.j)
                q = float(row.coefficient)

                q_min = q if q_min is None else min(q_min, q)
                q_max = q if q_max is None else max(q_max, q)
                q_abs_max = max(q_abs_max, abs(q))

                if i == j:
                    linear_qubo_terms += 1
                    # q_i x_i = q_i * (1 + s_i) / 2
                    ising_offset += q / 2.0
                    h[i] += q / 2.0
                else:
                    quadratic_qubo_terms += 1
                    # q_ij x_i x_j = q_ij/4 * (1 + s_i + s_j + s_i s_j)
                    j_ij = q / 4.0
                    ising_offset += q / 4.0
                    h[i] += q / 4.0
                    h[j] += q / 4.0
                    jf.write(f"{i},{j},{j_ij}\\n")
                    total_ising_couplers += 1
                    j_min = j_ij if j_min is None else min(j_min, j_ij)
                    j_max = j_ij if j_max is None else max(j_max, j_ij)
                    j_abs_max = max(j_abs_max, abs(j_ij))

    linear_out = Path(args.ising_linear_out)
    linear_out.parent.mkdir(parents=True, exist_ok=True)
    with linear_out.open("w") as hf:
        hf.write("i,h_i\\n")
        for i, h_i in enumerate(h):
            if abs(h_i) > 1e-12:
                hf.write(f"{i},{h_i}\\n")

    nonzero_h = [v for v in h if abs(v) > 1e-12]
    h_min = min(nonzero_h) if nonzero_h else 0.0
    h_max = max(nonzero_h) if nonzero_h else 0.0
    h_abs_max = max(abs(v) for v in nonzero_h) if nonzero_h else 0.0
    h_mean = sum(nonzero_h) / len(nonzero_h) if nonzero_h else 0.0

    ising_abs_max = max(h_abs_max, j_abs_max)
    scale_to_unit_abs_max = 1.0 / ising_abs_max if ising_abs_max > 0 else None

    possible_couplers = num_variables * (num_variables - 1) // 2
    coupler_density = total_ising_couplers / possible_couplers if possible_couplers else None

    summary = {
        "experiment": "sample_4x4_qubo_to_ising_metadata",
        "merged_qubo_csv": str(merged_csv),
        "num_variables": num_variables,
        "qubo_constant": qubo_constant,
        "ising_offset": ising_offset,
        "total_qubo_terms": total_qubo_terms,
        "linear_qubo_terms": linear_qubo_terms,
        "quadratic_qubo_terms": quadratic_qubo_terms,
        "ising_linear_nonzero_terms": len(nonzero_h),
        "ising_couplers": total_ising_couplers,
        "coupler_density": coupler_density,
        "qubo_coefficient_min": q_min,
        "qubo_coefficient_max": q_max,
        "qubo_coefficient_abs_max": q_abs_max,
        "ising_h_min": h_min,
        "ising_h_max": h_max,
        "ising_h_mean": h_mean,
        "ising_h_abs_max": h_abs_max,
        "ising_J_min": j_min,
        "ising_J_max": j_max,
        "ising_J_abs_max": j_abs_max,
        "ising_abs_max": ising_abs_max,
        "scale_to_unit_abs_max": scale_to_unit_abs_max,
        "ising_linear_csv": str(linear_out),
        "ising_coupler_csv": str(coupler_out),
        "energy_convention": "E_Ising(s) = offset + sum_i h_i s_i + sum_{i<j} J_ij s_i s_j, with x_i = (1 + s_i) / 2.",
        "note": "Prototype metadata conversion. Large Ising coupler CSV may remain a local artifact.",
    }

    summary_out = Path(args.summary_out)
    summary_out.parent.mkdir(parents=True, exist_ok=True)
    summary_out.write_text(json.dumps(summary, indent=2))

    compact_rows = [
        {"metric": "num_variables", "value": num_variables},
        {"metric": "qubo_constant", "value": qubo_constant},
        {"metric": "ising_offset", "value": ising_offset},
        {"metric": "total_qubo_terms", "value": total_qubo_terms},
        {"metric": "linear_qubo_terms", "value": linear_qubo_terms},
        {"metric": "quadratic_qubo_terms", "value": quadratic_qubo_terms},
        {"metric": "ising_linear_nonzero_terms", "value": len(nonzero_h)},
        {"metric": "ising_couplers", "value": total_ising_couplers},
        {"metric": "coupler_density", "value": coupler_density},
        {"metric": "ising_h_min", "value": h_min},
        {"metric": "ising_h_max", "value": h_max},
        {"metric": "ising_h_abs_max", "value": h_abs_max},
        {"metric": "ising_J_min", "value": j_min},
        {"metric": "ising_J_max", "value": j_max},
        {"metric": "ising_J_abs_max", "value": j_abs_max},
        {"metric": "ising_abs_max", "value": ising_abs_max},
        {"metric": "scale_to_unit_abs_max", "value": scale_to_unit_abs_max},
    ]
    pd.DataFrame(compact_rows).to_csv(args.compact_summary_out, index=False)

    print("=== QUBO-to-Ising metadata analysis complete ===")
    print(f"num_variables = {num_variables}")
    print(f"ising_offset = {ising_offset}")
    print(f"ising_linear_nonzero_terms = {len(nonzero_h)}")
    print(f"ising_couplers = {total_ising_couplers}")
    print(f"ising_h_abs_max = {h_abs_max}")
    print(f"ising_J_abs_max = {j_abs_max}")
    print(f"ising_abs_max = {ising_abs_max}")
    print(f"scale_to_unit_abs_max = {scale_to_unit_abs_max}")
    print(f"saved linear fields = {linear_out}")
    print(f"saved couplers = {coupler_out}")
    print(f"saved summary = {summary_out}")

if __name__ == "__main__":
    main()
