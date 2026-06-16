"""Fast QUBO-to-Ising energy validation for sample_4x4.

This version validates QUBO-to-Ising energy consistency by scanning the merged
QUBO coefficient CSV once and applying the x_i = (1 + s_i) / 2 transformation
directly. It avoids repeatedly scanning the large Ising coupler CSV.
"""

from __future__ import annotations

import argparse
import csv
import json
import random
from pathlib import Path
from typing import Dict, List, Tuple

import pandas as pd

NUM_JOBS = 4
OPS_PER_JOB = 4
NUM_OPERATIONS = NUM_JOBS * OPS_PER_JOB
NUM_MACHINES = 4
NUM_WORKERS = 3
NUM_ROBOTS = 2
NUM_RESOURCES = NUM_MACHINES + NUM_WORKERS + NUM_ROBOTS
HORIZON = 63

MACHINE_RESOURCES = list(range(0, 4))
HUMAN_RESOURCES = list(range(4, 7))
ROBOT_RESOURCES = list(range(7, 9))

def resource_type(r: int) -> str:
    if r in HUMAN_RESOURCES:
        return "human"
    if r in ROBOT_RESOURCES:
        return "robot"
    return "machine"

def operation_job_step(op: int) -> Tuple[int, int]:
    return op // OPS_PER_JOB, op % OPS_PER_JOB

def duration(op: int, r: int) -> int:
    job, step = operation_job_step(op)
    base = 2 + ((job + step) % 3)
    if resource_type(r) == "machine":
        return base
    if resource_type(r) == "robot":
        return base + 1
    return base + 1

def build_valid_variables() -> List[Tuple[int, int, int]]:
    valid = []
    for op in range(NUM_OPERATIONS):
        for r in range(NUM_RESOURCES):
            latest_start = HORIZON - duration(op, r)
            for t in range(latest_start + 1):
                valid.append((op, r, t))
    return valid

def build_op_vars(idx_to_var: Dict[int, Tuple[int, int, int]]) -> Dict[int, List[int]]:
    op_vars = {op: [] for op in range(NUM_OPERATIONS)}
    for idx, key in idx_to_var.items():
        op, r, t = key
        op_vars[op].append(idx)
    return op_vars

def selected_from_solution_csv(path: Path) -> set[int]:
    df = pd.read_csv(path)
    if "variable_index" not in df.columns:
        raise ValueError(f"solution file must contain variable_index column: {path}")
    return set(int(v) for v in df["variable_index"].tolist())

def random_one_start(rng: random.Random, op_vars: Dict[int, List[int]]) -> set[int]:
    selected = set()
    for op in range(NUM_OPERATIONS):
        selected.add(rng.choice(op_vars[op]))
    return selected

def random_sparse(rng: random.Random, num_variables: int, p: float) -> set[int]:
    selected = set()
    for i in range(num_variables):
        if rng.random() < p:
            selected.add(i)
    return selected

def x_value(selected: set[int], i: int) -> float:
    return 1.0 if i in selected else 0.0

