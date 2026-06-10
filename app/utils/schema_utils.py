import json
import tempfile
import gradio as gr


def clear_node_fields():
    return ""


def clear_shape_fields():
    return "", "", False, "", "", False


def clear_edge_fields():
    return "", "", "", False, "", ""


def empty_schema():
    return {
        "strict": True,
        "nodes": {},
        "edges": {}
    }


def pretty_json(data):
    return json.dumps(data, indent=2)


def parse_csv(text):
    if not text:
        return []
    return [x.strip() for x in text.split(",") if x.strip()]


def parse_properties(text):
    props = {}

    if not text:
        return props

    for line in text.splitlines():
        line = line.strip()

        if not line or ":" not in line:
            continue

        name, type_value = line.split(":", 1)
        props[name.strip()] = {"type": type_value.strip()}

    return props


def properties_to_text(props):
    if not props:
        return ""
    return "\n".join([f"{name}:{value.get('type', '')}" for name, value in props.items()])


def refresh(schema):
    node_choices = list(schema["nodes"].keys())
    edge_choices = list(schema["edges"].keys())

    return (
        gr.update(choices=node_choices, value=node_choices[0] if node_choices else None),
        gr.update(choices=edge_choices, value=edge_choices[0] if edge_choices else None),
        pretty_json(schema)
    )


def shape_choices(schema, selected_node):
    if not selected_node or selected_node not in schema["nodes"]:
        return []

    return [
        f"{i}: {', '.join(shape.get('labels', []))}"
        for i, shape in enumerate(schema["nodes"][selected_node])
    ]


def update_schema_strict(schema, strict):
    schema["strict"] = strict
    return (*refresh(schema), f"Set schema strict = {strict}.")


def update_shape_dropdown(schema, selected_node):
    choices = shape_choices(schema, selected_node)
    return gr.update(choices=choices, value=choices[0] if choices else None)


def get_shape_index(selected_shape):
    if not selected_shape:
        return None

    try:
        return int(str(selected_shape).split(":", 1)[0])
    except Exception:
        return None


# -----------------------------
# Environment validation helpers
# -----------------------------

def format_validation_errors(errors):
    return "Schema validation failed:\n" + "\n".join(f"- {error}" for error in errors)


def validate_properties_against_env(properties, env, env_section, context):
    errors = []

    if env is None:
        errors.append("Environment is missing.")
        return errors

    if env_section not in ["source", "target"]:
        errors.append(
            f"Invalid environment section '{env_section}'. Expected 'source' or 'target'."
        )
        return errors

    env_props = env.get(env_section, {})

    for prop_name, prop_data in properties.items():
        schema_type = prop_data.get("type")

        if prop_name not in env_props:
            errors.append(
                f"{context}: property '{prop_name}' is not declared in env.{env_section}."
            )
            continue

        env_type = env_props[prop_name]

        if schema_type != env_type:
            errors.append(
                f"{context}: property '{prop_name}' has type '{schema_type}' in schema "
                f"but '{env_type}' in env.{env_section}."
            )

    return errors


def validate_schema_properties_against_env(
    mandatory_properties,
    optional_properties,
    env,
    env_section,
    context,
):
    errors = []

    errors.extend(
        validate_properties_against_env(
            mandatory_properties,
            env,
            env_section,
            f"{context} mandatory properties",
        )
    )

    errors.extend(
        validate_properties_against_env(
            optional_properties,
            env,
            env_section,
            f"{context} optional properties",
        )
    )

    return errors


# -----------------------------
# Node helpers
# -----------------------------

def add_node(schema, node_key):
    node_key = node_key.strip()

    if not node_key:
        return (*refresh(schema), "Node key is required.")

    if node_key in schema["nodes"]:
        return (*refresh(schema), f"Node '{node_key}' already exists.")

    schema["nodes"][node_key] = []

    return (*refresh(schema), f"Added node '{node_key}'.")


def delete_node(schema, selected_node):
    if not selected_node:
        return (*refresh(schema), "Select a node first.")

    schema["nodes"].pop(selected_node, None)

    return (*refresh(schema), f"Deleted node '{selected_node}'.")


# -----------------------------
# Shape helpers
# -----------------------------

