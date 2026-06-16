"""Summarize sample_4x4 runtime and memory/profile metadata from existing result files.

This script does not rerun heavy experiments.
It reads existing JSON summaries and creates a compact engineering profile for the
sample_4x4 QUBO/Ising prototype pipeline.
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

def read_json(path: str) -> dict:
    p = Path(path)
    if not p.exists():
        print(f"WARNING: missing {p}")
        return {}
    return json.loads(p.read_text())

def file_size_mb(path: str):
    p = Path(path)
    if not p.exists():
        return None
    return p.stat().st_size / (1024 * 1024)

def main() -> None:
    feasibility = read_json("results/tables/sample_4x4_qubo_export_feasibility_summary.json")
    streaming = read_json("results/tables/sample_4x4_sparse_qubo_streaming_summary.json")
    streamed_validation = read_json("results/tables/sample_4x4_streamed_qubo_energy_validation_summary.json")
    merge = read_json("results/tables/sample_4x4_sparse_qubo_merge_summary.json")
    merged_validation = read_json("results/tables/sample_4x4_merged_qubo_energy_validation_summary.json")
    solver_ready = read_json("results/tables/sample_4x4_sparse_qubo_solver_ready_metadata.json")
    local_search = read_json("results/tables/sample_4x4_merged_qubo_local_search_summary.json")
    cpsat_sq = read_json("results/tables/sample_4x4_cpsat_squared_target_summary.json")
    sensitivity = read_json("results/tables/sample_4x4_local_search_parameter_sensitivity_best.json")
    tuned_components = read_json("results/tables/sample_4x4_tuned_local_qubo_solution_component_summary.json")
    ising_metadata = read_json("results/tables/sample_4x4_qubo_to_ising_metadata_summary.json")
    ising_validation = read_json("results/tables/sample_4x4_ising_energy_validation_summary.json")

    rows = []

    rows.append({
        "stage": "export_feasibility_estimate",
        "main_metric": "estimated_sparse_terms_before_merge",
        "main_value": feasibility.get("estimated_sparse_terms_before_merge"),
        "runtime_seconds": None,
        "validation_status": None,
        "notes": "Representative pre-export size and memory estimate.",
    })

    rows.append({
        "stage": "streaming_sparse_qubo_export",
        "main_metric": "streamed_rows",
        "main_value": streaming.get("rows_written") or streaming.get("total_rows") or streaming.get("streamed_rows"),
        "runtime_seconds": streaming.get("elapsed_seconds"),
        "validation_status": None,
        "notes": "Large streamed coefficient CSV is a local ignored artifact.",
    })

    rows.append({
        "stage": "streamed_qubo_energy_validation",
        "main_metric": "max_abs_error",
        "main_value": streamed_validation.get("max_abs_error"),
        "runtime_seconds": streamed_validation.get("elapsed_seconds"),
        "validation_status": streamed_validation.get("validation_status"),
        "notes": "Chunked validation of streamed sparse QUBO energy.",
    })

    rows.append({
        "stage": "duplicate_merge",
        "main_metric": "unique_pairs_after_drop",
        "main_value": merge.get("unique_pairs_after_drop"),
        "runtime_seconds": merge.get("elapsed_seconds"),
        "validation_status": None,
        "notes": "Merged duplicate (i,j) QUBO coefficient rows.",
    })

    rows.append({
        "stage": "merged_qubo_energy_validation",
        "main_metric": "max_abs_error",
        "main_value": merged_validation.get("max_abs_error"),
        "runtime_seconds": merged_validation.get("elapsed_seconds"),
        "validation_status": merged_validation.get("validation_status"),
        "notes": "Validation of compact merged sparse QUBO energy.",
    })

    rows.append({
        "stage": "solver_ready_metadata",
        "main_metric": "total_terms",
        "main_value": solver_ready.get("total_terms"),
        "runtime_seconds": None,
        "validation_status": None,
        "notes": "Generated sparse QUBO metadata, density, and scaling recommendation.",
    })

    rows.append({
        "stage": "local_qubo_search_initial",
        "main_metric": "best_energy",
        "main_value": local_search.get("best_energy"),
        "runtime_seconds": local_search.get("load_seconds"),
        "validation_status": "feasible_rate=" + str(local_search.get("feasible_rate")),
        "notes": "Initial operation-level local search on merged sparse QUBO.",
    })

    rows.append({
        "stage": "cpsat_squared_target_baseline",
        "main_metric": "objective_unscaled_from_solver",
        "main_value": cpsat_sq.get("objective_unscaled_from_solver"),
        "runtime_seconds": None,
        "validation_status": cpsat_sq.get("status"),
        "notes": "Objective-equivalent CP-SAT optimum for squared-target QUBO objective.",
    })

    best_case = sensitivity.get("best_case", {})
    rows.append({
        "stage": "local_search_parameter_sensitivity",
        "main_metric": "best_energy",
        "main_value": best_case.get("best_energy"),
        "runtime_seconds": None,
        "validation_status": "feasible_rate=" + str(best_case.get("feasible_rate")),
        "notes": "Best case: " + str(best_case.get("tag")),
    })

    rows.append({
        "stage": "tuned_local_component_analysis",
        "main_metric": "absolute_gap_to_cpsat",
        "main_value": tuned_components.get("absolute_gap_to_cpsat"),
        "runtime_seconds": None,
        "validation_status": "relative_gap=" + str(tuned_components.get("relative_gap_to_cpsat")),
        "notes": "Explains remaining tuned local gap by objective components.",
    })

    rows.append({
        "stage": "qubo_to_ising_metadata",
        "main_metric": "ising_couplers",
        "main_value": ising_metadata.get("ising_couplers"),
        "runtime_seconds": None,
        "validation_status": None,
        "notes": "Generated Ising offset, h fields, J couplers, and scaling metadata.",
    })

    rows.append({
        "stage": "ising_energy_validation",
        "main_metric": "max_abs_error",
        "main_value": ising_validation.get("max_abs_error"),
        "runtime_seconds": None,
        "validation_status": ising_validation.get("validation_status"),
        "notes": "Fast QUBO-to-Ising energy consistency validation.",
    })

    size_rows = [
        {"artifact": "streamed_qubo_coefficients_csv", "path": "results/tables/sample_4x4_sparse_qubo_coefficients_stream.csv", "size_mb": file_size_mb("results/tables/sample_4x4_sparse_qubo_coefficients_stream.csv"), "tracked": False},
        {"artifact": "merged_qubo_coefficients_csv", "path": "results/tables/sample_4x4_sparse_qubo_coefficients_merged.csv", "size_mb": file_size_mb("results/tables/sample_4x4_sparse_qubo_coefficients_merged.csv"), "tracked": False},
        {"artifact": "ising_couplers_csv", "path": "results/tables/sample_4x4_ising_couplers.csv", "size_mb": file_size_mb("results/tables/sample_4x4_ising_couplers.csv"), "tracked": False},
        {"artifact": "ising_linear_fields_csv", "path": "results/tables/sample_4x4_ising_linear_fields.csv", "size_mb": file_size_mb("results/tables/sample_4x4_ising_linear_fields.csv"), "tracked": True},
    ]

    profile = {
        "experiment": "sample_4x4_runtime_memory_profile_summary",
        "purpose": "Compact engineering profile built from existing summary artifacts; heavy experiments are not rerun.",
        "key_results": {
            "num_variables": solver_ready.get("num_variables"),
            "merged_terms": solver_ready.get("total_terms"),
            "quadratic_density": solver_ready.get("quadratic_density"),
            "cpsat_squared_target_optimum": cpsat_sq.get("objective_unscaled_from_solver"),
            "initial_local_best": local_search.get("best_energy"),
            "tuned_local_best": best_case.get("best_energy"),
            "tuned_gap_to_cpsat": tuned_components.get("absolute_gap_to_cpsat"),
            "ising_validation_status": ising_validation.get("validation_status"),
            "ising_validation_max_abs_error": ising_validation.get("max_abs_error"),
        },
        "pipeline_profile": rows,
        "large_artifacts": size_rows,
        "note": "File sizes are None when the large local ignored artifact is not present in the current working tree.",
    }

    out_csv = Path("results/tables/sample_4x4_runtime_memory_profile_summary.csv")
    out_json = Path("results/tables/sample_4x4_runtime_memory_profile_summary.json")
    size_csv = Path("results/tables/sample_4x4_large_artifact_size_summary.csv")
    out_csv.parent.mkdir(parents=True, exist_ok=True)

    pd.DataFrame(rows).to_csv(out_csv, index=False)
    pd.DataFrame(size_rows).to_csv(size_csv, index=False)
    out_json.write_text(json.dumps(profile, indent=2))

    print("=== sample_4x4 runtime/memory profile summary complete ===")
    print(f"saved pipeline summary CSV = {out_csv}")
    print(f"saved large artifact size CSV = {size_csv}")
    print(f"saved profile JSON = {out_json}")
    print(json.dumps(profile["key_results"], indent=2))

if __name__ == "__main__":
    main()
