import json

class SchemaLoader:
    def __init__(self, path):
        self.path = path
        self.schema = self._load()

    def _load(self):
        with open(self.path, "r") as f:
            raw_schema = json.load(f)

        return self._normalize_schema(raw_schema)

    def _normalize_schema(self, schema):
        return {
            "strict": schema.get("strict", True),
            "nodes": self._normalize_nodes(schema.get("nodes", {})),
            "edges": self._normalize_edges(schema.get("edges", {}))
        }

    # Node normalization
    def _normalize_nodes(self, nodes):
        normalized = {}

        for node_name, shapes in nodes.items():
            normalized[node_name] = []

            for shape in shapes:
                normalized[node_name].append({
                    "labels": shape.get("labels", [node_name]),
                    "optional_labels": shape.get("optional_labels", []),
                    "open_labels": shape.get("open_labels", False),

                    "mandatory_properties": self._normalize_properties(
                        shape.get("mandatory_properties", {})
                    ),

                    "optional_properties": self._normalize_properties(
                        shape.get("optional_properties", {})
                    ),

                    "open_properties": shape.get("open_properties", False)
                })

        return normalized

    # Edge normalization
    def _normalize_edges(self, edges):
        normalized = {}

        for edge_name, edge_def in edges.items():
            normalized[edge_name] = {
                "from": edge_def.get("from", []),
                "to": edge_def.get("to", []),

                "mandatory_properties": self._normalize_properties(
                    edge_def.get("mandatory_properties", {})
                ),

                "optional_properties": self._normalize_properties(
                    edge_def.get("optional_properties", {})
                ),

                "open_properties": edge_def.get("open_properties", False)
            }

        return normalized

    # Property normalization
    def _normalize_properties(self, properties):
        normalized = {}

        for prop_name, prop_def in properties.items():

            if isinstance(prop_def, str):
                normalized[prop_name] = {"type": prop_def}

            elif isinstance(prop_def, dict):
                normalized[prop_name] = {"type": prop_def.get("type")}

        return normalized

    def __getitem__(self, key):
        return self.schema[key]

    def get(self, key, default=None):
        return self.schema.get(key, default)

    def __repr__(self):
        return f"<SchemaLoader path={self.path}>"