"""
Component-wise energy validation for streamed sample_4x4 sparse QUBO export.

Purpose
-------
This script validates the large streamed sparse QUBO coefficient CSV without
loading the full coefficient dictionary into memory.

It does the following:

1. Builds the same representative sample_4x4 variable index used by the
   streaming exporter.
2. Generates sampled binary assignments:
   - all-zero vector
   - greedy feasible schedule
   - random one-start schedules
   - random binary schedules
3. Computes direct objective for each sampled assignment.
4. Computes streamed QUBO energy by scanning the coefficient CSV in chunks.
5. Compares streamed QUBO energy against direct objective.

The streamed coefficient file is expected at:

    results/tables/sample_4x4_sparse_qubo_coefficients_stream.csv

This file is intentionally ignored by Git because it is large.

This is a validation step, not an optimization step.
"""

from __future__ import annotations

import argparse
import csv
import json
import random
import time
from pathlib import Path
from typing import Dict, List, Tuple

import pandas as pd


# -----------------------------
# sample_4x4 representative scale
# Must match export_sample_4x4_sparse_qubo_streaming.py
# -----------------------------

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

DEFAULT_HUMAN_REWARD = 2.5
DEFAULT_TARGET_HUMAN_ASSIGNMENTS = 4
DEFAULT_LAMBDA_TARGET = 1.0
DEFAULT_ASSIGNMENT_PENALTY = 30.0
DEFAULT_RESOURCE_OVERLAP_PENALTY = 30.0
DEFAULT_PRECEDENCE_PENALTY = 30.0


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


def assignment_cost(op: int, r: int) -> float:
    _, step = operation_job_step(op)

    if resource_type(r) == "machine":
        return 2.0 + 0.3 * step
    if resource_type(r) == "robot":
        return 2.5 + 0.4 * step
    return 2.5 + 0.2 * step


def workload_cost(op: int, r: int) -> float:
    if r not in HUMAN_RESOURCES:
        return 0.0

    _, step = operation_job_step(op)
    return [1.0, 1.5, 2.0, 2.5][step]


def ergonomic_cost(op: int, r: int) -> float:
    if r not in HUMAN_RESOURCES:
        return 0.0

    _, step = operation_job_step(op)
    return [0.6, 0.9, 1.2, 1.5][step]


def start_time_weight(op: int) -> float:
    _, step = operation_job_step(op)
    return [0.00, 0.05, 0.10, 0.15][step]


def build_valid_variables() -> List[Tuple[int, int, int]]:
    valid = []

    for op in range(NUM_OPERATIONS):
        for r in range(NUM_RESOURCES):
            d = duration(op, r)
            latest_start = HORIZON - d

            for t in range(latest_start + 1):
                valid.append((op, r, t))

    return valid


def build_groups(idx_to_var: Dict[int, Tuple[int, int, int]]):
    op_vars: Dict[int, List[int]] = {op: [] for op in range(NUM_OPERATIONS)}
    resource_vars: Dict[int, List[int]] = {r: [] for r in range(NUM_RESOURCES)}
    human_vars: List[int] = []

    for idx, (op, r, t) in idx_to_var.items():
        op_vars[op].append(idx)
        resource_vars[r].append(idx)

        if r in HUMAN_RESOURCES:
            human_vars.append(idx)

    return op_vars, resource_vars, human_vars


def precedence_arcs() -> List[Tuple[int, int]]:
    arcs = []

    for job in range(NUM_JOBS):
        for step in range(OPS_PER_JOB - 1):
            pred = job * OPS_PER_JOB + step
            succ = job * OPS_PER_JOB + step + 1
            arcs.append((pred, succ))

    return arcs


# -----------------------------
# Sample assignment generation
# -----------------------------

def make_all_zero(num_variables: int) -> set[int]:
    return set()


