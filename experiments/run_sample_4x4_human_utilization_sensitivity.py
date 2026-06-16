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


def extract_resource(selected):
    """
    Robustly extract resource from evaluator schedule output.
    """
    resource = None

    if isinstance(selected, dict):
        resource = selected.get("resource")

    elif isinstance(selected, (list, tuple)):
        if len(selected) == 0:
            resource = None
        else:
            first = selected[0]

            if isinstance(first, dict):
                resource = first.get("resource")
            elif isinstance(first, (list, tuple)):
                resource = first[0]
            elif isinstance(first, str):
                resource = first

    return resource


def solve_with_min_human_assignments(instance, min_human_assignments):
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

    weights = instance["weights"]
    lambda_processing = weights["lambda_processing"]
    lambda_start_time = weights["lambda_start_time"]
    lambda_workload = weights["lambda_workload"]
    lambda_ergonomic = weights["lambda_ergonomic"]
    lambda_safety = weights["lambda_safety"]

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
    # Variables
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
    # Human utilization constraint
    # ------------------------------------------------------------
    human_use_terms = []

    for operation in operations:
        for worker in workers:
            for time in time_slots:
                key = (operation, worker, time)

                if key in x:
                    human_use_terms.append(x[key])

    human_assignments = model.NewIntVar(0, len(operations), "human_assignments")

    if human_use_terms:
        model.Add(human_assignments == sum(human_use_terms))
    else:
        model.Add(human_assignments == 0)

    model.Add(human_assignments >= min_human_assignments)

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
    solver.parameters.max_time_in_seconds = 120
    solver.parameters.num_search_workers = 8

    status = solver.Solve(model)
    status_name = solver.StatusName(status)

    row = {
        "min_human_assignments": min_human_assignments,
        "status": status_name,
        "objective_scaled": None,
        "objective_unscaled": None,
        "best_objective_bound_scaled": None,
        "best_objective_bound_unscaled": None,
        "wall_time": solver.WallTime(),
        "num_operations": len(operations),
        "num_resources": len(resources),
        "num_time_slots": len(time_slots),
        "num_binary_variables": num_variables,
        "bitstring": None,
        "selected_variables": None,
        "feasible": False,
        "num_violations": None,
        "human_assignment_count": None,
        "robot_assignment_count": None,
        "machine_assignment_count": None,
        "processing": None,
        "start_time": None,
        "workload": None,
        "ergonomic": None,
        "safety": None,
        "original_cost": None,
        "total_penalty": None,
        "total_cost": None,
        "schedule": None
    }

    if status not in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
        return row

    bitstring = make_empty_bitstring(num_variables)

    for operation in operations:
        for resource in resources:
            for time in time_slots:
                key = (operation, resource, time)

                if key in x and solver.Value(x[key]) == 1:
                    set_start(bitstring, operation, resource, time, var_to_index)

    result = evaluate_time_indexed_solution(
        bitstring,
        instance,
        var_to_index
    )

    human_count = 0
    robot_count = 0
    machine_count = 0

    for operation, selected in result["schedule"].items():
        resource = extract_resource(selected)

        if resource in workers:
            human_count += 1
        elif resource in robots:
            robot_count += 1
        elif resource is not None:
            machine_count += 1

    row.update({
        "objective_scaled": solver.ObjectiveValue(),
        "objective_unscaled": solver.ObjectiveValue() / SCALE,
        "best_objective_bound_scaled": solver.BestObjectiveBound(),
        "best_objective_bound_unscaled": solver.BestObjectiveBound() / SCALE,
        "bitstring": format_bitstring(bitstring),
        "selected_variables": sum(bitstring),
        "feasible": result["feasible"],
        "num_violations": result["num_violations"],
        "human_assignment_count": human_count,
        "robot_assignment_count": robot_count,
        "machine_assignment_count": machine_count,
        "processing": result["processing"],
        "start_time": result["start_time"],
        "workload": result["workload"],
        "ergonomic": result["ergonomic"],
        "safety": result["safety"],
        "original_cost": result["original_cost"],
        "total_penalty": result["total_penalty"],
        "total_cost": result["total_cost"],
        "schedule": str(result["schedule"])
    })

    return row


def main():
    instance_path = PROJECT_ROOT / "data" / "augmented" / "sample_4x4_hc_seed2026_time_indexed.json"
    output_path = PROJECT_ROOT / "results" / "tables" / "sample_4x4_human_utilization_sensitivity.csv"

    instance = load_instance(instance_path)

    min_values = [0, 1, 2, 3, 4]

    rows = []

    print("=== sample_4x4 human-utilization sensitivity ===")
    print("Instance:", instance_path)
    print("Minimum human assignment values:", min_values)

    for min_human_assignments in min_values:
        print()
        print("=" * 70)
        print("Solving min_human_assignments =", min_human_assignments)
        print("=" * 70)

        row = solve_with_min_human_assignments(
            instance,
            min_human_assignments=min_human_assignments
        )

        rows.append(row)

        print("Status:", row["status"])
        print("Feasible:", row["feasible"])
        print("Human assignments:", row["human_assignment_count"])
        print("Total cost:", row["total_cost"])
        print("Workload:", row["workload"])
        print("Ergonomic:", row["ergonomic"])
        print("Total penalty:", row["total_penalty"])
        print("Wall time:", row["wall_time"])

    df = pd.DataFrame(rows)

    baseline_cost = float(df[df["min_human_assignments"] == 0].iloc[0]["total_cost"])

    df["cost_increase_vs_min0"] = df["total_cost"] - baseline_cost
    df["percent_increase_vs_min0"] = df["cost_increase_vs_min0"] / baseline_cost * 100.0

    df.to_csv(output_path, index=False)

    print()
    print("=== Human-utilization sensitivity summary ===")
    print(df[[
        "min_human_assignments",
        "status",
        "feasible",
        "human_assignment_count",
        "robot_assignment_count",
        "machine_assignment_count",
        "processing",
        "start_time",
        "workload",
        "ergonomic",
        "safety",
        "total_cost",
        "cost_increase_vs_min0",
        "percent_increase_vs_min0"
    ]])

    print()
    print("Saved sensitivity results to:", output_path)


if __name__ == "__main__":
    main()
