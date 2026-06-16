"""Verify v0.2 release candidate readiness.

This script checks file presence, summary outputs, selected script compilation,
and selected headline values for the Human-Centered QUBO Scheduling v0.2 release candidate.

It does not rerun expensive experiments.
"""

from __future__ import annotations

import csv
import json
import py_compile
import subprocess
from pathlib import Path

DOC_FILES = [
    "README.md",
    "docs/project_milestone_v0_1_summary.md",
    "docs/project_roadmap_v0_2.md",
    "docs/project_milestone_v0_2_progress_summary.md",
    "docs/project_milestone_v0_2_current_overall_checkpoint.md",
    "docs/tiny_qaoa_package_v0_2_checkpoint_summary.md",
    "docs/project_v0_2_release_candidate_checklist.md",
    "docs/project_v0_2_release_style_summary.md",
    "docs/external_solver_benchmark_template.md",
    "docs/sample_4x4_qubo_pilot_technical_validation_report.md",
    "docs/sample_4x4_reproducibility_workflow.md",
]

SUMMARY_FILES = [
    "results/tables/sample_4x4_sparse_qubo_solver_ready_metadata.json",
    "results/tables/sample_4x4_cpsat_squared_target_summary.json",
    "results/tables/sample_4x4_local_search_parameter_sensitivity_best.json",
    "results/tables/sample_4x4_tuned_local_qubo_solution_component_summary.json",
    "results/tables/sample_4x4_qubo_to_ising_metadata_summary.json",
    "results/tables/sample_4x4_ising_energy_validation_summary.json",
    "results/tables/sample_4x4_runtime_memory_profile_summary.json",
    "results/tables/small_external_package_solver_benchmark_summary.json",
    "results/tables/small_package_scaled_export_validation_summary.json",
    "results/tables/small_package_dimod_bqm_energy_validation_summary.json",
    "results/tables/small_package_dimod_import_smoke_test_summary.json",
    "results/tables/tiny_qaoa_ready_package_summary.json",
    "results/tables/tiny_qiskit_optimization_smoke_test_summary.json",
    "results/tables/tiny_qiskit_classical_optimizer_smoke_test_summary.json",
    "results/tables/tiny_qaoa_simulator_smoke_test_summary.json",
    "results/tables/tiny_qaoa_parameter_sensitivity_best.json",
    "results/tables/external_solver_benchmark_schema.json",
]

PACKAGE_DIRS = [
    "exports/small_time_indexed_solver_package",
    "exports/tiny_qaoa_ready_package",
]

SCRIPTS_TO_COMPILE = [
    "scripts/create_external_solver_benchmark_template.py",
    "scripts/run_small_package_dimod_import_smoke_test.py",
    "scripts/validate_small_package_scaled_exports.py",
    "scripts/run_tiny_qiskit_optimization_smoke_test.py",
    "scripts/run_tiny_qiskit_classical_optimizer_smoke_test.py",
    "scripts/run_tiny_qaoa_simulator_smoke_test.py",
    "scripts/run_tiny_qaoa_parameter_sensitivity.py",
]

def add_check(rows, name, status, details):
    rows.append({"check_name": name, "status": status, "details": details})

def exists_check(rows, category, path):
    p = Path(path)
    add_check(rows, category + ": " + path, "PASS" if p.exists() else "FAIL", "exists=" + str(p.exists()))

def read_json(path):
    return json.loads(Path(path).read_text())