def make_greedy_feasible(
    var_to_idx: Dict[Tuple[int, int, int], int],
) -> set[int]:
    """
    Build a simple serial feasible schedule.

    For each job, operations run in precedence order.
    We use machine resources when possible and offset jobs to avoid obvious
    overlap. This is not optimized; it is only a validation sample.
    """

    selected: set[int] = set()

    job_offsets = {
        0: 0,
        1: 10,
        2: 20,
        3: 30,
    }

    for job in range(NUM_JOBS):
        current_time = job_offsets[job]

        for step in range(OPS_PER_JOB):
            op = job * OPS_PER_JOB + step

            chosen = None

            # Prefer machines first, then robots, then humans.
            resource_order = MACHINE_RESOURCES + ROBOT_RESOURCES + HUMAN_RESOURCES

            for r in resource_order:
                for t in range(current_time, HORIZON):
                    key = (op, r, t)

                    if key not in var_to_idx:
                        continue

                    finish = t + duration(op, r)

                    if finish <= HORIZON:
                        chosen = key
                        break

                if chosen is not None:
                    break

            if chosen is None:
                raise RuntimeError(f"Could not construct greedy assignment for op {op}")

            selected.add(var_to_idx[chosen])
            current_time = chosen[2] + duration(chosen[0], chosen[1])

    return selected


def make_random_one_start(
    rng: random.Random,
    op_vars: Dict[int, List[int]],
) -> set[int]:
    selected: set[int] = set()

    for op in range(NUM_OPERATIONS):
        selected.add(rng.choice(op_vars[op]))

    return selected


def make_random_sparse_binary(
    rng: random.Random,
    num_variables: int,
    activation_probability: float,
) -> set[int]:
    selected: set[int] = set()

    for idx in range(num_variables):
        if rng.random() < activation_probability:
            selected.add(idx)

    return selected


# -----------------------------
# Direct objective
# -----------------------------

def total_cost_without_reward(
    selected: set[int],
    idx_to_var: Dict[int, Tuple[int, int, int]],
) -> float:
    cost = 0.0

    for idx in selected:
        op, r, t = idx_to_var[idx]

        cost += (
            assignment_cost(op, r)
            + workload_cost(op, r)
            + ergonomic_cost(op, r)
            + start_time_weight(op) * t
        )

    return cost


def human_count(
    selected: set[int],
    idx_to_var: Dict[int, Tuple[int, int, int]],
) -> int:
    return sum(1 for idx in selected if idx_to_var[idx][1] in HUMAN_RESOURCES)


def assignment_penalty_value(
    selected: set[int],
    op_vars: Dict[int, List[int]],
    assignment_penalty: float,
) -> float:
    penalty = 0.0

    for op, vars_for_op in op_vars.items():
        count = sum(1 for idx in vars_for_op if idx in selected)
        penalty += assignment_penalty * (count - 1) ** 2

    return penalty


def resource_overlap_penalty_value(
    selected: set[int],
    idx_to_var: Dict[int, Tuple[int, int, int]],
    resource_overlap_penalty: float,
) -> float:
    penalty = 0.0
    selected_list = sorted(selected)

    for a_pos in range(len(selected_list)):
        i = selected_list[a_pos]
        op1, r1, t1 = idx_to_var[i]
        d1 = duration(op1, r1)
        start1 = t1
        finish1 = t1 + d1

        for b_pos in range(a_pos + 1, len(selected_list)):
            j = selected_list[b_pos]
            op2, r2, t2 = idx_to_var[j]

            if op1 == op2:
                continue

            if r1 != r2:
                continue

            d2 = duration(op2, r2)
            start2 = t2
            finish2 = t2 + d2

            if start1 < finish2 and start2 < finish1:
                penalty += resource_overlap_penalty

    return penalty


def precedence_penalty_value(
    selected: set[int],
    idx_to_var: Dict[int, Tuple[int, int, int]],
    precedence_penalty: float,
) -> float:
    penalty = 0.0

    selected_by_op: Dict[int, List[Tuple[int, int, int]]] = {
        op: [] for op in range(NUM_OPERATIONS)
    }

    for idx in selected:
        op, r, t = idx_to_var[idx]
        selected_by_op[op].append((op, r, t))

    for pred, succ in precedence_arcs():
        for pred_op, pred_r, pred_t in selected_by_op[pred]:
            pred_finish = pred_t + duration(pred_op, pred_r)

            for succ_op, succ_r, succ_t in selected_by_op[succ]:
                if succ_t < pred_finish:
                    penalty += precedence_penalty

    return penalty


