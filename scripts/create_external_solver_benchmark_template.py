"""Create external solver benchmark schema and example template.

This script creates a standardized benchmark schema for recording solver results
across QUBO/Ising/BQM workflows.

It does not run any solver.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

SCHEMA_FIELDS = [
    "experiment_id",
    "instance_id",
    "package_dir",
    "problem_family",
    "formulation_type",
    "vartype",
    "solver_name",
    "solver_backend",
    "solver_version",
    "run_type",
    "num_variables",
    "num_linear_terms",
    "num_quadratic_terms",
    "num_constraints_original",
    "reference_solver",
    "reference_energy",
    "reference_bitstring",
    "best_energy",
    "best_bitstring",
    "gap_to_reference",
    "relative_gap_to_reference",
    "feasible",
    "constraint_violation_count",
    "num_reads_or_restarts",
    "iterations_or_maxiter",
    "qaoa_reps",
    "seed",
    "runtime_seconds",
    "success_count",
    "success_rate",
    "status",
    "notes",
]

FIELD_DESCRIPTIONS = {
    "experiment_id": "Unique benchmark experiment identifier.",
    "instance_id": "Instance name, e.g., tiny_qaoa_ready_package or small_time_indexed_solver_package.",
    "package_dir": "Path to exported package directory.",
    "problem_family": "Problem class, e.g., human_centered_scheduling_qubo.",
    "formulation_type": "QUBO, Ising, BQM_BINARY, BQM_SPIN, QuadraticProgram, etc.",
    "vartype": "BINARY, SPIN, or mixed/software-specific.",
    "solver_name": "Solver or algorithm name.",
    "solver_backend": "Backend or primitive, e.g., StatevectorSampler, dimod, manual_bruteforce.",
    "solver_version": "Package or solver version if available.",
    "run_type": "bruteforce, classical_exact, simulated_annealing, qaoa_simulator, hardware, etc.",
    "num_variables": "Number of binary/spin variables.",
    "num_linear_terms": "Number of linear terms.",
    "num_quadratic_terms": "Number of quadratic terms/interactions.",
    "num_constraints_original": "Number of original explicit constraints before QUBO penalty conversion, if applicable.",
    "reference_solver": "Reference method, e.g., brute_force, CP-SAT, NumPyMinimumEigensolver.",
    "reference_energy": "Reference objective/energy value.",
    "reference_bitstring": "Reference best bitstring if available.",
    "best_energy": "Best energy found by solver.",
    "best_bitstring": "Best bitstring found by solver.",
    "gap_to_reference": "best_energy - reference_energy.",
    "relative_gap_to_reference": "gap_to_reference / abs(reference_energy), when meaningful.",
    "feasible": "Whether decoded solution is feasible under original constraints.",
    "constraint_violation_count": "Number of detected original-constraint violations.",
    "num_reads_or_restarts": "Reads, shots, samples, restarts, or repeated trials.",
    "iterations_or_maxiter": "Iterations or optimizer maxiter.",
    "qaoa_reps": "QAOA depth/reps if applicable.",
    "seed": "Random seed if applicable.",
    "runtime_seconds": "Wall-clock runtime in seconds if measured.",
    "success_count": "Number of successful optimum or target recoveries.",
    "success_rate": "success_count divided by attempts.",
    "status": "PASS, PARTIAL_PASS, FAIL, SKIPPED, or descriptive status.",
    "notes": "Important caveats, e.g., toy simulator only, no hardware execution.",
}

EXAMPLE_ROWS = [
    {
        "experiment_id": "tiny_qaoa_bruteforce_reference",
        "instance_id": "tiny_qaoa_ready_package",
        "package_dir": "exports/tiny_qaoa_ready_package",
        "problem_family": "human_centered_scheduling_qubo_toy",
        "formulation_type": "QUBO",
        "vartype": "BINARY",
        "solver_name": "manual_bruteforce",
        "solver_backend": "python_itertools",
        "solver_version": "",
        "run_type": "bruteforce",
        "num_variables": 6,
        "num_linear_terms": 6,
        "num_quadratic_terms": 7,
        "num_constraints_original": 3,
        "reference_solver": "manual_bruteforce",
        "reference_energy": 4.0,
        "reference_bitstring": "101001",
        "best_energy": 4.0,
        "best_bitstring": "101001",
        "gap_to_reference": 0.0,
        "relative_gap_to_reference": 0.0,
        "feasible": True,
        "constraint_violation_count": 0,
        "num_reads_or_restarts": 64,
        "iterations_or_maxiter": "",
        "qaoa_reps": "",
        "seed": "",
        "runtime_seconds": "",
        "success_count": 64,
        "success_rate": 1.0,
        "status": "PASS",
        "notes": "Exhaustive reference over all 64 assignments.",
    },
    {
        "experiment_id": "tiny_qaoa_statevector_qaoa_sensitivity_best",
        "instance_id": "tiny_qaoa_ready_package",
        "package_dir": "exports/tiny_qaoa_ready_package",
        "problem_family": "human_centered_scheduling_qubo_toy",
        "formulation_type": "QuadraticProgram_QAOA",
        "vartype": "BINARY",
        "solver_name": "QAOA",
        "solver_backend": "StatevectorSampler",
        "solver_version": "",
        "run_type": "qaoa_simulator",
        "num_variables": 6,
        "num_linear_terms": 6,
        "num_quadratic_terms": 7,
        "num_constraints_original": 3,
        "reference_solver": "manual_bruteforce",
        "reference_energy": 4.0,
        "reference_bitstring": "101001",
        "best_energy": 4.0,
        "best_bitstring": "101001",
        "gap_to_reference": 0.0,
        "relative_gap_to_reference": 0.0,
        "feasible": True,
        "constraint_violation_count": 0,
        "num_reads_or_restarts": 1,
        "iterations_or_maxiter": 50,
        "qaoa_reps": 1,
        "seed": 123,
        "runtime_seconds": "",
        "success_count": 44,
        "success_rate": 0.9778,
        "status": "PASS",
        "notes": "Toy QAOA simulator/software experiment only; no quantum hardware or quantum advantage claim.",
    },
    {
        "experiment_id": "small_package_sa_sensitivity_best",
        "instance_id": "small_time_indexed_solver_package",
        "package_dir": "exports/small_time_indexed_solver_package",
        "problem_family": "human_centered_scheduling_qubo_small",
        "formulation_type": "QUBO",
        "vartype": "BINARY",
        "solver_name": "simulated_annealing",
        "solver_backend": "custom_python_bitflip_sa",
        "solver_version": "",
        "run_type": "simulated_annealing",
        "num_variables": 15,
        "num_linear_terms": "",
        "num_quadratic_terms": 90,
        "num_constraints_original": "",
        "reference_solver": "manual_bruteforce",
        "reference_energy": 5.30,
        "reference_bitstring": "100000000000100",
        "best_energy": 5.30,
        "best_bitstring": "100000000000100",
        "gap_to_reference": 0.0,
        "relative_gap_to_reference": 0.0,
        "feasible": True,
        "constraint_violation_count": 0,
        "num_reads_or_restarts": 200,
        "iterations_or_maxiter": 10000,
        "qaoa_reps": "",
        "seed": 456,
        "runtime_seconds": "",
        "success_count": 145,
        "success_rate": 0.725,
        "status": "PASS",
        "notes": "Best custom SA sensitivity case; local classical heuristic.",
    },
]

def main() -> None:
    schema_csv = Path("results/tables/external_solver_benchmark_schema.csv")
    example_csv = Path("results/tables/external_solver_benchmark_template_example.csv")
    schema_json = Path("results/tables/external_solver_benchmark_schema.json")
    schema_csv.parent.mkdir(parents=True, exist_ok=True)

    with schema_csv.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["field", "description"])
        writer.writeheader()
        for field in SCHEMA_FIELDS:
            writer.writerow({"field": field, "description": FIELD_DESCRIPTIONS[field]})

    with example_csv.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=SCHEMA_FIELDS)
        writer.writeheader()
        writer.writerows(EXAMPLE_ROWS)

    schema_payload = {
        "experiment": "external_solver_benchmark_template_schema",
        "num_fields": len(SCHEMA_FIELDS),
        "fields": SCHEMA_FIELDS,
        "field_descriptions": FIELD_DESCRIPTIONS,
        "example_csv": str(example_csv),
        "schema_csv": str(schema_csv),
        "note": "Template only. This does not run any solver.",
    }
    schema_json.write_text(json.dumps(schema_payload, indent=2))

    print("=== external solver benchmark template created ===")
    print("schema_csv =", schema_csv)
    print("schema_json =", schema_json)
    print("example_csv =", example_csv)
    print("num_fields =", len(SCHEMA_FIELDS))

if __name__ == "__main__":
    main()
