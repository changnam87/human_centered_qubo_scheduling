"""
Streaming sparse QUBO export prototype for sample_4x4 scale.

Purpose
-------
Export a representative sample_4x4 time-indexed QUBO as sparse CSV rows without
building a full dense matrix or a monolithic in-memory QUBO dictionary.

The exported CSV has rows of the form:

    i, j, coefficient, term_group, op_i, resource_i, time_i, op_j, resource_j, time_j

QUBO convention:

    energy(x) = constant + sum_i Q[i,i] x_i + sum_{i<j} Q[i,j] x_i x_j

This script streams coefficient rows component by component:
1. linear_cost
2. assignment_penalty
3. human_target_penalty
4. resource_overlap_penalty
5. precedence_penalty

This is an export prototype. It does not solve the QUBO.
"""

from __future__ import annotations

import argparse
import csv
import json
import time
from pathlib import Path
from typing import Dict, List, Tuple


# -----------------------------
# sample_4x4 representative scale
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

DEFAULT_HUMAN_REWARD = 2.5
DEFAULT_TARGET_HUMAN_ASSIGNMENTS = 4
DEFAULT_LAMBDA_TARGET = 1.0
DEFAULT_ASSIGNMENT_PENALTY = 30.0
DEFAULT_RESOURCE_OVERLAP_PENALTY = 30.0
DEFAULT_PRECEDENCE_PENALTY = 30.0


def resource_type(r: int) -> str:
    if r in HUMAN_RESOURCES:
        return "human"
    if r in ROBOT_RESOURCES:
        return "robot"
    return "machine"


def operation_job_step(op: int) -> Tuple[int, int]:
    return op // OPS_PER_JOB, op % OPS_PER_JOB


def duration(op: int, r: int) -> int:
    """
    Representative deterministic duration model.

    This mirrors the feasibility-estimation script. It is not intended to encode
    every seed-specific augmented instance exactly.
    """

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


def build_valid_variables() -> List[Tuple[int, int, int]]:
    valid = []

    for op in range(NUM_OPERATIONS):
        for r in range(NUM_RESOURCES):
            d = duration(op, r)
            latest_start = HORIZON - d

            for t in range(latest_start + 1):
                valid.append((op, r, t))

    return valid


def var_name(op: int, r: int, t: int) -> str:
    return f"x_o{op}_r{r}_{resource_type(r)}_t{t}"


def canonical_pair(i: int, j: int) -> Tuple[int, int]:
    if i <= j:
        return i, j
    return j, i


class StreamingQuboWriter:
    def __init__(self, path: Path):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.file = self.path.open("w", newline="")
        self.fieldnames = [
            "i",
            "j",
            "coefficient",
            "term_group",
            "op_i",
            "resource_i",
            "time_i",
            "op_j",
            "resource_j",
            "time_j",
            "var_i",
            "var_j",
        ]
        self.writer = csv.DictWriter(self.file, fieldnames=self.fieldnames)
        self.writer.writeheader()
        self.counts: Dict[str, int] = {}

    def write_term(
        self,
        i: int,
        j: int,
        coefficient: float,
        term_group: str,
        idx_to_var: Dict[int, Tuple[int, int, int]],
    ) -> None:
        if abs(coefficient) <= 1e-12:
            return

        i, j = canonical_pair(i, j)
        op_i, r_i, t_i = idx_to_var[i]
        op_j, r_j, t_j = idx_to_var[j]

        self.writer.writerow(
            {
                "i": i,
                "j": j,
                "coefficient": coefficient,
                "term_group": term_group,
                "op_i": op_i,
                "resource_i": r_i,
                "time_i": t_i,
                "op_j": op_j,
                "resource_j": r_j,
                "time_j": t_j,
                "var_i": var_name(op_i, r_i, t_i),
                "var_j": var_name(op_j, r_j, t_j),
            }
        )

        self.counts[term_group] = self.counts.get(term_group, 0) + 1

    def close(self) -> None:
        self.file.close()


