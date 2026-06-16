"""
Small time-indexed QUBO parameter sensitivity.

Purpose
-------
This script runs brute-force QUBO optimization for a small time-indexed
scheduling QUBO under multiple parameter settings.

It varies:
1. human_reward
2. lambda_target for squared target human-utilization penalty
3. constraint_penalty used for assignment, resource overlap, and precedence

Main questions
--------------
- Does human_reward increase human assignment?
- Does lambda_target pull human_count toward the target?
- Are constraint penalties large enough to prevent infeasible optima?
- What parameter settings yield feasible, target-consistent schedules?

This is still a small prototype validation, not a final paper-level experiment.
"""

from __future__ import annotations

import argparse
import csv
import itertools
import json
from pathlib import Path
from typing import Dict, Tuple, List


# -----------------------------
# Small time-indexed problem
# -----------------------------

NUM_OPERATIONS = 2
NUM_RESOURCES = 2
HORIZON = 4

MACHINE = 0
HUMAN = 1
HUMAN_RESOURCES = [HUMAN]

PRECEDENCE_ARCS = [(0, 1)]

duration = {
    (0, MACHINE): 1,
    (0, HUMAN): 2,
    (1, MACHINE): 1,
    (1, HUMAN): 1,
}

assignment_cost = {
    (0, MACHINE): 2.0,
    (0, HUMAN): 3.0,
    (1, MACHINE): 2.5,
    (1, HUMAN): 3.2,
}

workload_cost = {
    (0, MACHINE): 0.0,
    (0, HUMAN): 1.0,
    (1, MACHINE): 0.0,
    (1, HUMAN): 1.2,
}

ergonomic_cost = {
    (0, MACHINE): 0.0,
    (0, HUMAN): 0.6,
    (1, MACHINE): 0.0,
    (1, HUMAN): 0.7,
}

start_time_weight = {
    0: 0.2,
    1: 0.2,
}

TARGET_HUMAN_ASSIGNMENTS = 1


# -----------------------------
# Variable indexing
# -----------------------------

valid_variables: List[Tuple[int, int, int]] = []

for o in range(NUM_OPERATIONS):
    for r in range(NUM_RESOURCES):
        latest_start = HORIZON - duration[(o, r)]
        for t in range(latest_start + 1):
            valid_variables.append((o, r, t))

VAR_TO_INDEX = {key: idx for idx, key in enumerate(valid_variables)}
INDEX_TO_VAR = {idx: key for key, idx in VAR_TO_INDEX.items()}
NUM_VARIABLES = len(valid_variables)


def var_name(idx: int) -> str:
    o, r, t = INDEX_TO_VAR[idx]
    r_label = "human" if r == HUMAN else "machine"
    return f"x_o{o}_r{r}_{r_label}_t{t}"


# -----------------------------
# QUBO helpers
# -----------------------------

QuboKey = Tuple[int, int]
QuboDict = Dict[QuboKey, float]


def add_linear(Q: QuboDict, i: int, coeff: float) -> None:
    Q[(i, i)] = Q.get((i, i), 0.0) + coeff


def add_quadratic(Q: QuboDict, i: int, j: int, coeff: float) -> None:
    if i == j:
        add_linear(Q, i, coeff)
        return

    a, b = sorted((i, j))
    Q[(a, b)] = Q.get((a, b), 0.0) + coeff


