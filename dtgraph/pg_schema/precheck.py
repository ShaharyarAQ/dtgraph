from pg_schema.validator import validate_node, validate_edge

def precheck_rule(rule_dict, schema):

    if "constructors" not in rule_dict:
        raise Exception("Invalid rule: missing constructors")

    for c in rule_dict["constructors"]:

        if "edge" in c:
            _precheck_edge(c, schema)
        else:
            _precheck_node(c, schema)

    return True

def _precheck_node(c, schema):

    node = _create_empty_node()

    # Labels
    labels = c.get("labels", [])
    for l in labels:
        node.labels.add(l)

    # Properties/keys
    for p in c.get("properties", []):
        node.properties[p["key"]] = _temp_value()

    # Validate against schema
    validate_node(node, schema)


def _precheck_edge(c, schema):

    edge_info = c.get("edge")
    src_info = c.get("src")
    tgt_info = c.get("tgt")

    if not edge_info or not src_info or not tgt_info:
        raise Exception("Invalid edge constructor")

    labels = edge_info.get("labels", [])
    if not labels or len(labels) != 1:
        raise Exception("Edge must have exactly one label")

    edge_label = labels[0]

    # Create simulated nodes
    source = _create_empty_node()
    target = _create_empty_node()

    # Assign labels if present
    source.labels.update(src_info.get("labels", []))
    target.labels.update(tgt_info.get("labels", []))

    # Fallback if labels missing (important!)
    edge_schema = schema["edges"].get(edge_label)

    if edge_schema:
        if not source.labels:
            source.labels.add(edge_schema["from"][0])

        if not target.labels:
            target.labels.add(edge_schema["to"][0])

    # Create simulated edge
    edge = _create_edge(edge_label, source, target)

    # Properties (keys only)
    for p in edge_info.get("properties", []):
        edge.properties[p["key"]] = _temp_value()

    # Validate
    validate_edge(edge, schema)


# Helpers
def _create_empty_node():
    class SimNode:
        pass

    node = SimNode()
    node.labels = set()
    node.properties = {}
    return node


def _create_edge(edge_type, source, target):
    class SimEdge:
        pass

    edge = SimEdge()
    edge.type = edge_type
    edge.source = source
    edge.target = target
    edge.properties = {}
    return edge


def _temp_value():
    return "temp"