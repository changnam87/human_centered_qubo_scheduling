"""
Batch CP-SAT pilot for sample_4x4 soft human-reward sensitivity.

Purpose
-------
This script extends the current single-instance sample_4x4 soft human-reward
sensitivity into a multi-seed pilot robustness check.

It generates synthetic augmented sample_4x4 instances for seeds 2001-2010,
runs CP-SAT for human_reward = 0, 1, 2, 3, 4, 5, and saves a result table.

Important
---------
This remains a prototype / pilot-validation experiment.
It is not intended to support final paper-level claims yet.

Core validation idea
--------------------
For each seed and reward value:

    reward_adjusted_objective
        = total_cost_without_reward
          - human_reward * human_assignment_count

The main quantity of interest is threshold behavior:
At what reward value does the solver first choose 1, 2, or 3 human assignments?
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


# -----------------------------
# Problem constants
# -----------------------------

NUM_JOBS = 4
NUM_OPS_PER_JOB = 4
NUM_OPERATIONS = NUM_JOBS * NUM_OPS_PER_JOB

NUM_MACHINES = 4
NUM_WORKERS = 3
NUM_ROBOTS = 2
NUM_RESOURCES = NUM_MACHINES + NUM_WORKERS + NUM_ROBOTS

HORIZON = 63

# Resource indexing:
# 0-3: machines
# 4-6: human workers
# 7-8: robots
MACHINE_RESOURCES = list(range(0, 4))
HUMAN_RESOURCES = list(range(4, 7))
ROBOT_RESOURCES = list(range(7, 9))

REWARD_VALUES = [0, 1, 2, 3, 4, 5]


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

    Design intent:
    - Machines/robots are usually cheaper than humans under reward = 0.
    - Humans activate workload and ergonomic terms.
    - A positive human_reward can eventually make human assignment attractive.
    - The seed perturbs durations and costs enough to test robustness.
    """

    rng = random.Random(seed)
    operations = build_operations()

    duration: Dict[Tuple[int, int], int] = {}
    base_assignment_cost: Dict[Tuple[int, int], float] = {}
    workload_cost: Dict[Tuple[int, int], float] = {}
    ergonomic_cost: Dict[Tuple[int, int], float] = {}
    start_time_weight: Dict[int, float] = {}

    for op in operations:
        # Small start-time weight creates scheduling pressure but avoids dominating
        # the human reward effect.
        start_time_weight[op.op_id] = rng.choice([0.00, 0.05, 0.10, 0.15])

        for r in range(NUM_RESOURCES):
            rt = resource_type(r)

            # Base duration depends on job, step, resource type, and seed.
            base_duration = 2 + ((op.job_id + op.step_id) % 3)
            jitter = rng.choice([0, 0, 1])

            if rt == "machine":
                dur = base_duration + jitter
            elif rt == "robot":
                dur = base_duration + rng.choice([0, 1, 1])
            else:
                # Humans can be slightly slower or comparable.
                dur = base_duration + rng.choice([0, 1, 2])

            duration[(op.op_id, r)] = max(1, dur)

            # Base assignment cost:
            # Machines/robots are attractive at reward = 0.
            if rt == "machine":
                cost = 2.0 + 0.3 * op.step_id + rng.choice([0.0, 0.2, 0.4])
                workload = 0.0
                ergonomic = 0.0
            elif rt == "robot":
                cost = 2.5 + 0.4 * op.step_id + rng.choice([0.0, 0.2, 0.5])
                workload = 0.0
                ergonomic = 0.0
            else:
                # Humans carry explicit workload and ergonomic terms.
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


