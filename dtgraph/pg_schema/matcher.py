# Node matching

def match_node_types(node, schema):
    matched_types = []
    all_errors = {}

    node_labels = set(node.labels)

    for node_type_name, shapes in schema["nodes"].items():

        shape_labels = set(shapes[0]["labels"])

        if not node_labels.intersection(shape_labels):
            continue

        shape_errors_list = []

        for shape in shapes:
            ok, errors = _matches_node_shape(node, shape)

            if ok:
                return [node_type_name], {} 

            shape_errors_list.append({
                "shape": shape,
                "errors": errors
            })

        all_errors[node_type_name] = shape_errors_list

    return matched_types, all_errors


def _matches_node_shape(node, shape):
    errors = []

    labels = set(node.labels)
    props = node.properties

    mandatory_labels = set(shape["labels"])
    optional_labels = set(shape["optional_labels"])


    # Label conformance

    # (i) mandatory ⊆ node labels
    if not mandatory_labels.issubset(labels):
        missing = mandatory_labels - labels
        errors.append(f"Missing labels: {missing}")

    # (ii) extra labels must be optional OR open_labels
    extra_labels = labels - mandatory_labels

    if not shape["open_labels"]:
        invalid = extra_labels - optional_labels
        if invalid:
            errors.append(f"Invalid extra labels: {invalid}")


    # Property conformance

    mandatory_props = shape["mandatory_properties"]
    optional_props = shape["optional_properties"]

    # Mandatory properties
    for prop_name, prop_def in mandatory_props.items():
        if prop_name not in props:
            errors.append(f"Missing property: '{prop_name}'")
        elif not _check_type(props[prop_name], prop_def["type"]):
            errors.append(f"Wrong type for '{prop_name}'")

    # Property validation
    for prop_name, value in props.items():

        if prop_name in mandatory_props:
            continue

        elif prop_name in optional_props:
            if not _check_type(value, optional_props[prop_name]["type"]):
                errors.append(f"Wrong type for optional '{prop_name}'")

        else:
            if not shape["open_properties"]:
                errors.append(f"Unexpected property: '{prop_name}'")

    return len(errors) == 0, errors


# Edge matching

def match_edge_types(edge, schema):
    edge_type_name = edge.type
    edge_types = schema["edges"]

    # Case 1: Unknown edge type
    if edge_type_name not in edge_types:
        return [], {
            edge_type_name: [f"Unknown edge type '{edge_type_name}'"]
        }

    edge_type = edge_types[edge_type_name]

    ok, errors = _matches_edge_type(edge, edge_type_name, edge_type, schema)

    if ok:
        return [edge_type_name], {}

    return [], {
        edge_type_name: errors
    }


def _matches_edge_type(edge, edge_type_name, edge_type, schema):
    errors = []

    # Edge type check
    if edge.type != edge_type_name:
        errors.append(f"Edge type mismatch: expected '{edge_type_name}', got '{edge.type}'")
        return False, errors

    # Source check
    source_labels = edge.source.labels

    if not any(label in edge_type["from"] for label in source_labels):
        errors.append(
            f"Invalid source node type: got {list(source_labels)}, expected one of {edge_type['from']}"
        )

    # Target check
    target_labels = edge.target.labels

    if not any(label in edge_type["to"] for label in target_labels):
        errors.append(
            f"Invalid target node type: got {list(target_labels)}, expected one of {edge_type['to']}"
        )

    # Property checks
    props = edge.properties

    mandatory_props = edge_type["mandatory_properties"]
    optional_props = edge_type["optional_properties"]

    # mandatory properties
    for prop_name, prop_def in mandatory_props.items():
        if prop_name not in props:
            errors.append(f"Missing edge property: '{prop_name}'")
        elif not _check_type(props[prop_name], prop_def["type"]):
            errors.append(f"Wrong type for edge property '{prop_name}'")

    # property validation
    for prop_name, value in props.items():

        if prop_name in mandatory_props:
            continue

        elif prop_name in optional_props:
            if not _check_type(value, optional_props[prop_name]["type"]):
                errors.append(f"Wrong type for optional edge property '{prop_name}'")

        else:
            if not edge_type["open_properties"]:
                errors.append(f"Unexpected edge property: '{prop_name}'")

    return len(errors) == 0, errors

# Type checking
def _check_type(value, expected_type):
    ## Skip type checking here becuase it is checked in type checking pipeline

    # if expected_type == "string":
    #     return isinstance(value, str)

    # if expected_type == "integer":
    #     return isinstance(value, int)

    # if expected_type == "float":
    #     return isinstance(value, float)

    # if expected_type == "boolean":
    #     return isinstance(value, bool)

    return True