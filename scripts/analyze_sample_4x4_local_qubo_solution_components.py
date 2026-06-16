"""
Analyze component costs for the best local-search solution from the merged
sample_4x4 sparse QUBO.

Purpose
-------
STEP 17 found a best local QUBO-search solution. This script reads the decoded
best solution CSV and recomputes interpretable objective components:

1. assignment cost
2. workload cost
3. ergonomic cost
4. start-time cost
5. total cost without reward
6. human reward term
7. squared target penalty
8. assignment/resource-overlap/precedence penalties
9. final representative QUBO objective

It also compares the local QUBO-search solution against the previously reported
sample_4x4 CP-SAT baseline summary values.

This remains prototype/pilot validation.
"""

from __future__ import annotations

import argparse
import csv
import json
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


def precedence_arcs() -> List[Tuple[int, int]]:
    arcs = []

    for job in range(NUM_JOBS):
        for step in range(OPS_PER_JOB - 1):
            pred = job * OPS_PER_JOB + step
            succ = job * OPS_PER_JOB + step + 1
            arcs.append((pred, succ))

    return arcs


def compute_assignment_violations(solution: pd.DataFrame) -> int:
    counts = solution.groupby("operation").size().to_dict()

    violations = 0

    for op in range(NUM_OPERATIONS):
        count = counts.get(op, 0)
        if count != 1:
            violations += abs(count - 1)

    return violations


def compute_overlap_violations(solution: pd.DataFrame) -> int:
    rows = solution.to_dict("records")
    violations = 0

    for a in range(len(rows)):
        row_a = rows[a]
        op_a = int(row_a["operation"])
        r_a = int(row_a["resource"])
        start_a = int(row_a["start_time"])
        finish_a = int(row_a["finish_time"])

        for b in range(a + 1, len(rows)):
            row_b = rows[b]
            op_b = int(row_b["operation"])
            r_b = int(row_b["resource"])
            start_b = int(row_b["start_time"])
            finish_b = int(row_b["finish_time"])

            if op_a == op_b:
                continue

            if r_a != r_b:
                continue

            if start_a < finish_b and start_b < finish_a:
                violations += 1

    return violations


def compute_precedence_violations(solution: pd.DataFrame) -> int:
    by_op = {
        int(row["operation"]): row
        for row in solution.to_dict("records")
    }

    violations = 0

    for pred, succ in precedence_arcs():
        if pred not in by_op or succ not in by_op:
            violations += 1
            continue

        pred_finish = int(by_op[pred]["finish_time"])
        succ_start = int(by_op[succ]["start_time"])

        if succ_start < pred_finish:
            violations += 1

    return violations


