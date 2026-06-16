import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

import pandas as pd


def bool_value(x):
    if isinstance(x, bool):
        return x
    return str(x).lower() == "true"


def add_solution_row(
    rows,
    instance_name,
    solver_or_solution,
    role,
    status,
    row,
    cpsat_cost,
    handcrafted_cost,
    notes
):
    total_cost = float(row["total_cost"])
    improvement = handcrafted_cost - total_cost
    improvement_percent = improvement / handcrafted_cost * 100.0

    rows.append({
        "instance_name": instance_name,
        "solver_or_solution": solver_or_solution,
        "role": role,
        "status": status,
        "num_operations": int(row.get("num_operations", 9)),
        "num_resources": int(row.get("num_resources", 6)),
        "num_time_slots": int(row.get("num_time_slots", 34)),
        "num_binary_variables": int(row.get("num_binary_variables", 1836)),
        "selected_variables": int(row.get("selected_variables", 9)),
        "feasible": bool_value(row["feasible"]),
        "num_violations": int(row["num_violations"]),
        "processing": float(row["processing"]),
        "start_time": float(row["start_time"]),
        "workload": float(row["workload"]),
        "ergonomic": float(row["ergonomic"]),
        "safety": float(row["safety"]),
        "original_cost": float(row["original_cost"]),
        "total_penalty": float(row["total_penalty"]),
        "total_cost": total_cost,
        "gap_to_cpsat": total_cost - cpsat_cost,
        "improvement_over_handcrafted": improvement,
        "improvement_percent_over_handcrafted": improvement_percent,
        "notes": notes
    })