def build_qubo(
    human_reward: float,
    lambda_target: float,
    constraint_penalty: float,
) -> Tuple[QuboDict, float]:
    """
    Build QUBO:

        E(x) = constant + sum_i Q[i,i] x_i + sum_{i<j} Q[i,j] x_i x_j
    """

    Q: QuboDict = {}
    constant = 0.0

    # Base cost.
    for idx, (o, r, t) in INDEX_TO_VAR.items():
        coeff = (
            assignment_cost[(o, r)]
            + workload_cost[(o, r)]
            + ergonomic_cost[(o, r)]
            + start_time_weight[o] * t
        )
        add_linear(Q, idx, coeff)

    # Soft human reward.
    human_vars = []

    for idx, (o, r, t) in INDEX_TO_VAR.items():
        if r in HUMAN_RESOURCES:
            add_linear(Q, idx, -human_reward)
            human_vars.append(idx)

    # Squared target penalty.
    constant += lambda_target * TARGET_HUMAN_ASSIGNMENTS**2

    human_linear_coeff = lambda_target * (1 - 2 * TARGET_HUMAN_ASSIGNMENTS)

    for i in human_vars:
        add_linear(Q, i, human_linear_coeff)

    for a in range(len(human_vars)):
        for b in range(a + 1, len(human_vars)):
            add_quadratic(Q, human_vars[a], human_vars[b], 2.0 * lambda_target)

    # One-start assignment penalty.
    for o in range(NUM_OPERATIONS):
        op_vars = [
            idx
            for idx, (oo, r, t) in INDEX_TO_VAR.items()
            if oo == o
        ]

        constant += constraint_penalty

        for i in op_vars:
            add_linear(Q, i, -constraint_penalty)

        for a in range(len(op_vars)):
            for b in range(a + 1, len(op_vars)):
                add_quadratic(Q, op_vars[a], op_vars[b], 2.0 * constraint_penalty)

    # Resource overlap penalty.
    for i in range(NUM_VARIABLES):
        o1, r1, t1 = INDEX_TO_VAR[i]
        d1 = duration[(o1, r1)]
        interval1 = set(range(t1, t1 + d1))

        for j in range(i + 1, NUM_VARIABLES):
            o2, r2, t2 = INDEX_TO_VAR[j]

            if o1 == o2:
                continue

            if r1 != r2:
                continue

            d2 = duration[(o2, r2)]
            interval2 = set(range(t2, t2 + d2))

            if interval1.intersection(interval2):
                add_quadratic(Q, i, j, constraint_penalty)

    # Precedence penalty.
    for pred, succ in PRECEDENCE_ARCS:
        pred_vars = [
            idx
            for idx, (o, r, t) in INDEX_TO_VAR.items()
            if o == pred
        ]
        succ_vars = [
            idx
            for idx, (o, r, t) in INDEX_TO_VAR.items()
            if o == succ
        ]

        for i in pred_vars:
            pred_o, pred_r, pred_t = INDEX_TO_VAR[i]
            pred_finish = pred_t + duration[(pred_o, pred_r)]

            for j in succ_vars:
                succ_o, succ_r, succ_t = INDEX_TO_VAR[j]

                if succ_t < pred_finish:
                    add_quadratic(Q, i, j, constraint_penalty)

    Q = {key: value for key, value in Q.items() if abs(value) > 1e-12}

    return Q, constant


def qubo_energy(bits: Tuple[int, ...], Q: QuboDict, constant: float) -> float:
    energy = constant

    for (i, j), coeff in Q.items():
        energy += coeff * bits[i] * bits[j]

    return energy


# -----------------------------
# Direct diagnostics
# -----------------------------

def selected_assignments(bits: Tuple[int, ...]) -> List[Tuple[int, int, int]]:
    selected = []

    for idx, value in enumerate(bits):
        if value == 1:
            selected.append(INDEX_TO_VAR[idx])

    return selected


def assignment_violation_count(bits: Tuple[int, ...]) -> int:
    violations = 0

    for o in range(NUM_OPERATIONS):
        count = sum(
            bits[idx]
            for idx, (oo, r, t) in INDEX_TO_VAR.items()
            if oo == o
        )

        if count != 1:
            violations += abs(count - 1)

    return violations


