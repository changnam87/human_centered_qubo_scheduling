import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

import pandas as pd

from src.core.instance import load_instance
from src.core.time_indexed_variables import create_time_indexed_variable_mapping
from src.solvers.time_indexed_local_search import seeded_time_indexed_local_search


def format_bitstring(bitstring):
    return "".join(str(int(v)) for v in bitstring)


def load_seed_bitstring(bitstring_text, num_variables):
    bitstring_text = str(bitstring_text).strip()
    bitstring_text = bitstring_text.zfill(num_variables)
    return [int(ch) for ch in bitstring_text]


def summarize_search(search_name, search_result, cpsat_cost):
    rows = []

    for item in search_result["all_results"]:
        result = item["result"]

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
            "cpsat_cost": cpsat_cost,
            "gap_to_cpsat": result["total_cost"] - cpsat_cost,
            "schedule": str(result["schedule"])
        })

    return rows


def main():
    instance_path = PROJECT_ROOT / "data" / "augmented" / "sample_4x4_hc_seed2026_time_indexed.json"
    cpsat_path = PROJECT_ROOT / "results" / "tables" / "sample_4x4_augmented_cpsat_result.csv"

    output_reads_path = PROJECT_ROOT / "results" / "tables" / "sample_4x4_augmented_seeded_search_results.csv"
    output_summary_path = PROJECT_ROOT / "results" / "tables" / "sample_4x4_augmented_seeded_search_summary.csv"

    print("=== sample_4x4 structure-aware seeded search ===")
    print("Instance:", instance_path)

    if not cpsat_path.exists():
        print("Missing CP-SAT result:", cpsat_path)
        print("Run this first:")
        print("python experiments/run_sample_4x4_augmented_cpsat.py")
        return

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

    cpsat_df = pd.read_csv(cpsat_path, dtype={"bitstring": str})
    cpsat_row = cpsat_df.iloc[0]

    cpsat_cost = float(cpsat_row["total_cost"])
    cpsat_seed = load_seed_bitstring(cpsat_row["bitstring"], num_variables)

    print()
    print("CP-SAT cost:", cpsat_cost)
    print("CP-SAT status:", cpsat_row["status"])

    all_rows = []

    # ------------------------------------------------------------
    # Search A: structure-aware random assignment-valid seed
    # ------------------------------------------------------------
    print()
    print("=== Running structure-aware search from random assignment-valid seeds ===")

    random_search = seeded_time_indexed_local_search(
        instance=instance,
        var_to_index=var_to_index,
        seed_bitstring=None,
        num_reads=20,
        num_steps=1000,
        initial_temperature=10.0,
        final_temperature=0.01,
        random_seed=2026
    )

    all_rows.extend(
        summarize_search(
            "structure_aware_random_seed",
            random_search,
            cpsat_cost
        )
    )

    # ------------------------------------------------------------
    # Search B: CP-SAT warm-start ablation
    # ------------------------------------------------------------
    print()
    print("=== Running structure-aware search from CP-SAT seed ===")

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

    all_rows.extend(
        summarize_search(
            "structure_aware_cpsat_seed",
            cpsat_search,
            cpsat_cost
        )
    )

    read_df = pd.DataFrame(all_rows)
    read_df.to_csv(output_reads_path, index=False)

    # ------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------
    summary_rows = []

    for search_name, group in read_df.groupby("search_name"):
        total_reads = len(group)
        feasible_group = group[group["feasible"] == True]
        feasible_reads = len(feasible_group)
        feasibility_rate = feasible_reads / total_reads
        zero_penalty_rate = (abs(group["total_penalty"]) < 1e-9).sum() / total_reads

        if feasible_reads > 0:
            best_feasible_cost = float(feasible_group["total_cost"].min())
            mean_feasible_cost = float(feasible_group["total_cost"].mean())
            best_gap_to_cpsat = float(feasible_group["gap_to_cpsat"].min())
            mean_gap_to_cpsat = float(feasible_group["gap_to_cpsat"].mean())
        else:
            best_feasible_cost = None
            mean_feasible_cost = None
            best_gap_to_cpsat = None
            mean_gap_to_cpsat = None

        summary_rows.append({
            "search_name": search_name,
            "cpsat_cost": cpsat_cost,
            "total_reads": total_reads,
            "feasible_reads": feasible_reads,
            "feasibility_rate": feasibility_rate,
            "zero_penalty_rate": zero_penalty_rate,
            "best_feasible_cost": best_feasible_cost,
            "mean_feasible_cost": mean_feasible_cost,
            "best_gap_to_cpsat": best_gap_to_cpsat,
            "mean_gap_to_cpsat": mean_gap_to_cpsat
        })

    summary_df = pd.DataFrame(summary_rows)
    summary_df.to_csv(output_summary_path, index=False)

    print()
    print("=== sample_4x4 seeded search summary ===")
    print(summary_df)

    print()
    print("Saved read-level results to:", output_reads_path)
    print("Saved summary to:", output_summary_path)


if __name__ == "__main__":
    main()
