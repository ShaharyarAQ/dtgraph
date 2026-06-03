import json
import tempfile
import gradio as gr

import io
from contextlib import redirect_stdout

from dtgraph import Rule
from dtgraph.type_checking.check_types import check_types
from type_checking.environment import Environment


def write_temp_json(data):
    temp = tempfile.NamedTemporaryFile(
        delete=False, suffix=".json", mode="w", encoding="utf-8"
    )
    json.dump(data, temp, indent=2)
    temp.close()
    return temp.name


def build_env_object(env_state):
    env_path = write_temp_json(env_state)
    return Environment(env_path)


def build_selected_rules(rules_state, selected_rules, env_state):
    env_obj = build_env_object(env_state)
    rule_objects = []

    for rule_name in selected_rules:
        rule_data = rules_state.get(rule_name)

        if not rule_data:
            continue

        rule_body = rule_data["body"]
        use_env = rule_data.get("use_env", True)
        type_strict = rule_data.get("type_strict", False)

        rule_obj = Rule(
            rule_body,
            env=env_obj if use_env else None,
            type_strict=type_strict,
        )

        rule_objects.append(rule_obj)

    return rule_objects


# def run_type_checking(rules_state, selected_rules, env_state):
#     try:
#         if not selected_rules:
#             return "Please select at least one rule."

#         env_obj = build_env_object(env_state)

#         rule_objects = build_selected_rules(
#             rules_state,
#             selected_rules,
#             env_state,
#         )

#         if not rule_objects:
#             return "No valid rules were created."

#         result = check_types(
#             rule_objects,
#             env_obj,
#         )

#         return f"Type checking completed successfully.\n\nResult:\n{result}"

#     except Exception:
#         return traceback.format_exc()

def run_type_checking(rules_state, selected_rules, env_state):
    log_buffer = io.StringIO()

    try:
        if not selected_rules:
            return "Please select at least one rule."

        env_obj = build_env_object(env_state)

        rule_objects = build_selected_rules(
            rules_state,
            selected_rules,
            env_state,
        )

        if not rule_objects:
            return "No valid rules were created."

        with redirect_stdout(log_buffer):
            check_types(
                rule_objects,
                env_obj,
            )

        logs = log_buffer.getvalue()

        return (
            "Type checking completed successfully.\n\n"
            f"Checked {len(rule_objects)} rule(s).\n\n"
            "Logs:\n"
            f"{logs}"
        )

    except Exception as e:
        logs = log_buffer.getvalue()

        return (
            "Type checking failed.\n\n"
            "Logs before failure:\n"
            f"{logs}\n\n"
            "Error:\n"
            f"{str(e)}"
        )


def refresh_rule_choices(rules_state):
    return gr.update(
        choices=list(rules_state.keys()),
        value=list(rules_state.keys()),
    )


def render_type_checking_tab(rules_state, env_state):
    gr.Markdown("## Type Checking")

    gr.Markdown("Select which rules should be checked against the environment.")

    selected_rules = gr.CheckboxGroup(
        label="Rules",
        choices=[],
    )

    refresh_rules_btn = gr.Button("Refresh Rules")
    run_btn = gr.Button("Run Type Checking", variant="primary")

    output = gr.Textbox(
        label="Type Checking Output",
        lines=18,
        interactive=False,
    )

    refresh_rules_btn.click(
        fn=refresh_rule_choices,
        inputs=[rules_state],
        outputs=[selected_rules],
    )

    run_btn.click(
        fn=run_type_checking,
        inputs=[
            rules_state,
            selected_rules,
            env_state,
        ],
        outputs=[output],
    )