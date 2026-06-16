"""Analyze best tuned local QUBO solution components against CP-SAT squared-target optimum."""

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
            if op_a == op_b or r_a != r_b:
                continue
            if start_a < finish_b and start_b < finish_a:
                violations += 1
    return violations

def compute_precedence_violations(solution: pd.DataFrame) -> int:
    by_op = {int(row["operation"]): row for row in solution.to_dict("records")}
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

def compute_components(solution: pd.DataFrame, human_reward: float, lambda_target: float, target_human_assignments: int) -> tuple[dict, pd.DataFrame]:
    operation_rows = []
    for row in solution.to_dict("records"):
        op = int(row["operation"])
        r = int(row["resource"])
        t = int(row["start_time"])
        a_cost = assignment_cost(op, r)
        w_cost = workload_cost(op, r)
        e_cost = ergonomic_cost(op, r)
        s_cost = start_time_weight(op) * t
        total = a_cost + w_cost + e_cost + s_cost
        operation_rows.append({
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
            "operation_cost_without_reward": total,
            "is_human_assignment": 1 if r in HUMAN_RESOURCES else 0,
            "is_machine_assignment": 1 if r in MACHINE_RESOURCES else 0,
            "is_robot_assignment": 1 if r in ROBOT_RESOURCES else 0,
        })
    op_df = pd.DataFrame(operation_rows)
    assignment_total = float(op_df["assignment_cost"].sum())
    workload_total = float(op_df["workload_cost"].sum())
    ergonomic_total = float(op_df["ergonomic_cost"].sum())
    start_time_total = float(op_df["start_time_cost"].sum())
    total_without_reward = float(op_df["operation_cost_without_reward"].sum())
    human_count = int(op_df["is_human_assignment"].sum())
    machine_count = int(op_df["is_machine_assignment"].sum())
    robot_count = int(op_df["is_robot_assignment"].sum())
    reward_term = human_reward * human_count
    target_penalty = lambda_target * (human_count - target_human_assignments) ** 2
    assignment_violations = compute_assignment_violations(solution)
    overlap_violations = compute_overlap_violations(solution)
    precedence_violations = compute_precedence_violations(solution)
    adjusted_objective = total_without_reward - reward_term + target_penalty
    components = {
        "assignment_cost": assignment_total,
        "workload_cost": workload_total,
        "ergonomic_cost": ergonomic_total,
        "start_time_cost": start_time_total,
        "total_cost_without_reward": total_without_reward,
        "human_count": human_count,
        "machine_count": machine_count,
        "robot_count": robot_count,
        "human_reward": human_reward,
        "reward_term": reward_term,
        "lambda_target": lambda_target,
        "target_human_assignments": target_human_assignments,
        "target_penalty": target_penalty,
        "assignment_violations": assignment_violations,
        "resource_overlap_violations": overlap_violations,
        "precedence_violations": precedence_violations,
        "adjusted_objective": adjusted_objective,
        "feasible": int(assignment_violations == 0 and overlap_violations == 0 and precedence_violations == 0),
    }
    return components, op_df

