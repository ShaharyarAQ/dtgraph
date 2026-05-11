from pg_schema.validator import validate_node, validate_edge

def precheck_rule(rule_dict, schema):

    if "constructors" not in rule_dict:
        raise Exception("Invalid rule: missing constructors")
    
    node_registry = {} 

    for c in rule_dict["constructors"]:

        if "edge" in c:

            # Validate source node
            _precheck_node(c["src"], schema, node_registry)

            # Validate target node if labels exist
            tgt = c.get("tgt", {})
            if tgt.get("labels"):
                _precheck_node(tgt, schema, node_registry)

            # Validate edge
            _precheck_edge(c, schema, node_registry)

        else:
            _precheck_node(c, schema, node_registry)

    return True

def _precheck_node(c, schema, registry):

    alias = c.get("alias")

    if alias in registry:
        node = registry[alias]
    else:
        node = _create_empty_node()
        if alias:
            registry[alias] = node

    # Labels
    for l in c.get("labels", []):
        node.labels.add(l)

    # Properties
    for p in c.get("properties", []):
        node.properties[p["key"]] = _temp_value()

    validate_node(node, schema)

def _precheck_edge(c, schema, registry):

    edge_info = c.get("edge")
    src_info = c.get("src")
    tgt_info = c.get("tgt")

    if not edge_info or not src_info or not tgt_info:
        raise Exception("Invalid edge constructor")

    labels = edge_info.get("labels", [])
    if not labels or len(labels) != 1:
        raise Exception("Edge must have exactly one label")

    edge_label = labels[0]

    # Get or create source node
    src_alias = src_info.get("alias")
    if src_alias and src_alias in registry:
        source = registry[src_alias]
    else:
        source = _create_empty_node()
        if src_alias:
            registry[src_alias] = source

    # Get or create target node
    tgt_alias = tgt_info.get("alias")
    if tgt_alias and tgt_alias in registry:
        target = registry[tgt_alias]
    else:
        target = _create_empty_node()
        if tgt_alias:
            registry[tgt_alias] = target

    # Assign label if present
    source.labels.update(src_info.get("labels", []))
    target.labels.update(tgt_info.get("labels", []))

    # Fallback if label missing
    edge_schema = schema["edges"].get(edge_label)

    if edge_schema:
        if not source.labels:
            source.labels.add(edge_schema["from"][0])

        if not target.labels:
            target.labels.add(edge_schema["to"][0])

    # Create edge
    edge = _create_edge(edge_label, source, target)

    # Properties
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