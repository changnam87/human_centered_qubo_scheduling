
def create_variable_mapping(operations, resources):
    """
    Create binary variable mapping for x[o, r].

    x[o, r] = 1 if operation o is assigned to resource r.
    x[o, r] = 0 otherwise.

    Returns
    -------
    variable_names : list
        List of variable names.
    index_to_var : dict
        Mapping from index to (operation, resource).
    var_to_index : dict
        Mapping from (operation, resource) to index.
    """
    variable_names = []
    index_to_var = {}
    var_to_index = {}

    index = 0

    for operation in operations:
        for resource in resources:
            var_name = f"x_{operation}_{resource}"

            variable_names.append(var_name)
            index_to_var[index] = (operation, resource)
            var_to_index[(operation, resource)] = index

            index += 1

    return variable_names, index_to_var, var_to_index


def print_variable_mapping(variable_names, index_to_var):
    """
    Print variable mapping in a readable format.
    """
    print("=== Variable Mapping ===")

    for index, name in enumerate(variable_names):
        operation, resource = index_to_var[index]
        print(index, name, f"= {operation} assigned to {resource}")


def get_x(bitstring, operation, resource, var_to_index):
    """
    Get x[operation, resource] from bitstring.
    """
    index = var_to_index[(operation, resource)]
    return bitstring[index]
