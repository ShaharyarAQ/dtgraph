import json
import tempfile
import traceback
import io
from contextlib import redirect_stdout

import gradio as gr

from dtgraph import Neo4jGraph, Rule, Transformation
from type_checking.environment import Environment


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


def build_selected_rules(rules_state, selected_rules, env_state):
    env_obj = build_env_object(env_state)
    rule_objects = []

    for rule_name in selected_rules:
        rule_data = rules_state.get(rule_name)

        if not rule_data:
            continue

        rule_obj = Rule(
            rule_data["body"],
            env=env_obj if rule_data.get("use_env", True) else None,
            type_strict=rule_data.get("type_strict", False),
        )

        rule_objects.append(rule_obj)

    return rule_objects


def refresh_rule_choices(rules_state):
    return gr.update(
        choices=list(rules_state.keys()),
        value=list(rules_state.keys()),
    )


def run_transformation(
    rules_state,
    selected_rules,
    env_state,
    uri,
    database,
    username,
    password,
    with_diagnose,
    explain,
    profile,
):
    log_buffer = io.StringIO()

    try:
        if not selected_rules:
            return None, "Please select at least one rule."

        rule_objects = build_selected_rules(
            rules_state,
            selected_rules,
            env_state,
        )

        if not rule_objects:
            return None, "No valid rules were created."

        graph = Neo4jGraph(
            uri,
            database=database,
            username=username,
            password=password,
        )

        transformation = Transformation(
            rule_objects,
            with_diagnose=with_diagnose,
            explain=explain,
            profile=profile,
        )

        with redirect_stdout(log_buffer):
            total_time = transformation.apply_on(graph)

        logs = log_buffer.getvalue()

        return (
            transformation,
            "Transformation completed successfully.\n\n"
            f"Applied {len(rule_objects)} rule(s).\n"
            f"Total execution time: {total_time} ms\n\n"
            "Logs:\n"
            f"{logs}",
        )

    except Exception:
        logs = log_buffer.getvalue()

        return (
            None,
            "Transformation failed.\n\n"
            "Logs before failure:\n"
            f"{logs}\n\n"
            "Error:\n"
            f"{traceback.format_exc()}",
        )


def abort_transformation(transformation_state):
    log_buffer = io.StringIO()

    try:
        if transformation_state is None:
            return None, "No active transformation to abort."

        with redirect_stdout(log_buffer):
            transformation_state.abort()

        logs = log_buffer.getvalue()

        return (
            None,
            "Transformation aborted successfully.\n\n"
            "Logs:\n"
            f"{logs}",
        )

    except Exception:
        logs = log_buffer.getvalue()

        return (
            transformation_state,
            "Abort failed.\n\n"
            "Logs before failure:\n"
            f"{logs}\n\n"
            "Error:\n"
            f"{traceback.format_exc()}",
        )


def render_transformation_tab(rules_state, env_state, transformation_state):
    gr.Markdown("## Transformation Execution")

    with gr.Accordion("Neo4j Connection", open=True):
        uri = gr.Textbox(
            label="URI",
            value="bolt://localhost:7687",
        )

        database = gr.Textbox(
            label="Database",
            value="neo4j",
        )

        username = gr.Textbox(
            label="Username",
            value="neo4j",
        )

        password = gr.Textbox(
            label="Password",
            value="internship",
            type="password",
        )

    gr.Markdown("## Select Rules")

    selected_rules = gr.CheckboxGroup(
        label="Rules",
        choices=[],
    )

    refresh_rules_btn = gr.Button("Refresh Rules")

    with gr.Row():
        with_diagnose = gr.Checkbox(
            label="with_diagnose",
            value=True,
        )

        explain = gr.Checkbox(
            label="EXPLAIN",
            value=False,
        )

        profile = gr.Checkbox(
            label="PROFILE",
            value=False,
        )

    with gr.Row():
        run_btn = gr.Button(
            "Apply Transformation",
            variant="primary",
        )

        abort_btn = gr.Button(
            "Abort Transformation",
            variant="stop",
        )

    output = gr.Textbox(
        label="Transformation Output",
        lines=20,
        interactive=False,
    )

    refresh_rules_btn.click(
        fn=refresh_rule_choices,
        inputs=[rules_state],
        outputs=[selected_rules],
    )

    run_btn.click(
        fn=run_transformation,
        inputs=[
            rules_state,
            selected_rules,
            env_state,
            uri,
            database,
            username,
            password,
            with_diagnose,
            explain,
            profile,
        ],
        outputs=[
            transformation_state,
            output,
        ],
    )

    abort_btn.click(
        fn=abort_transformation,
        inputs=[transformation_state],
        outputs=[
            transformation_state,
            output,
        ],
    )