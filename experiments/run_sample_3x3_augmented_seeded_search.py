import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

import pandas as pd

from src.core.instance import load_instance
from src.core.time_indexed_variables import create_time_indexed_variable_mapping
from src.core.time_indexed_evaluate import evaluate_time_indexed_solution
from src.solvers.time_indexed_local_search import seeded_time_indexed_local_search


def format_bitstring(bitstring):
    return "".join(str(int(v)) for v in bitstring)


def make_empty_bitstring(num_variables):
    return [0] * num_variables


def set_start(bitstring, operation, resource, time, var_to_index):
    index = var_to_index[(operation, resource, time)]
    bitstring[index] = 1


def build_handcrafted_seed(num_variables, var_to_index):
    """
    Feasible handcrafted seed with total cost 34.2.
    """
    bitstring = make_empty_bitstring(num_variables)

    schedule = [
        ("O0_0", "M0", 0),
        ("O0_1", "M1", 4),
        ("O0_2", "M2", 6),

        ("O1_0", "M0", 3),
        ("O1_1", "R0", 5),
        ("O1_2", "M1", 9),

        ("O2_0", "M1", 0),
        ("O2_1", "M2", 8),
        ("O2_2", "M0", 11),
    ]

    for operation, resource, time in schedule:
        set_start(bitstring, operation, resource, time, var_to_index)

    return bitstring


def load_cpsat_seed(path, num_variables):
    """
    Load CP-SAT bitstring if available.
    """
    if not path.exists():
        return None, None

    df = pd.read_csv(path, dtype={"bitstring": str})
    row = df.iloc[0]

    bitstring_text = row["bitstring"]

    # Pad just in case spreadsheet display removed leading zeros
    bitstring_text = bitstring_text.zfill(num_variables)

    bitstring = [int(ch) for ch in bitstring_text]

    return bitstring, row


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
    print("Total penalty:", result["total_penalty"])
    print("Total cost:", result["total_cost"])

    print()
    print("Schedule:")
    for operation, selected in result["schedule"].items():
        print(operation, ":", selected)


def main():
    instance_path = PROJECT_ROOT / "data" / "augmented" / "sample_3x3_hc_seed2026_time_indexed.json"

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

    print("=== sample_3x3 augmented seeded structure-aware search ===")
    print("Operations:", len(operations))
    print("Resources:", len(resources))
    print("Time slots:", len(time_slots))
    print("Binary variables:", num_variables)

    # ------------------------------------------------------------
    # Load baseline costs
    # ------------------------------------------------------------
    cpsat_path = PROJECT_ROOT / "results" / "tables" / "sample_3x3_augmented_cpsat_result.csv"

    cpsat_seed, cpsat_row = load_cpsat_seed(cpsat_path, num_variables)

    cpsat_cost = None
    if cpsat_row is not None:
        cpsat_cost = float(cpsat_row["total_cost"])
        print()
        print("CP-SAT baseline cost:", cpsat_cost)

    handcrafted_seed = build_handcrafted_seed(num_variables, var_to_index)

    handcrafted_result = evaluate_time_indexed_solution(
        handcrafted_seed,
        instance,
        var_to_index
    )

    print_solution("Handcrafted seed", handcrafted_result)

    # ------------------------------------------------------------
    # Run seeded search from handcrafted schedule
    # ------------------------------------------------------------
    print()
    print("=== Running search from handcrafted seed ===")

    hc_search = seeded_time_indexed_local_search(
        instance=instance,
        var_to_index=var_to_index,
        seed_bitstring=handcrafted_seed,
        num_reads=30,
        num_steps=1000,
        initial_temperature=10.0,
        final_temperature=0.01,
        random_seed=2026
    )

    hc_best_result = hc_search["best_result"]

    print_solution("Best search result from handcrafted seed", hc_best_result)

    # ------------------------------------------------------------
    # Run seeded search from CP-SAT solution if available
    # ------------------------------------------------------------
    cpsat_search = None
    cpsat_best_result = None

    if cpsat_seed is not None:
        print()
        print("=== Running search from CP-SAT seed ===")

        cpsat_search = seeded_time_indexed_local_search(
            instance=instance,
            var_to_index=var_to_index,
            seed_bitstring=cpsat_seed,
            num_reads=10,
            num_steps=500,
            initial_temperature=5.0,
            final_temperature=0.01,
            random_seed=3030
        )

        cpsat_best_result = cpsat_search["best_result"]

        print_solution("Best search result from CP-SAT seed", cpsat_best_result)

    # ------------------------------------------------------------
    # Save read-level results
    # ------------------------------------------------------------
    rows = []

    def add_rows(search_name, search_result):
        for item in search_result["all_results"]:
            result = item["result"]

            gap_to_cpsat = None
            if cpsat_cost is not None:
                gap_to_cpsat = result["total_cost"] - cpsat_cost

            rows.append({
                "search_name": search_name,
                "read": item["read"],
                "bitstring": format_bitstring(item["best_bitstring"]),
                "best_cost": item["best_cost"],
                "feasible": result["feasible"],
                "num_violations": result["num_violations"],
                "processing": result["processing"],
                "start_time": result["start_time"],
                "workload": result["workload"],
                "ergonomic": result["ergonomic"],
                "safety": result["safety"],
                "original_cost": result["original_cost"],
                "assignment_start_penalty": result["assignment_start_penalty"],
                "skill_penalty": result["skill_penalty"],
                "horizon_penalty": result["horizon_penalty"],
                "precedence_penalty": result["precedence_penalty"],
                "resource_overlap_penalty": result["resource_overlap_penalty"],
                "robot_utilization_penalty": result["robot_utilization_penalty"],
                "total_penalty": result["total_penalty"],
                "total_cost": result["total_cost"],
                "gap_to_cpsat": gap_to_cpsat,
                "schedule": str(result["schedule"])
            })

    add_rows("seeded_from_handcrafted", hc_search)

    if cpsat_search is not None:
        add_rows("seeded_from_cpsat", cpsat_search)

    df = pd.DataFrame(rows)

    output_path = PROJECT_ROOT / "results" / "tables" / "sample_3x3_augmented_seeded_search_results.csv"
    df.to_csv(output_path, index=False)

    print()
    print("Saved seeded search results to:", output_path)

    # ------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------
    feasible_df = df[df["feasible"] == True]

    print()
    print("=" * 70)
    print("Seeded search summary")
    print("=" * 70)
    print("Total reads:", len(df))
    print("Feasible reads:", len(feasible_df))
    print("Feasibility rate:", len(feasible_df) / len(df))

    if len(feasible_df) > 0:
        best = feasible_df.sort_values("total_cost").iloc[0]
        print("Best feasible cost:", best["total_cost"])

        if cpsat_cost is not None:
            print("Best feasible gap to CP-SAT:", best["total_cost"] - cpsat_cost)

    print("Handcrafted seed cost:", handcrafted_result["total_cost"])

    if cpsat_cost is not None:
        print("CP-SAT cost:", cpsat_cost)


if __name__ == "__main__":
    main()
