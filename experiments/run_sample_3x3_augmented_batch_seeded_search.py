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


def load_seed_bitstring(bitstring_text, num_variables):
    """
    Load long bitstring safely as string and pad leading zeros if needed.
    """
    bitstring_text = str(bitstring_text).strip()
    bitstring_text = bitstring_text.zfill(num_variables)
    return [int(ch) for ch in bitstring_text]


def main():
    batch_summary_path = PROJECT_ROOT / "results" / "tables" / "sample_3x3_augmented_batch_instance_summary.csv"
    cpsat_path = PROJECT_ROOT / "results" / "tables" / "sample_3x3_augmented_batch_cpsat_results.csv"

    output_reads_path = PROJECT_ROOT / "results" / "tables" / "sample_3x3_augmented_batch_seeded_search_results.csv"
    output_summary_path = PROJECT_ROOT / "results" / "tables" / "sample_3x3_augmented_batch_seeded_search_summary.csv"

    required_files = [
        batch_summary_path,
        cpsat_path
    ]

    print("=== Checking required files ===")

    for path in required_files:
        if path.exists():
            print("Found:", path)
        else:
            print("Missing:", path)
            return

    batch_df = pd.read_csv(batch_summary_path)
    cpsat_df = pd.read_csv(cpsat_path, dtype={"bitstring": str})

    read_rows = []
    summary_rows = []

    print()
    print("=== Running batch seeded structure-aware search ===")
    print("Number of instances:", len(batch_df))

    for _, batch_row in batch_df.iterrows():
        seed = int(batch_row["seed"])
        instance_path = PROJECT_ROOT / batch_row["output_file"]

        print()
        print("=" * 70)
        print("Seed:", seed)
        print("Instance:", instance_path)
        print("=" * 70)

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

        cpsat_row = cpsat_df[cpsat_df["seed"] == seed].iloc[0]
        cpsat_cost = float(cpsat_row["total_cost"])
        cpsat_bitstring = load_seed_bitstring(cpsat_row["bitstring"], num_variables)

        # ------------------------------------------------------------
        # Search A: random assignment-valid starts
        # No seed bitstring. This is not random-bit SA.
        # It preserves assignment, skill, and horizon by construction.
        # ------------------------------------------------------------
        print("Running structure-aware search from random assignment-valid seeds...")

        random_seed_search = seeded_time_indexed_local_search(
            instance=instance,
            var_to_index=var_to_index,
            seed_bitstring=None,
            num_reads=20,
            num_steps=1000,
            initial_temperature=10.0,
            final_temperature=0.01,
            random_seed=seed
        )

        # ------------------------------------------------------------
        # Search B: CP-SAT warm-start ablation
        # ------------------------------------------------------------
        print("Running structure-aware search from CP-SAT seed...")

        cpsat_seed_search = seeded_time_indexed_local_search(
            instance=instance,
            var_to_index=var_to_index,
            seed_bitstring=cpsat_bitstring,
            num_reads=10,
            num_steps=500,
            initial_temperature=5.0,
            final_temperature=0.01,
            random_seed=seed + 10000
        )

        searches = [
            ("structure_aware_random_seed", random_seed_search),
            ("structure_aware_cpsat_seed", cpsat_seed_search)
        ]

        for search_name, search_result in searches:
            for item in search_result["all_results"]:
                result = item["result"]

                read_rows.append({
                    "seed": seed,
                    "instance_file": str(instance_path.relative_to(PROJECT_ROOT)),
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

        # Per-instance summary
        for search_name, search_result in searches:
            rows = []

            for item in search_result["all_results"]:
                result = item["result"]
                rows.append({
                    "feasible": result["feasible"],
                    "total_penalty": result["total_penalty"],
                    "total_cost": result["total_cost"],
                    "gap_to_cpsat": result["total_cost"] - cpsat_cost
                })

            df = pd.DataFrame(rows)
            feasible_df = df[df["feasible"] == True]

            total_reads = len(df)
            feasible_reads = len(feasible_df)
            feasibility_rate = feasible_reads / total_reads
            zero_penalty_rate = (abs(df["total_penalty"]) < 1e-9).sum() / total_reads

            if feasible_reads > 0:
                best_feasible_cost = float(feasible_df["total_cost"].min())
                mean_feasible_cost = float(feasible_df["total_cost"].mean())
                best_gap_to_cpsat = float(feasible_df["gap_to_cpsat"].min())
                mean_gap_to_cpsat = float(feasible_df["gap_to_cpsat"].mean())
            else:
                best_feasible_cost = None
                mean_feasible_cost = None
                best_gap_to_cpsat = None
                mean_gap_to_cpsat = None

            summary_rows.append({
                "seed": seed,
                "instance_file": str(instance_path.relative_to(PROJECT_ROOT)),
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

            print()
            print("Search:", search_name)
            print("CP-SAT cost:", cpsat_cost)
            print("Feasibility rate:", feasibility_rate)
            print("Best feasible cost:", best_feasible_cost)
            print("Best gap to CP-SAT:", best_gap_to_cpsat)

    read_df = pd.DataFrame(read_rows)
    summary_df = pd.DataFrame(summary_rows)

    read_df.to_csv(output_reads_path, index=False)
    summary_df.to_csv(output_summary_path, index=False)

    print()
    print("=== Batch seeded search completed ===")
    print("Saved read-level results to:", output_reads_path)
    print("Saved summary to:", output_summary_path)

    print()
    print(summary_df[[
        "seed",
        "search_name",
        "cpsat_cost",
        "total_reads",
        "feasible_reads",
        "feasibility_rate",
        "best_feasible_cost",
        "best_gap_to_cpsat",
        "mean_gap_to_cpsat"
    ]])


if __name__ == "__main__":
    main()
