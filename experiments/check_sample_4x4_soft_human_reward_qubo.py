import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

import pandas as pd

from src.core.instance import load_instance
from src.core.time_indexed_variables import create_time_indexed_variable_mapping
from src.core.time_indexed_qubo import (
    build_time_indexed_qubo_matrix,
    time_indexed_qubo_energy
)


def load_bitstring(bitstring_text, num_variables):
    bitstring_text = str(bitstring_text).strip()
    bitstring_text = bitstring_text.zfill(num_variables)
    return [int(ch) for ch in bitstring_text]


def main():
    instance_path = PROJECT_ROOT / "data" / "augmented" / "sample_4x4_hc_seed2026_time_indexed.json"

    soft_reward_path = PROJECT_ROOT / "results" / "tables" / "sample_4x4_soft_human_reward_sensitivity.csv"

    output_path = PROJECT_ROOT / "results" / "tables" / "sample_4x4_soft_human_reward_qubo_validation.csv"

    print("=== sample_4x4 soft human-reward QUBO validation ===")
    print("Instance:", instance_path)
    print("Soft reward results:", soft_reward_path)

    if not soft_reward_path.exists():
        print("Missing:", soft_reward_path)
        print("Run this first:")
        print("python experiments/run_sample_4x4_soft_human_reward_sensitivity.py")
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

    soft_df = pd.read_csv(soft_reward_path, dtype={"bitstring": str})

    rows = []

    for _, row in soft_df.iterrows():
        human_reward = float(row["human_reward"])
        bitstring = load_bitstring(row["bitstring"], num_variables)

        total_cost_without_reward = float(row["total_cost_without_reward"])
        human_assignment_count = int(row["human_assignment_count"])
        reward_value = float(row["reward_value"])
        expected_reward_adjusted_objective = float(row["reward_adjusted_objective"])

        expected_manual = total_cost_without_reward - human_reward * human_assignment_count

        print()
        print("=" * 70)
        print("human_reward:", human_reward)
        print("=" * 70)

        print("Building QUBO matrix with human_reward =", human_reward)

        Q, constant_offset = build_time_indexed_qubo_matrix(
            instance,
            var_to_index,
            human_reward=human_reward
        )

        qubo_energy = time_indexed_qubo_energy(
            bitstring,
            Q,
            constant_offset=constant_offset
        )

        error_vs_expected_objective = qubo_energy - expected_reward_adjusted_objective
        abs_error_vs_expected_objective = abs(error_vs_expected_objective)

        error_vs_manual = qubo_energy - expected_manual
        abs_error_vs_manual = abs(error_vs_manual)

        print("Total cost without reward:", total_cost_without_reward)
        print("Human assignment count:", human_assignment_count)
        print("Reward value:", reward_value)
        print("Expected reward-adjusted objective:", expected_reward_adjusted_objective)
        print("Expected manual:", expected_manual)
        print("QUBO energy:", qubo_energy)
        print("Absolute error vs expected objective:", abs_error_vs_expected_objective)
        print("Absolute error vs manual:", abs_error_vs_manual)

        rows.append({
            "human_reward": human_reward,
            "num_operations": len(operations),
            "num_resources": len(resources),
            "num_time_slots": len(time_slots),
            "num_binary_variables": num_variables,
            "human_assignment_count": human_assignment_count,
            "total_cost_without_reward": total_cost_without_reward,
            "reward_value": reward_value,
            "expected_reward_adjusted_objective": expected_reward_adjusted_objective,
            "expected_manual": expected_manual,
            "qubo_energy": qubo_energy,
            "error_vs_expected_objective": error_vs_expected_objective,
            "abs_error_vs_expected_objective": abs_error_vs_expected_objective,
            "error_vs_manual": error_vs_manual,
            "abs_error_vs_manual": abs_error_vs_manual,
            "pass_expected_objective": abs_error_vs_expected_objective < 1e-6,
            "pass_manual": abs_error_vs_manual < 1e-6
        })

    result_df = pd.DataFrame(rows)
    result_df.to_csv(output_path, index=False)

    max_error = result_df["abs_error_vs_expected_objective"].max()

    print()
    print("=" * 70)
    print("Validation summary")
    print("=" * 70)
    print("Maximum absolute error:", max_error)

    if max_error < 1e-6:
        print("PASS: Soft human-reward QUBO energy matches reward-adjusted objective.")
    else:
        print("FAIL: Soft human-reward QUBO energy does not match reward-adjusted objective.")

    print()
    print("Saved validation results to:", output_path)


if __name__ == "__main__":
    main()
