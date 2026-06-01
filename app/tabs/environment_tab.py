import gradio as gr

from utils.environment_utils import (
    empty_env,
    pretty_json,
    clear_property_fields,
    clear_function_fields,
    add_env_property,
    delete_env_property,
    add_function,
    load_function,
    update_function,
    delete_function,
)


def render_environment_tab(env_state):
    gr.Markdown("## Environment Builder")

    status = gr.Textbox(label="Status", interactive=False)

    gr.Markdown("## Add Property / Variable")

    section = gr.Radio(
        label="Section",
        choices=["source", "target", "variables"],
        value="source"
    )

    with gr.Row():
        property_name = gr.Textbox(label="Name", placeholder="amount")
        property_type = gr.Textbox(label="Type", placeholder="float")

    with gr.Row():
        add_property_btn = gr.Button("Add / Update", variant="primary")
        delete_property_btn = gr.Button("Delete")

    gr.Markdown("## Add / Edit Function")

    with gr.Row():
        selected_function = gr.Dropdown(label="Selected function", choices=[], interactive=True)
        load_function_btn = gr.Button("Load Function")

    function_name = gr.Textbox(label="Function name", placeholder="head")
    function_inputs = gr.Textbox(label="Input types", placeholder="bag[string]")
    function_output = gr.Textbox(label="Output type", placeholder="string")

    with gr.Row():
        add_function_btn = gr.Button("Add Function", variant="primary")
        update_function_btn = gr.Button("Update Loaded Function")
        delete_function_btn = gr.Button("Delete Selected Function")

    gr.Markdown("## JSON Preview / Download")

    env_json = gr.Code(
        label="Generated Environment JSON",
        language="json",
        value=pretty_json(empty_env()),
        lines=22,
    )

    add_property_btn.click(
        fn=add_env_property,
        inputs=[env_state, section, property_name, property_type],
        outputs=[env_json, selected_function, status],
    ).then(
        fn=clear_property_fields,
        inputs=[],
        outputs=[property_name, property_type],
    )

    delete_property_btn.click(
        fn=delete_env_property,
        inputs=[env_state, section, property_name],
        outputs=[env_json, selected_function, status],
    ).then(
        fn=clear_property_fields,
        inputs=[],
        outputs=[property_name, property_type],
    )

    add_function_btn.click(
        fn=add_function,
        inputs=[env_state, function_name, function_inputs, function_output],
        outputs=[env_json, selected_function, status],
    ).then(
        fn=clear_function_fields,
        inputs=[],
        outputs=[function_name, function_inputs, function_output],
    )

    load_function_btn.click(
        fn=load_function,
        inputs=[env_state, selected_function],
        outputs=[function_name, function_inputs, function_output, status],
    )

    update_function_btn.click(
        fn=update_function,
        inputs=[env_state, selected_function, function_name, function_inputs, function_output],
        outputs=[env_json, selected_function, status],
    )

    delete_function_btn.click(
        fn=delete_function,
        inputs=[env_state, selected_function],
        outputs=[env_json, selected_function, status],
    ).then(
        fn=clear_function_fields,
        inputs=[],
        outputs=[function_name, function_inputs, function_output],
    )