
def create_time_indexed_variable_mapping(operations, resources, time_slots):
    """
    Create binary variable mapping for x[o, r, t].

    x[o, r, t] = 1 if operation o starts on resource r at time t.
    x[o, r, t] = 0 otherwise.

    Returns
    -------
    variable_names : list
        List of variable names.
    index_to_var : dict
        Mapping from index to (operation, resource, time).
    var_to_index : dict
        Mapping from (operation, resource, time) to index.
    """
    variable_names = []
    index_to_var = {}
    var_to_index = {}

    index = 0

    for operation in operations:
        for resource in resources:
            for time in time_slots:
                var_name = f"x_{operation}_{resource}_{time}"

                variable_names.append(var_name)
                index_to_var[index] = (operation, resource, time)
                var_to_index[(operation, resource, time)] = index

                index += 1

    return variable_names, index_to_var, var_to_index


def print_time_indexed_variable_mapping(variable_names, index_to_var, max_rows=30):
    """
    Print variable mapping in a readable format.

    max_rows is used to avoid printing too many variables.
    """
    print("=== Time-Indexed Variable Mapping ===")

    for index, name in enumerate(variable_names[:max_rows]):
        operation, resource, time = index_to_var[index]
        print(index, name, f"= {operation} starts on {resource} at time {time}")

    if len(variable_names) > max_rows:
        print(f"... ({len(variable_names) - max_rows} more variables not shown)")


def get_x_time(bitstring, operation, resource, time, var_to_index):
    """
    Get x[operation, resource, time] from bitstring.
    """
    index = var_to_index[(operation, resource, time)]
    return bitstring[index]
