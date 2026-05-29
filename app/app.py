import gradio as gr

from tabs.schema_tab import render_schema_tab
from utils.schema_utils import empty_schema

from tabs.environment_tab import render_environment_tab
from utils.env_utils import empty_env

from tabs.rules_tab import render_rules_tab
from utils.rules_utils import empty_rules


with gr.Blocks(title="DTGraph") as app:
    source_schema_state = gr.State(empty_schema())
    target_schema_state = gr.State(empty_schema())
    env_state = gr.State(empty_env())
    rules_state = gr.State(empty_rules())

    gr.Markdown("# DTGraph")

    with gr.Tab("Source Schema"):
        render_schema_tab(
            title="Source Schema Builder",
            schema_state=source_schema_state,
        )

    with gr.Tab("Target Schema"):
        render_schema_tab(
            title="Target Schema Builder",
            schema_state=target_schema_state,
        )

    with gr.Tab("Environment"):
        render_environment_tab(env_state)

    # with gr.Tab("Rules"):
    #     gr.Markdown("Rules editor will go here.")

    with gr.Tab("Rules"):
        render_rules_tab(rules_state)

    with gr.Tab("Schema Conformance"):
        gr.Markdown("Schema conformance checker will go here.")

    with gr.Tab("Type Checking"):
        gr.Markdown("Type checker will go here.")


if __name__ == "__main__":
    app.launch()