def main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument("--human-reward", type=float, default=DEFAULT_HUMAN_REWARD)
    parser.add_argument("--lambda-target", type=float, default=DEFAULT_LAMBDA_TARGET)
    parser.add_argument("--target-human-assignments", type=int, default=DEFAULT_TARGET_HUMAN_ASSIGNMENTS)
    parser.add_argument("--assignment-penalty", type=float, default=DEFAULT_ASSIGNMENT_PENALTY)
    parser.add_argument("--resource-overlap-penalty", type=float, default=DEFAULT_RESOURCE_OVERLAP_PENALTY)
    parser.add_argument("--precedence-penalty", type=float, default=DEFAULT_PRECEDENCE_PENALTY)

    parser.add_argument(
        "--out",
        type=str,
        default="results/tables/sample_4x4_sparse_qubo_coefficients_stream.csv",
    )

    parser.add_argument(
        "--summary-out",
        type=str,
        default="results/tables/sample_4x4_sparse_qubo_streaming_summary.json",
    )

    args = parser.parse_args()

    start_wall = time.time()

    valid_variables = build_valid_variables()
    var_to_idx = {key: idx for idx, key in enumerate(valid_variables)}
    idx_to_var = {idx: key for key, idx in var_to_idx.items()}
    num_variables = len(valid_variables)

    op_vars: Dict[int, List[int]] = {op: [] for op in range(NUM_OPERATIONS)}
    resource_vars: Dict[int, List[int]] = {r: [] for r in range(NUM_RESOURCES)}
    human_vars: List[int] = []

    for idx, (op, r, t) in idx_to_var.items():
        op_vars[op].append(idx)
        resource_vars[r].append(idx)
        if r in HUMAN_RESOURCES:
            human_vars.append(idx)

    out_path = Path(args.out)
    writer = StreamingQuboWriter(out_path)

    constant = 0.0

    # ------------------------------------------------------
    # 1. Linear cost terms
    # ------------------------------------------------------
    for idx, (op, r, t) in idx_to_var.items():
        coeff = (
            assignment_cost(op, r)
            + workload_cost(op, r)
            + ergonomic_cost(op, r)
            + start_time_weight(op) * t
        )

        if r in HUMAN_RESOURCES:
            coeff -= args.human_reward

        writer.write_term(
            idx,
            idx,
            coeff,
            "linear_cost_and_reward",
            idx_to_var,
        )

    # ------------------------------------------------------
    # 2. Squared target human-utilization penalty
    #
    # lambda * (human_count - target)^2
    # = lambda * [(1 - 2T) sum h_i + 2 sum_{i<j} h_i h_j + T^2]
    # ------------------------------------------------------
    constant += args.lambda_target * args.target_human_assignments**2

    human_linear_coeff = args.lambda_target * (1 - 2 * args.target_human_assignments)

    for i in human_vars:
        writer.write_term(
            i,
            i,
            human_linear_coeff,
            "human_target_penalty_linear",
            idx_to_var,
        )

    for a_pos in range(len(human_vars)):
        if a_pos % 500 == 0:
            print(f"human target pairs: {a_pos}/{len(human_vars)}")

        for b_pos in range(a_pos + 1, len(human_vars)):
            writer.write_term(
                human_vars[a_pos],
                human_vars[b_pos],
                2.0 * args.lambda_target,
                "human_target_penalty_quadratic",
                idx_to_var,
            )

    # ------------------------------------------------------
    # 3. One-start assignment penalty
    #
    # P * (sum x - 1)^2 = P * [-sum x + 2 sum pair + 1]
    # ------------------------------------------------------
    for op in range(NUM_OPERATIONS):
        print(f"assignment penalty op {op}/{NUM_OPERATIONS - 1}")

        vars_for_op = op_vars[op]
        constant += args.assignment_penalty

        for i in vars_for_op:
            writer.write_term(
                i,
                i,
                -args.assignment_penalty,
                "assignment_penalty_linear",
                idx_to_var,
            )

        for a_pos in range(len(vars_for_op)):
            for b_pos in range(a_pos + 1, len(vars_for_op)):
                writer.write_term(
                    vars_for_op[a_pos],
                    vars_for_op[b_pos],
                    2.0 * args.assignment_penalty,
                    "assignment_penalty_quadratic",
                    idx_to_var,
                )

    # ------------------------------------------------------
    # 4. Resource overlap penalty
    # ------------------------------------------------------
    for r in range(NUM_RESOURCES):
        print(f"resource overlap resource {r}/{NUM_RESOURCES - 1}")

        vars_for_resource = resource_vars[r]

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

                if start1 < finish2 and start2 < finish1:
                    writer.write_term(
                        i,
                        j,
                        args.resource_overlap_penalty,
                        "resource_overlap_penalty",
                        idx_to_var,
                    )

    # ------------------------------------------------------
    # 5. Precedence forbidden-pair penalties
    # ------------------------------------------------------
    precedence_arcs = []

    for job in range(NUM_JOBS):
        for step in range(OPS_PER_JOB - 1):
            pred = job * OPS_PER_JOB + step
            succ = job * OPS_PER_JOB + step + 1
            precedence_arcs.append((pred, succ))

    for arc_idx, (pred, succ) in enumerate(precedence_arcs):
        print(f"precedence arc {arc_idx + 1}/{len(precedence_arcs)}: {pred}->{succ}")

        pred_vars = op_vars[pred]
        succ_vars = op_vars[succ]

        for i in pred_vars:
            pred_op, pred_r, pred_t = idx_to_var[i]
            pred_finish = pred_t + duration(pred_op, pred_r)

            for j in succ_vars:
                succ_op, succ_r, succ_t = idx_to_var[j]

                if succ_t < pred_finish:
                    writer.write_term(
                        i,
                        j,
                        args.precedence_penalty,
                        "precedence_penalty",
                        idx_to_var,
                    )

    writer.close()

    elapsed = time.time() - start_wall
    total_rows = sum(writer.counts.values())

    summary = {
        "experiment": "sample_4x4_sparse_qubo_streaming_export",
        "jobs": NUM_JOBS,
        "ops_per_job": OPS_PER_JOB,
        "operations": NUM_OPERATIONS,
        "machines": NUM_MACHINES,
        "workers": NUM_WORKERS,
        "robots": NUM_ROBOTS,
        "resources": NUM_RESOURCES,
        "horizon": HORIZON,
        "num_variables": num_variables,
        "nominal_full_grid_variables": NUM_OPERATIONS * NUM_RESOURCES * HORIZON,
        "num_human_variables": len(human_vars),
        "human_reward": args.human_reward,
        "lambda_target": args.lambda_target,
        "target_human_assignments": args.target_human_assignments,
        "assignment_penalty": args.assignment_penalty,
        "resource_overlap_penalty": args.resource_overlap_penalty,
        "precedence_penalty": args.precedence_penalty,
        "constant": constant,
        "term_group_counts": writer.counts,
        "total_streamed_rows": total_rows,
        "elapsed_seconds": elapsed,
        "output_csv": str(out_path),
        "note": "Streaming sparse coefficient export; duplicate coefficients are not merged.",
    }

    summary_path = Path(args.summary_out)
    summary_path.parent.mkdir(parents=True, exist_ok=True)

    with summary_path.open("w") as f:
        json.dump(summary, f, indent=2)

    print("=== sample_4x4 streaming sparse QUBO export complete ===")
    print(f"num_variables = {num_variables}")
    print(f"num_human_variables = {len(human_vars)}")
    print(f"constant = {constant}")
    print(f"total_streamed_rows = {total_rows}")
    print(f"elapsed_seconds = {elapsed:.2f}")
    print("term_group_counts:")
    for key, value in writer.counts.items():
        print(f"  {key}: {value}")
    print(f"saved coefficients = {out_path}")
    print(f"saved summary = {summary_path}")


if __name__ == "__main__":
    main()
