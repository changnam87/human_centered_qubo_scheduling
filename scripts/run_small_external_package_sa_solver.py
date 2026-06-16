"""Minimal simulated annealing solver for the small external QUBO package.

This script reads exports/small_time_indexed_solver_package/qubo_coefficients.csv
and runs a simple bit-flip simulated annealing solver.

The brute-force optimum from the smoke test is known:
    best_qubo_energy = 5.30
    best_bitstring = 100000000000100

This script checks whether a lightweight heuristic solver can recover or approach
the brute-force optimum on the small package.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import random
from pathlib import Path

import pandas as pd

BRUTE_FORCE_OPTIMUM = 5.30
BRUTE_FORCE_BITSTRING = "100000000000100"

def load_qubo(package_dir: Path):
    metadata = json.loads((package_dir / "package_metadata.json").read_text())
    num_variables = int(metadata["num_variables"])
    constant = float(metadata["constant_offset"])
    df = pd.read_csv(package_dir / "qubo_coefficients.csv")
    coeffs = []
    adjacency = {i: [] for i in range(num_variables)}
    diag = [0.0 for _ in range(num_variables)]
    for row in df.itertuples(index=False):
        i = int(row.i)
        j = int(row.j)
        q = float(row.coefficient)
        coeffs.append((i, j, q))
        if i == j:
            diag[i] += q
        else:
            adjacency[i].append((j, q))
            adjacency[j].append((i, q))
    return num_variables, constant, coeffs, diag, adjacency, metadata

def energy(bits, constant, coeffs):
    e = constant
    for i, j, q in coeffs:
        e += q * bits[i] * bits[j]
    return e

def delta_flip(k, bits, diag, adjacency):
    sign = 1.0 - 2.0 * bits[k]
    interaction = 0.0
    for j, q in adjacency[k]:
        interaction += q * bits[j]
    return sign * (diag[k] + interaction)

def random_bits(rng, n):
    return [rng.randint(0, 1) for _ in range(n)]

def bitstring(bits):
    return "".join(str(int(b)) for b in bits)

def run_sa(rng, num_variables, constant, coeffs, diag, adjacency, iterations, initial_temperature, final_temperature):
    bits = random_bits(rng, num_variables)
    current_energy = energy(bits, constant, coeffs)
    best_bits = list(bits)
    best_energy = current_energy
    accepted = 0

    for it in range(iterations):
        if iterations > 1:
            frac = it / (iterations - 1)
        else:
            frac = 1.0
        temperature = initial_temperature * ((final_temperature / initial_temperature) ** frac)

        k = rng.randrange(num_variables)
        d = delta_flip(k, bits, diag, adjacency)

        accept = False
        if d <= 0:
            accept = True
        elif temperature > 0:
            if rng.random() < math.exp(-d / temperature):
                accept = True

        if accept:
            bits[k] = 1 - bits[k]
            current_energy += d
            accepted += 1
            if current_energy < best_energy:
                best_energy = current_energy
                best_bits = list(bits)

    exact_best_energy = energy(best_bits, constant, coeffs)
    return {
        "best_energy": exact_best_energy,
        "best_bitstring": bitstring(best_bits),
        "final_energy": current_energy,
        "accepted_moves": accepted,
    }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--package-dir", type=str, default="exports/small_time_indexed_solver_package")
    parser.add_argument("--restarts", type=int, default=100)
    parser.add_argument("--iterations", type=int, default=2000)
    parser.add_argument("--initial-temperature", type=float, default=10.0)
    parser.add_argument("--final-temperature", type=float, default=0.001)
    parser.add_argument("--seed", type=int, default=123)
    parser.add_argument("--runs-out", type=str, default="results/tables/small_external_package_sa_solver_runs.csv")
    parser.add_argument("--summary-out", type=str, default="results/tables/small_external_package_sa_solver_summary.json")
    args = parser.parse_args()

    package_dir = Path(args.package_dir)
    num_variables, constant, coeffs, diag, adjacency, metadata = load_qubo(package_dir)
    rng = random.Random(args.seed)

    rows = []
    global_best = None

    for restart in range(args.restarts):
        result = run_sa(
            rng=rng,
            num_variables=num_variables,
            constant=constant,
            coeffs=coeffs,
            diag=diag,
            adjacency=adjacency,
            iterations=args.iterations,
            initial_temperature=args.initial_temperature,
            final_temperature=args.final_temperature,
        )
        result["restart"] = restart
        result["gap_to_bruteforce"] = result["best_energy"] - BRUTE_FORCE_OPTIMUM
        result["matches_bruteforce_energy"] = abs(result["best_energy"] - BRUTE_FORCE_OPTIMUM) < 1e-9
        result["matches_bruteforce_bitstring"] = result["best_bitstring"] == BRUTE_FORCE_BITSTRING
        rows.append(result)
        if global_best is None or result["best_energy"] < global_best["best_energy"]:
            global_best = dict(result)

    success_count = sum(1 for row in rows if row["matches_bruteforce_energy"])
    success_rate = success_count / len(rows)

    runs_out = Path(args.runs_out)
    runs_out.parent.mkdir(parents=True, exist_ok=True)
    with runs_out.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    summary = {
        "experiment": "small_external_package_sa_solver",
        "package_dir": str(package_dir),
        "num_variables": num_variables,
        "restarts": args.restarts,
        "iterations": args.iterations,
        "initial_temperature": args.initial_temperature,
        "final_temperature": args.final_temperature,
        "seed": args.seed,
        "brute_force_optimum": BRUTE_FORCE_OPTIMUM,
        "brute_force_bitstring": BRUTE_FORCE_BITSTRING,
        "best_energy": global_best["best_energy"],
        "best_bitstring": global_best["best_bitstring"],
        "best_gap_to_bruteforce": global_best["gap_to_bruteforce"],
        "success_count": success_count,
        "success_rate": success_rate,
        "validation_status": "PASS" if abs(global_best["best_energy"] - BRUTE_FORCE_OPTIMUM) < 1e-9 else "FAIL",
        "runs_csv": str(runs_out),
        "note": "Minimal simulated annealing solver smoke test on small external package.",
    }

    summary_out = Path(args.summary_out)
    summary_out.parent.mkdir(parents=True, exist_ok=True)
    summary_out.write_text(json.dumps(summary, indent=2))

    print("=== small external package SA solver complete ===")
    print("num_variables =", num_variables)
    print("restarts =", args.restarts)
    print("iterations =", args.iterations)
    print("brute_force_optimum =", BRUTE_FORCE_OPTIMUM)
    print("best_energy =", global_best["best_energy"])
    print("best_bitstring =", global_best["best_bitstring"])
    print("best_gap_to_bruteforce =", global_best["gap_to_bruteforce"])
    print("success_count =", success_count)
    print("success_rate =", success_rate)
    print("validation_status =", summary["validation_status"])
    print("saved runs =", runs_out)
    print("saved summary =", summary_out)

if __name__ == "__main__":
    main()
