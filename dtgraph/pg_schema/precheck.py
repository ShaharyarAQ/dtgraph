import re
from pg_schema.validator import validate_node, validate_edge

def precheck_rule(generate_clause, schema, rule_text):

    rule_type = get_rule_type(generate_clause)

    if rule_type == "node":
        return _precheck_node_rule(generate_clause, schema)

    elif rule_type == "edge":
        return _precheck_edge_rule(generate_clause, schema, rule_text)

    else:
        raise ValueError("Unknown rule type")
    


# Rule type detection (Node rule or edge rule)
def get_rule_type(generate_clause: str):
    if re.search(r"-\s*\[.*?\]\s*->", generate_clause):
        return "edge"
    return "node"



def _precheck_node_rule(generate_clause, schema):

    labels = extract_node_labels(generate_clause)
    properties = extract_properties(generate_clause)

    simulated_node = _create_empty_node()

    # Add label
    for label in labels:
        simulated_node.labels.add(label)

    # Add properties
    for key in properties:
        simulated_node.properties[key] = _temp_value()

    # Validate
    validate_node(simulated_node, schema)

    return True


def _precheck_edge_rule(generate_clause, schema, rule_text):

    edge_label = extract_edge_label(generate_clause)
    properties = extract_properties(generate_clause)

    if not edge_label:
        raise ValueError("Edge label not found")

    source_node = _create_empty_node()
    target_node = _create_empty_node()

    edge_schema = schema["edges"].get(edge_label)

    if edge_schema:
        match_types = extract_match_types(rule_text)
        node_mapping = extract_node_mapping(generate_clause)

        source_var = node_mapping.get("x")
        target_var = node_mapping.get("y")

        if source_var and source_var in match_types:
            source_node.labels.add(match_types[source_var])

        if target_var and target_var in match_types:
            target_node.labels.add(match_types[target_var])

        # fallback
        if not source_node.labels:
            source_node.labels.add(edge_schema["from"][0])

        if not target_node.labels:
            target_node.labels.add(edge_schema["to"][0])

    simulated_edge = _create_edge(edge_label, source_node, target_node)

    for key in properties:
        simulated_edge.properties[key] = _temp_value()

    validate_edge(simulated_edge, schema)

    return True


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


def extract_match_types(rule_text: str):
    matches = re.findall(r"\((\w+):(\w+)\)", rule_text)
    return {var: label for var, label in matches}

def extract_node_mapping(generate_clause: str):
    matches = re.findall(r"\((\w+)\s*=\s*\((\w+)\)\s*:\)", generate_clause)
    return {new: old for new, old in matches}

def extract_node_labels(generate_clause: str):
    match = re.search(r"\)\s*:(\w+(?::\w+)*)", generate_clause)
    
    if not match:
        return []
    
    labels_str = match.group(1)
    return labels_str.split(":")


def extract_edge_label(generate_clause: str):
    match = re.search(r"\[.*?:(\w+)(?:\s*\{.*?\})?\s*\]", generate_clause, re.DOTALL)
    return match.group(1) if match else None


def extract_properties(generate_clause: str):
    match = re.search(r"\{(.*?)\}", generate_clause, re.DOTALL)

    if not match:
        return {}

    props_str = match.group(1)

    props = {}
    pairs = [p.strip() for p in props_str.split(",") if p.strip()]

    for pair in pairs:
        if "=" in pair:
            key, value = pair.split("=", 1)
            props[key.strip()] = value.strip()

    return props