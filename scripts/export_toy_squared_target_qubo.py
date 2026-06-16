"""
Export and validate a toy QUBO with squared target human-utilization penalty.

Purpose
-------
This script creates a small assignment-only QUBO that includes:

1. Assignment cost
2. Workload and ergonomic human-centered costs
3. Soft human reward
4. QUBO-compatible squared target human-utilization penalty
5. One-hot assignment penalty for each operation

The objective is:

    direct_objective(x)
        = total_cost_without_reward
          - human_reward * human_count
          + lambda_target * (human_count - target)^2
          + assignment_penalty * sum_i (sum_r x[i,r] - 1)^2

The exported QUBO has the form:

    energy(x)
        = constant
          + sum_i Q[i,i] x_i
          + sum_{i<j} Q[i,j] x_i x_j

This is a toy-level QUBO coefficient export and brute-force validation.
It is not yet the full 9072-variable sample_4x4 time-indexed QUBO.
"""

from __future__ import annotations

import csv
import itertools
import json
from pathlib import Path
from typing import Dict, Tuple, List


# -----------------------------
# Toy problem definition
# -----------------------------

NUM_OPERATIONS = 4
NUM_RESOURCES = 3

MACHINE = 0
HUMAN = 1
ROBOT = 2

HUMAN_RESOURCES = [HUMAN]

# x[i, r] variable index
# operation i assigned to resource r
def var_index(operation: int, resource: int) -> int:
    return operation * NUM_RESOURCES + resource


def var_name(operation: int, resource: int) -> str:
    resource_label = {
        MACHINE: "machine",
        HUMAN: "human",
        ROBOT: "robot",
    }[resource]

    return f"x_op{operation}_res{resource}_{resource_label}"


NUM_VARIABLES = NUM_OPERATIONS * NUM_RESOURCES

# Cost matrices:
# These are intentionally simple and interpretable.
assignment_cost = {
    # operation 0
    (0, MACHINE): 2.0,
    (0, HUMAN): 3.0,
    (0, ROBOT): 2.5,
    # operation 1
    (1, MACHINE): 2.5,
    (1, HUMAN): 3.2,
    (1, ROBOT): 2.4,
    # operation 2
    (2, MACHINE): 2.2,
    (2, HUMAN): 3.1,
    (2, ROBOT): 2.8,
    # operation 3
    (3, MACHINE): 2.4,
    (3, HUMAN): 3.0,
    (3, ROBOT): 2.6,
}

workload_cost = {}
ergonomic_cost = {}

for i in range(NUM_OPERATIONS):
    for r in range(NUM_RESOURCES):
        if r == HUMAN:
            workload_cost[(i, r)] = [1.0, 1.5, 1.2, 1.3][i]
            ergonomic_cost[(i, r)] = [0.6, 0.8, 0.7, 0.9][i]
        else:
            workload_cost[(i, r)] = 0.0
            ergonomic_cost[(i, r)] = 0.0


HUMAN_REWARD = 2.5
TARGET_HUMAN_ASSIGNMENTS = 2
LAMBDA_TARGET = 1.0
ASSIGNMENT_PENALTY = 20.0


# -----------------------------
# QUBO utility functions
# -----------------------------

QuboKey = Tuple[int, int]
QuboDict = Dict[QuboKey, float]


def add_linear(Q: QuboDict, i: int, coeff: float) -> None:
    key = (i, i)
    Q[key] = Q.get(key, 0.0) + coeff


def add_quadratic(Q: QuboDict, i: int, j: int, coeff: float) -> None:
    if i == j:
        add_linear(Q, i, coeff)
        return

    a, b = sorted((i, j))
    key = (a, b)
    Q[key] = Q.get(key, 0.0) + coeff


