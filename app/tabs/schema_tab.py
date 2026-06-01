import gradio as gr

from utils.schema_utils import (
    empty_schema,
    pretty_json,
    clear_node_fields,
    clear_shape_fields,
    clear_edge_fields,
    add_node,
    delete_node,
    update_schema_strict,
    update_shape_dropdown,
    add_shape,
    load_shape,
    update_shape,
    delete_shape,
    add_edge,
    load_edge,
    update_edge,
    delete_edge,
)


def render_schema_tab(title, schema_state):
    gr.Markdown(f"## {title}")

    status = gr.Textbox(label="Status", interactive=False)

    
    with gr.Row():
        schema_strict = gr.Checkbox(
            label="Strict schema",
            value=True,
            scale=1
        )

    gr.Markdown("## Add Node")

    with gr.Row():
        node_key_input = gr.Textbox(label="Node key", placeholder="Person")
        add_node_btn = gr.Button("Add Node", variant="primary")

    with gr.Row():
        selected_node = gr.Dropdown(label="Selected node", choices=[], interactive=True)
        delete_node_btn = gr.Button("Delete Selected Node")

    gr.Markdown("## Add / Edit Shape for Selected Node")

    with gr.Row():
        selected_shape = gr.Dropdown(
            label="Selected shape", choices=[], interactive=True
        )
        load_shape_btn = gr.Button("Load Shape")

    shape_labels = gr.Textbox(label="Labels", placeholder="Person, Scammer")
    shape_optional_labels = gr.Textbox(
        label="Optional labels", placeholder="OptionalLabel"
    )

    with gr.Row():
        shape_open_labels = gr.Checkbox(label="open_labels", value=False)
        shape_open_properties = gr.Checkbox(label="open_properties", value=False)

    shape_mandatory_properties = gr.Textbox(
        label="Mandatory properties", lines=4, placeholder="id:string\nname:string"
    )

    shape_optional_properties = gr.Textbox(
        label="Optional properties",
        lines=4,
        placeholder="email:string\nphone:string\nssn:string",
    )

    with gr.Row():
        add_shape_btn = gr.Button("Add Shape", variant="primary")
        update_shape_btn = gr.Button("Update Loaded Shape")
        delete_shape_btn = gr.Button("Delete Selected Shape")

    gr.Markdown("## Add / Edit Edge")

    with gr.Row():
        selected_edge = gr.Dropdown(label="Selected edge", choices=[], interactive=True)
        load_edge_btn = gr.Button("Load Edge")

    edge_name_input = gr.Textbox(label="Edge name", placeholder="AGGREGATED_CASHIN")

    with gr.Row():
        edge_from_input = gr.Textbox(label="From labels", placeholder="Person")
        edge_to_input = gr.Textbox(label="To labels", placeholder="CashInSummary")

    edge_open_properties = gr.Checkbox(label="open_properties", value=False)

    edge_mandatory_properties = gr.Textbox(
        label="Mandatory properties", lines=3, placeholder="weight:float"
    )

    edge_optional_properties = gr.Textbox(
        label="Optional properties", lines=3, placeholder="created_at:string"
    )

    with gr.Row():
        add_edge_btn = gr.Button("Add Edge", variant="primary")
        update_edge_btn = gr.Button("Update Loaded Edge")
        delete_edge_btn = gr.Button("Delete Selected Edge")

    gr.Markdown("## JSON Preview / Download")

    schema_json = gr.Code(
        label="Generated Schema JSON",
        language="json",
        value=pretty_json(empty_schema()),
        lines=24,
    )

    schema_strict.change(
    fn=update_schema_strict,
    inputs=[schema_state, schema_strict],
    outputs=[selected_node, selected_edge, schema_json, status],
    )

    add_node_btn.click(
        fn=add_node,
        inputs=[schema_state, node_key_input],
        outputs=[selected_node, selected_edge, schema_json, status],
    ).then(
        fn=update_shape_dropdown,
        inputs=[schema_state, selected_node],
        outputs=[selected_shape],
    ).then(
        fn=clear_node_fields,
        inputs=[],
        outputs=[node_key_input],
    )

    delete_node_btn.click(
        fn=delete_node,
        inputs=[schema_state, selected_node],
        outputs=[selected_node, selected_edge, schema_json, status],
    ).then(
        fn=update_shape_dropdown,
        inputs=[schema_state, selected_node],
        outputs=[selected_shape],
    )

    selected_node.change(
        fn=update_shape_dropdown,
        inputs=[schema_state, selected_node],
        outputs=[selected_shape],
    )

    add_shape_btn.click(
        fn=add_shape,
        inputs=[
            schema_state,
            selected_node,
            shape_labels,
            shape_optional_labels,
            shape_open_labels,
            shape_mandatory_properties,
            shape_optional_properties,
            shape_open_properties,
        ],
        outputs=[selected_node, selected_edge, schema_json, selected_shape, status],
    ).then(
        fn=clear_shape_fields,
        inputs=[],
        outputs=[
            shape_labels,
            shape_optional_labels,
            shape_open_labels,
            shape_mandatory_properties,
            shape_optional_properties,
            shape_open_properties,
        ],
    )

    load_shape_btn.click(
        fn=load_shape,
        inputs=[schema_state, selected_node, selected_shape],
        outputs=[
            shape_labels,
            shape_optional_labels,
            shape_open_labels,
            shape_mandatory_properties,
            shape_optional_properties,
            shape_open_properties,
            status,
        ],
    )

    update_shape_btn.click(
        fn=update_shape,
        inputs=[
            schema_state,
            selected_node,
            selected_shape,
            shape_labels,
            shape_optional_labels,
            shape_open_labels,
            shape_mandatory_properties,
            shape_optional_properties,
            shape_open_properties,
        ],
        outputs=[selected_node, selected_edge, schema_json, selected_shape, status],
    )

    delete_shape_btn.click(
        fn=delete_shape,
        inputs=[schema_state, selected_node, selected_shape],
        outputs=[selected_node, selected_edge, schema_json, selected_shape, status],
    ).then(
        fn=clear_shape_fields,
        inputs=[],
        outputs=[
            shape_labels,
            shape_optional_labels,
            shape_open_labels,
            shape_mandatory_properties,
            shape_optional_properties,
            shape_open_properties,
        ],
    )

    add_edge_btn.click(
        fn=add_edge,
        inputs=[
            schema_state,
            edge_name_input,
            edge_from_input,
            edge_to_input,
            edge_open_properties,
            edge_mandatory_properties,
            edge_optional_properties,
        ],
        outputs=[selected_node, selected_edge, schema_json, status],
    ).then(
        fn=clear_edge_fields,
        inputs=[],
        outputs=[
            edge_name_input,
            edge_from_input,
            edge_to_input,
            edge_open_properties,
            edge_mandatory_properties,
            edge_optional_properties,
        ],
    )

    load_edge_btn.click(
        fn=load_edge,
        inputs=[schema_state, selected_edge],
        outputs=[
            edge_name_input,
            edge_from_input,
            edge_to_input,
            edge_open_properties,
            edge_mandatory_properties,
            edge_optional_properties,
            status,
        ],
    )

    update_edge_btn.click(
        fn=update_edge,
        inputs=[
            schema_state,
            selected_edge,
            edge_name_input,
            edge_from_input,
            edge_to_input,
            edge_open_properties,
            edge_mandatory_properties,
            edge_optional_properties,
        ],
        outputs=[selected_node, selected_edge, schema_json, status],
    )

    delete_edge_btn.click(
        fn=delete_edge,
        inputs=[schema_state, selected_edge],
        outputs=[selected_node, selected_edge, schema_json, status],
    ).then(
        fn=clear_edge_fields,
        inputs=[],
        outputs=[
            edge_name_input,
            edge_from_input,
            edge_to_input,
            edge_open_properties,
            edge_mandatory_properties,
            edge_optional_properties,
        ],
    )
