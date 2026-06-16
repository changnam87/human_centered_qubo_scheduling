import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

import pandas as pd

from src.core.instance import load_instance, print_instance_summary
from src.core.variables import create_variable_mapping
from src.core.qubo import build_qubo_matrix
from src.core.evaluate import evaluate_solution
from src.solvers.simulated_annealing import simulated_annealing_qubo


def format_bitstring(bitstring):
    return "".join(str(int(v)) for v in bitstring)


def main():
    instance_path = PROJECT_ROOT / "data" / "toy" / "toy_v1.json"
    instance = load_instance(instance_path)

    print_instance_summary(instance)

    operations = instance["operations"]
    resources = instance["resources"]

    variable_names, index_to_var, var_to_index = create_variable_mapping(
        operations,
        resources
    )

    Q, constant_offset = build_qubo_matrix(instance, var_to_index)

    print()
    print("=== Loading brute-force optimum ===")

    brute_force_path = PROJECT_ROOT / "results" / "tables" / "toy_v1_bruteforce_results.csv"

    if not brute_force_path.exists():
        print("Brute-force result file not found.")
        print("Please run:")
        print("python experiments/run_toy_bruteforce.py")
        return

    bf_df = pd.read_csv(brute_force_path, dtype={"bitstring": str})
    bf_best = bf_df.sort_values("total_cost").iloc[0]

    optimum_energy = float(bf_best["total_cost"])
    optimum_bitstring = bf_best["bitstring"]

    print("Brute-force optimum bitstring:", optimum_bitstring)
    print("Brute-force optimum energy:", optimum_energy)

    print()
    print("=== Running SA sensitivity experiment ===")

    experiment_configs = [
        {
            "config_name": "steps_100_T10_to_001",
            "num_reads": 100,
            "num_steps": 100,
            "initial_temperature": 10.0,
            "final_temperature": 0.01
        },
        {
            "config_name": "steps_500_T10_to_001",
            "num_reads": 100,
            "num_steps": 500,
            "initial_temperature": 10.0,
            "final_temperature": 0.01
        },
        {
            "config_name": "steps_1000_T10_to_001",
            "num_reads": 100,
            "num_steps": 1000,
            "initial_temperature": 10.0,
            "final_temperature": 0.01
        },
        {
            "config_name": "steps_2000_T10_to_001",
            "num_reads": 100,
            "num_steps": 2000,
            "initial_temperature": 10.0,
            "final_temperature": 0.01
        },
        {
            "config_name": "steps_1000_T5_to_001",
            "num_reads": 100,
            "num_steps": 1000,
            "initial_temperature": 5.0,
            "final_temperature": 0.01
        },
        {
            "config_name": "steps_1000_T20_to_001",
            "num_reads": 100,
            "num_steps": 1000,
            "initial_temperature": 20.0,
            "final_temperature": 0.01
        },
        {
            "config_name": "steps_1000_T10_to_01",
            "num_reads": 100,
            "num_steps": 1000,
            "initial_temperature": 10.0,
            "final_temperature": 0.1
        }
    ]

    summary_rows = []
    read_rows = []

    base_seed = 1000

    for config_id, config in enumerate(experiment_configs):
        config_name = config["config_name"]

        print()
        print("Running config:", config_name)

        sa_result = simulated_annealing_qubo(
            Q=Q,
            constant_offset=constant_offset,
            num_reads=config["num_reads"],
            num_steps=config["num_steps"],
            initial_temperature=config["initial_temperature"],
            final_temperature=config["final_temperature"],
            seed=base_seed + config_id
        )

        best_bitstring = sa_result["best_bitstring"]
        best_energy = sa_result["best_energy"]
        best_decoded = evaluate_solution(best_bitstring, instance, var_to_index)

        num_optimum_reads = 0
        num_feasible_reads = 0
        energies = []

        for read_result in sa_result["all_results"]:
            bitstring = read_result["best_bitstring"]
            energy = float(read_result["best_energy"])
            decoded = evaluate_solution(bitstring, instance, var_to_index)

            energies.append(energy)

            is_optimum = abs(energy - optimum_energy) < 1e-9
            is_feasible = decoded["feasible"]

            if is_optimum:
                num_optimum_reads += 1

            if is_feasible:
                num_feasible_reads += 1

            read_rows.append({
                "config_name": config_name,
                "read": read_result["read"],
                "bitstring": format_bitstring(bitstring),
                "energy": energy,
                "is_optimum": is_optimum,
                "feasible": is_feasible,
                "assignment": str(decoded["assignment"]),
                "processing": decoded["processing"],
                "workload": decoded["workload"],
                "ergonomic": decoded["ergonomic"],
                "safety": decoded["safety"],
                "original_cost": decoded["original_cost"],
                "assignment_penalty": decoded["assignment_penalty"],
                "skill_penalty": decoded["skill_penalty"],
                "robot_utilization_penalty": decoded["robot_utilization_penalty"],
                "total_penalty": decoded["total_penalty"],
                "total_cost": decoded["total_cost"]
            })

        success_rate = num_optimum_reads / config["num_reads"]
        feasibility_rate = num_feasible_reads / config["num_reads"]

        summary_rows.append({
            "config_name": config_name,
            "num_reads": config["num_reads"],
            "num_steps": config["num_steps"],
            "initial_temperature": config["initial_temperature"],
            "final_temperature": config["final_temperature"],
            "best_bitstring": format_bitstring(best_bitstring),
            "best_energy": best_energy,
            "best_feasible": best_decoded["feasible"],
            "best_total_penalty": best_decoded["total_penalty"],
            "optimum_energy": optimum_energy,
            "absolute_gap": best_energy - optimum_energy,
            "num_optimum_reads": num_optimum_reads,
            "success_rate": success_rate,
            "num_feasible_reads": num_feasible_reads,
            "feasibility_rate": feasibility_rate,
            "min_energy": min(energies),
            "mean_energy": sum(energies) / len(energies),
            "max_energy": max(energies)
        })

        print("Best energy:", best_energy)
        print("Best bitstring:", format_bitstring(best_bitstring))
        print("Success rate:", success_rate)
        print("Feasibility rate:", feasibility_rate)

    summary_df = pd.DataFrame(summary_rows)
    read_df = pd.DataFrame(read_rows)

    summary_path = PROJECT_ROOT / "results" / "tables" / "toy_v1_sa_sensitivity_summary.csv"
    reads_path = PROJECT_ROOT / "results" / "tables" / "toy_v1_sa_sensitivity_reads.csv"

    summary_df.to_csv(summary_path, index=False)
    read_df.to_csv(reads_path, index=False)

    print()
    print("=== SA sensitivity experiment completed ===")
    print("Saved summary to:", summary_path)
    print("Saved read-level results to:", reads_path)

    print()
    print("=== Summary ===")
    print(summary_df[[
        "config_name",
        "num_steps",
        "initial_temperature",
        "final_temperature",
        "best_energy",
        "absolute_gap",
        "success_rate",
        "feasibility_rate",
        "mean_energy"
    ]])


if __name__ == "__main__":
    main()
