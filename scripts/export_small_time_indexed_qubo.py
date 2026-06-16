"""
Export and validate a small time-indexed scheduling QUBO.

Purpose
-------
This script moves beyond assignment-only QUBO export and builds a small
time-indexed scheduling QUBO with variables:

    x[o, r, t] = 1 if operation o starts on resource r at time t

The QUBO includes:
1. Base assignment/start-time cost
2. Workload and ergonomic human-centered cost
3. Soft human reward
4. Squared target human-utilization penalty
5. One-start assignment penalty
6. Resource overlap penalty
7. Precedence penalty

This is a small brute-force-validatable prototype, not the full sample_4x4 QUBO.
"""

from __future__ import annotations

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

# operation 0 must precede operation 1
PRECEDENCE_ARCS = [(0, 1)]

# Duration depends on operation and resource
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

HUMAN_REWARD = 2.0
TARGET_HUMAN_ASSIGNMENTS = 1
LAMBDA_TARGET = 1.0

ASSIGNMENT_PENALTY = 30.0
RESOURCE_OVERLAP_PENALTY = 30.0
PRECEDENCE_PENALTY = 30.0


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


def build_qubo() -> Tuple[QuboDict, float]:
    """
    Build QUBO:

        E(x) = constant + sum_i Q[i,i] x_i + sum_{i<j} Q[i,j] x_i x_j
    """

    Q: QuboDict = {}
    constant = 0.0

    # ------------------------------------------------------
    # 1. Base scheduling cost
    # ------------------------------------------------------
    for idx, (o, r, t) in INDEX_TO_VAR.items():
        coeff = (
            assignment_cost[(o, r)]
            + workload_cost[(o, r)]
            + ergonomic_cost[(o, r)]
            + start_time_weight[o] * t
        )
        add_linear(Q, idx, coeff)

    # ------------------------------------------------------
    # 2. Soft human reward
    # ------------------------------------------------------
    human_vars = []

    for idx, (o, r, t) in INDEX_TO_VAR.items():
        if r in HUMAN_RESOURCES:
            add_linear(Q, idx, -HUMAN_REWARD)
            human_vars.append(idx)

    # ------------------------------------------------------
    # 3. Squared target human utilization penalty
    #
    # lambda * (human_count - target)^2
    # = lambda * [(1 - 2T) sum h_i + 2 sum_{i<j} h_i h_j + T^2]
    # ------------------------------------------------------
    constant += LAMBDA_TARGET * TARGET_HUMAN_ASSIGNMENTS**2

    human_linear_coeff = LAMBDA_TARGET * (1 - 2 * TARGET_HUMAN_ASSIGNMENTS)

    for i in human_vars:
        add_linear(Q, i, human_linear_coeff)

    for a in range(len(human_vars)):
        for b in range(a + 1, len(human_vars)):
            add_quadratic(Q, human_vars[a], human_vars[b], 2.0 * LAMBDA_TARGET)

    # ------------------------------------------------------
    # 4. Each operation starts exactly once:
    #
    # P * (sum_{r,t} x[o,r,t] - 1)^2
    # = P * [-sum x + 2 sum_{i<j} x_i x_j + 1]
    # ------------------------------------------------------
    for o in range(NUM_OPERATIONS):
        op_vars = [
            idx
            for idx, (oo, r, t) in INDEX_TO_VAR.items()
            if oo == o
        ]

        constant += ASSIGNMENT_PENALTY

        for i in op_vars:
            add_linear(Q, i, -ASSIGNMENT_PENALTY)

        for a in range(len(op_vars)):
            for b in range(a + 1, len(op_vars)):
                add_quadratic(Q, op_vars[a], op_vars[b], 2.0 * ASSIGNMENT_PENALTY)

    # ------------------------------------------------------
    # 5. Resource overlap penalty:
    #
    # If two selected starts use the same resource and overlap in time,
    # penalize x_i x_j.
    # ------------------------------------------------------
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
                add_quadratic(Q, i, j, RESOURCE_OVERLAP_PENALTY)

    # ------------------------------------------------------
    # 6. Precedence penalty:
    #
    # For arc pred -> succ:
    # Penalize pairs where succ starts before pred finishes.
    #
    # This is represented as pairwise forbidden-combination penalties.
    # ------------------------------------------------------
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
                    add_quadratic(Q, i, j, PRECEDENCE_PENALTY)

    Q = {key: value for key, value in Q.items() if abs(value) > 1e-12}

    return Q, constant


# -----------------------------
# Direct objective for validation
# -----------------------------

def selected_assignments(bits: Tuple[int, ...]) -> List[Tuple[int, int, int]]:
    selected = []

    for idx, value in enumerate(bits):
        if value == 1:
            selected.append(INDEX_TO_VAR[idx])

    return selected


def assignment_penalty(bits: Tuple[int, ...]) -> float:
    penalty = 0.0

    for o in range(NUM_OPERATIONS):
        count = sum(
            bits[idx]
            for idx, (oo, r, t) in INDEX_TO_VAR.items()
            if oo == o
        )
        penalty += ASSIGNMENT_PENALTY * (count - 1) ** 2

    return penalty


