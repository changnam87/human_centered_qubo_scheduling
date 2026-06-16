"""
Batch pilot: target-based human utilization penalty for sample_4x4.

Purpose
-------
The previous overuse-penalty pilot penalized only excessive human assignment:

    max(0, human_count - target)

This script tests a target-deviation penalty that penalizes both under-use and
over-use of human resources:

    |human_count - target|

Objective
---------
    objective
        = total_cost_without_reward
          - human_reward * human_assignment_count
          + target_deviation_penalty * |human_assignment_count - target_human_assignments|

This remains a prototype / pilot validation experiment.
It should not be framed as final paper-level empirical evidence.
"""

from __future__ import annotations

import argparse
import csv
import json
import random
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple

from ortools.sat.python import cp_model


NUM_JOBS = 4
NUM_OPS_PER_JOB = 4
NUM_OPERATIONS = NUM_JOBS * NUM_OPS_PER_JOB

NUM_MACHINES = 4
NUM_WORKERS = 3
NUM_ROBOTS = 2
NUM_RESOURCES = NUM_MACHINES + NUM_WORKERS + NUM_ROBOTS

HORIZON = 63

MACHINE_RESOURCES = list(range(0, 4))
HUMAN_RESOURCES = list(range(4, 7))
ROBOT_RESOURCES = list(range(7, 9))

DEFAULT_HUMAN_REWARDS = [0.0, 1.0, 2.0, 2.5, 3.0]
DEFAULT_TARGET_DEVIATION_PENALTIES = [0.0, 0.5, 1.0, 2.0, 3.0, 4.0]


@dataclass
class Operation:
    op_id: int
    job_id: int
    step_id: int


@dataclass
class Instance:
    seed: int
    operations: List[Operation]
    duration: Dict[Tuple[int, int], int]
    base_assignment_cost: Dict[Tuple[int, int], float]
    workload_cost: Dict[Tuple[int, int], float]
    ergonomic_cost: Dict[Tuple[int, int], float]
    start_time_weight: Dict[int, float]


def resource_type(resource_id: int) -> str:
    if resource_id in HUMAN_RESOURCES:
        return "human"
    if resource_id in ROBOT_RESOURCES:
        return "robot"
    return "machine"


def build_operations() -> List[Operation]:
    operations = []
    op_id = 0

    for j in range(NUM_JOBS):
        for k in range(NUM_OPS_PER_JOB):
            operations.append(Operation(op_id=op_id, job_id=j, step_id=k))
            op_id += 1

    return operations


def generate_sample_4x4_augmented_instance(seed: int) -> Instance:
    """
    Generate one deterministic synthetic augmented sample_4x4 instance.

    This generator matches the previous fine-grid and overuse-penalty pilots so
    that results are directly comparable.
    """

    rng = random.Random(seed)
    operations = build_operations()

    duration: Dict[Tuple[int, int], int] = {}
    base_assignment_cost: Dict[Tuple[int, int], float] = {}
    workload_cost: Dict[Tuple[int, int], float] = {}
    ergonomic_cost: Dict[Tuple[int, int], float] = {}
    start_time_weight: Dict[int, float] = {}

    for op in operations:
        start_time_weight[op.op_id] = rng.choice([0.00, 0.05, 0.10, 0.15])

        for r in range(NUM_RESOURCES):
            rt = resource_type(r)

            base_duration = 2 + ((op.job_id + op.step_id) % 3)
            jitter = rng.choice([0, 0, 1])

            if rt == "machine":
                dur = base_duration + jitter
            elif rt == "robot":
                dur = base_duration + rng.choice([0, 1, 1])
            else:
                dur = base_duration + rng.choice([0, 1, 2])

            duration[(op.op_id, r)] = max(1, dur)

            if rt == "machine":
                cost = 2.0 + 0.3 * op.step_id + rng.choice([0.0, 0.2, 0.4])
                workload = 0.0
                ergonomic = 0.0
            elif rt == "robot":
                cost = 2.5 + 0.4 * op.step_id + rng.choice([0.0, 0.2, 0.5])
                workload = 0.0
                ergonomic = 0.0
            else:
                cost = 2.5 + 0.2 * op.step_id + rng.choice([0.0, 0.3, 0.6])
                workload = rng.choice([1.0, 1.5, 2.0, 2.5])
                ergonomic = rng.choice([0.6, 0.9, 1.2, 1.5])

            base_assignment_cost[(op.op_id, r)] = cost
            workload_cost[(op.op_id, r)] = workload
            ergonomic_cost[(op.op_id, r)] = ergonomic

    return Instance(
        seed=seed,
        operations=operations,
        duration=duration,
        base_assignment_cost=base_assignment_cost,
        workload_cost=workload_cost,
        ergonomic_cost=ergonomic_cost,
        start_time_weight=start_time_weight,
    )


