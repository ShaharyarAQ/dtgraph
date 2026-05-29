import json
import gradio as gr


def empty_rules():
    return {}


def pretty_json(data):
    return json.dumps(data, indent=2)


def clear_rule_fields():
    return "", "", True, False


def refresh_rules(rules):
    rule_choices = list(rules.keys())

    return (
        gr.update(choices=rule_choices, value=rule_choices[0] if rule_choices else None),
        pretty_json(rules),
    )


def add_rule(rules, rule_name, rule_body, use_env, type_strict):
    rule_name = rule_name.strip()

    if not rule_name:
        return (*refresh_rules(rules), "Rule name is required.")

    if not rule_body.strip():
        return (*refresh_rules(rules), "Rule body is required.")

    rules[rule_name] = {
        "body": rule_body.strip(),
        "use_env": use_env,
        "type_strict": type_strict,
    }

    return (*refresh_rules(rules), f"Added rule '{rule_name}'.")


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


def update_rule(rules, selected_rule, rule_name, rule_body, use_env, type_strict):
    if not selected_rule:
        return (*refresh_rules(rules), "Select a rule first.")

    rule_name = rule_name.strip()

    if not rule_name:
        return (*refresh_rules(rules), "Rule name is required.")

    if not rule_body.strip():
        return (*refresh_rules(rules), "Rule body is required.")

    rules.pop(selected_rule, None)

    rules[rule_name] = {
        "body": rule_body.strip(),
        "use_env": use_env,
        "type_strict": type_strict,
    }

    return (*refresh_rules(rules), f"Updated rule '{rule_name}'.")


def delete_rule(rules, selected_rule):
    if not selected_rule:
        return (*refresh_rules(rules), "Select a rule first.")

    rules.pop(selected_rule, None)

    return (*refresh_rules(rules), f"Deleted rule '{selected_rule}'.")