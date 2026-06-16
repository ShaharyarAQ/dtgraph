import json
import tempfile
import gradio as gr


def empty_env():
    return {
        "source": {},
        "target": {},
        "variables": {},
        "functions": {}
    }


def pretty_json(data):
    return json.dumps(data, indent=2)

def parse_csv(text):
    if not text:
        return []
    return [x.strip() for x in text.split(",") if x.strip()]


def refresh_env(env):
    function_choices = list(env["functions"].keys())

    return (
        pretty_json(env),
        gr.update(choices=function_choices, value=function_choices[0] if function_choices else None),
    )


def clear_property_fields():
    return "", ""


def clear_function_fields():
    return "", "", ""


def add_env_property(env, section, name, type_value):
    name = name.strip()
    type_value = type_value.strip()

    if not name:
        return (*refresh_env(env), "Property name is required.")

    if not type_value:
        return (*refresh_env(env), "Property type is required.")

    env[section][name] = type_value

    return (*refresh_env(env), f"Added '{name}' to {section}.")


def delete_env_property(env, section, name):
    name = name.strip()

    if not name:
        return (*refresh_env(env), "Property name is required.")

    env[section].pop(name, None)

    return (*refresh_env(env), f"Deleted '{name}' from {section}.")


def pairs_to_dataframe(pairs):
    return [[p["input"], p["output"]] for p in pairs]


def clear_function_io_fields():
    return "", ""


def clear_function_fields():
    return "", []


def parse_function_pairs(pairs):
    cleaned = []

    if not pairs:
        return cleaned

    for pair in pairs:
        input_type = str(pair.get("input", "")).strip()
        output_type = str(pair.get("output", "")).strip()

        if input_type and output_type:
            cleaned.append({
                "input": input_type,
                "output": output_type,
            })

        elif input_type or output_type:
            raise ValueError("Each input type must have a corresponding output type.")

    return cleaned

def add_function_io_pair(pairs, input_type, output_type):
    pairs = pairs or []

    input_type = input_type.strip()
    output_type = output_type.strip()

    if not input_type:
        return pairs, pairs_to_dataframe(pairs), "Input type is required."

    if not output_type:
        return pairs, pairs_to_dataframe(pairs), "Output type is required."

    pairs.append({
        "input": input_type,
        "output": output_type,
    })

    return pairs, pairs_to_dataframe(pairs), "Added input/output pair."


def delete_function_io_pair(pairs):
    pairs = pairs or []

    if not pairs:
        return pairs, pairs_to_dataframe(pairs), "No input/output pair to delete."

    pairs.pop()

    return pairs, pairs_to_dataframe(pairs), "Deleted last input/output pair."


def add_function(env, function_name, pairs):
    function_name = function_name.strip()

    if not function_name:
        return (*refresh_env(env), "Function name is required.")

    try:
        pairs = parse_function_pairs(pairs)
    except ValueError as e:
        return (*refresh_env(env), str(e))

    if not pairs:
        return (*refresh_env(env), "At least one input/output pair is required.")

    env["functions"][function_name] = {
        "inputs": [p["input"] for p in pairs],
        "outputs": [p["output"] for p in pairs],
    }

    return (*refresh_env(env), f"Added function '{function_name}'.")


def load_function(env, selected_function):
    if not selected_function or selected_function not in env["functions"]:
        return "", [], "Select a function first."

    function_data = env["functions"][selected_function]

    inputs = function_data.get("inputs", [])
    outputs = function_data.get("outputs", [])

    pairs = [
        {"input": input_type, "output": output_type}
        for input_type, output_type in zip(inputs, outputs)
    ]

    return selected_function, pairs, f"Loaded function '{selected_function}'."


def update_function(env, selected_function, function_name, pairs):
    if not selected_function:
        return (*refresh_env(env), "Select a function first.")

    function_name = function_name.strip()

    if not function_name:
        return (*refresh_env(env), "Function name is required.")

    try:
        pairs = parse_function_pairs(pairs)
    except ValueError as e:
        return (*refresh_env(env), str(e))

    if not pairs:
        return (*refresh_env(env), "At least one input/output pair is required.")

    env["functions"].pop(selected_function, None)

    env["functions"][function_name] = {
        "inputs": [p["input"] for p in pairs],
        "outputs": [p["output"] for p in pairs],
    }

    return (*refresh_env(env), f"Updated function '{function_name}'.")


def delete_function(env, selected_function):
    if not selected_function:
        return (*refresh_env(env), "Select a function first.")

    env["functions"].pop(selected_function, None)

    return (*refresh_env(env), f"Deleted function '{selected_function}'.")


def validate_env_structure(env):
    required_keys = ["source", "target", "variables", "functions"]
    errors = []

    if not isinstance(env, dict):
        return ["Environment JSON must be an object."]

    for key in required_keys:
        if key not in env:
            errors.append(f"Missing '{key}'.")

    for key in required_keys:
        if key in env and not isinstance(env[key], dict):
            errors.append(f"'{key}' must be an object.")

    return errors


def load_env_from_file(file):
    if file is None:
        env = empty_env()

        return (
            env,
            pretty_json(env),
            gr.update(choices=[], value=None),
            "Please upload an environment JSON file."
        )

    try:
        with open(file.name, "r", encoding="utf-8") as f:
            env = json.load(f)

        errors = validate_env_structure(env)

        if errors:
            empty = empty_env()

            return (
                empty,
                pretty_json(empty),
                gr.update(choices=[], value=None),
                "Invalid environment JSON:\n"
                + "\n".join(f"- {error}" for error in errors)
            )

        function_choices = list(env["functions"].keys())

        return (
            env,
            pretty_json(env),
            gr.update(
                choices=function_choices,
                value=function_choices[0] if function_choices else None,
            ),
            f"Loaded environment from '{file.name}'."
        )

    except Exception as e:
        env = empty_env()

        return (
            env,
            pretty_json(env),
            gr.update(choices=[], value=None),
            f"Failed to load environment:\n{str(e)}"
        )
    


def add_function_io_pair(pairs, input_type, output_type):
    pairs = pairs or []

    input_type = input_type.strip()
    output_type = output_type.strip()

    if not input_type:
        return pairs, "Input type is required."

    if not output_type:
        return pairs, "Output type is required."

    pairs.append({
        "input": input_type,
        "output": output_type,
    })

    return pairs, "Added input/output pair."


def update_function_pair_input(pairs, index, value):
    pairs = pairs or []

    if 0 <= index < len(pairs):
        pairs[index]["input"] = value.strip()

    return pairs


def update_function_pair_output(pairs, index, value):
    pairs = pairs or []

    if 0 <= index < len(pairs):
        pairs[index]["output"] = value.strip()

    return pairs


def delete_function_pair_at_index(pairs, index):
    pairs = pairs or []

    if 0 <= index < len(pairs):
        pairs.pop(index)

    return pairs