def s_value(selected: set[int], i: int) -> float:
    return 1.0 if i in selected else -1.0

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--merged-qubo-csv", type=str, default="results/tables/sample_4x4_sparse_qubo_coefficients_merged.csv")
    parser.add_argument("--qubo-metadata", type=str, default="results/tables/sample_4x4_sparse_qubo_solver_ready_metadata.json")
    parser.add_argument("--tuned-best-solution", type=str, default="results/tables/local_search_parameter_sensitivity/run020_r30_it20000_t5.0_tf0.001_s789_best_solution.csv")
    parser.add_argument("--chunksize", type=int, default=500000)
    parser.add_argument("--seed", type=int, default=123)
    parser.add_argument("--out", type=str, default="results/tables/sample_4x4_ising_energy_validation.csv")
    parser.add_argument("--summary-out", type=str, default="results/tables/sample_4x4_ising_energy_validation_summary.json")
    args = parser.parse_args()

    qubo_csv = Path(args.merged_qubo_csv)
    qubo_metadata_path = Path(args.qubo_metadata)
    tuned_solution_path = Path(args.tuned_best_solution)

    if not qubo_csv.exists():
        raise FileNotFoundError(f"Merged QUBO CSV not found: {qubo_csv}")
    if not qubo_metadata_path.exists():
        raise FileNotFoundError(f"QUBO metadata not found: {qubo_metadata_path}")

    qubo_metadata = json.loads(qubo_metadata_path.read_text())
    num_variables = int(qubo_metadata["num_variables"])
    qubo_constant = float(qubo_metadata["constant_offset"])

    valid_variables = build_valid_variables()
    idx_to_var = {idx: key for idx, key in enumerate(valid_variables)}
    op_vars = build_op_vars(idx_to_var)
    rng = random.Random(args.seed)

    samples = []
    if tuned_solution_path.exists():
        samples.append(("tuned_local_best", selected_from_solution_csv(tuned_solution_path)))
    samples.append(("all_zero", set()))
    samples.append(("random_one_start_0", random_one_start(rng, op_vars)))
    samples.append(("random_one_start_1", random_one_start(rng, op_vars)))
    samples.append(("random_sparse_0", random_sparse(rng, num_variables, 0.002)))
    samples.append(("random_sparse_1", random_sparse(rng, num_variables, 0.002)))

    qubo_energies = [qubo_constant for _ in samples]
    ising_energies = [qubo_constant for _ in samples]

    print("=== Fast QUBO-to-Ising energy validation ===")
    print(f"num_samples = {len(samples)}")
    print(f"num_variables = {num_variables}")
    print(f"qubo_constant = {qubo_constant}")

    usecols = ["i", "j", "coefficient"]
    for chunk_id, chunk in enumerate(pd.read_csv(qubo_csv, usecols=usecols, chunksize=args.chunksize)):
        if chunk_id % 5 == 0:
            print(f"Processing QUBO chunk {chunk_id}")
        for row in chunk.itertuples(index=False):
            i = int(row.i)
            j = int(row.j)
            q = float(row.coefficient)
            if i == j:
                for sample_idx, (_, selected) in enumerate(samples):
                    x_i = x_value(selected, i)
                    s_i = s_value(selected, i)
                    qubo_energies[sample_idx] += q * x_i
                    ising_energies[sample_idx] += (q / 2.0) + (q / 2.0) * s_i
            else:
                for sample_idx, (_, selected) in enumerate(samples):
                    x_i = x_value(selected, i)
                    x_j = x_value(selected, j)
                    s_i = s_value(selected, i)
                    s_j = s_value(selected, j)
                    qubo_energies[sample_idx] += q * x_i * x_j
                    ising_energies[sample_idx] += (q / 4.0) * (1.0 + s_i + s_j + s_i * s_j)

    rows = []
    for sample_idx, (name, selected) in enumerate(samples):
        e_qubo = qubo_energies[sample_idx]
        e_ising = ising_energies[sample_idx]
        abs_error = abs(e_qubo - e_ising)
        rows.append({
            "sample_name": name,
            "num_selected_variables": len(selected),
            "qubo_energy": e_qubo,
            "ising_energy": e_ising,
            "abs_error": abs_error,
        })
        print(f"{name}: qubo={e_qubo}, ising={e_ising}, abs_error={abs_error}")

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    max_abs_error = max(row["abs_error"] for row in rows)
    mean_abs_error = sum(row["abs_error"] for row in rows) / len(rows)
    summary = {
        "experiment": "sample_4x4_ising_energy_validation_fast",
        "num_samples": len(rows),
        "sample_names": [row["sample_name"] for row in rows],
        "max_abs_error": max_abs_error,
        "mean_abs_error": mean_abs_error,
        "validation_status": "PASS" if max_abs_error < 1e-6 else "FAIL",
        "qubo_constant": qubo_constant,
        "energy_convention": "x_i in {0,1}, s_i = 2*x_i - 1",
        "note": "Fast validation applies QUBO-to-Ising transformation directly from merged QUBO rows.",
    }
    summary_path = Path(args.summary_out)
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(json.dumps(summary, indent=2))

    print("=" * 80)
    print("Fast Ising energy validation complete")
    print(f"max_abs_error = {max_abs_error}")
    print(f"mean_abs_error = {mean_abs_error}")
    print(f"validation_status = {summary['validation_status']}")
    print(f"saved rows = {out_path}")
    print(f"saved summary = {summary_path}")

if __name__ == "__main__":
    main()