def main():
    rows = []

    for path in DOC_FILES:
        exists_check(rows, "doc_file", path)

    for path in SUMMARY_FILES:
        exists_check(rows, "summary_file", path)

    for path in PACKAGE_DIRS:
        exists_check(rows, "package_dir", path)

    for script in SCRIPTS_TO_COMPILE:
        try:
            py_compile.compile(script, doraise=True)
            add_check(rows, "py_compile: " + script, "PASS", "compiled")
        except Exception as exc:
            add_check(rows, "py_compile: " + script, "FAIL", repr(exc))

    # Headline value checks.
    try:
        small_bench = read_json("results/tables/small_external_package_solver_benchmark_summary.json")
        add_check(rows, "small_package_bruteforce_optimum", "PASS" if abs(float(small_bench["brute_force_optimum"]) - 5.30) < 1e-9 else "FAIL", str(small_bench.get("brute_force_optimum")))
        add_check(rows, "small_package_best_sa_success_rate", "PASS" if abs(float(small_bench["best_sa_success_rate"]) - 0.725) < 1e-9 else "FAIL", str(small_bench.get("best_sa_success_rate")))
    except Exception as exc:
        add_check(rows, "small_package_headline_values", "FAIL", repr(exc))

    try:
        dimod_summary = read_json("results/tables/small_package_dimod_import_smoke_test_summary.json")
        add_check(rows, "small_package_dimod_import_status", "PASS" if dimod_summary.get("status") == "PASS" else "FAIL", str(dimod_summary.get("status")))
    except Exception as exc:
        add_check(rows, "small_package_dimod_import_status", "FAIL", repr(exc))

    try:
        scaled_summary = read_json("results/tables/small_package_scaled_export_validation_summary.json")
        add_check(rows, "small_package_scaled_export_status", "PASS" if scaled_summary.get("validation_status") == "PASS" else "FAIL", str(scaled_summary.get("validation_status")))
        add_check(rows, "small_package_scaled_argmin_consistent", "PASS" if scaled_summary.get("argmin_consistent") is True else "FAIL", str(scaled_summary.get("argmin_consistent")))
    except Exception as exc:
        add_check(rows, "small_package_scaled_export_values", "FAIL", repr(exc))

    try:
        tiny_summary = read_json("results/tables/tiny_qaoa_ready_package_summary.json")
        add_check(rows, "tiny_package_known_best_bitstring", "PASS" if tiny_summary.get("best_bitstring") == "101001" else "FAIL", str(tiny_summary.get("best_bitstring")))
        add_check(rows, "tiny_package_known_best_energy", "PASS" if abs(float(tiny_summary["best_energy"]) - 4.0) < 1e-9 else "FAIL", str(tiny_summary.get("best_energy")))
    except Exception as exc:
        add_check(rows, "tiny_package_headline_values", "FAIL", repr(exc))

    try:
        qaoa_summary = read_json("results/tables/tiny_qaoa_simulator_smoke_test_summary.json")
        add_check(rows, "tiny_qaoa_smoke_status", "PASS" if qaoa_summary.get("status") == "PASS" else "FAIL", str(qaoa_summary.get("status")))
        add_check(rows, "tiny_qaoa_gap_to_known", "PASS" if abs(float(qaoa_summary["qaoa_gap_to_known"])) < 1e-9 else "FAIL", str(qaoa_summary.get("qaoa_gap_to_known")))
    except Exception as exc:
        add_check(rows, "tiny_qaoa_smoke_values", "FAIL", repr(exc))

    try:
        qaoa_sens = read_json("results/tables/tiny_qaoa_parameter_sensitivity_best.json")
        add_check(rows, "tiny_qaoa_sensitivity_success_rate", "PASS" if float(qaoa_sens["success_rate"]) >= 0.95 else "FAIL", str(qaoa_sens.get("success_rate")))
        add_check(rows, "tiny_qaoa_sensitivity_pass_count", "PASS" if int(qaoa_sens["pass_count"]) == 44 else "FAIL", str(qaoa_sens.get("pass_count")))
    except Exception as exc:
        add_check(rows, "tiny_qaoa_sensitivity_values", "FAIL", repr(exc))

    # Git status check.
    try:
        proc = subprocess.run(["git", "status", "--short"], capture_output=True, text=True, check=True)
        clean = proc.stdout.strip() == ""
        add_check(rows, "git_status_clean_before_verification_outputs", "PASS" if clean else "WARN", proc.stdout.strip())
    except Exception as exc:
        add_check(rows, "git_status_clean_before_verification_outputs", "WARN", repr(exc))

    out_csv = Path("results/tables/project_v0_2_release_candidate_verification_checks.csv")
    out_json = Path("results/tables/project_v0_2_release_candidate_verification_summary.json")
    out_csv.parent.mkdir(parents=True, exist_ok=True)

    with out_csv.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["check_name", "status", "details"])
        writer.writeheader()
        writer.writerows(rows)

    pass_count = sum(1 for r in rows if r["status"] == "PASS")
    fail_count = sum(1 for r in rows if r["status"] == "FAIL")
    warn_count = sum(1 for r in rows if r["status"] == "WARN")
    overall_status = "PASS" if fail_count == 0 else "FAIL"

    summary = {
        "experiment": "project_v0_2_release_candidate_verification",
        "overall_status": overall_status,
        "num_checks": len(rows),
        "pass_count": pass_count,
        "fail_count": fail_count,
        "warn_count": warn_count,
        "checks_csv": str(out_csv),
        "note": "Verification script for v0.2 release candidate readiness. Does not rerun expensive experiments.",
    }
    out_json.write_text(json.dumps(summary, indent=2))

    print("=== v0.2 release candidate verification complete ===")
    print("overall_status =", overall_status)
    print("num_checks =", len(rows))
    print("pass_count =", pass_count)
    print("fail_count =", fail_count)
    print("warn_count =", warn_count)
    print("saved checks =", out_csv)
    print("saved summary =", out_json)

if __name__ == "__main__":
    main()