def direct_objective(
    selected: set[int],
    idx_to_var: Dict[int, Tuple[int, int, int]],
    op_vars: Dict[int, List[int]],
    human_reward: float,
    lambda_target: float,
    target_human_assignments: int,
    assignment_penalty: float,
    resource_overlap_penalty: float,
    precedence_penalty: float,
) -> Dict[str, float]:
    h_count = human_count(selected, idx_to_var)

    base_cost = total_cost_without_reward(selected, idx_to_var)
    reward_term = human_reward * h_count
    target_penalty = lambda_target * (h_count - target_human_assignments) ** 2
    assign_pen = assignment_penalty_value(selected, op_vars, assignment_penalty)
    overlap_pen = resource_overlap_penalty_value(
        selected, idx_to_var, resource_overlap_penalty
    )
    prec_pen = precedence_penalty_value(selected, idx_to_var, precedence_penalty)

    total = base_cost - reward_term + target_penalty + assign_pen + overlap_pen + prec_pen

    return {
        "total_cost_without_reward": base_cost,
        "human_count": h_count,
        "reward_term": reward_term,
        "target_penalty": target_penalty,
        "assignment_penalty": assign_pen,
        "resource_overlap_penalty": overlap_pen,
        "precedence_penalty": prec_pen,
        "direct_objective": total,
    }


# -----------------------------
# Streamed CSV energy
# -----------------------------

def streamed_qubo_energy_for_samples(
    coeff_csv: Path,
    sample_selected_sets: List[set[int]],
    constant: float,
    chunksize: int,
) -> List[float]:
    energies = [constant for _ in sample_selected_sets]

    usecols = ["i", "j", "coefficient"]

    for chunk_id, chunk in enumerate(
        pd.read_csv(coeff_csv, usecols=usecols, chunksize=chunksize)
    ):
        if chunk_id % 20 == 0:
            print(f"Reading coefficient chunk {chunk_id}")

        # Iterate rows. For validation sample count kept small, this is acceptable.
        for row in chunk.itertuples(index=False):
            i = int(row.i)
            j = int(row.j)
            coeff = float(row.coefficient)

            for sample_idx, selected in enumerate(sample_selected_sets):
                if i in selected and j in selected:
                    energies[sample_idx] += coeff

    return energies


