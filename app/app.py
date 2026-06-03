import sys
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = APP_DIR.parent
DTGRAPH_DIR = PROJECT_ROOT / "dtgraph"

sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(DTGRAPH_DIR))

import gradio as gr

from tabs.schema_tab import render_schema_tab
from utils.schema_utils import empty_schema

from tabs.environment_tab import render_environment_tab
from utils.environment_utils import empty_env

from tabs.rules_tab import render_rules_tab
from utils.rules_utils import empty_rules

from tabs.conformance_tab import render_conformance_tab

from tabs.type_checking_tab import render_type_checking_tab

from tabs.transformation_tab import render_transformation_tab


with gr.Blocks(title="DTGraph") as app:

    source_schema_state = gr.State(empty_schema())
    target_schema_state = gr.State(empty_schema())
    env_state = gr.State(empty_env())
    rules_state = gr.State(empty_rules())
    transformation_state = gr.State(None)

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

    with gr.Tab("Rules"):
        render_rules_tab(rules_state)

    with gr.Tab("Schema Conformance"):
        render_conformance_tab(
            rules_state=rules_state,
            target_schema_state=target_schema_state,
            env_state=env_state,
        )

    with gr.Tab("Type Checking"):
        render_type_checking_tab(
            rules_state=rules_state,
            env_state=env_state,
        )

    with gr.Tab("Transformation"):
        render_transformation_tab(
            rules_state=rules_state,
            env_state=env_state,
            transformation_state=transformation_state,
        )


if __name__ == "__main__":
    app.launch()