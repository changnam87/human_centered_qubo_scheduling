"""CP-SAT baseline with squared-target objective equivalent to the representative sample_4x4 QUBO."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Dict, List, Tuple

from ortools.sat.python import cp_model

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

def operation_cost_without_reward(op: int, r: int, t: int) -> float:
    return assignment_cost(op, r) + workload_cost(op, r) + ergonomic_cost(op, r) + start_time_weight(op) * t

def build_valid_variables() -> List[Tuple[int, int, int]]:
    valid = []
    for op in range(NUM_OPERATIONS):
        for r in range(NUM_RESOURCES):
            latest_start = HORIZON - duration(op, r)
            for t in range(latest_start + 1):
                valid.append((op, r, t))
    return valid

def precedence_arcs() -> List[Tuple[int, int]]:
    arcs = []
    for job in range(NUM_JOBS):
        for step in range(OPS_PER_JOB - 1):
            pred = job * OPS_PER_JOB + step
            succ = job * OPS_PER_JOB + step + 1
            arcs.append((pred, succ))
    return arcs

def compute_components(rows, human_reward, lambda_target, target_human_assignments):
    assignment_total = 0.0
    workload_total = 0.0
    ergonomic_total = 0.0
    start_time_total = 0.0
    human_count = 0
    machine_count = 0
    robot_count = 0
    for row in rows:
        op = int(row["operation"])
        r = int(row["resource"])
        t = int(row["start_time"])
        assignment_total += assignment_cost(op, r)
        workload_total += workload_cost(op, r)
        ergonomic_total += ergonomic_cost(op, r)
        start_time_total += start_time_weight(op) * t
        if r in HUMAN_RESOURCES:
            human_count += 1
        elif r in ROBOT_RESOURCES:
            robot_count += 1
        else:
            machine_count += 1
    total_cost_without_reward = assignment_total + workload_total + ergonomic_total + start_time_total
    reward_term = human_reward * human_count
    target_penalty = lambda_target * (human_count - target_human_assignments) ** 2
    adjusted_objective = total_cost_without_reward - reward_term + target_penalty
    return {
        "assignment_cost": assignment_total,
        "workload_cost": workload_total,
        "ergonomic_cost": ergonomic_total,
        "start_time_cost": start_time_total,
        "total_cost_without_reward": total_cost_without_reward,
        "human_count": human_count,
        "machine_count": machine_count,
        "robot_count": robot_count,
        "reward_term": reward_term,
        "target_penalty": target_penalty,
        "adjusted_objective": adjusted_objective,
    }

def write_metric_csv(path: Path, values: Dict[str, float]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["metric", "value"])
        writer.writeheader()
        for key, value in values.items():
            writer.writerow({"metric": key, "value": value})

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--human-reward", type=float, default=2.5)
    parser.add_argument("--lambda-target", type=float, default=1.0)
    parser.add_argument("--target-human-assignments", type=int, default=4)
    parser.add_argument("--scale", type=int, default=100)
    parser.add_argument("--time-limit-seconds", type=float, default=60.0)
    parser.add_argument("--num-workers", type=int, default=8)
    parser.add_argument("--local-qubo-component-summary", type=str, default="results/tables/sample_4x4_local_qubo_solution_component_summary.json")
    parser.add_argument("--solution-out", type=str, default="results/tables/sample_4x4_cpsat_squared_target_solution.csv")
    parser.add_argument("--component-out", type=str, default="results/tables/sample_4x4_cpsat_squared_target_component_summary.csv")
    parser.add_argument("--comparison-out", type=str, default="results/tables/sample_4x4_cpsat_squared_target_vs_local_qubo_comparison.csv")
    parser.add_argument("--summary-out", type=str, default="results/tables/sample_4x4_cpsat_squared_target_summary.json")
    args = parser.parse_args()

    valid_variables = build_valid_variables()
    op_vars = {op: [] for op in range(NUM_OPERATIONS)}
    resource_vars = {r: [] for r in range(NUM_RESOURCES)}
    for key in valid_variables:
        op, r, t = key
        op_vars[op].append(key)
        resource_vars[r].append(key)

    model = cp_model.CpModel()
    x = {}
    for op, r, t in valid_variables:
        x[(op, r, t)] = model.NewBoolVar(f"x_o{op}_r{r}_t{t}")

    for op in range(NUM_OPERATIONS):
        model.Add(sum(x[key] for key in op_vars[op]) == 1)

    for r in range(NUM_RESOURCES):
        vars_for_resource = resource_vars[r]
        for a in range(len(vars_for_resource)):
            op1, r1, t1 = vars_for_resource[a]
            finish1 = t1 + duration(op1, r1)
            for b in range(a + 1, len(vars_for_resource)):
                op2, r2, t2 = vars_for_resource[b]
                if op1 == op2:
                    continue
                finish2 = t2 + duration(op2, r2)
                if t1 < finish2 and t2 < finish1:
                    model.Add(x[(op1, r1, t1)] + x[(op2, r2, t2)] <= 1)

    for pred, succ in precedence_arcs():
        for pred_key in op_vars[pred]:
            pred_op, pred_r, pred_t = pred_key
            pred_finish = pred_t + duration(pred_op, pred_r)
            for succ_key in op_vars[succ]:
                succ_op, succ_r, succ_t = succ_key
                if succ_t < pred_finish:
                    model.Add(x[pred_key] + x[succ_key] <= 1)

    scale = args.scale
    objective_terms = []
    for op, r, t in valid_variables:
        coeff = operation_cost_without_reward(op, r, t)
        if r in HUMAN_RESOURCES:
            coeff -= args.human_reward
        objective_terms.append(int(round(scale * coeff)) * x[(op, r, t)])

    human_vars = [x[(op, r, t)] for op, r, t in valid_variables if r in HUMAN_RESOURCES]
    human_count_var = model.NewIntVar(0, NUM_OPERATIONS, "human_count")
    model.Add(human_count_var == sum(human_vars))

    max_sq = max((h - args.target_human_assignments) ** 2 for h in range(NUM_OPERATIONS + 1))
    target_deviation_sq = model.NewIntVar(0, max_sq, "target_deviation_sq")
    table_rows = [(h, (h - args.target_human_assignments) ** 2) for h in range(NUM_OPERATIONS + 1)]
    model.AddAllowedAssignments([human_count_var, target_deviation_sq], table_rows)
    objective_terms.append(int(round(scale * args.lambda_target)) * target_deviation_sq)

    model.Minimize(sum(objective_terms))

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = args.time_limit_seconds
    solver.parameters.num_search_workers = args.num_workers
    status = solver.Solve(model)
    status_name = solver.StatusName(status)

    solution_rows = []
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        for op in range(NUM_OPERATIONS):
            for key in op_vars[op]:
                if solver.Value(x[key]) == 1:
                    op_selected, r, t = key
                    solution_rows.append({
                        "operation": op_selected,
                        "job": op_selected // OPS_PER_JOB,
                        "step": op_selected % OPS_PER_JOB,
                        "resource": r,
                        "resource_type": resource_type(r),
                        "start_time": t,
                        "duration": duration(op_selected, r),
                        "finish_time": t + duration(op_selected, r),
                    })
        solution_rows.sort(key=lambda row: (row["job"], row["step"]))

    components = compute_components(solution_rows, args.human_reward, args.lambda_target, args.target_human_assignments)
    objective_scaled = solver.ObjectiveValue()
    objective_unscaled = objective_scaled / scale
    components["solver_objective_scaled"] = objective_scaled
    components["solver_objective_unscaled"] = objective_unscaled
    components["abs_error_component_vs_solver"] = abs(components["adjusted_objective"] - objective_unscaled)

    solution_out = Path(args.solution_out)
    component_out = Path(args.component_out)
    comparison_out = Path(args.comparison_out)
    summary_out = Path(args.summary_out)
    solution_out.parent.mkdir(parents=True, exist_ok=True)

    with solution_out.open("w", newline="") as f:
        if solution_rows:
            writer = csv.DictWriter(f, fieldnames=list(solution_rows[0].keys()))
            writer.writeheader()
            writer.writerows(solution_rows)

    write_metric_csv(component_out, components)

    comparison_rows = []
    local_summary_path = Path(args.local_qubo_component_summary)
    if local_summary_path.exists():
        local_summary = json.loads(local_summary_path.read_text())
        local_adjusted = float(local_summary["recomputed_objective"])
        local_total = float(local_summary["total_cost_without_reward"])
        local_human = int(local_summary["human_count"])
        local_workload = float(local_summary["workload_cost"])
        local_ergonomic = float(local_summary["ergonomic_cost"])
        comparison_rows = [
            {"metric": "adjusted_objective", "cpsat_squared_target": components["adjusted_objective"], "local_qubo_best": local_adjusted, "local_minus_cpsat": local_adjusted - components["adjusted_objective"]},
            {"metric": "total_cost_without_reward", "cpsat_squared_target": components["total_cost_without_reward"], "local_qubo_best": local_total, "local_minus_cpsat": local_total - components["total_cost_without_reward"]},
            {"metric": "human_count", "cpsat_squared_target": components["human_count"], "local_qubo_best": local_human, "local_minus_cpsat": local_human - components["human_count"]},
            {"metric": "workload_cost", "cpsat_squared_target": components["workload_cost"], "local_qubo_best": local_workload, "local_minus_cpsat": local_workload - components["workload_cost"]},
            {"metric": "ergonomic_cost", "cpsat_squared_target": components["ergonomic_cost"], "local_qubo_best": local_ergonomic, "local_minus_cpsat": local_ergonomic - components["ergonomic_cost"]},
        ]
        with comparison_out.open("w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=list(comparison_rows[0].keys()))
            writer.writeheader()
            writer.writerows(comparison_rows)

    summary = {
        "experiment": "sample_4x4_cpsat_squared_target_baseline",
        "status": status_name,
        "objective_scaled": objective_scaled,
        "objective_unscaled_from_solver": objective_unscaled,
        "component_adjusted_objective": components["adjusted_objective"],
        "abs_error_component_vs_solver": components["abs_error_component_vs_solver"],
        "human_reward": args.human_reward,
        "lambda_target": args.lambda_target,
        "target_human_assignments": args.target_human_assignments,
        "scale": scale,
        "time_limit_seconds": args.time_limit_seconds,
        "num_workers": args.num_workers,
        "components": components,
        "solution_csv": str(solution_out),
        "component_csv": str(component_out),
        "comparison_csv": str(comparison_out),
        "note": "Objective-equivalent CP-SAT baseline for squared-target QUBO prototype.",
    }
    summary_out.write_text(json.dumps(summary, indent=2))

    print("=== CP-SAT squared-target baseline complete ===")
    print(f"status = {status_name}")
    print(f"solver_objective_unscaled = {objective_unscaled}")
    print(f"component_adjusted_objective = {components['adjusted_objective']}")
    print(f"human_count = {components['human_count']}")
    print(f"total_cost_without_reward = {components['total_cost_without_reward']}")
    print(f"reward_term = {components['reward_term']}")
    print(f"target_penalty = {components['target_penalty']}")
    print(f"machine_count = {components['machine_count']}")
    print(f"robot_count = {components['robot_count']}")
    print(f"saved solution = {solution_out}")
    print(f"saved components = {component_out}")
    print(f"saved comparison = {comparison_out}")
    print(f"saved summary = {summary_out}")

if __name__ == "__main__":
    main()
