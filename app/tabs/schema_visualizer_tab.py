import gradio as gr
from utils.schema_visualizer_utils import visualize_schema


def render_schema_visualizer_tab(source_schema_state, target_schema_state):
    gr.Markdown("## Schema Visualizer")

    with gr.Row():
        source_btn = gr.Button("Visualize Source Schema", variant="primary")
        target_btn = gr.Button("Visualize Target Schema", variant="primary")

    with gr.Accordion("Source Schema Graph", open=True):
        source_output = gr.HTML()

    with gr.Accordion("Target Schema Graph", open=True):
        target_output = gr.HTML()

    source_btn.click(
        fn=visualize_schema,
        inputs=[source_schema_state],
        outputs=[source_output],
    )

    target_btn.click(
        fn=visualize_schema,
        inputs=[target_schema_state],
        outputs=[target_output],
    )