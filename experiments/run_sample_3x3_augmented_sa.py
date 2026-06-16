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


def main():
    instance_path = PROJECT_ROOT / "data" / "augmented" / "sample_3x3_hc_seed2026_time_indexed.json"

    print("=== sample_3x3 augmented Simulated Annealing ===")
    print("Input:", instance_path)

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

    print()
    print("=== Dimensions ===")
    print("Operations:", len(operations))
    print("Resources:", len(resources))
    print("Time slots:", len(time_slots))
    print("Binary variables:", num_variables)

    print()
    print("=== Building QUBO matrix ===")

    Q, constant_offset = build_time_indexed_qubo_matrix(
        instance,
        var_to_index
    )

    print("Q shape:", Q.shape)
    print("Constant offset:", constant_offset)

    # ------------------------------------------------------------
    # Load CP-SAT baseline if available
    # ------------------------------------------------------------
    cpsat_path = PROJECT_ROOT / "results" / "tables" / "sample_3x3_augmented_cpsat_result.csv"

    cpsat_cost = None

    if cpsat_path.exists():
        cpsat_df = pd.read_csv(cpsat_path, dtype={"bitstring": str})
        cpsat_cost = float(cpsat_df.iloc[0]["total_cost"])

        print()
        print("=== CP-SAT baseline ===")
        print("CP-SAT total cost:", cpsat_cost)
    else:
        print()
        print("CP-SAT result not found. Run this first:")
        print("python experiments/run_sample_3x3_augmented_cpsat.py")

    # ------------------------------------------------------------
    # Run Simulated Annealing
    # ------------------------------------------------------------
    print()
    print("=== Running simulated annealing ===")

    sa_result = simulated_annealing_qubo(
        Q=Q,
        constant_offset=constant_offset,
        num_reads=200,
        num_steps=3000,
        initial_temperature=100.0,
        final_temperature=0.01,
        seed=2026
    )

    best_bitstring = sa_result["best_bitstring"]
    best_energy = float(sa_result["best_energy"])

    best_decoded = evaluate_time_indexed_solution(
        best_bitstring,
        instance,
        var_to_index
    )

    print()
    print("=== Best SA solution ===")
    print("Best SA energy:", best_energy)
    print("Feasible:", best_decoded["feasible"])
    print("Number of violations:", best_decoded["num_violations"])
    print("Processing:", best_decoded["processing"])
    print("Start time:", best_decoded["start_time"])
    print("Workload:", best_decoded["workload"])
    print("Ergonomic:", best_decoded["ergonomic"])
    print("Safety:", best_decoded["safety"])
    print("Original cost:", best_decoded["original_cost"])
    print("Assignment-start penalty:", best_decoded["assignment_start_penalty"])
    print("Skill penalty:", best_decoded["skill_penalty"])
    print("Horizon penalty:", best_decoded["horizon_penalty"])
    print("Precedence penalty:", best_decoded["precedence_penalty"])
    print("Resource-overlap penalty:", best_decoded["resource_overlap_penalty"])
    print("Robot-utilization penalty:", best_decoded["robot_utilization_penalty"])
    print("Total penalty:", best_decoded["total_penalty"])
    print("Total cost:", best_decoded["total_cost"])

    print()
    print("Schedule:")
    for operation, selected in best_decoded["schedule"].items():
        print(operation, ":", selected)

    if cpsat_cost is not None:
        print()
        print("=== Gap to CP-SAT ===")
        print("CP-SAT cost:", cpsat_cost)
        print("SA best total cost:", best_decoded["total_cost"])
        print("SA gap to CP-SAT:", best_decoded["total_cost"] - cpsat_cost)

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

        gap_to_cpsat = None
        if cpsat_cost is not None:
            gap_to_cpsat = decoded["total_cost"] - cpsat_cost

        rows.append({
            "read": read_result["read"],
            "bitstring": format_bitstring(bitstring),
            "energy": float(read_result["best_energy"]),
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
            "gap_to_cpsat": gap_to_cpsat,
            "schedule": str(decoded["schedule"])
        })

    df = pd.DataFrame(rows)

    output_path = PROJECT_ROOT / "results" / "tables" / "sample_3x3_augmented_sa_results.csv"
    df.to_csv(output_path, index=False)

    print()
    print("Saved SA results to:", output_path)

    # ------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------
    num_reads = len(df)
    num_feasible = int(df["feasible"].sum())
    feasibility_rate = num_feasible / num_reads

    zero_penalty_rate = (abs(df["total_penalty"]) < 1e-9).sum() / num_reads

    feasible_df = df[df["feasible"] == True]

    if len(feasible_df) > 0:
        best_feasible = feasible_df.sort_values("total_cost").iloc[0]
        best_feasible_cost = float(best_feasible["total_cost"])
        mean_feasible_cost = float(feasible_df["total_cost"].mean())
    else:
        best_feasible_cost = None
        mean_feasible_cost = None

    print()
    print("=" * 70)
    print("SA Summary")
    print("=" * 70)
    print("Number of reads:", num_reads)
    print("Number of feasible reads:", num_feasible)
    print("Feasibility rate:", feasibility_rate)
    print("Zero-penalty rate:", zero_penalty_rate)
    print("Best feasible cost:", best_feasible_cost)
    print("Mean feasible cost:", mean_feasible_cost)

    if cpsat_cost is not None and best_feasible_cost is not None:
        print("Best feasible gap to CP-SAT:", best_feasible_cost - cpsat_cost)

    if best_decoded["feasible"]:
        print("PASS: SA found a feasible schedule.")
    else:
        print("WARNING: Best SA solution is infeasible. Consider more steps or stronger penalties.")


if __name__ == "__main__":
    main()