def main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--coeff-csv",
        type=str,
        default="results/tables/sample_4x4_sparse_qubo_coefficients_stream.csv",
    )

    parser.add_argument(
        "--streaming-summary",
        type=str,
        default="results/tables/sample_4x4_sparse_qubo_streaming_summary.json",
    )

    parser.add_argument("--num-one-start-samples", type=int, default=5)
    parser.add_argument("--num-random-sparse-samples", type=int, default=5)
    parser.add_argument("--activation-probability", type=float, default=0.002)
    parser.add_argument("--seed", type=int, default=123)
    parser.add_argument("--chunksize", type=int, default=250000)

    parser.add_argument(
        "--out",
        type=str,
        default="results/tables/sample_4x4_streamed_qubo_energy_validation.csv",
    )

    parser.add_argument(
        "--summary-out",
        type=str,
        default="results/tables/sample_4x4_streamed_qubo_energy_validation_summary.json",
    )

    args = parser.parse_args()

    coeff_csv = Path(args.coeff_csv)

    if not coeff_csv.exists():
        raise FileNotFoundError(
            f"Coefficient CSV not found: {coeff_csv}. "
            "Run scripts/export_sample_4x4_sparse_qubo_streaming.py first."
        )

    streaming_summary = json.loads(Path(args.streaming_summary).read_text())

    human_reward = float(streaming_summary["human_reward"])
    lambda_target = float(streaming_summary["lambda_target"])
    target_human_assignments = int(streaming_summary["target_human_assignments"])
    assignment_penalty = float(streaming_summary["assignment_penalty"])
    resource_overlap_penalty = float(streaming_summary["resource_overlap_penalty"])
    precedence_penalty = float(streaming_summary["precedence_penalty"])
    constant = float(streaming_summary["constant"])

    valid_variables = build_valid_variables()
    var_to_idx = {key: idx for idx, key in enumerate(valid_variables)}
    idx_to_var = {idx: key for key, idx in var_to_idx.items()}
    op_vars, resource_vars, human_vars = build_groups(idx_to_var)

    rng = random.Random(args.seed)

    sample_names: List[str] = []
    sample_selected_sets: List[set[int]] = []

    sample_names.append("all_zero")
    sample_selected_sets.append(make_all_zero(len(valid_variables)))

    sample_names.append("greedy_feasible")
    sample_selected_sets.append(make_greedy_feasible(var_to_idx))

    for k in range(args.num_one_start_samples):
        sample_names.append(f"random_one_start_{k}")
        sample_selected_sets.append(make_random_one_start(rng, op_vars))

    for k in range(args.num_random_sparse_samples):
        sample_names.append(f"random_sparse_{k}")
        sample_selected_sets.append(
            make_random_sparse_binary(
                rng,
                len(valid_variables),
                args.activation_probability,
            )
        )

    start_wall = time.time()

    print("=== Computing direct objectives ===")

    direct_rows = []

    for name, selected in zip(sample_names, sample_selected_sets):
        components = direct_objective(
            selected=selected,
            idx_to_var=idx_to_var,
            op_vars=op_vars,
            human_reward=human_reward,
            lambda_target=lambda_target,
            target_human_assignments=target_human_assignments,
            assignment_penalty=assignment_penalty,
            resource_overlap_penalty=resource_overlap_penalty,
            precedence_penalty=precedence_penalty,
        )

        direct_rows.append(components)

        print(
            f"{name}: selected={len(selected)}, direct={components['direct_objective']:.4f}, "
            f"human_count={components['human_count']}"
        )

    print("=== Computing streamed QUBO energies from CSV ===")

    streamed_energies = streamed_qubo_energy_for_samples(
        coeff_csv=coeff_csv,
        sample_selected_sets=sample_selected_sets,
        constant=constant,
        chunksize=args.chunksize,
    )

    elapsed = time.time() - start_wall

    rows = []

    for name, selected, components, streamed_energy in zip(
        sample_names,
        sample_selected_sets,
        direct_rows,
        streamed_energies,
    ):
        abs_error = abs(streamed_energy - components["direct_objective"])

        rows.append(
            {
                "sample_name": name,
                "num_selected_variables": len(selected),
                "human_count": components["human_count"],
                "total_cost_without_reward": components["total_cost_without_reward"],
                "reward_term": components["reward_term"],
                "target_penalty": components["target_penalty"],
                "assignment_penalty": components["assignment_penalty"],
                "resource_overlap_penalty": components["resource_overlap_penalty"],
                "precedence_penalty": components["precedence_penalty"],
                "direct_objective": components["direct_objective"],
                "streamed_qubo_energy": streamed_energy,
                "abs_error": abs_error,
            }
        )

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    with out_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    max_abs_error = max(row["abs_error"] for row in rows)
    mean_abs_error = sum(row["abs_error"] for row in rows) / len(rows)

    summary = {
        "experiment": "sample_4x4_streamed_qubo_energy_validation",
        "coeff_csv": str(coeff_csv),
        "num_samples": len(rows),
        "sample_names": sample_names,
        "chunksize": args.chunksize,
        "elapsed_seconds": elapsed,
        "max_abs_error": max_abs_error,
        "mean_abs_error": mean_abs_error,
        "validation_status": "PASS" if max_abs_error < 1e-7 else "FAIL",
        "note": "Validation reads large streamed coefficient CSV in chunks; coefficient CSV is local and ignored by Git.",
    }

    summary_path = Path(args.summary_out)
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(json.dumps(summary, indent=2))

    print("=== sample_4x4 streamed QUBO energy validation complete ===")
    print(f"num_samples = {len(rows)}")
    print(f"elapsed_seconds = {elapsed:.2f}")
    print(f"max_abs_error = {max_abs_error}")
    print(f"mean_abs_error = {mean_abs_error}")
    print(f"validation_status = {summary['validation_status']}")
    print(f"saved validation rows = {out_path}")
    print(f"saved summary = {summary_path}")


if __name__ == "__main__":
    main()
