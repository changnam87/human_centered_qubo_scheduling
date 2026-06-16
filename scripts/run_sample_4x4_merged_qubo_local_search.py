"""
Prototype local search on merged sample_4x4 sparse QUBO.

This script loads the merged QUBO coefficient CSV and performs a simple
operation-level local search.

It is a prototype feasibility test, not a proof of optimality.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import random
import time
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd


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


def build_valid_variables() -> List[Tuple[int, int, int]]:
    valid = []

    for op in range(NUM_OPERATIONS):
        for r in range(NUM_RESOURCES):
            latest_start = HORIZON - duration(op, r)
            for t in range(latest_start + 1):
                valid.append((op, r, t))

    return valid


def build_op_vars(idx_to_var: Dict[int, Tuple[int, int, int]]) -> Dict[int, List[int]]:
    op_vars = {op: [] for op in range(NUM_OPERATIONS)}

    for idx, (op, r, t) in idx_to_var.items():
        op_vars[op].append(idx)

    return op_vars


def precedence_arcs() -> List[Tuple[int, int]]:
    arcs = []

    for job in range(NUM_JOBS):
        for step in range(OPS_PER_JOB - 1):
            pred = job * OPS_PER_JOB + step
            succ = job * OPS_PER_JOB + step + 1
            arcs.append((pred, succ))

    return arcs


def load_merged_qubo_as_adjacency(
    merged_csv: Path,
    num_variables: int,
    chunksize: int,
):
    """
    Load merged upper-triangular QUBO into:
      diag[i]
      adjacency[i] = list of (j, coeff) for i != j

    This is simpler than CSR and easier to debug.
    """

    diag = np.zeros(num_variables, dtype=np.float64)
    adjacency: List[List[Tuple[int, float]]] = [[] for _ in range(num_variables)]

    total_rows = 0
    linear_rows = 0
    quadratic_rows = 0

    print("=== Loading merged QUBO ===")
    print(f"Input: {merged_csv}")

    for chunk_id, chunk in enumerate(pd.read_csv(merged_csv, chunksize=chunksize)):
        if chunk_id % 5 == 0:
            print(f"chunk={chunk_id}, rows_read={total_rows}")

        total_rows += len(chunk)

        for row in chunk.itertuples(index=False):
            i = int(row.i)
            j = int(row.j)
            c = float(row.coefficient)

            if i == j:
                diag[i] += c
                linear_rows += 1
            else:
                adjacency[i].append((j, c))
                adjacency[j].append((i, c))
                quadratic_rows += 1

    print("=== Loaded merged QUBO ===")
    print(f"total_rows = {total_rows}")
    print(f"linear_rows = {linear_rows}")
    print(f"quadratic_rows = {quadratic_rows}")

    return diag, adjacency, total_rows, linear_rows, quadratic_rows


def qubo_energy(
    x: np.ndarray,
    constant: float,
    diag: np.ndarray,
    adjacency: List[List[Tuple[int, float]]],
) -> float:
    energy = constant + float(np.dot(diag, x))

    interaction = 0.0

    active = np.nonzero(x)[0]

    for i in active:
        for j, c in adjacency[int(i)]:
            if x[j] == 1:
                interaction += c

    energy += 0.5 * interaction
    return energy


def delta_flip(
    k: int,
    x: np.ndarray,
    diag: np.ndarray,
    adjacency: List[List[Tuple[int, float]]],
) -> float:
    """
    Delta for flipping x[k].
    """

    sign = 1.0 - 2.0 * float(x[k])
    interaction = 0.0

    for j, c in adjacency[k]:
        if x[j] == 1:
            interaction += c

    return sign * (float(diag[k]) + interaction)


def make_greedy_feasible(
    num_variables: int,
    var_to_idx: Dict[Tuple[int, int, int], int],
) -> Tuple[np.ndarray, Dict[int, int]]:
    x = np.zeros(num_variables, dtype=np.int8)
    selected_by_op: Dict[int, int] = {}

    job_offsets = {
        0: 0,
        1: 10,
        2: 20,
        3: 30,
    }

    for job in range(NUM_JOBS):
        current_time = job_offsets[job]

        for step in range(OPS_PER_JOB):
            op = job * OPS_PER_JOB + step
            chosen = None
            resource_order = MACHINE_RESOURCES + ROBOT_RESOURCES + HUMAN_RESOURCES

            for r in resource_order:
                for t in range(current_time, HORIZON):
                    key = (op, r, t)
                    if key not in var_to_idx:
                        continue

                    finish = t + duration(op, r)
                    if finish <= HORIZON:
                        chosen = key
                        break

                if chosen is not None:
                    break

            if chosen is None:
                raise RuntimeError(f"Could not construct greedy assignment for op {op}")

            idx = var_to_idx[chosen]
            x[idx] = 1
            selected_by_op[op] = idx
            current_time = chosen[2] + duration(chosen[0], chosen[1])

    return x, selected_by_op


def make_random_one_start(
    rng: random.Random,
    num_variables: int,
    op_vars: Dict[int, List[int]],
) -> Tuple[np.ndarray, Dict[int, int]]:
    x = np.zeros(num_variables, dtype=np.int8)
    selected_by_op: Dict[int, int] = {}

    for op in range(NUM_OPERATIONS):
        idx = rng.choice(op_vars[op])
        x[idx] = 1
        selected_by_op[op] = idx

    return x, selected_by_op


def human_count_from_x(
    x: np.ndarray,
    idx_to_var: Dict[int, Tuple[int, int, int]],
) -> int:
    count = 0

    for idx in np.nonzero(x)[0]:
        op, r, t = idx_to_var[int(idx)]
        if r in HUMAN_RESOURCES:
            count += 1

    return count


def assignment_violation_count(
    x: np.ndarray,
    op_vars: Dict[int, List[int]],
) -> int:
    violations = 0

    for op, vars_for_op in op_vars.items():
        count = int(x[vars_for_op].sum())
        if count != 1:
            violations += abs(count - 1)

    return violations


def overlap_violation_count(
    x: np.ndarray,
    idx_to_var: Dict[int, Tuple[int, int, int]],
) -> int:
    selected = [int(i) for i in np.nonzero(x)[0]]
    violations = 0

    for a in range(len(selected)):
        i = selected[a]
        op1, r1, t1 = idx_to_var[i]
        start1 = t1
        finish1 = t1 + duration(op1, r1)

        for b in range(a + 1, len(selected)):
            j = selected[b]
            op2, r2, t2 = idx_to_var[j]

            if op1 == op2 or r1 != r2:
                continue

            start2 = t2
            finish2 = t2 + duration(op2, r2)

            if start1 < finish2 and start2 < finish1:
                violations += 1

    return violations


def precedence_violation_count(
    x: np.ndarray,
    idx_to_var: Dict[int, Tuple[int, int, int]],
) -> int:
    selected_by_op = {op: [] for op in range(NUM_OPERATIONS)}

    for idx in np.nonzero(x)[0]:
        op, r, t = idx_to_var[int(idx)]
        selected_by_op[op].append((op, r, t))

    violations = 0

    for pred, succ in precedence_arcs():
        for pred_op, pred_r, pred_t in selected_by_op[pred]:
            pred_finish = pred_t + duration(pred_op, pred_r)

            for succ_op, succ_r, succ_t in selected_by_op[succ]:
                if succ_t < pred_finish:
                    violations += 1

    return violations


def decode_solution(
    x: np.ndarray,
    idx_to_var: Dict[int, Tuple[int, int, int]],
) -> List[Dict[str, object]]:
    rows = []

    for idx in np.nonzero(x)[0]:
        idx = int(idx)
        op, r, t = idx_to_var[idx]

        rows.append(
            {
                "operation": op,
                "job": op // OPS_PER_JOB,
                "step": op % OPS_PER_JOB,
                "resource": r,
                "resource_type": resource_type(r),
                "start_time": t,
                "duration": duration(op, r),
                "finish_time": t + duration(op, r),
                "variable_index": idx,
            }
        )

    rows.sort(key=lambda row: (row["job"], row["step"]))
    return rows


def run_local_search(
    rng: random.Random,
    x: np.ndarray,
    selected_by_op: Dict[int, int],
    current_energy: float,
    op_vars: Dict[int, List[int]],
    diag: np.ndarray,
    adjacency: List[List[Tuple[int, float]]],
    iterations: int,
    initial_temperature: float,
    final_temperature: float,
):
    best_x = x.copy()
    best_energy = current_energy
    accepted_moves = 0

    for it in range(iterations):
        op = rng.randrange(NUM_OPERATIONS)
        old_idx = selected_by_op[op]
        new_idx = rng.choice(op_vars[op])

        if new_idx == old_idx:
            continue

        if iterations > 1:
            frac = it / (iterations - 1)
        else:
            frac = 1.0

        temperature = initial_temperature * (
            (final_temperature / initial_temperature) ** frac
        )

        # Exact sequential two-flip delta.
        d1 = delta_flip(old_idx, x, diag, adjacency)
        x[old_idx] = 0

        d2 = delta_flip(new_idx, x, diag, adjacency)
        x[new_idx] = 1

        proposed_energy = current_energy + d1 + d2
        delta = proposed_energy - current_energy

        accept = False

        if delta <= 0:
            accept = True
        elif temperature > 0:
            if rng.random() < math.exp(-delta / temperature):
                accept = True

        if accept:
            current_energy = proposed_energy
            selected_by_op[op] = new_idx
            accepted_moves += 1

            if current_energy < best_energy:
                best_energy = current_energy
                best_x = x.copy()
        else:
            x[new_idx] = 0
            x[old_idx] = 1

    return best_x, best_energy, current_energy, accepted_moves


def main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--merged-csv",
        type=str,
        default="results/tables/sample_4x4_sparse_qubo_coefficients_merged.csv",
    )
    parser.add_argument(
        "--solver-ready-metadata",
        type=str,
        default="results/tables/sample_4x4_sparse_qubo_solver_ready_metadata.json",
    )

    parser.add_argument("--chunksize", type=int, default=500000)
    parser.add_argument("--restarts", type=int, default=3)
    parser.add_argument("--iterations", type=int, default=500)
    parser.add_argument("--seed", type=int, default=123)
    parser.add_argument("--initial-temperature", type=float, default=10.0)
    parser.add_argument("--final-temperature", type=float, default=0.01)

    parser.add_argument(
        "--runs-out",
        type=str,
        default="results/tables/sample_4x4_merged_qubo_local_search_runs.csv",
    )
    parser.add_argument(
        "--best-solution-out",
        type=str,
        default="results/tables/sample_4x4_merged_qubo_local_search_best_solution.csv",
    )
    parser.add_argument(
        "--summary-out",
        type=str,
        default="results/tables/sample_4x4_merged_qubo_local_search_summary.json",
    )

    args = parser.parse_args()

    merged_csv = Path(args.merged_csv)
    if not merged_csv.exists():
        raise FileNotFoundError(f"Merged QUBO CSV not found: {merged_csv}")

    metadata = json.loads(Path(args.solver_ready_metadata).read_text())
    constant = float(metadata["constant_offset"])

    valid_variables = build_valid_variables()
    var_to_idx = {key: idx for idx, key in enumerate(valid_variables)}
    idx_to_var = {idx: key for key, idx in var_to_idx.items()}
    op_vars = build_op_vars(idx_to_var)
    num_variables = len(valid_variables)

    rng = random.Random(args.seed)

    load_start = time.time()
    diag, adjacency, total_rows, linear_rows, quadratic_rows = load_merged_qubo_as_adjacency(
        merged_csv=merged_csv,
        num_variables=num_variables,
        chunksize=args.chunksize,
    )
    load_seconds = time.time() - load_start

    run_rows = []

    global_best_x = None
    global_best_energy = None
    global_best_run = None

    print("=== Starting local search ===")

    for restart in range(args.restarts):
        if restart == 0:
            init_type = "greedy_feasible"
            x, selected_by_op = make_greedy_feasible(num_variables, var_to_idx)
        else:
            init_type = "random_one_start"
            x, selected_by_op = make_random_one_start(rng, num_variables, op_vars)

        initial_energy = qubo_energy(x, constant, diag, adjacency)

        run_start = time.time()
        best_x, best_energy, final_energy, accepted_moves = run_local_search(
            rng=rng,
            x=x,
            selected_by_op=selected_by_op,
            current_energy=initial_energy,
            op_vars=op_vars,
            diag=diag,
            adjacency=adjacency,
            iterations=args.iterations,
            initial_temperature=args.initial_temperature,
            final_temperature=args.final_temperature,
        )
        run_seconds = time.time() - run_start

        h_count = human_count_from_x(best_x, idx_to_var)
        assign_viol = assignment_violation_count(best_x, op_vars)
        overlap_viol = overlap_violation_count(best_x, idx_to_var)
        precedence_viol = precedence_violation_count(best_x, idx_to_var)

        feasible = assign_viol == 0 and overlap_viol == 0 and precedence_viol == 0

        row = {
            "restart": restart,
            "init_type": init_type,
            "initial_energy": initial_energy,
            "best_energy": best_energy,
            "final_energy": final_energy,
            "energy_improvement": initial_energy - best_energy,
            "accepted_moves": accepted_moves,
            "run_seconds": run_seconds,
            "human_count": h_count,
            "assignment_violations": assign_viol,
            "overlap_violations": overlap_viol,
            "precedence_violations": precedence_viol,
            "feasible": feasible,
        }

        run_rows.append(row)

        print(
            f"restart={restart} init={init_type} "
            f"initial={initial_energy:.2f} best={best_energy:.2f} "
            f"improve={initial_energy - best_energy:.2f} "
            f"humans={h_count} feasible={feasible} accepted={accepted_moves}"
        )

        if global_best_energy is None or best_energy < global_best_energy:
            global_best_energy = best_energy
            global_best_x = best_x.copy()
            global_best_run = restart

    runs_out = Path(args.runs_out)
    runs_out.parent.mkdir(parents=True, exist_ok=True)

    with runs_out.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(run_rows[0].keys()))
        writer.writeheader()
        writer.writerows(run_rows)

    best_solution_rows = decode_solution(global_best_x, idx_to_var)

    best_solution_out = Path(args.best_solution_out)
    best_solution_out.parent.mkdir(parents=True, exist_ok=True)

    with best_solution_out.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(best_solution_rows[0].keys()))
        writer.writeheader()
        writer.writerows(best_solution_rows)

    feasible_runs = sum(1 for row in run_rows if row["feasible"])

    summary = {
        "experiment": "sample_4x4_merged_qubo_local_search",
        "merged_csv": str(merged_csv),
        "num_variables": num_variables,
        "constant_offset": constant,
        "total_merged_rows": total_rows,
        "linear_rows": linear_rows,
        "quadratic_rows": quadratic_rows,
        "restarts": args.restarts,
        "iterations": args.iterations,
        "seed": args.seed,
        "initial_temperature": args.initial_temperature,
        "final_temperature": args.final_temperature,
        "load_seconds": load_seconds,
        "best_energy": global_best_energy,
        "best_run": global_best_run,
        "feasible_runs": feasible_runs,
        "feasible_rate": feasible_runs / len(run_rows),
        "runs_csv": str(runs_out),
        "best_solution_csv": str(best_solution_out),
        "note": "Prototype local heuristic search; not a proof of optimality.",
    }

    summary_out = Path(args.summary_out)
    summary_out.parent.mkdir(parents=True, exist_ok=True)
    summary_out.write_text(json.dumps(summary, indent=2))

    print("=== Local search complete ===")
    print(f"best_energy = {global_best_energy}")
    print(f"best_run = {global_best_run}")
    print(f"feasible_runs = {feasible_runs}/{len(run_rows)}")
    print(f"load_seconds = {load_seconds:.2f}")
    print(f"saved runs = {runs_out}")
    print(f"saved best solution = {best_solution_out}")
    print(f"saved summary = {summary_out}")


if __name__ == "__main__":
    main()
