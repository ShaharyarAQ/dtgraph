from pg_schema.matcher import match_node_types, match_edge_types



def validate_node(node, schema):
    strict = schema.get("strict", True)
    node_types = schema["nodes"]
    labels = set(node.labels)

    # Type existence check
    if strict:
        if not any(label in node_types for label in labels):
            raise ValueError(
                f"No valid node type found in labels {labels}"
            )

    # Matching check
    matches, errors = match_node_types(node, schema)

    if strict:
        if not matches:
            msg = "Node validation failed:\n"
            msg += f"Labels: {labels}\n"
            msg += f"Properties: {node.properties}\n"

            for node_type, errs in errors.items():
                msg += f"\nTried type '{node_type}':\n"
                for e in errs:
                    msg += f"  - {e}\n"

            raise ValueError(msg)

    return True


# Edge validation
def validate_edge(edge, schema):
    strict = schema.get("strict", True)
    edge_types = schema["edges"]

    # Type existence check
    if strict:
        if edge.type not in edge_types:
            raise ValueError(
                f"Unknown edge type '{edge.type}' in strict mode. "
                f"The relationship type '{edge.type}' is not defined in the provided schema."
            )

    # Matching check
    matches, errors = match_edge_types(edge, schema)

    if strict:
        if not matches:
            msg = "Edge validation failed:\n"
            msg += f"Type: {edge.type}\n"
            msg += f"Properties: {edge.properties}\n"

            for edge_type, errs in errors.items():
                msg += f"\nTried type '{edge_type}':\n"
                for e in errs:
                    msg += f"  - {e}\n"

            raise ValueError(msg)

    return True


# Graph validation
def validate_graph(graph, schema):
    for node in graph.nodes:
        validate_node(node, schema)

    for edge in graph.edges:
        validate_edge(edge, schema)

    return True