def overlap_penalty(bits: Tuple[int, ...]) -> float:
    penalty = 0.0

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
                penalty += RESOURCE_OVERLAP_PENALTY

    return penalty


def precedence_penalty(bits: Tuple[int, ...]) -> float:
    penalty = 0.0

    selected = selected_assignments(bits)

    for pred, succ in PRECEDENCE_ARCS:
        pred_selected = [(o, r, t) for o, r, t in selected if o == pred]
        succ_selected = [(o, r, t) for o, r, t in selected if o == succ]

        for pred_o, pred_r, pred_t in pred_selected:
            pred_finish = pred_t + duration[(pred_o, pred_r)]

            for succ_o, succ_r, succ_t in succ_selected:
                if succ_t < pred_finish:
                    penalty += PRECEDENCE_PENALTY

    return penalty


def direct_objective(bits: Tuple[int, ...]) -> float:
    total_cost_without_reward = 0.0
    human_count = 0

    for idx, value in enumerate(bits):
        if value == 0:
            continue

        o, r, t = INDEX_TO_VAR[idx]

        total_cost_without_reward += (
            assignment_cost[(o, r)]
            + workload_cost[(o, r)]
            + ergonomic_cost[(o, r)]
            + start_time_weight[o] * t
        )

        if r in HUMAN_RESOURCES:
            human_count += 1

    reward_term = HUMAN_REWARD * human_count
    squared_target_penalty = LAMBDA_TARGET * (
        human_count - TARGET_HUMAN_ASSIGNMENTS
    ) ** 2

    return (
        total_cost_without_reward
        - reward_term
        + squared_target_penalty
        + assignment_penalty(bits)
        + overlap_penalty(bits)
        + precedence_penalty(bits)
    )


def qubo_energy(bits: Tuple[int, ...], Q: QuboDict, constant: float) -> float:
    energy = constant

    for (i, j), coeff in Q.items():
        energy += coeff * bits[i] * bits[j]

    return energy


def is_feasible(bits: Tuple[int, ...]) -> bool:
    # Each operation exactly once.
    for o in range(NUM_OPERATIONS):
        count = sum(
            bits[idx]
            for idx, (oo, r, t) in INDEX_TO_VAR.items()
            if oo == o
        )
        if count != 1:
            return False

    if overlap_penalty(bits) > 0:
        return False

    if precedence_penalty(bits) > 0:
        return False

    return True


def decode_solution(bits: Tuple[int, ...]) -> List[Dict[str, object]]:
    decoded = []

    for idx, value in enumerate(bits):
        if value == 0:
            continue

        o, r, t = INDEX_TO_VAR[idx]
        decoded.append(
            {
                "operation": o,
                "resource": r,
                "resource_type": "human" if r == HUMAN else "machine",
                "start_time": t,
                "duration": duration[(o, r)],
                "finish_time": t + duration[(o, r)],
                "variable_index": idx,
                "variable_name": var_name(idx),
            }
        )

    return decoded


def main() -> None:
    Q, constant = build_qubo()

    out_dir = Path("results/tables")
    out_dir.mkdir(parents=True, exist_ok=True)

    coeff_path = out_dir / "small_time_indexed_qubo_coefficients.csv"
    validation_path = out_dir / "small_time_indexed_qubo_energy_validation.csv"
    summary_path = out_dir / "small_time_indexed_qubo_summary.json"
    solution_path = out_dir / "small_time_indexed_qubo_best_solution.csv"

    # Save coefficients.
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
            writer.writerow(
                {
                    "i": i,
                    "j": j,
                    "coefficient": coeff,
                    "var_i": var_name(i),
                    "var_j": var_name(j),
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
        feasible = is_feasible(bits)

        max_abs_error = max(max_abs_error, abs_error)

        human_count = sum(
            bits[idx]
            for idx, (o, r, t) in INDEX_TO_VAR.items()
            if r in HUMAN_RESOURCES
        )

        row = {
            "bitstring": "".join(str(b) for b in bits),
            "feasible": feasible,
            "human_count": human_count,
            "direct_objective": direct,
            "qubo_energy": energy,
            "abs_error": abs_error,
            "assignment_penalty": assignment_penalty(bits),
            "overlap_penalty": overlap_penalty(bits),
            "precedence_penalty": precedence_penalty(bits),
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
            "start_time",
            "duration",
            "finish_time",
            "variable_index",
            "variable_name",
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(decoded)

    summary = {
        "num_operations": NUM_OPERATIONS,
        "num_resources": NUM_RESOURCES,
        "horizon": HORIZON,
        "num_variables": NUM_VARIABLES,
        "human_reward": HUMAN_REWARD,
        "target_human_assignments": TARGET_HUMAN_ASSIGNMENTS,
        "lambda_target": LAMBDA_TARGET,
        "assignment_penalty": ASSIGNMENT_PENALTY,
        "resource_overlap_penalty": RESOURCE_OVERLAP_PENALTY,
        "precedence_penalty": PRECEDENCE_PENALTY,
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

    print("=== Small time-indexed QUBO export and validation ===")
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
