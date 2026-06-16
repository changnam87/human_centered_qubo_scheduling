import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

import pandas as pd

from src.core.instance import load_instance
from src.core.time_indexed_variables import create_time_indexed_variable_mapping
from src.core.time_indexed_evaluate import evaluate_time_indexed_solution
from src.core.time_indexed_qubo import build_time_indexed_qubo_matrix
from src.solvers.simulated_annealing import simulated_annealing_qubo


def format_bitstring(bitstring):
    return "".join(str(int(v)) for v in bitstring)


def make_empty_bitstring(num_variables):
    return [0] * num_variables


def set_start(bitstring, operation, resource, time, var_to_index):
    index = var_to_index[(operation, resource, time)]
    bitstring[index] = 1


def build_handcrafted_feasible_schedule(num_variables, var_to_index):
    """
    Reference feasible schedule:

    O11 -> M at time 0
    O12 -> M at time 1
    O21 -> R at time 0
    O22 -> M at time 3
    """
    bitstring = make_empty_bitstring(num_variables)

    set_start(bitstring, "O11", "M", 0, var_to_index)
    set_start(bitstring, "O12", "M", 1, var_to_index)
    set_start(bitstring, "O21", "R", 0, var_to_index)
    set_start(bitstring, "O22", "M", 3, var_to_index)

    return bitstring


