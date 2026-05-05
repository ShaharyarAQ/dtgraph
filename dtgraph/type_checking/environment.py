import json


class Environment:

    def __init__(self, path):
        with open(path) as f:
            data = json.load(f)

        self.source = data["source"]
        self.target = data["target"]
        self.variables = data["variables"]
        self.functions = data["functions"]