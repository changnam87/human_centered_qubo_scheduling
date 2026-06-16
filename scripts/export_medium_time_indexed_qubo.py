"""
Export and validate a medium time-indexed scheduling QUBO.

Purpose
-------
This script scales the previous small time-indexed QUBO prototype to a medium
prototype with:

    operations = 3
    resources = 3
    horizon = 6

Variables:

    x[o, r, t] = 1 if operation o starts on resource r at time t

The QUBO includes:
1. assignment/start-time cost
2. workload and ergonomic human-centered costs
3. soft human reward
4. squared target human-utilization penalty
5. one-start assignment penalties
6. resource overlap penalties
7. precedence penalties

Because the number of binary assignments may be too large for full brute force,
this script performs:
1. coefficient export
2. exhaustive validation only if variable count is small enough
3. sampled validation otherwise
4. feasible schedule generation and energy validation

This remains prototype / pilot validation.
"""

from __future__ import annotations

import argparse
import csv
import itertools
import json
import random
from pathlib import Path
from typing import Dict, Tuple, List


# -----------------------------
# Medium time-indexed problem
# -----------------------------

NUM_OPERATIONS = 3
NUM_RESOURCES = 3
HORIZON = 6

MACHINE_A = 0
MACHINE_B = 1
HUMAN = 2

HUMAN_RESOURCES = [HUMAN]

PRECEDENCE_ARCS = [
    (0, 1),
    (1, 2),
]

duration = {
    (0, MACHINE_A): 1,
    (0, MACHINE_B): 2,
    (0, HUMAN): 2,

    (1, MACHINE_A): 2,
    (1, MACHINE_B): 1,
    (1, HUMAN): 2,

    (2, MACHINE_A): 1,
    (2, MACHINE_B): 2,
    (2, HUMAN): 1,
}

assignment_cost = {
    (0, MACHINE_A): 2.0,
    (0, MACHINE_B): 2.4,
    (0, HUMAN): 3.0,

    (1, MACHINE_A): 2.6,
    (1, MACHINE_B): 2.2,
    (1, HUMAN): 3.2,

    (2, MACHINE_A): 2.1,
    (2, MACHINE_B): 2.7,
    (2, HUMAN): 3.1,
}

workload_cost = {}
ergonomic_cost = {}

for o in range(NUM_OPERATIONS):
    for r in range(NUM_RESOURCES):
        if r == HUMAN:
            workload_cost[(o, r)] = [1.0, 1.4, 1.2][o]
            ergonomic_cost[(o, r)] = [0.6, 0.8, 0.7][o]
        else:
            workload_cost[(o, r)] = 0.0
            ergonomic_cost[(o, r)] = 0.0

start_time_weight = {
    0: 0.10,
    1: 0.15,
    2: 0.10,
}

DEFAULT_HUMAN_REWARD = 2.5
DEFAULT_TARGET_HUMAN_ASSIGNMENTS = 1
DEFAULT_LAMBDA_TARGET = 1.0
DEFAULT_CONSTRAINT_PENALTY = 30.0


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


def resource_label(r: int) -> str:
    if r == MACHINE_A:
        return "machine_a"
    if r == MACHINE_B:
        return "machine_b"
    if r == HUMAN:
        return "human"
    return f"resource_{r}"


