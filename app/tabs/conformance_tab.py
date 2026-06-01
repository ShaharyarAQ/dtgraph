import json
import tempfile
import traceback
import gradio as gr

from dtgraph import Rule
from dtgraph.pg_schema.check_schema import check_schema
from pg_schema.loader import SchemaLoader
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


def build_schema_object(schema_state):
    schema_path = write_temp_json(schema_state)
    return SchemaLoader(schema_path)


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


def run_schema_conformance(rules_state, selected_rules, target_schema_state, env_state):
    try:
        if not selected_rules:
            return "Please select at least one rule."

        schema_obj = build_schema_object(target_schema_state)
        rule_objects = build_selected_rules(rules_state, selected_rules, env_state)

        if not rule_objects:
            return "No valid rules were created."

        result = check_schema(
            rule_objects,
            schema_obj,
        )

        return f"Schema conformance completed successfully.\n\nResult:\n{result}"

    except Exception:
        return traceback.format_exc()


def refresh_rule_choices(rules_state):
    return gr.update(choices=list(rules_state.keys()), value=list(rules_state.keys()))


def render_conformance_tab(rules_state, target_schema_state, env_state):
    gr.Markdown("## Schema Conformance")

    gr.Markdown("Select which rules should be checked against the target schema.")

    selected_rules = gr.CheckboxGroup(
        label="Rules",
        choices=[],
    )

    refresh_rules_btn = gr.Button("Refresh Rules")
    run_btn = gr.Button("Run Schema Conformance", variant="primary")

    output = gr.Textbox(
        label="Conformance Output",
        lines=18,
        interactive=False,
    )

    refresh_rules_btn.click(
        fn=refresh_rule_choices,
        inputs=[rules_state],
        outputs=[selected_rules],
    )

    run_btn.click(
        fn=run_schema_conformance,
        inputs=[
            rules_state,
            selected_rules,
            target_schema_state,
            env_state,
        ],
        outputs=[output],
    )
