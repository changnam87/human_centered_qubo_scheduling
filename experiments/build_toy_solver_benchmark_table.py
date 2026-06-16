import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

import pandas as pd


def main():
    tables_dir = PROJECT_ROOT / "results" / "tables"

    brute_force_path = tables_dir / "toy_v1_bruteforce_results.csv"
    qubo_validation_path = tables_dir / "toy_v1_qubo_validation.csv"
    ising_validation_path = tables_dir / "toy_v1_ising_validation.csv"
    sa_results_path = tables_dir / "toy_v1_simulated_annealing_results.csv"
    sa_sensitivity_path = tables_dir / "toy_v1_sa_sensitivity_summary.csv"

    required_files = [
        brute_force_path,
        qubo_validation_path,
        ising_validation_path,
        sa_results_path,
        sa_sensitivity_path
    ]

    print("=== Checking required files ===")

    for path in required_files:
        if path.exists():
            print("Found:", path)
        else:
            print("Missing:", path)
            print()
            print("Please generate missing files before running this script.")
            return

    print()
    print("=== Loading results ===")

    bf_df = pd.read_csv(brute_force_path, dtype={"bitstring": str})
    qubo_df = pd.read_csv(qubo_validation_path, dtype={"bitstring": str})
    ising_df = pd.read_csv(ising_validation_path, dtype={"bitstring": str})
    sa_df = pd.read_csv(sa_results_path, dtype={"bitstring": str})
    sa_sens_df = pd.read_csv(sa_sensitivity_path, dtype={"best_bitstring": str})

    # ------------------------------------------------------------
    # Brute force summary
    # ------------------------------------------------------------
    bf_best = bf_df.sort_values("total_cost").iloc[0]
    bf_num_solutions = len(bf_df)
    bf_num_feasible = int(bf_df["feasible"].sum())
    bf_feasibility_rate = bf_num_feasible / bf_num_solutions

    optimum_energy = float(bf_best["total_cost"])
    optimum_bitstring = bf_best["bitstring"]

    # ------------------------------------------------------------
    # QUBO validation summary
    # ------------------------------------------------------------
    qubo_max_abs_error = float(qubo_df["abs_error"].max())
    qubo_best = qubo_df.sort_values("energy_from_Q").iloc[0]

    # ------------------------------------------------------------
    # Ising validation summary
    # ------------------------------------------------------------
    ising_max_abs_error = float(ising_df["abs_error"].max())
    ising_best = ising_df.sort_values("energy_ising").iloc[0]

    # ------------------------------------------------------------
    # SA single-run summary
    # ------------------------------------------------------------
    sa_best = sa_df.sort_values("energy").iloc[0]
    sa_num_reads = len(sa_df)
    sa_num_feasible = int(sa_df["feasible"].sum())
    sa_feasibility_rate = sa_num_feasible / sa_num_reads
    sa_num_optimum = int((abs(sa_df["energy"] - optimum_energy) < 1e-9).sum())
    sa_success_rate = sa_num_optimum / sa_num_reads
    sa_mean_energy = float(sa_df["energy"].mean())
    sa_best_energy = float(sa_best["energy"])
    sa_gap = sa_best_energy - optimum_energy

    # ------------------------------------------------------------
    # SA sensitivity best configuration
    # ------------------------------------------------------------
    sa_sens_best_success = sa_sens_df.sort_values(
        ["success_rate", "mean_energy"],
        ascending=[False, True]
    ).iloc[0]

    # ------------------------------------------------------------
    # Build benchmark summary
    # ------------------------------------------------------------
    rows = []

    rows.append({
        "component": "Brute force enumeration",
        "role": "Exact validation for toy instance",
        "num_candidates_or_reads": bf_num_solutions,
        "best_bitstring": optimum_bitstring,
        "best_energy_or_cost": optimum_energy,
        "absolute_gap_to_bruteforce": 0.0,
        "feasibility_rate": bf_feasibility_rate,
        "success_rate": 1.0,
        "mean_energy": None,
        "max_abs_validation_error": None,
        "notes": "Enumerated all 2^12 binary assignments."
    })

    rows.append({
        "component": "QUBO matrix validation",
        "role": "Validate x^T Q x + offset against evaluator",
        "num_candidates_or_reads": len(qubo_df),
        "best_bitstring": qubo_best["bitstring"],
        "best_energy_or_cost": float(qubo_best["energy_from_Q"]),
        "absolute_gap_to_bruteforce": float(qubo_best["energy_from_Q"]) - optimum_energy,
        "feasibility_rate": None,
        "success_rate": None,
        "mean_energy": None,
        "max_abs_validation_error": qubo_max_abs_error,
        "notes": "Checks QUBO matrix energy for all bitstrings."
    })

    rows.append({
        "component": "Ising conversion validation",
        "role": "Validate Ising energy against QUBO energy",
        "num_candidates_or_reads": len(ising_df),
        "best_bitstring": ising_best["bitstring"],
        "best_energy_or_cost": float(ising_best["energy_ising"]),
        "absolute_gap_to_bruteforce": float(ising_best["energy_ising"]) - optimum_energy,
        "feasibility_rate": None,
        "success_rate": None,
        "mean_energy": None,
        "max_abs_validation_error": ising_max_abs_error,
        "notes": "Checks QUBO-to-Ising conversion for all bitstrings."
    })

    rows.append({
        "component": "Simulated annealing",
        "role": "QUBO-compatible heuristic baseline",
        "num_candidates_or_reads": sa_num_reads,
        "best_bitstring": sa_best["bitstring"],
        "best_energy_or_cost": sa_best_energy,
        "absolute_gap_to_bruteforce": sa_gap,
        "feasibility_rate": sa_feasibility_rate,
        "success_rate": sa_success_rate,
        "mean_energy": sa_mean_energy,
        "max_abs_validation_error": None,
        "notes": "Single SA setting: 100 reads, 1000 steps, seed 42."
    })

    rows.append({
        "component": "SA sensitivity best setting",
        "role": "Annealing-parameter sensitivity analysis",
        "num_candidates_or_reads": int(sa_sens_best_success["num_reads"]),
        "best_bitstring": sa_sens_best_success["best_bitstring"],
        "best_energy_or_cost": float(sa_sens_best_success["best_energy"]),
        "absolute_gap_to_bruteforce": float(sa_sens_best_success["absolute_gap"]),
        "feasibility_rate": float(sa_sens_best_success["feasibility_rate"]),
        "success_rate": float(sa_sens_best_success["success_rate"]),
        "mean_energy": float(sa_sens_best_success["mean_energy"]),
        "max_abs_validation_error": None,
        "notes": (
            "Best sensitivity setting by success rate: "
            + str(sa_sens_best_success["config_name"])
        )
    })

    summary_df = pd.DataFrame(rows)

    output_path = tables_dir / "toy_v1_solver_benchmark_summary.csv"
    summary_df.to_csv(output_path, index=False)

    print()
    print("=== Solver benchmark summary ===")
    print(summary_df)

    print()
    print("Saved benchmark summary to:", output_path)


if __name__ == "__main__":
    main()
