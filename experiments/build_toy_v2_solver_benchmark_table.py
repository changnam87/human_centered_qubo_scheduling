import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

import pandas as pd

from src.core.instance import load_instance
from src.core.time_indexed_variables import create_time_indexed_variable_mapping
from src.core.time_indexed_evaluate import evaluate_time_indexed_solution


def make_empty_bitstring(num_variables):
    return [0] * num_variables


def set_start(bitstring, operation, resource, time, var_to_index):
    index = var_to_index[(operation, resource, time)]
    bitstring[index] = 1


def format_bitstring(bitstring):
    return "".join(str(int(v)) for v in bitstring)


def build_handcrafted_feasible_schedule(num_variables, var_to_index):
    bitstring = make_empty_bitstring(num_variables)

    set_start(bitstring, "O11", "M", 0, var_to_index)
    set_start(bitstring, "O12", "M", 1, var_to_index)
    set_start(bitstring, "O21", "R", 0, var_to_index)
    set_start(bitstring, "O22", "M", 3, var_to_index)

    return bitstring


def main():
    tables_dir = PROJECT_ROOT / "results" / "tables"

    instance_path = PROJECT_ROOT / "data" / "toy" / "toy_v2_time_indexed.json"
    qubo_validation_path = tables_dir / "toy_v2_qubo_validation.csv"
    ising_validation_path = tables_dir / "toy_v2_ising_validation.csv"
    sa_results_path = tables_dir / "toy_v2_simulated_annealing_results.csv"
    sa_sensitivity_path = tables_dir / "toy_v2_sa_sensitivity_summary.csv"
    cpsat_result_path = tables_dir / "toy_v2_cpsat_result.csv"

    required_files = [
        instance_path,
        qubo_validation_path,
        ising_validation_path,
        sa_results_path,
        sa_sensitivity_path,
        cpsat_result_path
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
    print("=== Loading Toy v2 instance ===")

    instance = load_instance(instance_path)

    operations = instance["operations"]
    resources = instance["resources"]
    time_slots = instance["time_slots"]

    variable_names, index_to_var, var_to_index = create_time_indexed_variable_mapping(
        operations,
        resources,
        time_slots
    )

    num_variables = len(variable_names)

    print("Number of operations:", len(operations))
    print("Number of resources:", len(resources))
    print("Number of time slots:", len(time_slots))
    print("Number of binary variables:", num_variables)

    # ------------------------------------------------------------
    # Reference handcrafted feasible schedule
    # ------------------------------------------------------------
    reference_bitstring = build_handcrafted_feasible_schedule(
        num_variables,
        var_to_index
    )

    reference_result = evaluate_time_indexed_solution(
        reference_bitstring,
        instance,
        var_to_index
    )

    reference_cost = float(reference_result["total_cost"])
    reference_total_penalty = float(reference_result["total_penalty"])
    reference_feasible = reference_result["feasible"]

    # ------------------------------------------------------------
    # QUBO validation summary
    # ------------------------------------------------------------
    qubo_df = pd.read_csv(qubo_validation_path, dtype={"bitstring": str})

    qubo_max_abs_error = float(qubo_df["abs_error"].max())

    feasible_qubo_row = qubo_df[
        qubo_df["label"] == "Feasible reference schedule"
    ].iloc[0]

    infeasible_qubo_row = qubo_df[
        qubo_df["label"] == "Infeasible reference schedule"
    ].iloc[0]

    # ------------------------------------------------------------
    # Ising validation summary
    # ------------------------------------------------------------
    ising_df = pd.read_csv(ising_validation_path, dtype={"bitstring": str})

    ising_max_abs_error = float(ising_df["abs_error"].max())

    feasible_ising_row = ising_df[
        ising_df["label"] == "Feasible reference schedule"
    ].iloc[0]

    # ------------------------------------------------------------
    # CP-SAT baseline summary
    # ------------------------------------------------------------
    cpsat_df = pd.read_csv(cpsat_result_path, dtype={"bitstring": str})
    cpsat_row = cpsat_df.iloc[0]

    cpsat_status = cpsat_row["status"]
    cpsat_bitstring = cpsat_row["bitstring"]
    cpsat_total_cost = float(cpsat_row["total_cost"])
    cpsat_feasible = bool(cpsat_row["feasible"])
    cpsat_total_penalty = float(cpsat_row["total_penalty"])
    cpsat_objective_unscaled = float(cpsat_row["objective_unscaled"])

    # ------------------------------------------------------------
    # SA single setting summary
    # ------------------------------------------------------------
    sa_df = pd.read_csv(sa_results_path, dtype={"bitstring": str})

    sa_num_reads = len(sa_df)
    sa_num_feasible = int(sa_df["feasible"].sum())
    sa_feasibility_rate = sa_num_feasible / sa_num_reads

    sa_num_zero_penalty = int((abs(sa_df["total_penalty"]) < 1e-9).sum())
    sa_zero_penalty_rate = sa_num_zero_penalty / sa_num_reads

    sa_best = sa_df.sort_values("total_cost").iloc[0]
    sa_best_total_cost = float(sa_best["total_cost"])
    sa_best_feasible = bool(sa_best["feasible"])
    sa_best_total_penalty = float(sa_best["total_penalty"])
    sa_mean_energy = float(sa_df["energy"].mean())

    sa_num_reference_or_better = int(
        ((sa_df["feasible"] == True) & (sa_df["total_cost"] <= reference_cost + 1e-9)).sum()
    )
    sa_reference_or_better_rate = sa_num_reference_or_better / sa_num_reads

    # ------------------------------------------------------------
    # SA sensitivity summary
    # ------------------------------------------------------------
    sa_sens_df = pd.read_csv(sa_sensitivity_path, dtype={"best_bitstring": str})

    sa_sens_best_stability = sa_sens_df.sort_values(
        ["feasibility_rate", "zero_penalty_rate", "best_total_cost", "mean_energy"],
        ascending=[False, False, True, True]
    ).iloc[0]

    sa_sens_best_quality = sa_sens_df.sort_values(
        ["reference_or_better_rate", "best_total_cost", "mean_energy"],
        ascending=[False, True, True]
    ).iloc[0]

    # ------------------------------------------------------------
    # Build summary table
    # ------------------------------------------------------------
    rows = []

    rows.append({
        "component": "Toy v2 instance",
        "role": "Time-indexed scheduling test instance",
        "num_variables": num_variables,
        "num_candidates_or_reads": None,
        "best_bitstring": None,
        "best_energy_or_cost": None,
        "reference_cost": reference_cost,
        "absolute_gap_to_reference": None,
        "feasibility_rate": None,
        "zero_penalty_rate": None,
        "reference_or_better_rate": None,
        "mean_energy": None,
        "max_abs_validation_error": None,
        "notes": "4 operations x 3 resources x 6 time slots = 72 binary variables."
    })

    rows.append({
        "component": "Handcrafted feasible schedule",
        "role": "Reference feasible schedule",
        "num_variables": num_variables,
        "num_candidates_or_reads": 1,
        "best_bitstring": format_bitstring(reference_bitstring),
        "best_energy_or_cost": reference_cost,
        "reference_cost": reference_cost,
        "absolute_gap_to_reference": 0.0,
        "feasibility_rate": 1.0 if reference_feasible else 0.0,
        "zero_penalty_rate": 1.0 if abs(reference_total_penalty) < 1e-9 else 0.0,
        "reference_or_better_rate": 1.0,
        "mean_energy": reference_cost,
        "max_abs_validation_error": None,
        "notes": "Used as reference because brute force is infeasible for 72 variables."
    })

    rows.append({
        "component": "QUBO matrix validation",
        "role": "Validate x^T Q x + offset against evaluator",
        "num_variables": num_variables,
        "num_candidates_or_reads": len(qubo_df),
        "best_bitstring": feasible_qubo_row["bitstring"],
        "best_energy_or_cost": float(feasible_qubo_row["qubo_energy"]),
        "reference_cost": reference_cost,
        "absolute_gap_to_reference": float(feasible_qubo_row["qubo_energy"]) - reference_cost,
        "feasibility_rate": None,
        "zero_penalty_rate": None,
        "reference_or_better_rate": None,
        "mean_energy": None,
        "max_abs_validation_error": qubo_max_abs_error,
        "notes": "Validated on handcrafted feasible and infeasible schedules."
    })

    rows.append({
        "component": "Ising conversion validation",
        "role": "Validate Ising Hamiltonian energy against QUBO energy",
        "num_variables": num_variables,
        "num_candidates_or_reads": len(ising_df),
        "best_bitstring": feasible_ising_row["bitstring"],
        "best_energy_or_cost": float(feasible_ising_row["energy_ising"]),
        "reference_cost": reference_cost,
        "absolute_gap_to_reference": float(feasible_ising_row["energy_ising"]) - reference_cost,
        "feasibility_rate": None,
        "zero_penalty_rate": None,
        "reference_or_better_rate": None,
        "mean_energy": None,
        "max_abs_validation_error": ising_max_abs_error,
        "notes": "Validated on handcrafted feasible and infeasible schedules using tolerance 1e-6."
    })

    rows.append({
        "component": "Infeasible schedule check",
        "role": "Verify that violations create positive penalties",
        "num_variables": num_variables,
        "num_candidates_or_reads": 1,
        "best_bitstring": infeasible_qubo_row["bitstring"],
        "best_energy_or_cost": float(infeasible_qubo_row["function_total_cost"]),
        "reference_cost": reference_cost,
        "absolute_gap_to_reference": float(infeasible_qubo_row["function_total_cost"]) - reference_cost,
        "feasibility_rate": 0.0 if not bool(infeasible_qubo_row["feasible"]) else 1.0,
        "zero_penalty_rate": 0.0,
        "reference_or_better_rate": 0.0,
        "mean_energy": float(infeasible_qubo_row["function_total_cost"]),
        "max_abs_validation_error": None,
        "notes": "Deliberately violates precedence and resource overlap."
    })

    rows.append({
        "component": "CP-SAT baseline",
        "role": "Classical exact/strong baseline",
        "num_variables": num_variables,
        "num_candidates_or_reads": 1,
        "best_bitstring": cpsat_bitstring,
        "best_energy_or_cost": cpsat_total_cost,
        "reference_cost": reference_cost,
        "absolute_gap_to_reference": cpsat_total_cost - reference_cost,
        "feasibility_rate": 1.0 if cpsat_feasible else 0.0,
        "zero_penalty_rate": 1.0 if abs(cpsat_total_penalty) < 1e-9 else 0.0,
        "reference_or_better_rate": 1.0 if cpsat_total_cost <= reference_cost + 1e-9 else 0.0,
        "mean_energy": cpsat_total_cost,
        "max_abs_validation_error": None,
        "notes": "CP-SAT status: " + str(cpsat_status) + "; objective_unscaled: " + str(cpsat_objective_unscaled)
    })

    rows.append({
        "component": "Simulated annealing",
        "role": "QUBO-compatible heuristic baseline",
        "num_variables": num_variables,
        "num_candidates_or_reads": sa_num_reads,
        "best_bitstring": sa_best["bitstring"],
        "best_energy_or_cost": sa_best_total_cost,
        "reference_cost": reference_cost,
        "absolute_gap_to_reference": sa_best_total_cost - reference_cost,
        "feasibility_rate": sa_feasibility_rate,
        "zero_penalty_rate": sa_zero_penalty_rate,
        "reference_or_better_rate": sa_reference_or_better_rate,
        "mean_energy": sa_mean_energy,
        "max_abs_validation_error": None,
        "notes": "Single SA setting: 300 reads, 5000 steps, T=50 to 0.01."
    })

    rows.append({
        "component": "SA sensitivity best stability setting",
        "role": "Most stable SA setting by feasibility and zero-penalty rate",
        "num_variables": num_variables,
        "num_candidates_or_reads": int(sa_sens_best_stability["num_reads"]),
        "best_bitstring": sa_sens_best_stability["best_bitstring"],
        "best_energy_or_cost": float(sa_sens_best_stability["best_total_cost"]),
        "reference_cost": reference_cost,
        "absolute_gap_to_reference": float(sa_sens_best_stability["best_total_cost"]) - reference_cost,
        "feasibility_rate": float(sa_sens_best_stability["feasibility_rate"]),
        "zero_penalty_rate": float(sa_sens_best_stability["zero_penalty_rate"]),
        "reference_or_better_rate": float(sa_sens_best_stability["reference_or_better_rate"]),
        "mean_energy": float(sa_sens_best_stability["mean_energy"]),
        "max_abs_validation_error": None,
        "notes": "Best stability config: " + str(sa_sens_best_stability["config_name"])
    })

    rows.append({
        "component": "SA sensitivity best quality setting",
        "role": "Best SA setting by reference-or-better rate",
        "num_variables": num_variables,
        "num_candidates_or_reads": int(sa_sens_best_quality["num_reads"]),
        "best_bitstring": sa_sens_best_quality["best_bitstring"],
        "best_energy_or_cost": float(sa_sens_best_quality["best_total_cost"]),
        "reference_cost": reference_cost,
        "absolute_gap_to_reference": float(sa_sens_best_quality["best_total_cost"]) - reference_cost,
        "feasibility_rate": float(sa_sens_best_quality["feasibility_rate"]),
        "zero_penalty_rate": float(sa_sens_best_quality["zero_penalty_rate"]),
        "reference_or_better_rate": float(sa_sens_best_quality["reference_or_better_rate"]),
        "mean_energy": float(sa_sens_best_quality["mean_energy"]),
        "max_abs_validation_error": None,
        "notes": "Best quality config: " + str(sa_sens_best_quality["config_name"])
    })

    summary_df = pd.DataFrame(rows)

    output_path = tables_dir / "toy_v2_solver_benchmark_summary.csv"
    summary_df.to_csv(output_path, index=False)

    print()
    print("=== Toy v2 solver benchmark summary ===")
    print(summary_df[[
        "component",
        "num_variables",
        "best_energy_or_cost",
        "reference_cost",
        "absolute_gap_to_reference",
        "feasibility_rate",
        "zero_penalty_rate",
        "reference_or_better_rate",
        "mean_energy",
        "max_abs_validation_error",
        "notes"
    ]])

    print()
    print("Saved benchmark summary to:", output_path)


if __name__ == "__main__":
    main()
