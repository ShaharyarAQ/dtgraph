from pyvis.network import Network
import html


def props_to_label(props):
    if not props:
        return []

    return [f"{name}: {data.get('type', '')}" for name, data in props.items()]


def node_display_label(node_key, shapes):
    lines = []

    for shape in shapes:
        labels = shape.get("labels", [])
        optional_labels = [f"{label}?" for label in shape.get("optional_labels", [])]

        main_label = ":".join(labels + optional_labels)

        if main_label:
            lines.append(main_label)
        else:
            lines.append(node_key)

        mandatory_props = props_to_label(shape.get("mandatory_properties", {}))
        optional_props = props_to_label(shape.get("optional_properties", {}))

        if mandatory_props or optional_props:
            lines.append("")
            lines.extend(mandatory_props)

            for prop in optional_props:
                lines.append(f"{prop}?")

    return "\n".join(lines)


def build_label_to_node_map(nodes):
    label_to_node = {}

    for node_key, shapes in nodes.items():
        label_to_node[node_key] = node_key

        for shape in shapes:
            for label in shape.get("labels", []):
                label_to_node[label] = node_key

            for label in shape.get("optional_labels", []):
                label_to_node[label] = node_key

    return label_to_node


def visualize_schema(schema):
    if not schema:
        return "<p>No schema available.</p>"

    nodes = schema.get("nodes", {})
    edges = schema.get("edges", {})

    if not nodes:
        return "<p>No nodes found in schema.</p>"

    net = Network(
        height="650px",
        width="100%",
        directed=True,
        notebook=False,
        bgcolor="#e5e7eb",
        font_color="#111827",
        cdn_resources="in_line",
    )

    net.set_options("""
    {
      "nodes": {
        "shape": "circle",
        "margin": 12,
        "size": 35,
        "font": {
        "size": 14,
        "color": "#111827",
        "multi": true
        },
        "borderWidth": 2
      },
      "edges": {
        "arrows": {
          "to": {
            "enabled": true,
            "scaleFactor": 0.8
          }
        },
        "font": {
          "size": 12,
          "align": "middle",
          "color": "#111827"
        },
        "color": {
          "color": "#9ca3af",
          "highlight": "#2563eb"
        },
        "smooth": {
          "enabled": true,
          "type": "dynamic"
        }
      },
      "physics": {
        "enabled": true,
        "barnesHut": {
          "gravitationalConstant": -25000,
          "springLength": 190,
          "springConstant": 0.04,
          "avoidOverlap": 1
        },
        "stabilization": {
          "enabled": true,
          "iterations": 300
        }
      },
        "interaction": {
        "hover": false,
        "navigationButtons": true,
        "keyboard": true
        }
    }
    """)

    colors = [
        "#2563eb",
        "#16a34a",
        "#dc2626",
        "#9333ea",
        "#ea580c",
        "#0891b2",
        "#ca8a04",
        "#4f46e5",
        "#be123c",
        "#0f766e",
    ]

    for index, (node_key, shapes) in enumerate(nodes.items()):
        net.add_node(
            node_key,
            label=node_display_label(node_key, shapes),
            color=colors[index % len(colors)],
        )

    label_to_node = build_label_to_node_map(nodes)

    edge_id = 0

    for edge_name, edge_data in edges.items():
        from_labels = edge_data.get("from", [])
        to_labels = edge_data.get("to", [])

        for from_label in from_labels:
            from_node = label_to_node.get(from_label)

            if not from_node:
                continue

            for to_label in to_labels:
                to_node = label_to_node.get(to_label)

                if not to_node:
                    continue

                net.add_edge(
                    from_node,
                    to_node,
                    label=edge_name,
                    id=f"edge_{edge_id}",
                )

                edge_id += 1

    graph_html = net.generate_html(notebook=False)
    escaped_html = html.escape(graph_html)

    return f"""
    <iframe
        srcdoc="{escaped_html}"
        style="width:100%; height:700px; border:1px solid #9ca3af; border-radius:8px; background:#e5e7eb;"
    ></iframe>
    """
