"""Export a tiny QAOA/Qiskit-ready QUBO package.

This script creates a very small QUBO package suitable for Qiskit Optimization
and QAOA-oriented toy experiments.

This step only exports and validates the tiny package.
It does not run Qiskit, QAOA, quantum hardware, or a quantum simulator.
"""

from __future__ import annotations

import csv
import itertools
import json
from pathlib import Path

def qubo_energy(bits, coeffs, offset):
    e = offset
    for i, j, q in coeffs:
        e += q * bits[i] * bits[j]
    return e

def bitstring(bits):
    return "".join(str(int(b)) for b in bits)

def main():
    out_dir = Path("exports/tiny_qaoa_ready_package")
    out_dir.mkdir(parents=True, exist_ok=True)

    # Tiny 6-variable QUBO.
    # Interpretation: choose one option from each of three binary pairs.
    # Variables:
    #   x0, x1 = pair 0 options
    #   x2, x3 = pair 1 options
    #   x4, x5 = pair 2 options
    # Penalties encourage exactly one variable selected in each pair.
    num_variables = 6
    offset = 30.0
    coeffs = []

    # Linear objective preferences.
    linear_costs = {
        0: 1.0,
        1: 3.0,
        2: 2.0,
        3: 1.5,
        4: 2.5,
        5: 1.0,
    }

    # Exactly-one penalty for each pair: P * (x_a + x_b - 1)^2.
    # For binary variables:
    # P*(x_a + x_b - 1)^2 = P - P*x_a - P*x_b + 2P*x_a*x_b.
    penalty = 10.0
    pairs = [(0, 1), (2, 3), (4, 5)]

    diag = {i: linear_costs[i] for i in range(num_variables)}
    quad = {}

    for a, b in pairs:
        diag[a] = diag.get(a, 0.0) - penalty
        diag[b] = diag.get(b, 0.0) - penalty
        key = (min(a, b), max(a, b))
        quad[key] = quad.get(key, 0.0) + 2.0 * penalty

    # Add small cross preferences to make the landscape nontrivial.
    extra_quadratic = {
        (0, 3): 0.5,
        (1, 2): 1.0,
        (3, 5): 0.25,
        (0, 4): 0.75,
    }
    for key, value in extra_quadratic.items():
        key = (min(key[0], key[1]), max(key[0], key[1]))
        quad[key] = quad.get(key, 0.0) + value

    for i in range(num_variables):
        coeffs.append((i, i, diag[i]))
    for (i, j), q in sorted(quad.items()):
        coeffs.append((i, j, q))
    coeffs.sort(key=lambda x: (x[0], x[1]))

    qubo_csv = out_dir / "qubo_coefficients.csv"
    with qubo_csv.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["i", "j", "coefficient"])
        writer.writeheader()
        for i, j, q in coeffs:
            writer.writerow({"i": i, "j": j, "coefficient": q})

    rows = []
    for bits_tuple in itertools.product([0, 1], repeat=num_variables):
        bits = list(bits_tuple)
        e = qubo_energy(bits, coeffs, offset)
        pair_sums = [bits[a] + bits[b] for a, b in pairs]
        feasible = all(v == 1 for v in pair_sums)
        rows.append({
            "bitstring": bitstring(bits),
            "energy": e,
            "feasible_exactly_one_per_pair": feasible,
            "pair0_sum": pair_sums[0],
            "pair1_sum": pair_sums[1],
            "pair2_sum": pair_sums[2],
        })

    best = min(rows, key=lambda r: r["energy"])
    feasible_rows = [r for r in rows if r["feasible_exactly_one_per_pair"]]
    best_feasible = min(feasible_rows, key=lambda r: r["energy"])

    brute_csv = out_dir / "bruteforce_energy_table.csv"
    with brute_csv.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    # Qiskit-friendly simple JSON representation.
    qiskit_json = out_dir / "qiskit_qubo.json"
    qiskit_payload = {
        "format": "qiskit_optimization_qubo_ready",
        "num_binary_variables": num_variables,
        "variables": ["x" + str(i) for i in range(num_variables)],
        "objective_sense": "minimize",
        "constant": offset,
        "linear": {"x" + str(i): diag[i] for i in range(num_variables)},
        "quadratic": {
            "x" + str(i) + ",x" + str(j): q
            for (i, j), q in sorted(quad.items())
        },
        "energy_convention": "constant + sum_i linear_i x_i + sum_{i<j} quadratic_ij x_i x_j",
        "known_best_bitstring": best["bitstring"],
        "known_best_energy": best["energy"],
    }
    qiskit_json.write_text(json.dumps(qiskit_payload, indent=2))

    metadata = {
        "package": "tiny_qaoa_ready_package",
        "purpose": "Tiny QUBO package for Qiskit Optimization and QAOA-oriented toy experiments.",
        "num_variables": num_variables,
        "num_assignments_enumerated": len(rows),
        "constant_offset": offset,
        "num_qubo_terms": len(coeffs),
        "num_linear_terms": num_variables,
        "num_quadratic_terms": len(quad),
        "exactly_one_pairs": pairs,
        "penalty": penalty,
        "best_bitstring": best["bitstring"],
        "best_energy": best["energy"],
        "best_is_feasible": best["feasible_exactly_one_per_pair"],
        "best_feasible_bitstring": best_feasible["bitstring"],
        "best_feasible_energy": best_feasible["energy"],
        "qubo_coefficients_csv": str(qubo_csv),
        "bruteforce_energy_table_csv": str(brute_csv),
        "qiskit_qubo_json": str(qiskit_json),
        "note": "Export only. Qiskit/QAOA execution is not performed in this step.",
    }
    metadata_path = out_dir / "package_metadata.json"
    metadata_path.write_text(json.dumps(metadata, indent=2))

    readme = out_dir / "README.md"
    readme.write_text("\\n".join([
        "# Tiny QAOA-Ready QUBO Package",
        "",
        "This package contains a tiny 6-variable QUBO suitable for Qiskit Optimization and QAOA-oriented toy experiments.",
        "",
        "This package is intentionally tiny. It is not the sample_4x4 QUBO.",
        "",
        "## Files",
        "",
        "- qubo_coefficients.csv: upper-triangular QUBO coefficients.",
        "- qiskit_qubo.json: Qiskit-friendly QUBO representation.",
        "- bruteforce_energy_table.csv: exhaustive energy table over all 64 assignments.",
        "- package_metadata.json: package metadata and known optimum.",
        "",
        "## Known optimum",
        "",
        "Best bitstring: " + str(best["bitstring"]),
        "Best energy: " + str(best["energy"]),
        "Best is feasible: " + str(best["feasible_exactly_one_per_pair"]),
        "",
        "This step does not run Qiskit, QAOA, quantum hardware, or a quantum simulator.",
    ]) + "\\n")

    summary_out = Path("results/tables/tiny_qaoa_ready_package_summary.json")
    summary_out.parent.mkdir(parents=True, exist_ok=True)
    summary_out.write_text(json.dumps(metadata, indent=2))

    print("=== tiny QAOA-ready package export complete ===")
    print("out_dir =", out_dir)
    print("num_variables =", num_variables)
    print("num_assignments_enumerated =", len(rows))
    print("best_bitstring =", best["bitstring"])
    print("best_energy =", best["energy"])
    print("best_is_feasible =", best["feasible_exactly_one_per_pair"])
    print("saved summary =", summary_out)

if __name__ == "__main__":
    main()
