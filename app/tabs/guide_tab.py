import gradio as gr


def info_box(text):
    gr.HTML(f"""
    <div style="
        border-left: 5px solid #2563eb;
        background: rgba(37, 99, 235, 0.15);
        padding: 12px 16px;
        border-radius: 8px;
        margin: 10px 0;
    ">
        {text}
    </div>
    """)


def render_guide_tab():
    gr.Markdown("# DTGraph Application Guide")

    gr.Markdown(
        "This guide explains the recommended workflow for using the DTGraph application."
    )

    info_box(
        "<b>Workflow:</b> Environment → Source Schema → Target Schema → Rules → Schema Conformance → Transformation"
    )

    with gr.Accordion("1. Environment", open=True):
        gr.Markdown("""
Use the **Environment** tab to define property names, variable names, and functions used by schemas and rules.

### Sections

- **source**: properties available in the source graph
- **target**: properties expected in the target graph
- **variables**: rule variables
- **functions**: helper functions used inside rules
""")

        gr.Code(
            label="Environment JSON Example",
            language="json",
            interactive=False,
            buttons = [],
            value="""{
  "source": {
    "name": "string",
    "age": "integer"
  },
  "target": {
    "fullName": "string"
  },
  "variables": {
    "amounts": "bag[string]"
  },
  "functions": {
    "toString": {
      "inputs": ["integer"],
      "outputs": ["string"]
    }
  }
}""",
        )

    with gr.Accordion("2. Source Schema", open=True):
        gr.Markdown("""
Use the **Source Schema** tab to define the expected structure of the input graph.

### A source schema contains

- node types
- node labels
- mandatory properties
- optional properties
- edge types
- edge endpoints
- edge properties
""")

        gr.Code(
            label="Source Graph Example",
            interactive=False,
            buttons = [],
            value="(:Person)-[:ACTED_IN]->(:Movie)",
        )

        gr.Markdown(
            "The source schema should describe the labels and properties expected before transformation."
        )

    with gr.Accordion("3. Target Schema", open=True):
        gr.Markdown("""
Use the **Target Schema** tab to define the expected structure of the transformed graph.

The target schema is used later during schema conformance checking.
""")

        gr.Code(
            label="Target Graph Example",
            interactive=False,
            buttons = [],
            value="(:Actor)-[:ACTED_WITH]->(:Actor)",
        )

        gr.Markdown(
            "The target schema should describe the graph structure that your rules are expected to generate."
        )

    with gr.Accordion("4. Rules", open=True):
        gr.Markdown("""
Use the **Rules** tab to create transformation rules.

A rule describes how patterns from the source graph are transformed into target graph patterns.

### Each rule has

- a rule name
- a rule body
- environment usage option
- type strict option
""")

        info_box(
            "<b>Important:</b> Type checking is integrated inside rule creation. "
            "When you add or update a rule, DTGraph validates the rule immediately."
        )

        gr.Markdown("""
### Rule Validation

- If **Use created env** is enabled, the rule is checked using the environment defined in the Environment tab.
- If **Type strict** is enabled, stricter type validation is applied.
""")

    with gr.Accordion("5. Schema Conformance", open=True):
        gr.Markdown("""
Use the **Schema Conformance** tab to check whether selected rules conform to the target schema.

This step verifies whether rules can generate graph elements that are valid according to the target schema.

### It checks

- whether generated node labels exist in the target schema
- whether generated edge types are allowed
- whether edge endpoints match the schema
- whether generated properties are valid
- whether property types match the environment and schema
""")

    with gr.Accordion("6. Transformation", open=True):
        gr.Markdown("""
Use the **Transformation** tab to apply selected rules to a Neo4j graph.

### You need to provide

- Neo4j URI
- database name
- username
- password
- selected rules
""")

        gr.Code(
            label="Default Neo4j Values",
            interactive=False,
            buttons = [],
            value="""URI: bolt://localhost:7687
Database: neo4j
Username: neo4j""",
        )

        gr.Markdown("""
After execution, the output box shows:

- transformation status
- number of applied rules
- execution time
- logs

You can also use **Abort Transformation** if an active transformation needs to be stopped.
""")

    with gr.Accordion("Recommended Usage Order", open=True):
        gr.Code(
            label="Recommended Workflow",
            interactive=False,
            buttons = [],
            value="""1. Create or upload the environment.
2. Create or upload the source schema.
3. Create or upload the target schema.
4. Create or upload rules.
5. Run schema conformance.
6. Apply transformation on Neo4j.
7. Review the result and logs.""",
        )

    with gr.Accordion("Common Issues", open=True):
        gr.Markdown("""
### Property not declared in environment

This means a schema property is not present in the selected environment section.
""")

        gr.Code(
            label="Example Error",
            interactive=False,
            buttons = [],
            value="property 'name' is not declared in env.source",
        )

        gr.Markdown("""
### Rule validation failed

This usually means:

- the rule syntax is invalid
- the rule uses an undefined property
- the rule uses an invalid function
- type strict checking failed

### Schema conformance failed

Check:

- target node labels
- target edge names
- edge source and target labels
- mandatory properties
- property types

### Transformation failed

This may happen because of:

- incorrect Neo4j credentials
- Neo4j server not running
- invalid database name
- rule execution error
- graph data not matching the expected rule pattern
""")

    with gr.Accordion("Best Practices", open=True):
        gr.Markdown("""
- Define the environment before creating source and target schemas.
- Keep source and target properties separated.
- Start with small schemas and simple rules.
- Validate each rule before adding many rules.
- Run schema conformance before transformation.
- Check logs carefully when something fails.
""")
