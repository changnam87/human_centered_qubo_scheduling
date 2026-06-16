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


def main():
    instance_path = PROJECT_ROOT / "data" / "augmented" / "sample_3x3_hc_seed2026_time_indexed.json"

    print("=== Augmented sample_3x3 CP-SAT baseline ===")
    print("Input:", instance_path)

    instance = load_instance(instance_path)

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

    print()
    print("=== Dimensions ===")
    print("Operations:", len(operations))
    print("Resources:", len(resources))
    print("Workers:", workers)
    print("Robots:", robots)
    print("Time slots:", len(time_slots))
    print("Binary variables:", num_variables)

    # ------------------------------------------------------------
    # Build CP-SAT model
    # ------------------------------------------------------------
    model = cp_model.CpModel()

    x = {}

    for operation in operations:
        for resource in resources:
            for time in time_slots:
                duration = processing_time[operation][resource]
                end_time = time + duration

                # Create variables only for starts within horizon.
                # Skill incompatibility is handled separately by forbidding x=1.
                if end_time <= planning_horizon:
                    x[(operation, resource, time)] = model.NewBoolVar(
                        f"x_{operation}_{resource}_{time}"
                    )

    # ------------------------------------------------------------
    # Constraint 1: each operation starts exactly once
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
    # Constraint 2: skill compatibility
    # ------------------------------------------------------------
    for operation in operations:
        for resource in resources:
            if skill_compatibility[operation][resource] == 0:
                for time in time_slots:
                    key = (operation, resource, time)
                    if key in x:
                        model.Add(x[key] == 0)

    # ------------------------------------------------------------
    # Constraint 3: precedence
    # end(before) <= start(after)
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
    # Constraint 4: resource no-overlap
    #
    # For each resource and each time point tau:
    # at most one operation can be active.
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
    # Soft robot utilization term
    # robot_use close to target
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
    #
    # CP-SAT requires integer coefficients.
    # Use SCALE=10 to preserve lambda_start_time=0.2.
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
    solver.parameters.max_time_in_seconds = 60
    solver.parameters.num_search_workers = 8

    status = solver.Solve(model)

    print()
    print("=== CP-SAT solve status ===")
    print("Status:", solver.StatusName(status))
    print("Objective value scaled:", solver.ObjectiveValue())
    print("Objective value unscaled:", solver.ObjectiveValue() / SCALE)
    print("Wall time:", solver.WallTime())

    if status not in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
        print("No feasible solution found.")
        return

    # ------------------------------------------------------------
    # Convert solution to full bitstring
    # ------------------------------------------------------------
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

    print()
    print("=== CP-SAT decoded solution ===")
    print("Bitstring length:", len(bitstring))
    print("Selected variables:", sum(bitstring))
    print("Feasible:", result["feasible"])
    print("Number of violations:", result["num_violations"])

    print()
    print("Cost breakdown:")
    print("Processing:", result["processing"])
    print("Start time:", result["start_time"])
    print("Workload:", result["workload"])
    print("Ergonomic:", result["ergonomic"])
    print("Safety:", result["safety"])
    print("Original cost:", result["original_cost"])

    print()
    print("Penalty breakdown:")
    print("Assignment-start penalty:", result["assignment_start_penalty"])
    print("Skill penalty:", result["skill_penalty"])
    print("Horizon penalty:", result["horizon_penalty"])
    print("Precedence penalty:", result["precedence_penalty"])
    print("Resource-overlap penalty:", result["resource_overlap_penalty"])
    print("Robot-utilization penalty:", result["robot_utilization_penalty"])
    print("Total penalty:", result["total_penalty"])

    print()
    print("Total cost:", result["total_cost"])

    print()
    print("Schedule:")
    for operation, selected in result["schedule"].items():
        print(operation, ":", selected)

    # ------------------------------------------------------------
    # Compare against handcrafted validation schedule if available
    # ------------------------------------------------------------
    handcrafted_path = PROJECT_ROOT / "results" / "tables" / "sample_3x3_augmented_qubo_validation.csv"

    handcrafted_cost = None

    if handcrafted_path.exists():
        hc_df = pd.read_csv(handcrafted_path, dtype={"bitstring": str})
        handcrafted_cost = float(hc_df.iloc[0]["total_cost"])

        print()
        print("=== Comparison with handcrafted schedule ===")
        print("Handcrafted total cost:", handcrafted_cost)
        print("CP-SAT total cost:", result["total_cost"])
        print("Improvement over handcrafted:", handcrafted_cost - result["total_cost"])

    # ------------------------------------------------------------
    # Save result
    # ------------------------------------------------------------
    output_path = PROJECT_ROOT / "results" / "tables" / "sample_3x3_augmented_cpsat_result.csv"

    row = {
        "solver": "CP-SAT",
        "status": solver.StatusName(status),
        "objective_scaled": solver.ObjectiveValue(),
        "objective_unscaled": solver.ObjectiveValue() / SCALE,
        "wall_time": solver.WallTime(),
        "num_operations": len(operations),
        "num_resources": len(resources),
        "num_time_slots": len(time_slots),
        "num_binary_variables": num_variables,
        "bitstring": format_bitstring(bitstring),
        "selected_variables": sum(bitstring),
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
        "handcrafted_cost": handcrafted_cost,
        "improvement_over_handcrafted": None if handcrafted_cost is None else handcrafted_cost - result["total_cost"],
        "schedule": str(result["schedule"])
    }

    pd.DataFrame([row]).to_csv(output_path, index=False)

    print()
    print("Saved CP-SAT result to:", output_path)


if __name__ == "__main__":
    main()