def main():
    tables_dir = PROJECT_ROOT / "results" / "tables"

    handcrafted_path = tables_dir / "sample_3x3_augmented_qubo_validation.csv"
    cpsat_path = tables_dir / "sample_3x3_augmented_cpsat_result.csv"
    seeded_path = tables_dir / "sample_3x3_augmented_seeded_search_results.csv"

    required_files = [
        handcrafted_path,
        cpsat_path,
        seeded_path
    ]

    print("=== Checking required files ===")

    for path in required_files:
        if path.exists():
            print("Found:", path)
        else:
            print("Missing:", path)
            print("Please generate missing files before running this script.")
            return

    print()
    print("=== Loading results ===")

    handcrafted_df = pd.read_csv(handcrafted_path, dtype={"bitstring": str})
    cpsat_df = pd.read_csv(cpsat_path, dtype={"bitstring": str})
    seeded_df = pd.read_csv(seeded_path, dtype={"bitstring": str})

    handcrafted = handcrafted_df.iloc[0]
    cpsat = cpsat_df.iloc[0]

    instance_name = handcrafted["instance_name"]

    handcrafted_cost = float(handcrafted["total_cost"])
    cpsat_cost = float(cpsat["total_cost"])

    rows = []

    # ------------------------------------------------------------
    # Handcrafted reference
    # ------------------------------------------------------------
    rows.append({
        "instance_name": instance_name,
        "solver_or_solution": "Handcrafted feasible schedule",
        "role": "Initial feasible reference",
        "status": "FEASIBLE",
        "num_operations": int(handcrafted["num_operations"]),
        "num_resources": int(handcrafted["num_resources"]),
        "num_time_slots": int(handcrafted["num_time_slots"]),
        "num_binary_variables": int(handcrafted["num_binary_variables"]),
        "selected_variables": int(handcrafted["selected_variables"]),
        "feasible": bool_value(handcrafted["feasible"]),
        "num_violations": int(handcrafted["num_violations"]),
        "processing": float(handcrafted["processing"]),
        "start_time": float(handcrafted["start_time"]),
        "workload": float(handcrafted["workload"]),
        "ergonomic": float(handcrafted["ergonomic"]),
        "safety": float(handcrafted["safety"]),
        "original_cost": float(handcrafted["original_cost"]),
        "total_penalty": float(handcrafted["total_penalty"]),
        "total_cost": handcrafted_cost,
        "gap_to_cpsat": handcrafted_cost - cpsat_cost,
        "improvement_over_handcrafted": 0.0,
        "improvement_percent_over_handcrafted": 0.0,
        "notes": "Handcrafted schedule used for first QUBO validation."
    })

    # ------------------------------------------------------------
    # CP-SAT
    # ------------------------------------------------------------
    rows.append({
        "instance_name": instance_name,
        "solver_or_solution": "CP-SAT",
        "role": "Classical exact/strong baseline",
        "status": cpsat["status"],
        "num_operations": int(cpsat["num_operations"]),
        "num_resources": int(cpsat["num_resources"]),
        "num_time_slots": int(cpsat["num_time_slots"]),
        "num_binary_variables": int(cpsat["num_binary_variables"]),
        "selected_variables": int(cpsat["selected_variables"]),
        "feasible": bool_value(cpsat["feasible"]),
        "num_violations": int(cpsat["num_violations"]),
        "processing": float(cpsat["processing"]),
        "start_time": float(cpsat["start_time"]),
        "workload": float(cpsat["workload"]),
        "ergonomic": float(cpsat["ergonomic"]),
        "safety": float(cpsat["safety"]),
        "original_cost": float(cpsat["original_cost"]),
        "total_penalty": float(cpsat["total_penalty"]),
        "total_cost": cpsat_cost,
        "gap_to_cpsat": 0.0,
        "improvement_over_handcrafted": handcrafted_cost - cpsat_cost,
        "improvement_percent_over_handcrafted": (handcrafted_cost - cpsat_cost) / handcrafted_cost * 100.0,
        "notes": "CP-SAT found the best known solution for the augmented sample instance."
    })

    # ------------------------------------------------------------
    # Seeded search: best from handcrafted seed
    # ------------------------------------------------------------
    seeded_hc = seeded_df[
        (seeded_df["search_name"] == "seeded_from_handcrafted")
        & (seeded_df["feasible"] == True)
    ]

    if len(seeded_hc) > 0:
        best_seeded_hc = seeded_hc.sort_values("total_cost").iloc[0]

        add_solution_row(
            rows=rows,
            instance_name=instance_name,
            solver_or_solution="Seeded structure-aware search from handcrafted",
            role="QUBO-compatible structure-aware heuristic",
            status="FEASIBLE",
            row=best_seeded_hc,
            cpsat_cost=cpsat_cost,
            handcrafted_cost=handcrafted_cost,
            notes="Best feasible solution from operation-level reassignment search seeded by handcrafted schedule."
        )

    # ------------------------------------------------------------
    # Seeded search: best from CP-SAT seed
    # ------------------------------------------------------------
    seeded_cpsat = seeded_df[
        (seeded_df["search_name"] == "seeded_from_cpsat")
        & (seeded_df["feasible"] == True)
    ]

    if len(seeded_cpsat) > 0:
        best_seeded_cpsat = seeded_cpsat.sort_values("total_cost").iloc[0]

        add_solution_row(
            rows=rows,
            instance_name=instance_name,
            solver_or_solution="Seeded structure-aware search from CP-SAT",
            role="QUBO-compatible structure-aware heuristic",
            status="FEASIBLE",
            row=best_seeded_cpsat,
            cpsat_cost=cpsat_cost,
            handcrafted_cost=handcrafted_cost,
            notes="Best feasible solution from operation-level reassignment search seeded by CP-SAT solution."
        )

    # ------------------------------------------------------------
    # Seeded search aggregate rows
    # ------------------------------------------------------------
    aggregate_rows = []

    for search_name, group in seeded_df.groupby("search_name"):
        total_reads = len(group)
        feasible_group = group[group["feasible"] == True]
        feasible_reads = len(feasible_group)
        feasibility_rate = feasible_reads / total_reads

        if feasible_reads > 0:
            best_feasible_cost = float(feasible_group["total_cost"].min())
            mean_feasible_cost = float(feasible_group["total_cost"].mean())
            best_gap_to_cpsat = best_feasible_cost - cpsat_cost
        else:
            best_feasible_cost = None
            mean_feasible_cost = None
            best_gap_to_cpsat = None

        aggregate_rows.append({
            "search_name": search_name,
            "total_reads": total_reads,
            "feasible_reads": feasible_reads,
            "feasibility_rate": feasibility_rate,
            "best_feasible_cost": best_feasible_cost,
            "mean_feasible_cost": mean_feasible_cost,
            "best_gap_to_cpsat": best_gap_to_cpsat
        })

    aggregate_df = pd.DataFrame(aggregate_rows)

    summary_df = pd.DataFrame(rows)

    output_path = tables_dir / "sample_3x3_augmented_solver_summary.csv"
    aggregate_path = tables_dir / "sample_3x3_augmented_seeded_search_summary.csv"

    summary_df.to_csv(output_path, index=False)
    aggregate_df.to_csv(aggregate_path, index=False)

    print()
    print("=== sample_3x3 augmented solver summary ===")
    print(summary_df[[
        "solver_or_solution",
        "status",
        "feasible",
        "num_violations",
        "processing",
        "start_time",
        "workload",
        "ergonomic",
        "safety",
        "total_penalty",
        "total_cost",
        "gap_to_cpsat",
        "improvement_over_handcrafted",
        "improvement_percent_over_handcrafted"
    ]])

    print()
    print("=== seeded search aggregate summary ===")
    print(aggregate_df)

    print()
    print("Saved solver summary to:", output_path)
    print("Saved seeded search summary to:", aggregate_path)


if __name__ == "__main__":
    main()