def overlap_violation_count(bits: Tuple[int, ...]) -> int:
    violations = 0

    selected = [
        (idx, INDEX_TO_VAR[idx])
        for idx, value in enumerate(bits)
        if value == 1
    ]

    for a in range(len(selected)):
        i, (o1, r1, t1) = selected[a]
        d1 = duration[(o1, r1)]
        interval1 = set(range(t1, t1 + d1))

        for b in range(a + 1, len(selected)):
            j, (o2, r2, t2) = selected[b]

            if o1 == o2:
                continue

            if r1 != r2:
                continue

            d2 = duration[(o2, r2)]
            interval2 = set(range(t2, t2 + d2))

            if interval1.intersection(interval2):
                violations += 1

    return violations


def precedence_violation_count(bits: Tuple[int, ...]) -> int:
    violations = 0

    selected = selected_assignments(bits)

    for pred, succ in PRECEDENCE_ARCS:
        pred_selected = [(o, r, t) for o, r, t in selected if o == pred]
        succ_selected = [(o, r, t) for o, r, t in selected if o == succ]

        for pred_o, pred_r, pred_t in pred_selected:
            pred_finish = pred_t + duration[(pred_o, pred_r)]

            for succ_o, succ_r, succ_t in succ_selected:
                if succ_t < pred_finish:
                    violations += 1

    return violations


def is_feasible(bits: Tuple[int, ...]) -> bool:
    return (
        assignment_violation_count(bits) == 0
        and overlap_violation_count(bits) == 0
        and precedence_violation_count(bits) == 0
    )


def human_count(bits: Tuple[int, ...]) -> int:
    return sum(
        bits[idx]
        for idx, (o, r, t) in INDEX_TO_VAR.items()
        if r in HUMAN_RESOURCES
    )


def total_cost_without_reward(bits: Tuple[int, ...]) -> float:
    cost = 0.0

    for idx, value in enumerate(bits):
        if value == 0:
            continue

        o, r, t = INDEX_TO_VAR[idx]

        cost += (
            assignment_cost[(o, r)]
            + workload_cost[(o, r)]
            + ergonomic_cost[(o, r)]
            + start_time_weight[o] * t
        )

    return cost


def decode_solution(bits: Tuple[int, ...]) -> str:
    parts = []

    for idx, value in enumerate(bits):
        if value == 0:
            continue

        o, r, t = INDEX_TO_VAR[idx]
        r_label = "human" if r == HUMAN else "machine"
        finish = t + duration[(o, r)]
        parts.append(f"op{o}->{r_label}@{t}-{finish}")

    return "; ".join(parts)


def parse_float_list(value: str) -> List[float]:
    return [float(v.strip()) for v in value.split(",") if v.strip()]