def var_name(idx: int) -> str:
    o, r, t = INDEX_TO_VAR[idx]
    return f"x_o{o}_r{r}_{resource_label(r)}_t{t}"


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
    target_human_assignments: int,
    constraint_penalty: float,
) -> Tuple[QuboDict, float]:
    """
    Build QUBO:

        E(x) = constant + sum_i Q[i,i] x_i + sum_{i<j} Q[i,j] x_i x_j
    """

    Q: QuboDict = {}
    constant = 0.0

    # 1. Base scheduling cost.
    for idx, (o, r, t) in INDEX_TO_VAR.items():
        coeff = (
            assignment_cost[(o, r)]
            + workload_cost[(o, r)]
            + ergonomic_cost[(o, r)]
            + start_time_weight[o] * t
        )
        add_linear(Q, idx, coeff)

    # 2. Soft human reward.
    human_vars = []

    for idx, (o, r, t) in INDEX_TO_VAR.items():
        if r in HUMAN_RESOURCES:
            add_linear(Q, idx, -human_reward)
            human_vars.append(idx)

    # 3. Squared target human-utilization penalty.
    constant += lambda_target * target_human_assignments**2

    human_linear_coeff = lambda_target * (1 - 2 * target_human_assignments)

    for i in human_vars:
        add_linear(Q, i, human_linear_coeff)

    for a in range(len(human_vars)):
        for b in range(a + 1, len(human_vars)):
            add_quadratic(Q, human_vars[a], human_vars[b], 2.0 * lambda_target)

    # 4. Each operation starts exactly once.
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

    # 5. Resource overlap penalties.
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

    # 6. Precedence penalties.
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
# Direct objective and diagnostics
# -----------------------------

def selected_assignments(bits: Tuple[int, ...]) -> List[Tuple[int, int, int]]:
    selected = []

    for idx, value in enumerate(bits):
        if value == 1:
            selected.append(INDEX_TO_VAR[idx])

    return selected


def assignment_penalty_value(bits: Tuple[int, ...], constraint_penalty: float) -> float:
    penalty = 0.0

    for o in range(NUM_OPERATIONS):
        count = sum(
            bits[idx]
            for idx, (oo, r, t) in INDEX_TO_VAR.items()
            if oo == o
        )
        penalty += constraint_penalty * (count - 1) ** 2

    return penalty


def overlap_penalty_value(bits: Tuple[int, ...], constraint_penalty: float) -> float:
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
                penalty += constraint_penalty

    return penalty


def precedence_penalty_value(bits: Tuple[int, ...], constraint_penalty: float) -> float:
    penalty = 0.0
    selected = selected_assignments(bits)

    for pred, succ in PRECEDENCE_ARCS:
        pred_selected = [(o, r, t) for o, r, t in selected if o == pred]
        succ_selected = [(o, r, t) for o, r, t in selected if o == succ]

        for pred_o, pred_r, pred_t in pred_selected:
            pred_finish = pred_t + duration[(pred_o, pred_r)]

            for succ_o, succ_r, succ_t in succ_selected:
                if succ_t < pred_finish:
                    penalty += constraint_penalty

    return penalty


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
    return int(overlap_penalty_value(bits, 1.0))


def precedence_violation_count(bits: Tuple[int, ...]) -> int:
    return int(precedence_penalty_value(bits, 1.0))


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


def direct_objective(
    bits: Tuple[int, ...],
    human_reward: float,
    lambda_target: float,
    target_human_assignments: int,
    constraint_penalty: float,
) -> float:
    h_count = human_count(bits)

    return (
        total_cost_without_reward(bits)
        - human_reward * h_count
        + lambda_target * (h_count - target_human_assignments) ** 2
        + assignment_penalty_value(bits, constraint_penalty)
        + overlap_penalty_value(bits, constraint_penalty)
        + precedence_penalty_value(bits, constraint_penalty)
    )


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
                "resource_type": resource_label(r),
                "start_time": t,
                "duration": duration[(o, r)],
                "finish_time": t + duration[(o, r)],
                "variable_index": idx,
                "variable_name": var_name(idx),
            }
        )

    return decoded


def random_bits(rng: random.Random) -> Tuple[int, ...]:
    return tuple(rng.choice([0, 1]) for _ in range(NUM_VARIABLES))


def random_one_start_bits(rng: random.Random) -> Tuple[int, ...]:
    bits = [0] * NUM_VARIABLES

    for o in range(NUM_OPERATIONS):
        op_indices = [
            idx
            for idx, (oo, r, t) in INDEX_TO_VAR.items()
            if oo == o
        ]
        chosen = rng.choice(op_indices)
        bits[chosen] = 1

    return tuple(bits)


