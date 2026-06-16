import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

import pandas as pd


def bool_value(x):
    if isinstance(x, bool):
        return x
    return str(x).lower() == "true"


def main():
    tables_dir = PROJECT_ROOT / "results" / "tables"

    random_sa_path = tables_dir / "sample_3x3_augmented_sa_results.csv"
    seeded_results_path = tables_dir / "sample_3x3_augmented_seeded_search_results.csv"
    cpsat_path = tables_dir / "sample_3x3_augmented_cpsat_result.csv"
    handcrafted_path = tables_dir / "sample_3x3_augmented_qubo_validation.csv"

    required_files = [
        random_sa_path,
        seeded_results_path,
        cpsat_path,
        handcrafted_path
    ]

    print("=== Checking required files ===")

    for path in required_files:
        if path.exists():
            print("Found:", path)
        else:
            print("Missing:", path)
            print("Please generate missing files before running this script.")
            return

    random_sa_df = pd.read_csv(random_sa_path, dtype={"bitstring": str})
    seeded_df = pd.read_csv(seeded_results_path, dtype={"bitstring": str})
    cpsat_df = pd.read_csv(cpsat_path, dtype={"bitstring": str})
    handcrafted_df = pd.read_csv(handcrafted_path, dtype={"bitstring": str})

    cpsat_cost = float(cpsat_df.iloc[0]["total_cost"])
    handcrafted_cost = float(handcrafted_df.iloc[0]["total_cost"])

    rows = []

    # ------------------------------------------------------------
    # Random-bit SA summary
    # ------------------------------------------------------------
    random_total_reads = len(random_sa_df)
    random_feasible_df = random_sa_df[random_sa_df["feasible"] == True]
    random_feasible_reads = len(random_feasible_df)
    random_feasibility_rate = random_feasible_reads / random_total_reads

    random_zero_penalty_reads = int((abs(random_sa_df["total_penalty"]) < 1e-9).sum())
    random_zero_penalty_rate = random_zero_penalty_reads / random_total_reads

    if random_feasible_reads > 0:
        random_best_feasible_cost = float(random_feasible_df["total_cost"].min())
        random_mean_feasible_cost = float(random_feasible_df["total_cost"].mean())
        random_best_gap_to_cpsat = random_best_feasible_cost - cpsat_cost
    else:
        random_best_feasible_cost = None
        random_mean_feasible_cost = None
        random_best_gap_to_cpsat = None

    rows.append({
        "method": "Random-bit simulated annealing",
        "move_type": "Single arbitrary bit flip",
        "seed_type": "Random full bitstring",
        "total_reads": random_total_reads,
        "feasible_reads": random_feasible_reads,
        "feasibility_rate": random_feasibility_rate,
        "zero_penalty_reads": random_zero_penalty_reads,
        "zero_penalty_rate": random_zero_penalty_rate,
        "best_feasible_cost": random_best_feasible_cost,
        "mean_feasible_cost": random_mean_feasible_cost,
        "cpsat_cost": cpsat_cost,
        "handcrafted_cost": handcrafted_cost,
        "best_gap_to_cpsat": random_best_gap_to_cpsat,
        "best_improvement_over_handcrafted": None if random_best_feasible_cost is None else handcrafted_cost - random_best_feasible_cost,
        "notes": "Naive bit-level SA on 1836 variables; expected to struggle with feasibility."
    })

    # ------------------------------------------------------------
    # Structure-aware seeded search summaries by seed type
    # ------------------------------------------------------------
    for search_name, group in seeded_df.groupby("search_name"):
        total_reads = len(group)
        feasible_group = group[group["feasible"] == True]
        feasible_reads = len(feasible_group)
        feasibility_rate = feasible_reads / total_reads

        zero_penalty_reads = int((abs(group["total_penalty"]) < 1e-9).sum())
        zero_penalty_rate = zero_penalty_reads / total_reads

        if feasible_reads > 0:
            best_feasible_cost = float(feasible_group["total_cost"].min())
            mean_feasible_cost = float(feasible_group["total_cost"].mean())
            best_gap_to_cpsat = best_feasible_cost - cpsat_cost
            best_improvement_over_handcrafted = handcrafted_cost - best_feasible_cost
        else:
            best_feasible_cost = None
            mean_feasible_cost = None
            best_gap_to_cpsat = None
            best_improvement_over_handcrafted = None

        if search_name == "seeded_from_handcrafted":
            seed_type = "Handcrafted feasible seed"
            method_label = "Structure-aware seeded search from handcrafted"
        elif search_name == "seeded_from_cpsat":
            seed_type = "CP-SAT optimal seed"
            method_label = "Structure-aware seeded search from CP-SAT"
        else:
            seed_type = search_name
            method_label = "Structure-aware seeded search"

        rows.append({
            "method": method_label,
            "move_type": "Operation-level resource/time reassignment",
            "seed_type": seed_type,
            "total_reads": total_reads,
            "feasible_reads": feasible_reads,
            "feasibility_rate": feasibility_rate,
            "zero_penalty_reads": zero_penalty_reads,
            "zero_penalty_rate": zero_penalty_rate,
            "best_feasible_cost": best_feasible_cost,
            "mean_feasible_cost": mean_feasible_cost,
            "cpsat_cost": cpsat_cost,
            "handcrafted_cost": handcrafted_cost,
            "best_gap_to_cpsat": best_gap_to_cpsat,
            "best_improvement_over_handcrafted": best_improvement_over_handcrafted,
            "notes": "Preserves assignment-start validity, skill compatibility, and horizon feasibility by construction."
        })

    comparison_df = pd.DataFrame(rows)

    output_path = tables_dir / "sample_3x3_augmented_search_method_comparison.csv"
    comparison_df.to_csv(output_path, index=False)

    print()
    print("=== Search method comparison ===")
    print(comparison_df[[
        "method",
        "total_reads",
        "feasible_reads",
        "feasibility_rate",
        "zero_penalty_rate",
        "best_feasible_cost",
        "mean_feasible_cost",
        "best_gap_to_cpsat",
        "best_improvement_over_handcrafted"
    ]])

    print()
    print("Saved comparison to:", output_path)


if __name__ == "__main__":
    main()