def main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--human-rewards",
        type=str,
        default="0.0,1.0,2.0,3.0,4.0",
    )

    parser.add_argument(
        "--lambda-targets",
        type=str,
        default="0.0,0.5,1.0,2.0,3.0",
    )

    parser.add_argument(
        "--constraint-penalties",
        type=str,
        default="1.0,5.0,10.0,30.0",
    )

    parser.add_argument(
        "--out",
        type=str,
        default="results/tables/small_time_indexed_qubo_parameter_sensitivity.csv",
    )

    parser.add_argument(
        "--summary-out",
        type=str,
        default="results/tables/small_time_indexed_qubo_parameter_sensitivity_summary.json",
    )

    args = parser.parse_args()

    human_rewards = parse_float_list(args.human_rewards)
    lambda_targets = parse_float_list(args.lambda_targets)
    constraint_penalties = parse_float_list(args.constraint_penalties)

    out_path = Path(args.out)
    summary_path = Path(args.summary_out)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.parent.mkdir(parents=True, exist_ok=True)

    rows = []

    for human_reward in human_rewards:
        for lambda_target in lambda_targets:
            for constraint_penalty in constraint_penalties:
                Q, constant = build_qubo(
                    human_reward=human_reward,
                    lambda_target=lambda_target,
                    constraint_penalty=constraint_penalty,
                )

                best_all = None
                best_feasible = None

                for bits in itertools.product([0, 1], repeat=NUM_VARIABLES):
                    energy = qubo_energy(bits, Q, constant)
                    feasible = is_feasible(bits)

                    row_candidate = {
                        "human_reward": human_reward,
                        "lambda_target": lambda_target,
                        "constraint_penalty": constraint_penalty,
                        "bitstring": "".join(str(b) for b in bits),
                        "qubo_energy": energy,
                        "feasible": feasible,
                        "human_count": human_count(bits),
                        "distance_from_target": abs(
                            human_count(bits) - TARGET_HUMAN_ASSIGNMENTS
                        ),
                        "total_cost_without_reward": total_cost_without_reward(bits),
                        "assignment_violations": assignment_violation_count(bits),
                        "overlap_violations": overlap_violation_count(bits),
                        "precedence_violations": precedence_violation_count(bits),
                        "decoded_solution": decode_solution(bits),
                    }

                    if best_all is None or energy < best_all["qubo_energy"]:
                        best_all = row_candidate

                    if feasible:
                        if best_feasible is None or energy < best_feasible["qubo_energy"]:
                            best_feasible = row_candidate

                # Record only optimum diagnostics per parameter setting.
                best_all_is_feasible = best_all["feasible"]

                if best_feasible is None:
                    feasible_gap = None
                    best_feasible_energy = None
                    best_feasible_human_count = None
                    best_feasible_distance = None
                    best_feasible_solution = ""
                else:
                    feasible_gap = best_feasible["qubo_energy"] - best_all["qubo_energy"]
                    best_feasible_energy = best_feasible["qubo_energy"]
                    best_feasible_human_count = best_feasible["human_count"]
                    best_feasible_distance = best_feasible["distance_from_target"]
                    best_feasible_solution = best_feasible["decoded_solution"]

                rows.append(
                    {
                        "human_reward": human_reward,
                        "lambda_target": lambda_target,
                        "constraint_penalty": constraint_penalty,
                        "num_variables": NUM_VARIABLES,
                        "num_qubo_terms": len(Q),
                        "constant": constant,
                        "best_all_energy": best_all["qubo_energy"],
                        "best_all_feasible": best_all_is_feasible,
                        "best_all_human_count": best_all["human_count"],
                        "best_all_distance_from_target": best_all["distance_from_target"],
                        "best_all_assignment_violations": best_all["assignment_violations"],
                        "best_all_overlap_violations": best_all["overlap_violations"],
                        "best_all_precedence_violations": best_all["precedence_violations"],
                        "best_all_solution": best_all["decoded_solution"],
                        "best_feasible_energy": best_feasible_energy,
                        "best_feasible_human_count": best_feasible_human_count,
                        "best_feasible_distance_from_target": best_feasible_distance,
                        "best_feasible_solution": best_feasible_solution,
                        "feasible_gap": feasible_gap,
                    }
                )

    with out_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    num_settings = len(rows)
    num_best_feasible = sum(1 for row in rows if row["best_all_feasible"])
    num_best_infeasible = num_settings - num_best_feasible

    summary = {
        "experiment": "small_time_indexed_qubo_parameter_sensitivity",
        "num_operations": NUM_OPERATIONS,
        "num_resources": NUM_RESOURCES,
        "horizon": HORIZON,
        "num_variables": NUM_VARIABLES,
        "target_human_assignments": TARGET_HUMAN_ASSIGNMENTS,
        "human_rewards": human_rewards,
        "lambda_targets": lambda_targets,
        "constraint_penalties": constraint_penalties,
        "num_parameter_settings": num_settings,
        "num_settings_best_all_feasible": num_best_feasible,
        "num_settings_best_all_infeasible": num_best_infeasible,
        "output_csv": str(out_path),
    }

    with summary_path.open("w") as f:
        json.dump(summary, f, indent=2)

    print("=== Small time-indexed QUBO parameter sensitivity ===")
    print(f"num_parameter_settings = {num_settings}")
    print(f"best_all feasible settings = {num_best_feasible}")
    print(f"best_all infeasible settings = {num_best_infeasible}")
    print(f"saved results = {out_path}")
    print(f"saved summary = {summary_path}")


if __name__ == "__main__":
    main()
