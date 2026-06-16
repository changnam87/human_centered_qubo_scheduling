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

    O11 -> M at time 0, duration 1, ends at 1
    O12 -> M at time 1, duration 2, ends at 3
    O21 -> R at time 0, duration 2, ends at 2
    O22 -> M at time 3, duration 1, ends at 4
    """
    bitstring = make_empty_bitstring(num_variables)

    set_start(bitstring, "O11", "M", 0, var_to_index)
    set_start(bitstring, "O12", "M", 1, var_to_index)
    set_start(bitstring, "O21", "R", 0, var_to_index)
    set_start(bitstring, "O22", "M", 3, var_to_index)

    return bitstring


def print_solution(label, result):
    print()
    print("=" * 70)
    print(label)
    print("=" * 70)

    print("Feasible:", result["feasible"])
    print("Number of violations:", result["num_violations"])
    print("Processing:", result["processing"])
    print("Start time:", result["start_time"])
    print("Workload:", result["workload"])
    print("Ergonomic:", result["ergonomic"])
    print("Safety:", result["safety"])
    print("Original cost:", result["original_cost"])
    print("Assignment-start penalty:", result["assignment_start_penalty"])
    print("Skill penalty:", result["skill_penalty"])
    print("Horizon penalty:", result["horizon_penalty"])
    print("Precedence penalty:", result["precedence_penalty"])
    print("Resource-overlap penalty:", result["resource_overlap_penalty"])
    print("Robot-utilization penalty:", result["robot_utilization_penalty"])
    print("Total penalty:", result["total_penalty"])
    print("Total cost:", result["total_cost"])

    print()
    print("Schedule:")
    for operation, selected in result["schedule"].items():
        print(operation, ":", selected)

    if result["num_violations"] > 0:
        print()
        print("Violations:")
        for violation in result["violations"]:
            print("-", violation["message"])


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

    print("=== Toy v2 simulated annealing ===")
    print("Number of binary variables:", num_variables)

    print()
    print("=== Building QUBO matrix ===")

    Q, constant_offset = build_time_indexed_qubo_matrix(
        instance,
        var_to_index
    )

    print("Q shape:", Q.shape)
    print("Constant offset:", constant_offset)

    # ------------------------------------------------------------
    # Evaluate handcrafted feasible reference schedule
    # ------------------------------------------------------------
    handcrafted_bitstring = build_handcrafted_feasible_schedule(
        num_variables,
        var_to_index
    )

    handcrafted_result = evaluate_time_indexed_solution(
        handcrafted_bitstring,
        instance,
        var_to_index
    )

    print_solution("Handcrafted feasible reference schedule", handcrafted_result)

    # ------------------------------------------------------------
    # Run simulated annealing
    # ------------------------------------------------------------
    print()
    print("=== Running simulated annealing ===")

    sa_result = simulated_annealing_qubo(
        Q=Q,
        constant_offset=constant_offset,
        num_reads=300,
        num_steps=5000,
        initial_temperature=50.0,
        final_temperature=0.01,
        seed=2026
    )

    best_bitstring = sa_result["best_bitstring"]

    best_result = evaluate_time_indexed_solution(
        best_bitstring,
        instance,
        var_to_index
    )

    print_solution("Best solution found by simulated annealing", best_result)

    # ------------------------------------------------------------
    # Save read-level results
    # ------------------------------------------------------------
    rows = []

    for read_result in sa_result["all_results"]:
        bitstring = read_result["best_bitstring"]
        decoded = evaluate_time_indexed_solution(
            bitstring,
            instance,
            var_to_index
        )

        rows.append({
            "read": read_result["read"],
            "bitstring": format_bitstring(bitstring),
            "energy": read_result["best_energy"],
            "feasible": decoded["feasible"],
            "num_violations": decoded["num_violations"],
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
            "total_cost": decoded["total_cost"],
            "schedule": str(decoded["schedule"])
        })

    df = pd.DataFrame(rows)

    output_path = PROJECT_ROOT / "results" / "tables" / "toy_v2_simulated_annealing_results.csv"
    df.to_csv(output_path, index=False)

    print()
    print("Saved SA results to:", output_path)

    # ------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------
    feasible_df = df[df["feasible"] == True]

    num_reads = len(df)
    num_feasible = len(feasible_df)
    feasibility_rate = num_feasible / num_reads

    best_energy = float(df["energy"].min())
    mean_energy = float(df["energy"].mean())

    handcrafted_cost = handcrafted_result["total_cost"]
    best_sa_cost = best_result["total_cost"]

    print()
    print("=" * 70)
    print("Summary")
    print("=" * 70)
    print("Number of reads:", num_reads)
    print("Number of feasible reads:", num_feasible)
    print("Feasibility rate:", feasibility_rate)
    print("Best SA energy:", best_energy)
    print("Mean SA energy:", mean_energy)
    print("Handcrafted feasible total cost:", handcrafted_cost)
    print("Best SA total cost:", best_sa_cost)
    print("Best SA feasible:", best_result["feasible"])
    print("Best SA total penalty:", best_result["total_penalty"])
    print("Improvement over handcrafted:", handcrafted_cost - best_sa_cost)

    if best_result["feasible"]:
        print("PASS: SA found a feasible schedule.")
    else:
        print("WARNING: Best SA solution is infeasible. Penalty weights or SA settings may need adjustment.")


if __name__ == "__main__":
    main()