def solve_soft_reward_instance(
    instance: Instance,
    human_reward: int,
    time_limit_seconds: float,
    num_workers: int,
) -> Dict[str, object]:
    """
    Solve one CP-SAT time-indexed scheduling instance.

    Decision variable:
        x[o, r, t] = 1 if operation o starts on resource r at time t.

    Variable count:
        16 operations * 9 resources * 63 time points = 9072 binary variables.
    """

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

    # Each operation must be assigned exactly once.
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

    # Start-time expression for each operation.
    start_expr = {}
    for op in instance.operations:
        start_expr[op.op_id] = sum(
            t * x[(op.op_id, r, t)]
            for r in range(NUM_RESOURCES)
            for t in range(HORIZON)
            if (op.op_id, r, t) in x
        )

    # Precedence constraints within each job:
    # operation k+1 cannot start before operation k finishes.
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

    # No-overlap constraints per resource and time point.
    # For every resource r and time tau, at most one active operation.
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

    # Objective components.
    # Scale by 100 to keep CP-SAT objective integral.
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

    reward_scaled = int(round(SCALE * human_reward)) * sum(human_assignment_terms)

    objective_scaled = total_without_reward_scaled - reward_scaled

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
    else:
        selected = []

    def selected_sum(component: Dict[Tuple[int, int], float]) -> float:
        return sum(component[(op_id, r)] for op_id, _, _, r, _ in selected)

    start_time_cost = sum(
        instance.start_time_weight[op_id] * t
        for op_id, _, _, _, t in selected
    )

    assignment_cost = selected_sum(instance.base_assignment_cost)
    workload = selected_sum(instance.workload_cost)
    ergonomic = selected_sum(instance.ergonomic_cost)

    human_assignments = sum(1 for op_id, j, k, r, t in selected if r in HUMAN_RESOURCES)

    total_cost_without_reward = (
        start_time_cost + assignment_cost + workload + ergonomic
    )

    reward_adjusted_objective = (
        total_cost_without_reward - human_reward * human_assignments
    )

    # CP-SAT objective value is scaled. Compare for diagnostic only.
    solver_objective = None
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        solver_objective = solver.ObjectiveValue() / SCALE

    return {
        "seed": instance.seed,
        "human_reward": human_reward,
        "status": status_name,
        "objective_cp_sat": solver_objective,
        "reward_adjusted_objective": reward_adjusted_objective,
        "total_cost_without_reward": total_cost_without_reward,
        "start_time_cost": start_time_cost,
        "assignment_cost": assignment_cost,
        "workload": workload,
        "ergonomic": ergonomic,
        "human_assignments": human_assignments,
        "machine_assignments": sum(1 for _, _, _, r, _ in selected if r in MACHINE_RESOURCES),
        "robot_assignments": sum(1 for _, _, _, r, _ in selected if r in ROBOT_RESOURCES),
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


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed-start", type=int, default=2001)
    parser.add_argument("--seed-end", type=int, default=2010)
    parser.add_argument("--time-limit", type=float, default=30.0)
    parser.add_argument("--num-workers", type=int, default=8)
    parser.add_argument(
        "--out",
        type=str,
        default="results/tables/sample_4x4_soft_human_reward_batch_sensitivity.csv",
    )
    parser.add_argument(
        "--meta-out",
        type=str,
        default="results/tables/sample_4x4_soft_human_reward_batch_metadata.json",
    )

    args = parser.parse_args()

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    rows: List[Dict[str, object]] = []

    seeds = list(range(args.seed_start, args.seed_end + 1))

    print("=== sample_4x4 soft human-reward batch pilot ===")
    print(f"Seeds: {seeds}")
    print(f"Rewards: {REWARD_VALUES}")
    print(f"Time limit per solve: {args.time_limit} seconds")
    print(f"Output: {out_path}")

    for seed in seeds:
        instance = generate_sample_4x4_augmented_instance(seed)
        print(f"\n--- Seed {seed} ---")

        for reward in REWARD_VALUES:
            result = solve_soft_reward_instance(
                instance=instance,
                human_reward=reward,
                time_limit_seconds=args.time_limit,
                num_workers=args.num_workers,
            )
            rows.append(result)

            print(
                "reward={reward:>2} | status={status:<8} | humans={humans:>2} | "
                "cost_wo_reward={cost:>7.2f} | reward_obj={obj:>7.2f} | "
                "time={sec:>5.2f}s".format(
                    reward=reward,
                    status=result["status"],
                    humans=result["human_assignments"],
                    cost=result["total_cost_without_reward"],
                    obj=result["reward_adjusted_objective"],
                    sec=result["wall_seconds"],
                )
            )

    fieldnames = list(rows[0].keys())

    with out_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    meta = {
        "experiment": "sample_4x4_soft_human_reward_batch_sensitivity",
        "seed_start": args.seed_start,
        "seed_end": args.seed_end,
        "seeds": seeds,
        "reward_values": REWARD_VALUES,
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
        "note": "Prototype/pilot robustness check; not final paper-level evidence.",
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