def add_shape(
    schema,
    selected_node,
    labels,
    optional_labels,
    open_labels,
    mandatory_properties,
    optional_properties,
    open_properties,
    env,
    env_section,
):
    if not selected_node:
        return (*refresh(schema), update_shape_dropdown(schema, selected_node), "Select a node first.")

    mandatory_props = parse_properties(mandatory_properties)
    optional_props = parse_properties(optional_properties)

    errors = validate_schema_properties_against_env(
        mandatory_props,
        optional_props,
        env,
        env_section,
        f"Node '{selected_node}'",
    )

    if errors:
        return (
            *refresh(schema),
            update_shape_dropdown(schema, selected_node),
            format_validation_errors(errors),
        )

    shape = {
        "labels": parse_csv(labels),
        "optional_labels": parse_csv(optional_labels),
        "open_labels": open_labels,
        "mandatory_properties": mandatory_props,
        "optional_properties": optional_props,
        "open_properties": open_properties,
    }

    schema["nodes"][selected_node].append(shape)

    return (
        *refresh(schema),
        update_shape_dropdown(schema, selected_node),
        f"Added shape to node '{selected_node}'."
    )


def load_shape(schema, selected_node, selected_shape):
    idx = get_shape_index(selected_shape)

    if selected_node not in schema["nodes"] or idx is None:
        return "", "", False, "", "", False, "Select a shape first."

    shape = schema["nodes"][selected_node][idx]

    return (
        ", ".join(shape.get("labels", [])),
        ", ".join(shape.get("optional_labels", [])),
        shape.get("open_labels", False),
        properties_to_text(shape.get("mandatory_properties", {})),
        properties_to_text(shape.get("optional_properties", {})),
        shape.get("open_properties", False),
        f"Loaded shape {idx}."
    )


def update_shape(
    schema,
    selected_node,
    selected_shape,
    labels,
    optional_labels,
    open_labels,
    mandatory_properties,
    optional_properties,
    open_properties,
    env,
    env_section,
):
    idx = get_shape_index(selected_shape)

    if selected_node not in schema["nodes"] or idx is None:
        return (*refresh(schema), update_shape_dropdown(schema, selected_node), "Select a shape first.")

    mandatory_props = parse_properties(mandatory_properties)
    optional_props = parse_properties(optional_properties)

    errors = validate_schema_properties_against_env(
        mandatory_props,
        optional_props,
        env,
        env_section,
        f"Node '{selected_node}', shape {idx}",
    )

    if errors:
        return (
            *refresh(schema),
            update_shape_dropdown(schema, selected_node),
            format_validation_errors(errors),
        )

    schema["nodes"][selected_node][idx] = {
        "labels": parse_csv(labels),
        "optional_labels": parse_csv(optional_labels),
        "open_labels": open_labels,
        "mandatory_properties": mandatory_props,
        "optional_properties": optional_props,
        "open_properties": open_properties,
    }

    return (
        *refresh(schema),
        update_shape_dropdown(schema, selected_node),
        f"Updated shape {idx}."
    )


def delete_shape(schema, selected_node, selected_shape):
    idx = get_shape_index(selected_shape)

    if selected_node not in schema["nodes"] or idx is None:
        return (*refresh(schema), update_shape_dropdown(schema, selected_node), "Select a shape first.")

    schema["nodes"][selected_node].pop(idx)

    return (
        *refresh(schema),
        update_shape_dropdown(schema, selected_node),
        f"Deleted shape {idx}."
    )


# -----------------------------
# Edge helpers
# -----------------------------

def add_edge(
    schema,
    edge_name,
    from_labels,
    to_labels,
    open_properties,
    mandatory_properties,
    optional_properties,
    env,
    env_section,
):
    edge_name = edge_name.strip()

    if not edge_name:
        return (*refresh(schema), "Edge name is required.")

    mandatory_props = parse_properties(mandatory_properties)
    optional_props = parse_properties(optional_properties)

    errors = validate_schema_properties_against_env(
        mandatory_props,
        optional_props,
        env,
        env_section,
        f"Edge '{edge_name}'",
    )

    if errors:
        return (*refresh(schema), format_validation_errors(errors))

    schema["edges"][edge_name] = {
        "from": parse_csv(from_labels),
        "to": parse_csv(to_labels),
        "open_properties": open_properties,
        "mandatory_properties": mandatory_props,
        "optional_properties": optional_props,
    }

    return (*refresh(schema), f"Added edge '{edge_name}'.")


