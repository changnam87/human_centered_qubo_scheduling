"""
Toy validation for QUBO-compatible squared target human-utilization penalty.

Purpose
-------
Validate that the direct squared target penalty:

    lambda_target * (sum_i h_i - target)^2

matches the expanded QUBO form:

    lambda_target * [
        (1 - 2 * target) * sum_i h_i
        + 2 * sum_{i<j} h_i h_j
        + target^2
    ]

for all binary assignments h.

This is a formulation-level validation, not a full scheduling solve.
"""

from __future__ import annotations

import itertools
import csv
from pathlib import Path


def direct_squared_penalty(bits, target, lambda_target):
    human_count = sum(bits)
    return lambda_target * (human_count - target) ** 2


def expanded_qubo_penalty(bits, target, lambda_target):
    linear_sum = sum(bits)
    pair_sum = 0

    for i in range(len(bits)):
        for j in range(i + 1, len(bits)):
            pair_sum += bits[i] * bits[j]

    return lambda_target * (
        (1 - 2 * target) * linear_sum
        + 2 * pair_sum
        + target**2
    )


def main():
    num_operations = 6
    target = 2
    lambda_values = [0.5, 1.0, 2.0, 3.0]

    out_path = Path("results/tables/squared_target_penalty_qubo_toy_validation.csv")
    out_path.parent.mkdir(parents=True, exist_ok=True)

    rows = []
    max_abs_error = 0.0

    for lambda_target in lambda_values:
        for bits in itertools.product([0, 1], repeat=num_operations):
            direct = direct_squared_penalty(bits, target, lambda_target)
            expanded = expanded_qubo_penalty(bits, target, lambda_target)
            abs_error = abs(direct - expanded)
            max_abs_error = max(max_abs_error, abs_error)

            rows.append(
                {
                    "num_operations": num_operations,
                    "target": target,
                    "lambda_target": lambda_target,
                    "bitstring": "".join(str(b) for b in bits),
                    "human_count": sum(bits),
                    "direct_penalty": direct,
                    "expanded_qubo_penalty": expanded,
                    "abs_error": abs_error,
                }
            )

    with out_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    print("=== Squared target QUBO toy validation ===")
    print(f"num_operations = {num_operations}")
    print(f"target = {target}")
    print(f"lambda values = {lambda_values}")
    print(f"rows = {len(rows)}")
    print(f"max_abs_error = {max_abs_error}")
    print(f"saved = {out_path}")

    if max_abs_error < 1e-9:
        print("VALIDATION PASS")
    else:
        print("VALIDATION FAIL")


if __name__ == "__main__":
    main()