def generate_greedy_feasible_bits() -> Tuple[int, ...]:
    """
    Generate a simple feasible schedule respecting precedence.

    This is not necessarily optimal. It is a sanity-check feasible solution.
    """

    bits = [0] * NUM_VARIABLES
    current_time = 0

    for o in range(NUM_OPERATIONS):
        # Prefer machine first for simplicity.
        candidate = None

        for r in range(NUM_RESOURCES):
            for t in range(current_time, HORIZON):
                if (o, r, t) not in VAR_TO_INDEX:
                    continue

                finish = t + duration[(o, r)]
                if finish <= HORIZON:
                    candidate = (o, r, t)
                    break

            if candidate is not None:
                break

        if candidate is None:
            raise RuntimeError("Could not construct greedy feasible schedule.")

        idx = VAR_TO_INDEX[candidate]
        bits[idx] = 1
        current_time = candidate[2] + duration[(candidate[0], candidate[1])]

    return tuple(bits)


def evaluate_sample(
    bits: Tuple[int, ...],
    Q: QuboDict,
    constant: float,
    human_reward: float,
    lambda_target: float,
    target_human_assignments: int,
    constraint_penalty: float,
) -> Dict[str, object]:
    direct = direct_objective(
        bits,
        human_reward=human_reward,
        lambda_target=lambda_target,
        target_human_assignments=target_human_assignments,
        constraint_penalty=constraint_penalty,
    )
    energy = qubo_energy(bits, Q, constant)

    return {
        "bitstring": "".join(str(b) for b in bits),
        "direct_objective": direct,
        "qubo_energy": energy,
        "abs_error": abs(direct - energy),
        "feasible": is_feasible(bits),
        "human_count": human_count(bits),
        "distance_from_target": abs(human_count(bits) - target_human_assignments),
        "assignment_violations": assignment_violation_count(bits),
        "overlap_violations": overlap_violation_count(bits),
        "precedence_violations": precedence_violation_count(bits),
        "decoded_solution": "; ".join(
            f"op{row['operation']}->{row['resource_type']}@{row['start_time']}-{row['finish_time']}"
            for row in decode_solution(bits)
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument("--human-reward", type=float, default=DEFAULT_HUMAN_REWARD)
    parser.add_argument("--lambda-target", type=float, default=DEFAULT_LAMBDA_TARGET)
    parser.add_argument(
        "--target-human-assignments",
        type=int,
        default=DEFAULT_TARGET_HUMAN_ASSIGNMENTS,
    )
    parser.add_argument(
        "--constraint-penalty",
        type=float,
        default=DEFAULT_CONSTRAINT_PENALTY,
    )
    parser.add_argument("--random-samples", type=int, default=5000)
    parser.add_argument("--seed", type=int, default=123)
    parser.add_argument("--bruteforce-limit", type=int, default=20)

    args = parser.parse_args()

    Q, constant = build_qubo(
        human_reward=args.human_reward,
        lambda_target=args.lambda_target,
        target_human_assignments=args.target_human_assignments,
        constraint_penalty=args.constraint_penalty,
    )

    out_dir = Path("results/tables")
    out_dir.mkdir(parents=True, exist_ok=True)

    coeff_path = out_dir / "medium_time_indexed_qubo_coefficients.csv"
    validation_path = out_dir / "medium_time_indexed_qubo_energy_validation_samples.csv"
    summary_path = out_dir / "medium_time_indexed_qubo_summary.json"
    solution_path = out_dir / "medium_time_indexed_qubo_greedy_feasible_solution.csv"

    # Save coefficients.
    with coeff_path.open("w", newline="") as f:
        fieldnames = ["i", "j", "coefficient", "var_i", "var_j", "term_type"]
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

    rng = random.Random(args.seed)
    rows = []

    # Include all-zero vector.
    rows.append(
        evaluate_sample(
            tuple([0] * NUM_VARIABLES),
            Q,
            constant,
            args.human_reward,
            args.lambda_target,
            args.target_human_assignments,
            args.constraint_penalty,
        )
    )

    # Include greedy feasible solution.
    greedy_bits = generate_greedy_feasible_bits()
    greedy_eval = evaluate_sample(
        greedy_bits,
        Q,
        constant,
        args.human_reward,
        args.lambda_target,
        args.target_human_assignments,
        args.constraint_penalty,
    )
    rows.append(greedy_eval)

    # Random arbitrary binary samples.
    for _ in range(args.random_samples):
        bits = random_bits(rng)
        rows.append(
            evaluate_sample(
                bits,
                Q,
                constant,
                args.human_reward,
                args.lambda_target,
                args.target_human_assignments,
                args.constraint_penalty,
            )
        )

    # Random one-start samples.
    for _ in range(args.random_samples):
        bits = random_one_start_bits(rng)
        rows.append(
            evaluate_sample(
                bits,
                Q,
                constant,
                args.human_reward,
                args.lambda_target,
                args.target_human_assignments,
                args.constraint_penalty,
            )
        )

    # Optional exhaustive validation if small enough.
    exhaustive_performed = False

    if NUM_VARIABLES <= args.bruteforce_limit:
        exhaustive_performed = True
        for bits in itertools.product([0, 1], repeat=NUM_VARIABLES):
            rows.append(
                evaluate_sample(
                    bits,
                    Q,
                    constant,
                    args.human_reward,
                    args.lambda_target,
                    args.target_human_assignments,
                    args.constraint_penalty,
                )
            )

    with validation_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    with solution_path.open("w", newline="") as f:
        decoded = decode_solution(greedy_bits)
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

    max_abs_error = max(row["abs_error"] for row in rows)
    mean_abs_error = sum(row["abs_error"] for row in rows) / len(rows)
    feasible_rows = sum(1 for row in rows if row["feasible"])

    summary = {
        "experiment": "medium_time_indexed_qubo_export",
        "num_operations": NUM_OPERATIONS,
        "num_resources": NUM_RESOURCES,
        "horizon": HORIZON,
        "num_variables": NUM_VARIABLES,
        "human_reward": args.human_reward,
        "lambda_target": args.lambda_target,
        "target_human_assignments": args.target_human_assignments,
        "constraint_penalty": args.constraint_penalty,
        "constant": constant,
        "num_qubo_terms": len(Q),
        "num_linear_terms": sum(1 for i, j in Q if i == j),
        "num_quadratic_terms": sum(1 for i, j in Q if i != j),
        "random_samples": args.random_samples,
        "total_validation_rows": len(rows),
        "feasible_validation_rows": feasible_rows,
        "exhaustive_performed": exhaustive_performed,
        "bruteforce_limit": args.bruteforce_limit,
        "max_abs_error": max_abs_error,
        "mean_abs_error": mean_abs_error,
        "validation_status": "PASS" if max_abs_error < 1e-9 else "FAIL",
        "greedy_feasible_solution": greedy_eval,
        "coefficient_csv": str(coeff_path),
        "validation_csv": str(validation_path),
        "greedy_solution_csv": str(solution_path),
    }

    with summary_path.open("w") as f:
        json.dump(summary, f, indent=2)

    print("=== Medium time-indexed QUBO export and sampled validation ===")
    print(f"num_variables = {NUM_VARIABLES}")
    print(f"num_qubo_terms = {len(Q)}")
    print(f"num_linear_terms = {summary['num_linear_terms']}")
    print(f"num_quadratic_terms = {summary['num_quadratic_terms']}")
    print(f"exhaustive_performed = {exhaustive_performed}")
    print(f"total_validation_rows = {len(rows)}")
    print(f"max_abs_error = {max_abs_error}")
    print(f"validation_status = {summary['validation_status']}")
    print(f"feasible_validation_rows = {feasible_rows}")
    print(f"saved coefficients = {coeff_path}")
    print(f"saved validation samples = {validation_path}")
    print(f"saved summary = {summary_path}")
    print(f"saved greedy solution = {solution_path}")


if __name__ == "__main__":
    main()