def build_qubo() -> Tuple[QuboDict, float]:
    """
    Build QUBO coefficient dictionary and constant.

    QUBO energy convention:

        E(x) = constant + sum_i Q[i,i] x_i + sum_{i<j} Q[i,j] x_i x_j
    """

    Q: QuboDict = {}
    constant = 0.0

    # ------------------------------------------------------
    # 1. Base cost terms:
    # assignment + workload + ergonomic
    # ------------------------------------------------------
    for op in range(NUM_OPERATIONS):
        for r in range(NUM_RESOURCES):
            idx = var_index(op, r)
            coeff = (
                assignment_cost[(op, r)]
                + workload_cost[(op, r)]
                + ergonomic_cost[(op, r)]
            )
            add_linear(Q, idx, coeff)

    # ------------------------------------------------------
    # 2. Soft human reward:
    # - human_reward * human_count
    # ------------------------------------------------------
    for op in range(NUM_OPERATIONS):
        for r in HUMAN_RESOURCES:
            idx = var_index(op, r)
            add_linear(Q, idx, -HUMAN_REWARD)

    # ------------------------------------------------------
    # 3. Squared target penalty:
    # lambda * (human_count - target)^2
    #
    # human_count = sum_i h_i
    # h_i is x[i, HUMAN]
    #
    # expansion:
    # lambda * [(1 - 2T) * sum_i h_i
    #           + 2 * sum_{i<j} h_i h_j
    #           + T^2]
    # ------------------------------------------------------
    human_vars: List[int] = [
        var_index(op, HUMAN)
        for op in range(NUM_OPERATIONS)
    ]

    constant += LAMBDA_TARGET * (TARGET_HUMAN_ASSIGNMENTS ** 2)

    linear_coeff = LAMBDA_TARGET * (1 - 2 * TARGET_HUMAN_ASSIGNMENTS)

    for idx in human_vars:
        add_linear(Q, idx, linear_coeff)

    for a_pos in range(len(human_vars)):
        for b_pos in range(a_pos + 1, len(human_vars)):
            add_quadratic(
                Q,
                human_vars[a_pos],
                human_vars[b_pos],
                2.0 * LAMBDA_TARGET,
            )

    # ------------------------------------------------------
    # 4. One-hot assignment penalty:
    #
    # assignment_penalty * (sum_r x[i,r] - 1)^2
    #
    # For each operation i:
    # (sum_r x_r - 1)^2
    # = (sum_r x_r)^2 - 2 sum_r x_r + 1
    # = sum_r x_r + 2 sum_{r<s} x_r x_s - 2 sum_r x_r + 1
    # = - sum_r x_r + 2 sum_{r<s} x_r x_s + 1
    # ------------------------------------------------------
    for op in range(NUM_OPERATIONS):
        op_vars = [var_index(op, r) for r in range(NUM_RESOURCES)]

        constant += ASSIGNMENT_PENALTY

        for idx in op_vars:
            add_linear(Q, idx, -ASSIGNMENT_PENALTY)

        for a_pos in range(len(op_vars)):
            for b_pos in range(a_pos + 1, len(op_vars)):
                add_quadratic(
                    Q,
                    op_vars[a_pos],
                    op_vars[b_pos],
                    2.0 * ASSIGNMENT_PENALTY,
                )

    # Remove near-zero coefficients.
    Q = {key: value for key, value in Q.items() if abs(value) > 1e-12}

    return Q, constant


def qubo_energy(bits: Tuple[int, ...], Q: QuboDict, constant: float) -> float:
    energy = constant

    for (i, j), coeff in Q.items():
        energy += coeff * bits[i] * bits[j]

    return energy


def direct_objective(bits: Tuple[int, ...]) -> float:
    total_cost_without_reward = 0.0
    human_count = 0

    assignment_penalty_value = 0.0

    for op in range(NUM_OPERATIONS):
        assigned_sum = 0

        for r in range(NUM_RESOURCES):
            idx = var_index(op, r)
            value = bits[idx]
            assigned_sum += value

            if value == 1:
                total_cost_without_reward += (
                    assignment_cost[(op, r)]
                    + workload_cost[(op, r)]
                    + ergonomic_cost[(op, r)]
                )

                if r in HUMAN_RESOURCES:
                    human_count += 1

        assignment_penalty_value += ASSIGNMENT_PENALTY * (assigned_sum - 1) ** 2

    squared_target_penalty = (
        LAMBDA_TARGET * (human_count - TARGET_HUMAN_ASSIGNMENTS) ** 2
    )

    reward_term = HUMAN_REWARD * human_count

    return (
        total_cost_without_reward
        - reward_term
        + squared_target_penalty
        + assignment_penalty_value
    )


def is_feasible_one_hot(bits: Tuple[int, ...]) -> bool:
    for op in range(NUM_OPERATIONS):
        assigned_sum = sum(bits[var_index(op, r)] for r in range(NUM_RESOURCES))

        if assigned_sum != 1:
            return False

    return True