def write_metric_csv(path: Path, values: Dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["metric", "value"])
        writer.writeheader()
        for key, value in values.items():
            writer.writerow({"metric": key, "value": value})

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--best-json", type=str, default="results/tables/sample_4x4_local_search_parameter_sensitivity_best.json")
    parser.add_argument("--cpsat-summary", type=str, default="results/tables/sample_4x4_cpsat_squared_target_summary.json")
    parser.add_argument("--component-out", type=str, default="results/tables/sample_4x4_tuned_local_qubo_solution_component_summary.csv")
    parser.add_argument("--operation-out", type=str, default="results/tables/sample_4x4_tuned_local_qubo_solution_operation_components.csv")
    parser.add_argument("--comparison-out", type=str, default="results/tables/sample_4x4_tuned_local_qubo_vs_cpsat_squared_target_comparison.csv")
    parser.add_argument("--summary-out", type=str, default="results/tables/sample_4x4_tuned_local_qubo_solution_component_summary.json")
    args = parser.parse_args()

    best_json = json.loads(Path(args.best_json).read_text())
    best_case = best_json["best_case"]
    best_solution_path = Path(best_case["best_solution_csv"])
    local_summary_path = Path(best_case["summary_json"])
    cpsat_summary = json.loads(Path(args.cpsat_summary).read_text())
    local_summary = json.loads(local_summary_path.read_text())
    solution = pd.read_csv(best_solution_path)

    human_reward = float(cpsat_summary["human_reward"])
    lambda_target = float(cpsat_summary["lambda_target"])
    target_human_assignments = int(cpsat_summary["target_human_assignments"])
    cpsat_components = cpsat_summary["components"]

    local_components, op_df = compute_components(solution, human_reward, lambda_target, target_human_assignments)
    local_components["local_search_best_energy"] = float(local_summary["best_energy"])
    local_components["abs_error_vs_local_search_energy"] = abs(local_components["adjusted_objective"] - float(local_summary["best_energy"]))
    local_components["best_case_tag"] = best_case["tag"]
    local_components["best_case_run_id"] = int(best_case["run_id"])
    local_components["best_case_seed"] = int(best_case["seed"])
    local_components["best_case_restarts"] = int(best_case["restarts"])
    local_components["best_case_iterations"] = int(best_case["iterations"])
    local_components["best_case_initial_temperature"] = float(best_case["initial_temperature"])
    local_components["best_case_final_temperature"] = float(best_case["final_temperature"])

    comparison_metrics = [
        "adjusted_objective",
        "total_cost_without_reward",
        "assignment_cost",
        "workload_cost",
        "ergonomic_cost",
        "start_time_cost",
        "human_count",
        "machine_count",
        "robot_count",
        "reward_term",
        "target_penalty",
    ]
    comparison_rows = []
    for metric in comparison_metrics:
        cpsat_value = float(cpsat_components[metric])
        local_value = float(local_components[metric])
        comparison_rows.append({
            "metric": metric,
            "cpsat_squared_target": cpsat_value,
            "tuned_local_qubo": local_value,
            "local_minus_cpsat": local_value - cpsat_value,
        })

    component_out = Path(args.component_out)
    operation_out = Path(args.operation_out)
    comparison_out = Path(args.comparison_out)
    summary_out = Path(args.summary_out)
    component_out.parent.mkdir(parents=True, exist_ok=True)
    write_metric_csv(component_out, local_components)
    op_df.to_csv(operation_out, index=False)
    pd.DataFrame(comparison_rows).to_csv(comparison_out, index=False)

    summary = {
        "experiment": "sample_4x4_tuned_local_qubo_solution_component_analysis",
        "best_case": best_case,
        "best_solution_csv": str(best_solution_path),
        "local_components": local_components,
        "cpsat_components": cpsat_components,
        "absolute_gap_to_cpsat": local_components["adjusted_objective"] - float(cpsat_components["adjusted_objective"]),
        "relative_gap_to_cpsat": (local_components["adjusted_objective"] - float(cpsat_components["adjusted_objective"])) / float(cpsat_components["adjusted_objective"]),
        "component_summary_csv": str(component_out),
        "operation_components_csv": str(operation_out),
        "comparison_csv": str(comparison_out),
        "note": "Best tuned local QUBO solution component analysis; heuristic, not proof of optimality.",
    }
    summary_out.write_text(json.dumps(summary, indent=2))

    print("=== Tuned local QUBO solution component analysis complete ===")
    print(f"best_case = {best_case['tag']}")
    print(f"adjusted_objective = {local_components['adjusted_objective']}")
    print(f"cpsat_adjusted_objective = {cpsat_components['adjusted_objective']}")
    print(f"absolute_gap = {summary['absolute_gap_to_cpsat']}")
    print(f"relative_gap = {summary['relative_gap_to_cpsat']}")
    print(f"human_count = {local_components['human_count']}")
    print(f"feasible = {local_components['feasible']}")
    print(f"saved component summary = {component_out}")
    print(f"saved comparison = {comparison_out}")
    print(f"saved summary = {summary_out}")

if __name__ == "__main__":
    main()
