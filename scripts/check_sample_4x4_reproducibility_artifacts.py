"""Check sample_4x4 reproducibility artifacts.

This script checks whether key tracked summaries and large local ignored artifacts
needed for the sample_4x4 QUBO/Ising prototype pipeline are present.

It does not regenerate artifacts. It only reports status.
"""

from __future__ import annotations

from pathlib import Path
import json

TRACKED_EXPECTED = [
    "README.md",
    "docs/sample_4x4_qubo_pilot_technical_validation_report.md",
    "results/current_pilot_checkpoint.md",
    "results/sample_4x4_current_release_checkpoint_summary.md",
    "results/tables/sample_4x4_sparse_qubo_solver_ready_metadata.json",
    "results/tables/sample_4x4_cpsat_squared_target_summary.json",
    "results/tables/sample_4x4_local_search_parameter_sensitivity_best.json",
    "results/tables/sample_4x4_tuned_local_qubo_solution_component_summary.json",
    "results/tables/sample_4x4_qubo_to_ising_metadata_summary.json",
    "results/tables/sample_4x4_ising_energy_validation_summary.json",
    "results/tables/sample_4x4_runtime_memory_profile_summary.json",
]

LARGE_LOCAL_ARTIFACTS = [
    "results/tables/sample_4x4_sparse_qubo_coefficients_stream.csv",
    "results/tables/sample_4x4_sparse_qubo_coefficients_merged.csv",
    "results/tables/sample_4x4_ising_couplers.csv",
]

OPTIONAL_LOCAL_ARTIFACTS = [
    "results/tables/local_search_parameter_sensitivity/run020_r30_it20000_t5.0_tf0.001_s789_best_solution.csv",
    "results/tables/local_search_parameter_sensitivity/run020_r30_it20000_t5.0_tf0.001_s789_summary.json",
]

def size_mb(path: Path):
    if not path.exists():
        return None
    return path.stat().st_size / (1024 * 1024)

def rows_for(paths, category):
    rows = []
    for item in paths:
        p = Path(item)
        rows.append({
            "category": category,
            "path": item,
            "exists": p.exists(),
            "size_mb": size_mb(p),
        })
    return rows

def main() -> None:
    rows = []
    rows.extend(rows_for(TRACKED_EXPECTED, "tracked_expected"))
    rows.extend(rows_for(LARGE_LOCAL_ARTIFACTS, "large_local_ignored"))
    rows.extend(rows_for(OPTIONAL_LOCAL_ARTIFACTS, "optional_local"))

    missing_tracked = [r["path"] for r in rows if r["category"] == "tracked_expected" and not r["exists"]]
    missing_large = [r["path"] for r in rows if r["category"] == "large_local_ignored" and not r["exists"]]

    print("=== sample_4x4 reproducibility artifact check ===")
    for row in rows:
        size_text = "" if row["size_mb"] is None else f" size_mb={row['size_mb']:.2f}"
        print(f"[{row['category']}] exists={row['exists']} {row['path']}{size_text}")

    print("")
    print(f"missing_tracked_count = {len(missing_tracked)}")
    print(f"missing_large_local_count = {len(missing_large)}")

    summary = {
        "experiment": "sample_4x4_reproducibility_artifact_check",
        "tracked_expected_count": len(TRACKED_EXPECTED),
        "large_local_artifact_count": len(LARGE_LOCAL_ARTIFACTS),
        "optional_local_artifact_count": len(OPTIONAL_LOCAL_ARTIFACTS),
        "missing_tracked": missing_tracked,
        "missing_large_local": missing_large,
        "rows": rows,
        "note": "Large local artifacts are intentionally ignored by Git and may need regeneration.",
    }

    out = Path("results/tables/sample_4x4_reproducibility_artifact_check_summary.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(summary, indent=2))
    print(f"saved summary = {out}")

if __name__ == "__main__":
    main()
