import gradio as gr

from utils.environment_utils import (
    add_function_io_pair,
    clear_function_io_fields,
    delete_function_pair_at_index,
    empty_env,
    load_env_from_file,
    pretty_json,
    clear_property_fields,
    clear_function_fields,
    add_env_property,
    delete_env_property,
    add_function,
    load_function,
    update_function,
    delete_function,
    update_function_pair_input,
    update_function_pair_output,
)


def render_environment_tab(env_state):
    gr.Markdown("## Environment Builder")

    status = gr.Textbox(label="Status", interactive=False)

    with gr.Accordion("Upload Environment JSON", open=False):
        upload_env = gr.File(
            label="Upload Environment JSON",
            file_types=[".json"],
        )

    with gr.Accordion("Properties / Variables", open=False):
        gr.Markdown("## Add Property / Variable")

        section = gr.Radio(
            label="Section",
            choices=["source", "target", "variables"],
            value="source"
        )

        with gr.Row():
            property_name = gr.Textbox(label="Name", placeholder="property")
            property_type = gr.Textbox(label="Type", placeholder="float")

        with gr.Row():
            add_property_btn = gr.Button("Add / Update", variant="primary")
            delete_property_btn = gr.Button("Delete", variant="stop")

    with gr.Accordion("Functions", open=False):
        gr.Markdown("## Add / Edit Function")

        with gr.Row():
            selected_function = gr.Dropdown(label="Selected function", choices=[], interactive=True)
            load_function_btn = gr.Button("Load Function")

        function_name = gr.Textbox(label="Function name", placeholder="name")
        

        function_pairs_state = gr.State([])

        with gr.Row():
            new_function_input = gr.Textbox(label="Input type", placeholder="bag[string]")
            new_function_output = gr.Textbox(label="Output type", placeholder="string")
            add_pair_btn = gr.Button("Add Pair", variant="primary")

        pairs_container = gr.Column()


        @gr.render(inputs=function_pairs_state)
        def render_function_pairs(pairs):
            pairs = pairs or []

            for idx, pair in enumerate(pairs):
                with gr.Row():
                    input_box = gr.Textbox(
                        label=f"Input {idx + 1}",
                        value=pair.get("input", ""),
                        interactive=True,
                    )

                    output_box = gr.Textbox(
                        label=f"Output {idx + 1}",
                        value=pair.get("output", ""),
                        interactive=True,
                    )

                    delete_btn = gr.Button("Delete", variant="stop")

                    input_box.change(
                        fn=update_function_pair_input,
                        inputs=[function_pairs_state, gr.State(idx), input_box],
                        outputs=[function_pairs_state],
                    )

                    output_box.change(
                        fn=update_function_pair_output,
                        inputs=[function_pairs_state, gr.State(idx), output_box],
                        outputs=[function_pairs_state],
                    )

                    delete_btn.click(
                        fn=delete_function_pair_at_index,
                        inputs=[function_pairs_state, gr.State(idx)],
                        outputs=[function_pairs_state],
                    )

        with gr.Row():
            add_function_btn = gr.Button("Add Function", variant="primary")
            update_function_btn = gr.Button("Update Loaded Function")
            delete_function_btn = gr.Button("Delete Loaded Function", variant="stop")

    gr.Markdown("## JSON Preview / Download")

    env_json = gr.Code(
        label="Generated Environment JSON",
        language="json",
        value=pretty_json(empty_env()),
        lines=22,
    )

    upload_env.change(
    fn=load_env_from_file,
    inputs=[upload_env],
    outputs=[
        env_state,
        env_json,
        selected_function,
        status,
    ],
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

    add_pair_btn.click(
        fn=add_function_io_pair,
        inputs=[function_pairs_state, new_function_input, new_function_output],
        outputs=[function_pairs_state, status],
    ).then(
        fn=clear_function_io_fields,
        inputs=[],
        outputs=[new_function_input, new_function_output],
    )

    add_function_btn.click(
        fn=add_function,
        inputs=[env_state, function_name, function_pairs_state],
        outputs=[env_json, selected_function, status],
    )

    load_function_btn.click(
        fn=load_function,
        inputs=[env_state, selected_function],
        outputs=[function_name, function_pairs_state, status],
    )

    update_function_btn.click(
        fn=update_function,
        inputs=[env_state, selected_function, function_name, function_pairs_state],
        outputs=[env_json, selected_function, status],
    )
    
    delete_function_btn.click(
        fn=delete_function,
        inputs=[env_state, selected_function],
        outputs=[env_json, selected_function, status],
    ).then(
        fn=clear_function_fields,
        inputs=[],
        outputs=[function_name, function_pairs_state],
    )