def decode_solution(bits: Tuple[int, ...]) -> List[Dict[str, object]]:
    decoded = []

    for op in range(NUM_OPERATIONS):
        for r in range(NUM_RESOURCES):
            idx = var_index(op, r)

            if bits[idx] == 1:
                decoded.append(
                    {
                        "operation": op,
                        "resource": r,
                        "resource_type": (
                            "human"
                            if r == HUMAN
                            else "machine"
                            if r == MACHINE
                            else "robot"
                        ),
                        "variable_index": idx,
                        "variable_name": var_name(op, r),
                    }
                )

    return decoded


def main() -> None:
    Q, constant = build_qubo()

    out_dir = Path("results/tables")
    out_dir.mkdir(parents=True, exist_ok=True)

    coeff_path = out_dir / "toy_squared_target_qubo_coefficients.csv"
    validation_path = out_dir / "toy_squared_target_qubo_energy_validation.csv"
    summary_path = out_dir / "toy_squared_target_qubo_summary.json"
    solution_path = out_dir / "toy_squared_target_qubo_best_solution.csv"

    # Save QUBO coefficients.
    with coeff_path.open("w", newline="") as f:
        fieldnames = [
            "i",
            "j",
            "coefficient",
            "var_i",
            "var_j",
            "term_type",
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for (i, j), coeff in sorted(Q.items()):
            op_i = i // NUM_RESOURCES
            res_i = i % NUM_RESOURCES
            op_j = j // NUM_RESOURCES
            res_j = j % NUM_RESOURCES

            writer.writerow(
                {
                    "i": i,
                    "j": j,
                    "coefficient": coeff,
                    "var_i": var_name(op_i, res_i),
                    "var_j": var_name(op_j, res_j),
                    "term_type": "linear" if i == j else "quadratic",
                }
            )

    rows = []
    max_abs_error = 0.0

    best_all = None
    best_feasible = None

    for bits in itertools.product([0, 1], repeat=NUM_VARIABLES):
        direct = direct_objective(bits)
        energy = qubo_energy(bits, Q, constant)
        abs_error = abs(direct - energy)
        feasible = is_feasible_one_hot(bits)

        max_abs_error = max(max_abs_error, abs_error)

        human_count = sum(bits[var_index(op, HUMAN)] for op in range(NUM_OPERATIONS))

        row = {
            "bitstring": "".join(str(b) for b in bits),
            "feasible_one_hot": feasible,
            "human_count": human_count,
            "direct_objective": direct,
            "qubo_energy": energy,
            "abs_error": abs_error,
        }

        rows.append(row)

        if best_all is None or energy < best_all["qubo_energy"]:
            best_all = row

        if feasible:
            if best_feasible is None or energy < best_feasible["qubo_energy"]:
                best_feasible = row

    with validation_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    best_bits = tuple(int(c) for c in best_feasible["bitstring"])
    decoded = decode_solution(best_bits)

    with solution_path.open("w", newline="") as f:
        fieldnames = [
            "operation",
            "resource",
            "resource_type",
            "variable_index",
            "variable_name",
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(decoded)

    summary = {
        "num_operations": NUM_OPERATIONS,
        "num_resources": NUM_RESOURCES,
        "num_variables": NUM_VARIABLES,
        "human_reward": HUMAN_REWARD,
        "target_human_assignments": TARGET_HUMAN_ASSIGNMENTS,
        "lambda_target": LAMBDA_TARGET,
        "assignment_penalty": ASSIGNMENT_PENALTY,
        "constant": constant,
        "num_qubo_terms": len(Q),
        "num_linear_terms": sum(1 for i, j in Q if i == j),
        "num_quadratic_terms": sum(1 for i, j in Q if i != j),
        "num_bruteforce_rows": len(rows),
        "max_abs_error": max_abs_error,
        "validation_status": "PASS" if max_abs_error < 1e-9 else "FAIL",
        "best_all": best_all,
        "best_feasible": best_feasible,
        "coefficient_csv": str(coeff_path),
        "validation_csv": str(validation_path),
        "best_solution_csv": str(solution_path),
    }

    with summary_path.open("w") as f:
        json.dump(summary, f, indent=2)

    print("=== Toy squared target QUBO export and validation ===")
    print(f"num_variables = {NUM_VARIABLES}")
    print(f"num_qubo_terms = {len(Q)}")
    print(f"constant = {constant}")
    print(f"max_abs_error = {max_abs_error}")
    print(f"validation_status = {summary['validation_status']}")
    print(f"best_feasible = {best_feasible}")
    print(f"saved coefficients = {coeff_path}")
    print(f"saved validation = {validation_path}")
    print(f"saved summary = {summary_path}")
    print(f"saved best solution = {solution_path}")


if __name__ == "__main__":
    main()