def solve_instance(
    instance: Instance,
    human_reward: float,
    target_deviation_penalty: float,
    target_human_assignments: int,
    time_limit_seconds: float,
    num_workers: int,
) -> Dict[str, object]:

    model = cp_model.CpModel()

    x: Dict[Tuple[int, int, int], cp_model.IntVar] = {}

    for op in instance.operations:
        for r in range(NUM_RESOURCES):
            dur = instance.duration[(op.op_id, r)]
            latest_start = HORIZON - dur

            for t in range(latest_start + 1):
                x[(op.op_id, r, t)] = model.NewBoolVar(
                    f"x_o{op.op_id}_r{r}_t{t}"
                )

    # Each operation starts exactly once.
    for op in instance.operations:
        model.Add(
            sum(
                x[(op.op_id, r, t)]
                for r in range(NUM_RESOURCES)
                for t in range(HORIZON)
                if (op.op_id, r, t) in x
            )
            == 1
        )

    # Start-time expression.
    start_expr = {}

    for op in instance.operations:
        start_expr[op.op_id] = sum(
            t * x[(op.op_id, r, t)]
            for r in range(NUM_RESOURCES)
            for t in range(HORIZON)
            if (op.op_id, r, t) in x
        )

    # Job precedence constraints.
    for j in range(NUM_JOBS):
        for k in range(NUM_OPS_PER_JOB - 1):
            pred_op = j * NUM_OPS_PER_JOB + k
            succ_op = j * NUM_OPS_PER_JOB + k + 1

            pred_duration_expr = sum(
                instance.duration[(pred_op, r)] * x[(pred_op, r, t)]
                for r in range(NUM_RESOURCES)
                for t in range(HORIZON)
                if (pred_op, r, t) in x
            )

            model.Add(start_expr[succ_op] >= start_expr[pred_op] + pred_duration_expr)

    # Resource capacity constraints.
    for r in range(NUM_RESOURCES):
        for tau in range(HORIZON):
            active_terms = []

            for op in instance.operations:
                dur = instance.duration[(op.op_id, r)]

                for t in range(max(0, tau - dur + 1), tau + 1):
                    if (op.op_id, r, t) in x and t <= tau < t + dur:
                        active_terms.append(x[(op.op_id, r, t)])

            if active_terms:
                model.Add(sum(active_terms) <= 1)

    SCALE = 100

    start_time_cost_terms = []
    assignment_cost_terms = []
    workload_cost_terms = []
    ergonomic_cost_terms = []
    human_assignment_terms = []

    for op in instance.operations:
        for r in range(NUM_RESOURCES):
            for t in range(HORIZON):
                key = (op.op_id, r, t)

                if key not in x:
                    continue

                var = x[key]

                start_time_cost_terms.append(
                    int(round(SCALE * instance.start_time_weight[op.op_id] * t)) * var
                )

                assignment_cost_terms.append(
                    int(round(SCALE * instance.base_assignment_cost[(op.op_id, r)]))
                    * var
                )

                workload_cost_terms.append(
                    int(round(SCALE * instance.workload_cost[(op.op_id, r)])) * var
                )

                ergonomic_cost_terms.append(
                    int(round(SCALE * instance.ergonomic_cost[(op.op_id, r)])) * var
                )

                if r in HUMAN_RESOURCES:
                    human_assignment_terms.append(var)

    total_without_reward_scaled = (
        sum(start_time_cost_terms)
        + sum(assignment_cost_terms)
        + sum(workload_cost_terms)
        + sum(ergonomic_cost_terms)
    )

    human_count = model.NewIntVar(0, NUM_OPERATIONS, "human_assignment_count")
    model.Add(human_count == sum(human_assignment_terms))

    diff_from_target = model.NewIntVar(
        -target_human_assignments,
        NUM_OPERATIONS - target_human_assignments,
        "diff_from_target",
    )
    model.Add(diff_from_target == human_count - target_human_assignments)

    target_deviation = model.NewIntVar(0, NUM_OPERATIONS, "target_deviation")
    model.AddAbsEquality(target_deviation, diff_from_target)

    reward_scaled = int(round(SCALE * human_reward))
    target_deviation_penalty_scaled = int(round(SCALE * target_deviation_penalty))

    objective_scaled = (
        total_without_reward_scaled
        - reward_scaled * human_count
        + target_deviation_penalty_scaled * target_deviation
    )

    model.Minimize(objective_scaled)

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = time_limit_seconds
    solver.parameters.num_search_workers = num_workers
    solver.parameters.random_seed = instance.seed

    wall_start = time.time()
    status = solver.Solve(model)
    wall_seconds = time.time() - wall_start

    status_name = solver.StatusName(status)

    selected = []

    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        for op in instance.operations:
            for r in range(NUM_RESOURCES):
                for t in range(HORIZON):
                    key = (op.op_id, r, t)

                    if key in x and solver.Value(x[key]) == 1:
                        selected.append((op.op_id, op.job_id, op.step_id, r, t))

    def selected_sum(component: Dict[Tuple[int, int], float]) -> float:
        return sum(component[(op_id, r)] for op_id, _, _, r, _ in selected)

    start_time_cost = sum(
        instance.start_time_weight[op_id] * t
        for op_id, _, _, _, t in selected
    )

    assignment_cost = selected_sum(instance.base_assignment_cost)
    workload = selected_sum(instance.workload_cost)
    ergonomic = selected_sum(instance.ergonomic_cost)

    human_assignments = sum(
        1 for _, _, _, r, _ in selected if r in HUMAN_RESOURCES
    )

    machine_assignments = sum(
        1 for _, _, _, r, _ in selected if r in MACHINE_RESOURCES
    )

    robot_assignments = sum(
        1 for _, _, _, r, _ in selected if r in ROBOT_RESOURCES
    )

    distance_from_target = abs(human_assignments - target_human_assignments)

    total_cost_without_reward = (
        start_time_cost + assignment_cost + workload + ergonomic
    )

    reward_term = human_reward * human_assignments
    target_deviation_penalty_term = target_deviation_penalty * distance_from_target

    adjusted_objective_manual = (
        total_cost_without_reward
        - reward_term
        + target_deviation_penalty_term
    )

    solver_objective = None

    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        solver_objective = solver.ObjectiveValue() / SCALE

    return {
        "seed": instance.seed,
        "human_reward": human_reward,
        "target_deviation_penalty": target_deviation_penalty,
        "target_human_assignments": target_human_assignments,
        "status": status_name,
        "objective_cp_sat": solver_objective,
        "adjusted_objective_manual": adjusted_objective_manual,
        "total_cost_without_reward": total_cost_without_reward,
        "reward_term": reward_term,
        "target_deviation_penalty_term": target_deviation_penalty_term,
        "start_time_cost": start_time_cost,
        "assignment_cost": assignment_cost,
        "workload": workload,
        "ergonomic": ergonomic,
        "human_assignments": human_assignments,
        "distance_from_target": distance_from_target,
        "machine_assignments": machine_assignments,
        "robot_assignments": robot_assignments,
        "num_selected_operations": len(selected),
        "wall_seconds": wall_seconds,
        "num_binary_variables": NUM_OPERATIONS * NUM_RESOURCES * HORIZON,
        "jobs": NUM_JOBS,
        "machines": NUM_MACHINES,
        "operations": NUM_OPERATIONS,
        "workers": NUM_WORKERS,
        "robots": NUM_ROBOTS,
        "resources": NUM_RESOURCES,
        "planning_horizon": HORIZON,
    }


