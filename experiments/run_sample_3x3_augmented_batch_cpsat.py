import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

import pandas as pd
from ortools.sat.python import cp_model

from src.core.instance import load_instance
from src.core.time_indexed_variables import create_time_indexed_variable_mapping
from src.core.time_indexed_evaluate import evaluate_time_indexed_solution


def get_workers(instance):
    if "workers" in instance:
        return instance["workers"]
    if "H" in instance["resources"]:
        return ["H"]
    return []


def get_robots(instance):
    if "robots" in instance:
        return instance["robots"]
    if "R" in instance["resources"]:
        return ["R"]
    return []


def get_safety_risk(instance):
    if "robot_safety_risk" in instance:
        return instance["robot_safety_risk"]
    return instance["safety_risk"]


def make_empty_bitstring(num_variables):
    return [0] * num_variables


def set_start(bitstring, operation, resource, time, var_to_index):
    index = var_to_index[(operation, resource, time)]
    bitstring[index] = 1


def format_bitstring(bitstring):
    return "".join(str(int(v)) for v in bitstring)


def solve_instance_with_cpsat(instance, time_limit_seconds=60, num_workers=8):
    operations = instance["operations"]
    resources = instance["resources"]
    time_slots = instance["time_slots"]
    workers = get_workers(instance)
    robots = get_robots(instance)

    processing_time = instance["processing_time"]
    processing_cost = instance["processing_cost"]
    skill_compatibility = instance["skill_compatibility"]
    precedence = instance["precedence"]

    workload_score = instance["workload_score"]
    ergonomic_risk = instance["ergonomic_risk"]
    safety_risk = get_safety_risk(instance)

    lambda_processing = instance["weights"]["lambda_processing"]
    lambda_start_time = instance["weights"]["lambda_start_time"]
    lambda_workload = instance["weights"]["lambda_workload"]
    lambda_ergonomic = instance["weights"]["lambda_ergonomic"]
    lambda_safety = instance["weights"]["lambda_safety"]

    planning_horizon = instance["planning_horizon"]

    variable_names, index_to_var, var_to_index = create_time_indexed_variable_mapping(
        operations,
        resources,
        time_slots
    )

    num_variables = len(variable_names)

    model = cp_model.CpModel()
    x = {}

    # ------------------------------------------------------------
    # Create variables
    # ------------------------------------------------------------
    for operation in operations:
        for resource in resources:
            for time in time_slots:
                duration = processing_time[operation][resource]
                end_time = time + duration

                if end_time <= planning_horizon:
                    x[(operation, resource, time)] = model.NewBoolVar(
                        f"x_{operation}_{resource}_{time}"
                    )

    # ------------------------------------------------------------
    # Each operation starts exactly once
    # ------------------------------------------------------------
    for operation in operations:
        candidates = []

        for resource in resources:
            for time in time_slots:
                key = (operation, resource, time)

                if key in x:
                    candidates.append(x[key])

        model.Add(sum(candidates) == 1)

    # ------------------------------------------------------------
    # Skill compatibility
    # ------------------------------------------------------------
    for operation in operations:
        for resource in resources:
            if skill_compatibility[operation][resource] == 0:
                for time in time_slots:
                    key = (operation, resource, time)

                    if key in x:
                        model.Add(x[key] == 0)

    # ------------------------------------------------------------
    # Precedence
    # ------------------------------------------------------------
    for before, after in precedence:
        before_start_terms = []
        before_duration_terms = []
        after_start_terms = []

        for resource in resources:
            for time in time_slots:
                before_key = (before, resource, time)
                after_key = (after, resource, time)

                if before_key in x:
                    before_start_terms.append(time * x[before_key])
                    before_duration_terms.append(
                        processing_time[before][resource] * x[before_key]
                    )

                if after_key in x:
                    after_start_terms.append(time * x[after_key])

        model.Add(
            sum(before_start_terms) + sum(before_duration_terms)
            <= sum(after_start_terms)
        )

    # ------------------------------------------------------------
    # Resource no-overlap
    # ------------------------------------------------------------
    for resource in resources:
        for tau in range(planning_horizon):
            active_terms = []

            for operation in operations:
                for start in time_slots:
                    key = (operation, resource, start)

                    if key not in x:
                        continue

                    duration = processing_time[operation][resource]
                    end = start + duration

                    if start <= tau < end:
                        active_terms.append(x[key])

            if active_terms:
                model.Add(sum(active_terms) <= 1)

    # ------------------------------------------------------------
    # Robot utilization soft objective
    # ------------------------------------------------------------
    robot_use_terms = []

    for operation in operations:
        for robot in robots:
            for time in time_slots:
                key = (operation, robot, time)

                if key in x:
                    robot_use_terms.append(x[key])

    robot_use = model.NewIntVar(0, len(operations), "robot_use")

    if robot_use_terms:
        model.Add(robot_use == sum(robot_use_terms))
    else:
        model.Add(robot_use == 0)

    robot_target = instance["penalties"]["robot_utilization_target"]

    robot_deviation = model.NewIntVar(0, len(operations), "robot_deviation")
    model.AddAbsEquality(robot_deviation, robot_use - robot_target)

    # ------------------------------------------------------------
    # Objective
    # ------------------------------------------------------------
    SCALE = 10
    objective_terms = []

    for operation in operations:
        for resource in resources:
            for time in time_slots:
                key = (operation, resource, time)

                if key not in x:
                    continue

                coeff = 0.0
                coeff += lambda_processing * processing_cost[operation][resource]
                coeff += lambda_start_time * time

                if resource in workers:
                    coeff += lambda_workload * workload_score[operation]
                    coeff += lambda_ergonomic * ergonomic_risk[operation]

                if resource in robots:
                    coeff += lambda_safety * safety_risk[operation]

                objective_terms.append(int(round(SCALE * coeff)) * x[key])

    P_robot = instance["penalties"]["P_robot_utilization"]
    objective_terms.append(int(round(SCALE * P_robot)) * robot_deviation)

    model.Minimize(sum(objective_terms))

    # ------------------------------------------------------------
    # Solve
    # ------------------------------------------------------------
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = time_limit_seconds
    solver.parameters.num_search_workers = num_workers

    status = solver.Solve(model)
    status_name = solver.StatusName(status)

    result = {
        "status": status_name,
        "objective_scaled": solver.ObjectiveValue() if status in [cp_model.OPTIMAL, cp_model.FEASIBLE] else None,
        "objective_unscaled": solver.ObjectiveValue() / SCALE if status in [cp_model.OPTIMAL, cp_model.FEASIBLE] else None,
        "wall_time": solver.WallTime(),
        "num_operations": len(operations),
        "num_resources": len(resources),
        "num_time_slots": len(time_slots),
        "num_binary_variables": num_variables,
        "bitstring": None,
        "selected_variables": None,
        "feasible": False,
        "num_violations": None,
        "processing": None,
        "start_time": None,
        "workload": None,
        "ergonomic": None,
        "safety": None,
        "original_cost": None,
        "assignment_start_penalty": None,
        "skill_penalty": None,
        "horizon_penalty": None,
        "precedence_penalty": None,
        "resource_overlap_penalty": None,
        "robot_utilization_penalty": None,
        "total_penalty": None,
        "total_cost": None,
        "schedule": None
    }

    if status not in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
        return result

    bitstring = make_empty_bitstring(num_variables)

    for operation in operations:
        for resource in resources:
            for time in time_slots:
                key = (operation, resource, time)

                if key in x and solver.Value(x[key]) == 1:
                    set_start(bitstring, operation, resource, time, var_to_index)

    decoded = evaluate_time_indexed_solution(
        bitstring,
        instance,
        var_to_index
    )

    result.update({
        "bitstring": format_bitstring(bitstring),
        "selected_variables": sum(bitstring),
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

    return result


def main():
    batch_summary_path = PROJECT_ROOT / "results" / "tables" / "sample_3x3_augmented_batch_instance_summary.csv"

    output_path = PROJECT_ROOT / "results" / "tables" / "sample_3x3_augmented_batch_cpsat_results.csv"

    if not batch_summary_path.exists():
        print("Missing batch summary:", batch_summary_path)
        print("Run this first:")
        print("python experiments/generate_sample_3x3_augmented_batch.py")
        return

    batch_df = pd.read_csv(batch_summary_path)

    rows = []

    print("=== Running batch CP-SAT baseline ===")
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

        result = solve_instance_with_cpsat(
            instance,
            time_limit_seconds=60,
            num_workers=8
        )

        row = {
            "base_instance": batch_row["base_instance"],
            "seed": seed,
            "instance_file": str(instance_path.relative_to(PROJECT_ROOT)),
            **result
        }

        rows.append(row)

        print("Status:", result["status"])
        print("Feasible:", result["feasible"])
        print("Total cost:", result["total_cost"])
        print("Total penalty:", result["total_penalty"])
        print("Wall time:", result["wall_time"])

    results_df = pd.DataFrame(rows)
    results_df.to_csv(output_path, index=False)

    print()
    print("=== Batch CP-SAT completed ===")
    print("Saved results to:", output_path)

    print()
    print(results_df[[
        "seed",
        "status",
        "feasible",
        "total_cost",
        "processing",
        "start_time",
        "workload",
        "ergonomic",
        "safety",
        "total_penalty",
        "wall_time"
    ]])


if __name__ == "__main__":
    main()