def main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--best-solution",
        type=str,
        default="results/tables/sample_4x4_merged_qubo_local_search_best_solution.csv",
    )

    parser.add_argument(
        "--local-search-summary",
        type=str,
        default="results/tables/sample_4x4_merged_qubo_local_search_summary.json",
    )

    parser.add_argument(
        "--streaming-summary",
        type=str,
        default="results/tables/sample_4x4_sparse_qubo_streaming_summary.json",
    )

    parser.add_argument(
        "--component-out",
        type=str,
        default="results/tables/sample_4x4_local_qubo_solution_component_summary.csv",
    )

    parser.add_argument(
        "--operation-out",
        type=str,
        default="results/tables/sample_4x4_local_qubo_solution_operation_components.csv",
    )

    parser.add_argument(
        "--comparison-out",
        type=str,
        default="results/tables/sample_4x4_local_qubo_vs_cpsat_baseline_comparison.csv",
    )

    parser.add_argument(
        "--summary-out",
        type=str,
        default="results/tables/sample_4x4_local_qubo_solution_component_summary.json",
    )

    args = parser.parse_args()

    best_solution_path = Path(args.best_solution)
    local_summary_path = Path(args.local_search_summary)
    streaming_summary_path = Path(args.streaming_summary)

    if not best_solution_path.exists():
        raise FileNotFoundError(f"Best solution CSV not found: {best_solution_path}")

    solution = pd.read_csv(best_solution_path)
    local_summary = json.loads(local_summary_path.read_text())
    streaming_summary = json.loads(streaming_summary_path.read_text())

    human_reward = float(streaming_summary["human_reward"])
    lambda_target = float(streaming_summary["lambda_target"])
    target_human_assignments = int(streaming_summary["target_human_assignments"])

    assignment_penalty_weight = float(streaming_summary["assignment_penalty"])
    overlap_penalty_weight = float(streaming_summary["resource_overlap_penalty"])
    precedence_penalty_weight = float(streaming_summary["precedence_penalty"])

    operation_rows = []

    for row in solution.to_dict("records"):
        op = int(row["operation"])
        r = int(row["resource"])
        t = int(row["start_time"])

        a_cost = assignment_cost(op, r)
        w_cost = workload_cost(op, r)
        e_cost = ergonomic_cost(op, r)
        s_cost = start_time_weight(op) * t
        total_without_reward = a_cost + w_cost + e_cost + s_cost

        operation_rows.append(
            {
                "operation": op,
                "job": int(row["job"]),
                "step": int(row["step"]),
                "resource": r,
                "resource_type": resource_type(r),
                "start_time": t,
                "duration": int(row["duration"]),
                "finish_time": int(row["finish_time"]),
                "assignment_cost": a_cost,
                "workload_cost": w_cost,
                "ergonomic_cost": e_cost,
                "start_time_cost": s_cost,
                "operation_cost_without_reward": total_without_reward,
                "is_human_assignment": 1 if r in HUMAN_RESOURCES else 0,
                "is_machine_assignment": 1 if r in MACHINE_RESOURCES else 0,
                "is_robot_assignment": 1 if r in ROBOT_RESOURCES else 0,
            }
        )

    op_df = pd.DataFrame(operation_rows)

    assignment_cost_total = float(op_df["assignment_cost"].sum())
    workload_total = float(op_df["workload_cost"].sum())
    ergonomic_total = float(op_df["ergonomic_cost"].sum())
    start_time_cost_total = float(op_df["start_time_cost"].sum())
    total_cost_without_reward = float(op_df["operation_cost_without_reward"].sum())

    human_count = int(op_df["is_human_assignment"].sum())
    machine_count = int(op_df["is_machine_assignment"].sum())
    robot_count = int(op_df["is_robot_assignment"].sum())

    reward_term = human_reward * human_count
    target_penalty = lambda_target * (human_count - target_human_assignments) ** 2

    assignment_violations = compute_assignment_violations(solution)
    overlap_violations = compute_overlap_violations(solution)
    precedence_violations = compute_precedence_violations(solution)

    assignment_penalty = assignment_penalty_weight * assignment_violations
    overlap_penalty = overlap_penalty_weight * overlap_violations
    precedence_penalty = precedence_penalty_weight * precedence_violations

    recomputed_objective = (
        total_cost_without_reward
        - reward_term
        + target_penalty
        + assignment_penalty
        + overlap_penalty
        + precedence_penalty
    )

    local_search_best_energy = float(local_summary["best_energy"])
    abs_error_vs_local_search_energy = abs(recomputed_objective - local_search_best_energy)

    feasible = (
        assignment_violations == 0
        and overlap_violations == 0
        and precedence_violations == 0
    )

    component_rows = [
        {"metric": "assignment_cost", "value": assignment_cost_total},
        {"metric": "workload_cost", "value": workload_total},
        {"metric": "ergonomic_cost", "value": ergonomic_total},
        {"metric": "start_time_cost", "value": start_time_cost_total},
        {"metric": "total_cost_without_reward", "value": total_cost_without_reward},
        {"metric": "human_reward", "value": human_reward},
        {"metric": "human_count", "value": human_count},
        {"metric": "machine_count", "value": machine_count},
        {"metric": "robot_count", "value": robot_count},
        {"metric": "reward_term", "value": reward_term},
        {"metric": "lambda_target", "value": lambda_target},
        {"metric": "target_human_assignments", "value": target_human_assignments},
        {"metric": "target_penalty", "value": target_penalty},
        {"metric": "assignment_violations", "value": assignment_violations},
        {"metric": "resource_overlap_violations", "value": overlap_violations},
        {"metric": "precedence_violations", "value": precedence_violations},
        {"metric": "assignment_penalty", "value": assignment_penalty},
        {"metric": "resource_overlap_penalty", "value": overlap_penalty},
        {"metric": "precedence_penalty", "value": precedence_penalty},
        {"metric": "recomputed_objective", "value": recomputed_objective},
        {"metric": "local_search_best_energy", "value": local_search_best_energy},
        {
            "metric": "abs_error_vs_local_search_energy",
            "value": abs_error_vs_local_search_energy,
        },
        {"metric": "feasible", "value": int(feasible)},
    ]

    component_df = pd.DataFrame(component_rows)

    # CP-SAT baseline values previously established for sample_4x4 baseline.
    # Important: the local QUBO representative objective includes human reward
    # and squared target penalty, so direct comparison should be interpreted
    # carefully.
    cpsat_baseline = {
        "total_cost_without_reward": 57.0,
        "human_count": 0,
        "workload_cost": 0.0,
        "ergonomic_cost": 0.0,
        "local_or_adjusted_objective": 57.0,
    }

    local_qubo = {
        "total_cost_without_reward": total_cost_without_reward,
        "human_count": human_count,
        "workload_cost": workload_total,
        "ergonomic_cost": ergonomic_total,
        "local_or_adjusted_objective": recomputed_objective,
    }

    comparison_rows = []

    for metric in cpsat_baseline:
        comparison_rows.append(
            {
                "metric": metric,
                "cpsat_baseline": cpsat_baseline[metric],
                "local_qubo_best": local_qubo[metric],
                "difference_local_minus_cpsat": local_qubo[metric]
                - cpsat_baseline[metric],
                "interpretation_note": (
                    "Objectives are not identical when local QUBO includes human reward and target penalty."
                    if metric == "local_or_adjusted_objective"
                    else ""
                ),
            }
        )

    comparison_df = pd.DataFrame(comparison_rows)

    component_out = Path(args.component_out)
    operation_out = Path(args.operation_out)
    comparison_out = Path(args.comparison_out)
    summary_out = Path(args.summary_out)

    component_out.parent.mkdir(parents=True, exist_ok=True)

    component_df.to_csv(component_out, index=False)
    op_df.to_csv(operation_out, index=False)
    comparison_df.to_csv(comparison_out, index=False)

    summary = {
        "experiment": "sample_4x4_local_qubo_solution_component_analysis",
        "best_solution_csv": str(best_solution_path),
        "component_summary_csv": str(component_out),
        "operation_components_csv": str(operation_out),
        "comparison_csv": str(comparison_out),
        "assignment_cost": assignment_cost_total,
        "workload_cost": workload_total,
        "ergonomic_cost": ergonomic_total,
        "start_time_cost": start_time_cost_total,
        "total_cost_without_reward": total_cost_without_reward,
        "human_count": human_count,
        "machine_count": machine_count,
        "robot_count": robot_count,
        "reward_term": reward_term,
        "target_penalty": target_penalty,
        "assignment_violations": assignment_violations,
        "resource_overlap_violations": overlap_violations,
        "precedence_violations": precedence_violations,
        "recomputed_objective": recomputed_objective,
        "local_search_best_energy": local_search_best_energy,
        "abs_error_vs_local_search_energy": abs_error_vs_local_search_energy,
        "feasible": feasible,
        "cpsat_baseline_reference": cpsat_baseline,
        "note": "Prototype comparison. CP-SAT baseline and QUBO local search objective variants should be interpreted carefully.",
    }

    summary_out.write_text(json.dumps(summary, indent=2))

    print("=== Local QUBO solution component analysis complete ===")
    print(f"assignment_cost = {assignment_cost_total}")
    print(f"workload_cost = {workload_total}")
    print(f"ergonomic_cost = {ergonomic_total}")
    print(f"start_time_cost = {start_time_cost_total}")
    print(f"total_cost_without_reward = {total_cost_without_reward}")
    print(f"human_count = {human_count}")
    print(f"machine_count = {machine_count}")
    print(f"robot_count = {robot_count}")
    print(f"reward_term = {reward_term}")
    print(f"target_penalty = {target_penalty}")
    print(f"recomputed_objective = {recomputed_objective}")
    print(f"local_search_best_energy = {local_search_best_energy}")
    print(f"abs_error_vs_local_search_energy = {abs_error_vs_local_search_energy}")
    print(f"feasible = {feasible}")
    print(f"saved component summary = {component_out}")
    print(f"saved operation components = {operation_out}")
    print(f"saved comparison = {comparison_out}")
    print(f"saved summary JSON = {summary_out}")


if __name__ == "__main__":
    main()