def parse_float_list(value: str) -> List[float]:
    return [float(v.strip()) for v in value.split(",") if v.strip()]


def main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument("--seed-start", type=int, default=2001)
    parser.add_argument("--seed-end", type=int, default=2010)
    parser.add_argument("--time-limit", type=float, default=30.0)
    parser.add_argument("--num-workers", type=int, default=8)
    parser.add_argument("--target-human-assignments", type=int, default=4)

    parser.add_argument(
        "--human-rewards",
        type=str,
        default="0.0,1.0,2.0,2.5,3.0",
    )

    parser.add_argument(
        "--target-deviation-penalties",
        type=str,
        default="0.0,0.5,1.0,2.0,3.0,4.0",
    )

    parser.add_argument(
        "--out",
        type=str,
        default="results/tables/sample_4x4_target_deviation_penalty_batch.csv",
    )

    parser.add_argument(
        "--meta-out",
        type=str,
        default="results/tables/sample_4x4_target_deviation_penalty_batch_metadata.json",
    )

    args = parser.parse_args()

    seeds = list(range(args.seed_start, args.seed_end + 1))
    human_rewards = parse_float_list(args.human_rewards)
    target_deviation_penalties = parse_float_list(args.target_deviation_penalties)

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    rows: List[Dict[str, object]] = []

    print("=== sample_4x4 target-deviation penalty batch pilot ===")
    print(f"Seeds: {seeds}")
    print(f"Human rewards: {human_rewards}")
    print(f"Target deviation penalties: {target_deviation_penalties}")
    print(f"Target human assignments: {args.target_human_assignments}")
    print(f"Time limit per solve: {args.time_limit} seconds")
    print(f"Output: {out_path}")

    for seed in seeds:
        instance = generate_sample_4x4_augmented_instance(seed)
        print(f"\n--- Seed {seed} ---")

        for human_reward in human_rewards:
            for target_deviation_penalty in target_deviation_penalties:
                result = solve_instance(
                    instance=instance,
                    human_reward=human_reward,
                    target_deviation_penalty=target_deviation_penalty,
                    target_human_assignments=args.target_human_assignments,
                    time_limit_seconds=args.time_limit,
                    num_workers=args.num_workers,
                )

                rows.append(result)

                print(
                    "reward={reward:>3.1f} | dev_penalty={penalty:>3.1f} | "
                    "status={status:<8} | humans={humans:>2} | "
                    "dist={dist:>2} | adj_obj={obj:>7.2f} | time={sec:>5.2f}s".format(
                        reward=human_reward,
                        penalty=target_deviation_penalty,
                        status=result["status"],
                        humans=result["human_assignments"],
                        dist=result["distance_from_target"],
                        obj=result["adjusted_objective_manual"],
                        sec=result["wall_seconds"],
                    )
                )

    fieldnames = list(rows[0].keys())

    with out_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    meta = {
        "experiment": "sample_4x4_target_deviation_penalty_batch",
        "seed_start": args.seed_start,
        "seed_end": args.seed_end,
        "seeds": seeds,
        "human_rewards": human_rewards,
        "target_deviation_penalties": target_deviation_penalties,
        "target_human_assignments": args.target_human_assignments,
        "time_limit_seconds": args.time_limit,
        "num_workers": args.num_workers,
        "jobs": NUM_JOBS,
        "machines": NUM_MACHINES,
        "operations": NUM_OPERATIONS,
        "workers": NUM_WORKERS,
        "robots": NUM_ROBOTS,
        "resources": NUM_RESOURCES,
        "planning_horizon": HORIZON,
        "binary_variables": NUM_OPERATIONS * NUM_RESOURCES * HORIZON,
        "output_csv": str(out_path),
        "note": "Prototype/pilot target-deviation penalty test; not final paper-level evidence.",
    }

    meta_path = Path(args.meta_out)
    meta_path.parent.mkdir(parents=True, exist_ok=True)

    with meta_path.open("w") as f:
        json.dump(meta, f, indent=2)

    print("\n=== DONE ===")
    print(f"Saved result table: {out_path}")
    print(f"Saved metadata: {meta_path}")


if __name__ == "__main__":
    main()
