"""
Estimate QUBO coefficient export feasibility for sample_4x4 scale.

Purpose
-------
This script estimates the size of a sparse time-indexed QUBO for the sample_4x4
prototype scale:

    operations = 16
    resources = 9
    horizon = 63

The goal is not to solve the QUBO. The goal is to estimate whether coefficient
export is feasible and which terms dominate QUBO size.

QUBO components considered:
1. Linear cost terms
2. One-start assignment penalties
3. Squared target human-utilization penalty
4. Resource overlap penalties
5. Job precedence forbidden-pair penalties

This is a feasibility/scaling study before full sample_4x4 coefficient export.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Dict, List, Tuple


# -----------------------------
# sample_4x4 scale
# -----------------------------

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

TARGET_HUMAN_ASSIGNMENTS = 4


def resource_type(r: int) -> str:
    if r in HUMAN_RESOURCES:
        return "human"
    if r in ROBOT_RESOURCES:
        return "robot"
    return "machine"


def operation_job_step(op: int) -> Tuple[int, int]:
    job = op // OPS_PER_JOB
    step = op % OPS_PER_JOB
    return job, step


def duration(op: int, r: int) -> int:
    """
    Deterministic representative duration model for size estimation.

    This does not need to exactly match every previous augmentation seed.
    It is used to estimate valid start counts and overlap/precedence term scale.
    """

    job, step = operation_job_step(op)
    base = 2 + ((job + step) % 3)

    if resource_type(r) == "machine":
        return base
    if resource_type(r) == "robot":
        return base + 1
    return base + 1


def build_valid_variables() -> List[Tuple[int, int, int]]:
    valid = []

    for op in range(NUM_OPERATIONS):
        for r in range(NUM_RESOURCES):
            d = duration(op, r)
            latest_start = HORIZON - d

            for t in range(latest_start + 1):
                valid.append((op, r, t))

    return valid


def main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--export-sample-coefficients",
        action="store_true",
        help="Export a small sample of representative coefficient rows.",
    )

    parser.add_argument(
        "--sample-coeff-limit",
        type=int,
        default=20000,
        help="Maximum number of sample coefficient rows to write.",
    )

    parser.add_argument(
        "--out-summary",
        type=str,
        default="results/tables/sample_4x4_qubo_export_feasibility_summary.json",
    )

    parser.add_argument(
        "--out-table",
        type=str,
        default="results/tables/sample_4x4_qubo_export_feasibility_terms.csv",
    )

    parser.add_argument(
        "--out-sample-coeffs",
        type=str,
        default="results/tables/sample_4x4_qubo_export_sample_coefficients.csv",
    )

    args = parser.parse_args()

    valid_variables = build_valid_variables()
    var_to_idx = {key: idx for idx, key in enumerate(valid_variables)}
    idx_to_var = {idx: key for key, idx in var_to_idx.items()}

    num_variables = len(valid_variables)

    # Variables grouped by operation, resource, human assignment.
    op_vars: Dict[int, List[int]] = {op: [] for op in range(NUM_OPERATIONS)}
    resource_vars: Dict[int, List[int]] = {r: [] for r in range(NUM_RESOURCES)}
    human_vars: List[int] = []

    for idx, (op, r, t) in idx_to_var.items():
        op_vars[op].append(idx)
        resource_vars[r].append(idx)

        if r in HUMAN_RESOURCES:
            human_vars.append(idx)

    # -----------------------------
    # Term count estimates
    # -----------------------------

    linear_terms = num_variables

    # One-start assignment penalty:
    # For each operation, all pairwise combinations among that operation's variables.
    assignment_quadratic_terms = 0
    assignment_terms_by_operation = {}

    for op, vars_for_op in op_vars.items():
        n = len(vars_for_op)
        q = n * (n - 1) // 2
        assignment_terms_by_operation[op] = q
        assignment_quadratic_terms += q

    # Squared target human utilization:
    # All pairwise combinations among human variables.
    num_human_vars = len(human_vars)
    human_target_quadratic_terms = num_human_vars * (num_human_vars - 1) // 2

    # Resource overlap terms:
    # Pair variables on same resource, different operations, overlapping intervals.
    resource_overlap_terms = 0
    resource_overlap_terms_by_resource = {}

    for r in range(NUM_RESOURCES):
        vars_for_resource = resource_vars[r]
        count = 0

        for a_pos in range(len(vars_for_resource)):
            i = vars_for_resource[a_pos]
            op1, r1, t1 = idx_to_var[i]
            d1 = duration(op1, r1)
            start1 = t1
            finish1 = t1 + d1

            for b_pos in range(a_pos + 1, len(vars_for_resource)):
                j = vars_for_resource[b_pos]
                op2, r2, t2 = idx_to_var[j]

                if op1 == op2:
                    continue

                d2 = duration(op2, r2)
                start2 = t2
                finish2 = t2 + d2

                overlap = start1 < finish2 and start2 < finish1

                if overlap:
                    count += 1

        resource_overlap_terms_by_resource[r] = count
        resource_overlap_terms += count

    # Precedence terms:
    # For each job: op k -> op k+1.
    precedence_arcs = []

    for job in range(NUM_JOBS):
        for step in range(OPS_PER_JOB - 1):
            pred = job * OPS_PER_JOB + step
            succ = job * OPS_PER_JOB + step + 1
            precedence_arcs.append((pred, succ))

    precedence_terms = 0
    precedence_terms_by_arc = {}

    for pred, succ in precedence_arcs:
        pred_vars = op_vars[pred]
        succ_vars = op_vars[succ]
        count = 0

        for i in pred_vars:
            pred_op, pred_r, pred_t = idx_to_var[i]
            pred_finish = pred_t + duration(pred_op, pred_r)

            for j in succ_vars:
                succ_op, succ_r, succ_t = idx_to_var[j]

                if succ_t < pred_finish:
                    count += 1

        precedence_terms_by_arc[f"{pred}->{succ}"] = count
        precedence_terms += count

    # Approximate total sparse terms before merging duplicates.
    # Some terms may overlap across components and merge in actual QUBO.
    estimated_sparse_terms_before_merge = (
        linear_terms
        + assignment_quadratic_terms
        + human_target_quadratic_terms
        + resource_overlap_terms
        + precedence_terms
    )

    # Conservative memory estimate:
    # Assume CSV row ~80-150 bytes compressed? Python dict entry much bigger.
    # Use rough sparse in-memory estimate 100 bytes/key-value as lower-ish estimate,
    # 200 bytes/key-value as safer estimate.
    memory_estimate_100_bytes_mb = estimated_sparse_terms_before_merge * 100 / (1024**2)
    memory_estimate_200_bytes_mb = estimated_sparse_terms_before_merge * 200 / (1024**2)

    rows = [
        {
            "term_group": "linear_terms",
            "count": linear_terms,
            "description": "One linear term per valid x[operation, resource, start_time] variable.",
        },
        {
            "term_group": "assignment_quadratic_terms",
            "count": assignment_quadratic_terms,
            "description": "Pairwise terms from one-start-per-operation penalties.",
        },
        {
            "term_group": "human_target_quadratic_terms",
            "count": human_target_quadratic_terms,
            "description": "Pairwise terms from squared target human-utilization penalty.",
        },
        {
            "term_group": "resource_overlap_terms",
            "count": resource_overlap_terms,
            "description": "Forbidden pair terms for overlapping use of the same resource.",
        },
        {
            "term_group": "precedence_terms",
            "count": precedence_terms,
            "description": "Forbidden pair terms for job precedence violations.",
        },
        {
            "term_group": "estimated_sparse_terms_before_merge",
            "count": estimated_sparse_terms_before_merge,
            "description": "Approximate sparse term count before duplicate coefficient merging.",
        },
    ]

    out_table = Path(args.out_table)
    out_table.parent.mkdir(parents=True, exist_ok=True)

    with out_table.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["term_group", "count", "description"])
        writer.writeheader()
        writer.writerows(rows)

    summary = {
        "experiment": "sample_4x4_qubo_export_feasibility",
        "jobs": NUM_JOBS,
        "ops_per_job": OPS_PER_JOB,
        "operations": NUM_OPERATIONS,
        "machines": NUM_MACHINES,
        "workers": NUM_WORKERS,
        "robots": NUM_ROBOTS,
        "resources": NUM_RESOURCES,
        "horizon": HORIZON,
        "target_human_assignments": TARGET_HUMAN_ASSIGNMENTS,
        "num_variables_representative_valid_starts": num_variables,
        "nominal_variables_if_full_grid": NUM_OPERATIONS * NUM_RESOURCES * HORIZON,
        "num_human_variables": num_human_vars,
        "linear_terms": linear_terms,
        "assignment_quadratic_terms": assignment_quadratic_terms,
        "human_target_quadratic_terms": human_target_quadratic_terms,
        "resource_overlap_terms": resource_overlap_terms,
        "precedence_terms": precedence_terms,
        "estimated_sparse_terms_before_merge": estimated_sparse_terms_before_merge,
        "memory_estimate_100_bytes_mb": memory_estimate_100_bytes_mb,
        "memory_estimate_200_bytes_mb": memory_estimate_200_bytes_mb,
        "precedence_arcs": precedence_arcs,
        "assignment_terms_by_operation": assignment_terms_by_operation,
        "resource_overlap_terms_by_resource": resource_overlap_terms_by_resource,
        "precedence_terms_by_arc": precedence_terms_by_arc,
        "note": "Representative size estimate; exact term count may vary by seed-specific durations and coefficient merging.",
    }

    out_summary = Path(args.out_summary)
    out_summary.parent.mkdir(parents=True, exist_ok=True)

    with out_summary.open("w") as f:
        json.dump(summary, f, indent=2)

    # Optional sample coefficient rows for structure inspection, not full QUBO.
    if args.export_sample_coefficients:
        out_sample = Path(args.out_sample_coeffs)
        out_sample.parent.mkdir(parents=True, exist_ok=True)

        written = 0

        with out_sample.open("w", newline="") as f:
            fieldnames = [
                "i",
                "j",
                "term_group",
                "op_i",
                "resource_i",
                "time_i",
                "op_j",
                "resource_j",
                "time_j",
                "note",
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

            # sample linear terms
            for i in range(min(num_variables, args.sample_coeff_limit)):
                op, r, t = idx_to_var[i]
                writer.writerow(
                    {
                        "i": i,
                        "j": i,
                        "term_group": "linear",
                        "op_i": op,
                        "resource_i": r,
                        "time_i": t,
                        "op_j": op,
                        "resource_j": r,
                        "time_j": t,
                        "note": "sample linear variable",
                    }
                )
                written += 1
                if written >= args.sample_coeff_limit:
                    break

            # sample assignment pairs
            if written < args.sample_coeff_limit:
                for op, vars_for_op in op_vars.items():
                    for a_pos in range(len(vars_for_op)):
                        for b_pos in range(a_pos + 1, len(vars_for_op)):
                            i = vars_for_op[a_pos]
                            j = vars_for_op[b_pos]
                            op_i, r_i, t_i = idx_to_var[i]
                            op_j, r_j, t_j = idx_to_var[j]

                            writer.writerow(
                                {
                                    "i": i,
                                    "j": j,
                                    "term_group": "assignment_pair",
                                    "op_i": op_i,
                                    "resource_i": r_i,
                                    "time_i": t_i,
                                    "op_j": op_j,
                                    "resource_j": r_j,
                                    "time_j": t_j,
                                    "note": "sample one-start penalty pair",
                                }
                            )
                            written += 1

                            if written >= args.sample_coeff_limit:
                                break
                        if written >= args.sample_coeff_limit:
                            break
                    if written >= args.sample_coeff_limit:
                        break

        summary["sample_coefficients_csv"] = str(out_sample)
        summary["sample_coefficients_rows"] = written

        with out_summary.open("w") as f:
            json.dump(summary, f, indent=2)

    print("=== sample_4x4 QUBO export feasibility estimate ===")
    print(f"representative valid-start variables = {num_variables}")
    print(f"nominal full-grid variables = {NUM_OPERATIONS * NUM_RESOURCES * HORIZON}")
    print(f"human variables = {num_human_vars}")
    print(f"linear terms = {linear_terms}")
    print(f"assignment quadratic terms = {assignment_quadratic_terms}")
    print(f"human target quadratic terms = {human_target_quadratic_terms}")
    print(f"resource overlap terms = {resource_overlap_terms}")
    print(f"precedence terms = {precedence_terms}")
    print(f"estimated sparse terms before merge = {estimated_sparse_terms_before_merge}")
    print(f"memory estimate @100 bytes/term = {memory_estimate_100_bytes_mb:.2f} MB")
    print(f"memory estimate @200 bytes/term = {memory_estimate_200_bytes_mb:.2f} MB")
    print(f"saved summary = {out_summary}")
    print(f"saved term table = {out_table}")

    if args.export_sample_coefficients:
        print(f"saved sample coefficients = {args.out_sample_coeffs}")


if __name__ == "__main__":
    main()
