import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

import pandas as pd
from ortools.sat.python import cp_model

from src.core.instance import load_instance
from src.core.time_indexed_variables import create_time_indexed_variable_mapping
from src.core.time_indexed_evaluate import evaluate_time_indexed_solution


def make_empty_bitstring(num_variables):
    return [0] * num_variables


def set_start(bitstring, operation, resource, time, var_to_index):
    index = var_to_index[(operation, resource, time)]
    bitstring[index] = 1


def format_bitstring(bitstring):
    return "".join(str(int(v)) for v in bitstring)


def main():
    instance_path = PROJECT_ROOT / "data" / "toy" / "toy_v2_time_indexed.json"
    instance = load_instance(instance_path)

    operations = instance["operations"]
    resources = instance["resources"]
    time_slots = instance["time_slots"]
    processing_time = instance["processing_time"]
    processing_cost = instance["processing_cost"]
    skill_compatibility = instance["skill_compatibility"]
    precedence = instance["precedence"]

    workload_score = instance["workload_score"]
    ergonomic_risk = instance["ergonomic_risk"]
    robot_safety_risk = instance["robot_safety_risk"]

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

    print("=== Toy v2 CP-SAT baseline ===")
    print("Number of binary variables:", num_variables)

    # ------------------------------------------------------------
    # Build CP-SAT model
    # ------------------------------------------------------------
    model = cp_model.CpModel()

    x = {}

    for operation in operations:
        for resource in resources:
            for time in time_slots:
                # Do not create variables for starts that exceed horizon
                duration = processing_time[operation][resource]
                end_time = time + duration

                if end_time <= planning_horizon:
                    x[(operation, resource, time)] = model.NewBoolVar(
                        f"x_{operation}_{resource}_{time}"
                    )
                else:
                    # Keep variable absent. Treated as impossible.
                    pass

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
    # Incompatible operation-resource assignments are forbidden.
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
    # For each pair before -> after:
    # end(before) <= start(after)
    #
    # Time-indexed linear form:
    # start_before = sum_{r,t} t * x[before,r,t]
    # duration_before = sum_{r,t} p[before,r] * x[before,r,t]
    # start_after = sum_{r,t} t * x[after,r,t]
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
                    before_duration_terms.append(processing_time[before][resource] * x[before_key])

                if after_key in x:
                    after_start_terms.append(time * x[after_key])

        model.Add(
            sum(before_start_terms) + sum(before_duration_terms)
            <= sum(after_start_terms)
        )

    # ------------------------------------------------------------
    # Constraint 4: resource no-overlap
    #
    # For every resource and time point tau:
    # at most one operation can be active on that resource.
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
    # Optional: robot utilization target
    # In QUBO this was a soft penalty. For CP-SAT baseline,
    # keep it as soft objective term rather than hard constraint.
    # ------------------------------------------------------------
    robot_use_terms = []

    for operation in operations:
        for time in time_slots:
            key = (operation, "R", time)
            if key in x:
                robot_use_terms.append(x[key])

    robot_use = model.NewIntVar(0, len(operations), "robot_use")
    model.Add(robot_use == sum(robot_use_terms))

    robot_target = instance["penalties"]["robot_utilization_target"]

    robot_deviation = model.NewIntVar(0, len(operations), "robot_deviation")
    model.AddAbsEquality(robot_deviation, robot_use - robot_target)

    # ------------------------------------------------------------
    # Objective
    #
    # CP-SAT uses integer coefficients. We multiply all decimal costs by 10.
    # For example, lambda_start_time=0.2 becomes 2.
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

                if resource == "H":
                    coeff += lambda_workload * workload_score[operation]
                    coeff += lambda_ergonomic * ergonomic_risk[operation]

                if resource == "R":
                    coeff += lambda_safety * robot_safety_risk[operation]

                objective_terms.append(int(round(SCALE * coeff)) * x[key])

    # Robot utilization penalty:
    # QUBO used squared deviation. CP-SAT baseline uses absolute deviation
    # as a simple linear soft penalty.
    P_robot = instance["penalties"]["P_robot_utilization"]
    objective_terms.append(int(round(SCALE * P_robot)) * robot_deviation)

    model.Minimize(sum(objective_terms))

    # ------------------------------------------------------------
    # Solve
    # ------------------------------------------------------------
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 30
    solver.parameters.num_search_workers = 8

    status = solver.Solve(model)

    print()
    print("=== CP-SAT solve status ===")
    print("Status:", solver.StatusName(status))
    print("Objective value scaled:", solver.ObjectiveValue())
    print("Objective value unscaled:", solver.ObjectiveValue() / SCALE)

    if status not in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
        print("No feasible solution found.")
        return

    # ------------------------------------------------------------
    # Convert CP-SAT solution to full 72-length bitstring
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
    print("Bitstring:", format_bitstring(bitstring))
    print("Feasible:", result["feasible"])
    print("Number of violations:", result["num_violations"])
    print("Processing:", result["processing"])
    print("Start time:", result["start_time"])
    print("Workload:", result["workload"])
    print("Ergonomic:", result["ergonomic"])
    print("Safety:", result["safety"])
    print("Original cost:", result["original_cost"])
    print("Assignment-start penalty:", result["assignment_start_penalty"])
    print("Skill penalty:", result["skill_penalty"])
    print("Horizon penalty:", result["horizon_penalty"])
    print("Precedence penalty:", result["precedence_penalty"])
    print("Resource-overlap penalty:", result["resource_overlap_penalty"])
    print("Robot-utilization penalty:", result["robot_utilization_penalty"])
    print("Total penalty:", result["total_penalty"])
    print("Total cost:", result["total_cost"])

    print()
    print("Schedule:")
    for operation, selected in result["schedule"].items():
        print(operation, ":", selected)

    # ------------------------------------------------------------
    # Save result
    # ------------------------------------------------------------
    output_path = PROJECT_ROOT / "results" / "tables" / "toy_v2_cpsat_result.csv"

    row = {
        "solver": "CP-SAT",
        "status": solver.StatusName(status),
        "objective_scaled": solver.ObjectiveValue(),
        "objective_unscaled": solver.ObjectiveValue() / SCALE,
        "bitstring": format_bitstring(bitstring),
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
        "schedule": str(result["schedule"])
    }

    pd.DataFrame([row]).to_csv(output_path, index=False)

    print()
    print("Saved CP-SAT result to:", output_path)


if __name__ == "__main__":
    main()