def load_edge(schema, selected_edge):
    if not selected_edge or selected_edge not in schema["edges"]:
        return "", "", "", False, "", "", "Select an edge first."

    edge = schema["edges"][selected_edge]

    return (
        selected_edge,
        ", ".join(edge.get("from", [])),
        ", ".join(edge.get("to", [])),
        edge.get("open_properties", False),
        properties_to_text(edge.get("mandatory_properties", {})),
        properties_to_text(edge.get("optional_properties", {})),
        f"Loaded edge '{selected_edge}'."
    )


def update_edge(
    schema,
    selected_edge,
    edge_name,
    from_labels,
    to_labels,
    open_properties,
    mandatory_properties,
    optional_properties,
    env,
    env_section,
):
    if not selected_edge:
        return (*refresh(schema), "Select an edge first.")

    new_edge_name = edge_name.strip()

    if not new_edge_name:
        return (*refresh(schema), "Edge name is required.")

    mandatory_props = parse_properties(mandatory_properties)
    optional_props = parse_properties(optional_properties)

    errors = validate_schema_properties_against_env(
        mandatory_props,
        optional_props,
        env,
        env_section,
        f"Edge '{new_edge_name}'",
    )

    if errors:
        return (*refresh(schema), format_validation_errors(errors))

    schema["edges"].pop(selected_edge, None)

    schema["edges"][new_edge_name] = {
        "from": parse_csv(from_labels),
        "to": parse_csv(to_labels),
        "open_properties": open_properties,
        "mandatory_properties": mandatory_props,
        "optional_properties": optional_props,
    }

    return (*refresh(schema), f"Updated edge '{new_edge_name}'.")


def delete_edge(schema, selected_edge):
    if not selected_edge:
        return (*refresh(schema), "Select an edge first.")

    schema["edges"].pop(selected_edge, None)

    return (*refresh(schema), f"Deleted edge '{selected_edge}'.")


# -----------------------------
# Upload helper
# -----------------------------


def validate_schema_structure(schema):
    errors = []

    if not isinstance(schema, dict):
        return ["Schema JSON must be an object."]

    if "nodes" not in schema:
        errors.append("Missing 'nodes'.")

    if "edges" not in schema:
        errors.append("Missing 'edges'.")

    if "nodes" in schema and not isinstance(schema["nodes"], dict):
        errors.append("'nodes' must be an object.")

    if "edges" in schema and not isinstance(schema["edges"], dict):
        errors.append("'edges' must be an object.")

    if "strict" in schema and not isinstance(schema["strict"], bool):
        errors.append("'strict' must be true or false.")

    return errors

def load_schema_from_file(file, env, env_section):
    if file is None:
        schema = empty_schema()

        return (
            schema,
            *refresh(schema),
            "Schema upload cleared. Reset to empty schema."
        )

    try:
        with open(file.name, "r", encoding="utf-8") as f:
            schema = json.load(f)

        structure_errors = validate_schema_structure(schema)

        if structure_errors:
            empty = empty_schema()

            return (
                empty,
                *refresh(empty),
                "Invalid schema JSON:\n"
                + "\n".join(f"- {error}" for error in structure_errors)
            )

        schema.setdefault("strict", True)

        errors = validate_full_schema_against_env(
            schema,
            env,
            env_section,
        )

        if errors:
            empty = empty_schema()

            return (
                empty,
                *refresh(empty),
                format_validation_errors(errors),
            )

        return (
            schema,
            *refresh(schema),
            f"Loaded schema from '{file.name}'."
        )

    except Exception as e:
        schema = empty_schema()

        return (
            schema,
            *refresh(schema),
            f"Failed to load schema:\n{str(e)}"
        )
    

def validate_full_schema_against_env(schema, env, env_section):
    errors = []

    for node_key, shapes in schema.get("nodes", {}).items():
        for shape_index, shape in enumerate(shapes):
            errors.extend(
                validate_schema_properties_against_env(
                    shape.get("mandatory_properties", {}),
                    shape.get("optional_properties", {}),
                    env,
                    env_section,
                    f"Node '{node_key}', shape {shape_index + 1}",
                )
            )

    for edge_name, edge_data in schema.get("edges", {}).items():
        errors.extend(
            validate_schema_properties_against_env(
                edge_data.get("mandatory_properties", {}),
                edge_data.get("optional_properties", {}),
                env,
                env_section,
                f"Edge '{edge_name}'",
            )
        )

    return errors