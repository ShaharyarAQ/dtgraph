import json
import gradio as gr
import tempfile
from type_checking.environment import Environment
import ast

from dtgraph import Rule


def write_temp_json(data):
    temp = tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".json",
        mode="w",
        encoding="utf-8",
    )
    json.dump(data, temp, indent=2)
    temp.close()
    return temp.name


def build_env_object(env_state):
    env_path = write_temp_json(env_state)
    return Environment(env_path)

def empty_rules():
    return {}


def pretty_json(data):
    return json.dumps(data, indent=2)


def clear_rule_fields():
    return "", "", True, False


def refresh_rules(rules):
    rule_choices = list(rules.keys())

    return (
        gr.update(
            choices=rule_choices,
            value=rule_choices[0] if rule_choices else None,
            allow_custom_value=False,
        ),
        pretty_json(rules),
    )


def validate_rule_body(rule_body, use_env, type_strict, env_state):
    try:
        env_obj = build_env_object(env_state) if use_env else None

        Rule(
            rule_body.strip(),
            env=env_obj,
            type_strict=type_strict,
        )

        if use_env and type_strict:
            return True, "Rule syntax and types are valid."

        return True, "Rule syntax is valid."

    except Exception as e:
        return False, f"Rule validation failed:\n{str(e)}"


def add_rule(rules, rule_name, rule_body, use_env, type_strict, env_state):
    rule_name = (rule_name or "").strip()
    rule_body = (rule_body or "").strip()

    if not rule_name:
        return (*refresh_rules(rules), "Rule name is required.")

    if not rule_body:
        return (*refresh_rules(rules), "Rule body is required.")

    is_valid, message = validate_rule_body(
        rule_body,
        use_env,
        type_strict,
        env_state,
    )

    if not is_valid:
        return (*refresh_rules(rules), message)

    rules[rule_name] = {
        "body": rule_body,
        "use_env": use_env,
        "type_strict": type_strict,
    }

    return (*refresh_rules(rules), f"Added rule '{rule_name}'.\n{message}")


def load_rule(rules, selected_rule):
    if not selected_rule or selected_rule not in rules:
        return "", "", True, False, "Select a rule first."

    rule = rules[selected_rule]

    return (
        selected_rule,
        rule.get("body", ""),
        rule.get("use_env", True),
        rule.get("type_strict", False),
        f"Loaded rule '{selected_rule}'."
    )


def update_rule(rules, selected_rule, rule_name, rule_body, use_env, type_strict, env_state):
    if not selected_rule:
        return (*refresh_rules(rules), "Select a rule first.")

    rule_name = (rule_name or "").strip()
    rule_body = (rule_body or "").strip()

    if not rule_name:
        return (*refresh_rules(rules), "Rule name is required.")

    if not rule_body:
        return (*refresh_rules(rules), "Rule body is required.")

    is_valid, message = validate_rule_body(
        rule_body,
        use_env,
        type_strict,
        env_state,
    )

    if not is_valid:
        return (*refresh_rules(rules), message)

    rules.pop(selected_rule, None)

    rules[rule_name] = {
        "body": rule_body,
        "use_env": use_env,
        "type_strict": type_strict,
    }

    return (*refresh_rules(rules), f"Updated rule '{rule_name}'.\n{message}")


def delete_rule(rules, selected_rule):
    if not selected_rule:
        return (*refresh_rules(rules), "Select a rule first.")

    rules.pop(selected_rule, None)

    return (*refresh_rules(rules), f"Deleted rule '{selected_rule}'.")



### Rules Uploading

def extract_rules_from_python_file(file_content):
    tree = ast.parse(file_content)

    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "Rules":
                    return ast.literal_eval(node.value)

    raise ValueError("Python file must contain a variable named 'Rules'.")


def validate_rules_file_structure(data):
    errors = []

    if not isinstance(data, list):
        return ["Rules must be a list."]

    for index, rule_data in enumerate(data):
        context = f"Rule at index {index}"

        if not isinstance(rule_data, dict):
            errors.append(f"{context} must be an object/dictionary.")
            continue

        required_keys = ["name", "body", "use_env", "type_strict"]

        for key in required_keys:
            if key not in rule_data:
                errors.append(f"{context} is missing required key '{key}'.")

        if "name" in rule_data and not isinstance(rule_data["name"], str):
            errors.append(f"{context}: 'name' must be a string.")

        if "body" in rule_data and not isinstance(rule_data["body"], str):
            errors.append(f"{context}: 'body' must be a string.")

        if "use_env" in rule_data and not isinstance(rule_data["use_env"], bool):
            errors.append(f"{context}: 'use_env' must be True or False.")

        if "type_strict" in rule_data and not isinstance(rule_data["type_strict"], bool):
            errors.append(f"{context}: 'type_strict' must be True or False.")

    return errors


def load_rules_from_file(file, env_state):
    if file is None:
        rules = empty_rules()
        return (
            rules,
            *refresh_rules(rules),
            "Rules upload cleared. Reset to empty rules."
        )

    try:
        with open(file.name, "r", encoding="utf-8") as f:
            file_content = f.read()

        uploaded_rules = extract_rules_from_python_file(file_content)

        structure_errors = validate_rules_file_structure(uploaded_rules)

        if structure_errors:
            rules = empty_rules()
            return (
                rules,
                *refresh_rules(rules),
                "Invalid rules Python file:\n"
                + "\n".join(f"- {error}" for error in structure_errors)
            )

        validated_rules = {}

        for rule_data in uploaded_rules:
            rule_name = rule_data["name"].strip()
            rule_body = rule_data["body"].strip()
            use_env = rule_data["use_env"]
            type_strict = rule_data["type_strict"]

            if not rule_name:
                rules = empty_rules()
                return (
                    rules,
                    *refresh_rules(rules),
                    "Invalid rules Python file:\n- Rule name cannot be empty."
                )

            if rule_name in validated_rules:
                rules = empty_rules()
                return (
                    rules,
                    *refresh_rules(rules),
                    f"Invalid rules Python file:\n- Duplicate rule name '{rule_name}'."
                )

            if not rule_body:
                rules = empty_rules()
                return (
                    rules,
                    *refresh_rules(rules),
                    f"Invalid rules Python file:\n- Rule '{rule_name}' body cannot be empty."
                )

            is_valid, message = validate_rule_body(
                rule_body,
                use_env,
                type_strict,
                env_state,
            )

            if not is_valid:
                rules = empty_rules()
                return (
                    rules,
                    *refresh_rules(rules),
                    f"Rule upload failed while validating '{rule_name}'.\n\n{message}"
                )

            validated_rules[rule_name] = {
                "body": rule_body,
                "use_env": use_env,
                "type_strict": type_strict,
            }

        return (
            validated_rules,
            *refresh_rules(validated_rules),
            f"Loaded {len(validated_rules)} rule(s) from '{file.name}'."
        )

    except Exception as e:
        rules = empty_rules()
        return (
            rules,
            *refresh_rules(rules),
            f"Failed to load rules:\n{str(e)}"
        )