def main():
    instance_path = PROJECT_ROOT / "data" / "toy" / "toy_v2_time_indexed.json"
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

    print("=== Toy v2 SA sensitivity analysis ===")
    print("Number of binary variables:", num_variables)

    Q, constant_offset = build_time_indexed_qubo_matrix(
        instance,
        var_to_index
    )

    # ------------------------------------------------------------
    # Reference feasible schedule
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

    reference_cost = reference_result["total_cost"]

    print()
    print("Reference feasible total cost:", reference_cost)

    # ------------------------------------------------------------
    # SA experiment configurations
    # ------------------------------------------------------------
    experiment_configs = [
        {
            "config_name": "steps_1000_T50_to_001",
            "num_reads": 300,
            "num_steps": 1000,
            "initial_temperature": 50.0,
            "final_temperature": 0.01
        },
        {
            "config_name": "steps_3000_T50_to_001",
            "num_reads": 300,
            "num_steps": 3000,
            "initial_temperature": 50.0,
            "final_temperature": 0.01
        },
        {
            "config_name": "steps_5000_T50_to_001",
            "num_reads": 300,
            "num_steps": 5000,
            "initial_temperature": 50.0,
            "final_temperature": 0.01
        },
        {
            "config_name": "steps_10000_T50_to_001",
            "num_reads": 300,
            "num_steps": 10000,
            "initial_temperature": 50.0,
            "final_temperature": 0.01
        },
        {
            "config_name": "steps_5000_T20_to_001",
            "num_reads": 300,
            "num_steps": 5000,
            "initial_temperature": 20.0,
            "final_temperature": 0.01
        },
        {
            "config_name": "steps_5000_T100_to_001",
            "num_reads": 300,
            "num_steps": 5000,
            "initial_temperature": 100.0,
            "final_temperature": 0.01
        },
        {
            "config_name": "steps_5000_T50_to_01",
            "num_reads": 300,
            "num_steps": 5000,
            "initial_temperature": 50.0,
            "final_temperature": 0.1
        },
        {
            "config_name": "steps_5000_T50_to_0001",
            "num_reads": 300,
            "num_steps": 5000,
            "initial_temperature": 50.0,
            "final_temperature": 0.001
        }
    ]

    summary_rows = []
    read_rows = []

    base_seed = 3000

    for config_id, config in enumerate(experiment_configs):
        config_name = config["config_name"]

        print()
        print("=" * 70)
        print("Running config:", config_name)
        print("=" * 70)

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
        best_energy = float(sa_result["best_energy"])

        best_decoded = evaluate_time_indexed_solution(
            best_bitstring,
            instance,
            var_to_index
        )

        num_feasible_reads = 0
        num_zero_penalty_reads = 0
        num_reference_or_better_reads = 0

        energies = []
        total_costs = []
        feasible_costs = []

        for read_result in sa_result["all_results"]:
            bitstring = read_result["best_bitstring"]
            energy = float(read_result["best_energy"])

            decoded = evaluate_time_indexed_solution(
                bitstring,
                instance,
                var_to_index
            )

            feasible = decoded["feasible"]
            zero_penalty = abs(decoded["total_penalty"]) < 1e-9
            total_cost = float(decoded["total_cost"])

            energies.append(energy)
            total_costs.append(total_cost)

            if feasible:
                num_feasible_reads += 1
                feasible_costs.append(total_cost)

            if zero_penalty:
                num_zero_penalty_reads += 1

            if feasible and total_cost <= reference_cost + 1e-9:
                num_reference_or_better_reads += 1

            read_rows.append({
                "config_name": config_name,
                "read": read_result["read"],
                "bitstring": format_bitstring(bitstring),
                "energy": energy,
                "feasible": feasible,
                "num_violations": decoded["num_violations"],
                "zero_penalty": zero_penalty,
                "reference_or_better": feasible and total_cost <= reference_cost + 1e-9,
                "processing": decoded["processing"],
                "start_time": decoded["start_time"],
                "workload": decoded["workload"],
                "ergonomic": decoded["ergonomic"],
                "safety": decoded["safety"],
                "original_cost": decoded["original_cost"],
                "assignment_start_penalty": decoded["assignment_start_penalty"],
                "skill_penalty": decoded["skill_penalty"],
                "horizon_penalty": decoded["horizon_penalty"],
                "precedence_penalty": decoded["precedence_penalty"],
                "resource_overlap_penalty": decoded["resource_overlap_penalty"],
                "robot_utilization_penalty": decoded["robot_utilization_penalty"],
                "total_penalty": decoded["total_penalty"],
                "total_cost": total_cost,
                "schedule": str(decoded["schedule"])
            })

        feasibility_rate = num_feasible_reads / config["num_reads"]
        zero_penalty_rate = num_zero_penalty_reads / config["num_reads"]
        reference_or_better_rate = num_reference_or_better_reads / config["num_reads"]

        if feasible_costs:
            best_feasible_cost = min(feasible_costs)
            mean_feasible_cost = sum(feasible_costs) / len(feasible_costs)
        else:
            best_feasible_cost = None
            mean_feasible_cost = None

        summary_rows.append({
            "config_name": config_name,
            "num_reads": config["num_reads"],
            "num_steps": config["num_steps"],
            "initial_temperature": config["initial_temperature"],
            "final_temperature": config["final_temperature"],
            "reference_cost": reference_cost,
            "best_bitstring": format_bitstring(best_bitstring),
            "best_energy": best_energy,
            "best_total_cost": best_decoded["total_cost"],
            "best_feasible": best_decoded["feasible"],
            "best_total_penalty": best_decoded["total_penalty"],
            "best_feasible_cost": best_feasible_cost,
            "mean_feasible_cost": mean_feasible_cost,
            "mean_energy": sum(energies) / len(energies),
            "min_energy": min(energies),
            "max_energy": max(energies),
            "num_feasible_reads": num_feasible_reads,
            "feasibility_rate": feasibility_rate,
            "num_zero_penalty_reads": num_zero_penalty_reads,
            "zero_penalty_rate": zero_penalty_rate,
            "num_reference_or_better_reads": num_reference_or_better_reads,
            "reference_or_better_rate": reference_or_better_rate,
            "improvement_over_reference": reference_cost - best_decoded["total_cost"]
        })

        print("Best energy:", best_energy)
        print("Best total cost:", best_decoded["total_cost"])
        print("Best feasible:", best_decoded["feasible"])
        print("Best total penalty:", best_decoded["total_penalty"])
        print("Feasibility rate:", feasibility_rate)
        print("Zero penalty rate:", zero_penalty_rate)
        print("Reference-or-better rate:", reference_or_better_rate)
        print("Improvement over reference:", reference_cost - best_decoded["total_cost"])

    summary_df = pd.DataFrame(summary_rows)
    read_df = pd.DataFrame(read_rows)

    summary_path = PROJECT_ROOT / "results" / "tables" / "toy_v2_sa_sensitivity_summary.csv"
    reads_path = PROJECT_ROOT / "results" / "tables" / "toy_v2_sa_sensitivity_reads.csv"

    summary_df.to_csv(summary_path, index=False)
    read_df.to_csv(reads_path, index=False)

    print()
    print("=" * 70)
    print("SA sensitivity analysis completed")
    print("=" * 70)
    print("Saved summary to:", summary_path)
    print("Saved read-level results to:", reads_path)

    print()
    print("=== Summary table ===")
    print(summary_df[[
        "config_name",
        "num_steps",
        "initial_temperature",
        "final_temperature",
        "best_total_cost",
        "best_feasible",
        "best_total_penalty",
        "feasibility_rate",
        "zero_penalty_rate",
        "reference_or_better_rate",
        "mean_energy"
    ]])


if __name__ == "__main__":
    main()
