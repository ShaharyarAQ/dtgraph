import json


class SchemaLoader:
    def __init__(self, path, env=None, section=None):
        self.path = path
        self.env = env
        self.section = section
        self.schema = self._load()

    def _load(self):
        with open(self.path, "r") as f:
            raw_schema = json.load(f)

        normalized = self._normalize_schema(raw_schema)

        ## Validating provided schema (source/target) against the given environment

        if self.env is not None:
            errors = self.validate_schema_against_env(
                normalized,
                self.env,
                self.section
            )

            if errors:
                raise ValueError(
                    f"{self.section.capitalize()} schema validation failed:\n"
                    + "\n".join(f"- {e}" for e in errors)
                )

        return normalized

    def _normalize_schema(self, schema):
        return {
            "strict": schema.get("strict", True),
            "nodes": self._normalize_nodes(schema.get("nodes", {})),
            "edges": self._normalize_edges(schema.get("edges", {})),
        }

    # Node normalization
    def _normalize_nodes(self, nodes):
        normalized = {}

        for node_name, shapes in nodes.items():
            normalized[node_name] = []

            for shape in shapes:
                normalized[node_name].append(
                    {
                        "labels": shape.get("labels", [node_name]),
                        "optional_labels": shape.get("optional_labels", []),
                        "open_labels": shape.get("open_labels", False),
                        "mandatory_properties": self._normalize_properties(
                            shape.get("mandatory_properties", {})
                        ),
                        "optional_properties": self._normalize_properties(
                            shape.get("optional_properties", {})
                        ),
                        "open_properties": shape.get("open_properties", False),
                    }
                )

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
                "open_properties": edge_def.get("open_properties", False),
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
    

    ### Schema validation against the provided Environment

    def validate_schema_against_env(self, schema_data, env, section):
        errors = []

        if env is None:
            return errors

        if section not in ["source", "target"]:
            errors.append(
                f"Invalid environment section '{section}'. Expected 'source' or 'target'."
            )
            return errors

        env_props = getattr(env, section, None)

        if env_props is None:
            errors.append(f"Environment does not contain section '{section}'.")
            return errors

        # validate node properties
        for node_key, shapes in schema_data.get("nodes", {}).items():
            for shape_index, shape in enumerate(shapes):
                for prop_group in ["mandatory_properties", "optional_properties"]:
                    for prop_name, prop_data in shape.get(prop_group, {}).items():
                        schema_type = prop_data.get("type")

                        if prop_name not in env_props:
                            errors.append(
                                f"Node '{node_key}', shape {shape_index + 1}: "
                                f"property '{prop_name}' is not declared in env.{section}."
                            )
                            continue

                        env_type = env_props[prop_name]

                        if schema_type != env_type:
                            errors.append(
                                f"Node '{node_key}', shape {shape_index + 1}: "
                                f"property '{prop_name}' has type '{schema_type}' in schema "
                                f"but '{env_type}' in env.{section}."
                            )

        # validate edge properties
        for edge_name, edge_data in schema_data.get("edges", {}).items():
            for prop_group in ["mandatory_properties", "optional_properties"]:
                for prop_name, prop_data in edge_data.get(prop_group, {}).items():
                    schema_type = prop_data.get("type")

                    if prop_name not in env_props:
                        errors.append(
                            f"Edge '{edge_name}': property '{prop_name}' "
                            f"is not declared in env.{section}."
                        )
                        continue

                    env_type = env_props[prop_name]

                    if schema_type != env_type:
                        errors.append(
                            f"Edge '{edge_name}': property '{prop_name}' has type "
                            f"'{schema_type}' in schema but '{env_type}' in env.{section}."
                        )

        return errors
