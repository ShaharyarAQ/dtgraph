import gradio as gr

from utils.rules_utils import (
    empty_rules,
    pretty_json,
    clear_rule_fields,
    add_rule,
    load_rule,
    update_rule,
    delete_rule,
)


def render_rules_tab(rules_state):
    gr.Markdown("## Rules Editor")

    status = gr.Textbox(label="Status", interactive=False)

    with gr.Row():
        selected_rule = gr.Dropdown(label="Selected rule", choices=[], interactive=True)
        load_rule_btn = gr.Button("Load Rule")

    rule_name = gr.Textbox(label="Rule name", placeholder="Rule1")

    rule_body = gr.Code(
        label="Rule body",
        language="python",
        lines=18,
        value=""
    )

    with gr.Row():
        use_env = gr.Checkbox(label="Use created env", value=True)
        type_strict = gr.Checkbox(label="type_strict", value=False)

    with gr.Row():
        add_rule_btn = gr.Button("Add Rule", variant="primary")
        update_rule_btn = gr.Button("Update Loaded Rule")
        delete_rule_btn = gr.Button("Delete Selected Rule", variant="stop")

    gr.Markdown("### Stored Rules Preview")

    rules_json = gr.Code(
        label="Rules",
        language="json",
        value=pretty_json(empty_rules()),
        lines=18,
    )

    add_rule_btn.click(
        fn=add_rule,
        inputs=[rules_state, rule_name, rule_body, use_env, type_strict],
        outputs=[selected_rule, rules_json, status],
    ).then(
        fn=clear_rule_fields,
        inputs=[],
        outputs=[rule_name, rule_body, use_env, type_strict],
    )

    load_rule_btn.click(
        fn=load_rule,
        inputs=[rules_state, selected_rule],
        outputs=[rule_name, rule_body, use_env, type_strict, status],
    )

    update_rule_btn.click(
        fn=update_rule,
        inputs=[rules_state, selected_rule, rule_name, rule_body, use_env, type_strict],
        outputs=[selected_rule, rules_json, status],
    )

    delete_rule_btn.click(
        fn=delete_rule,
        inputs=[rules_state, selected_rule],
        outputs=[selected_rule, rules_json, status],
    ).then(
        fn=clear_rule_fields,
        inputs=[],
        outputs=[rule_name, rule_body, use_env, type_strict],
    )