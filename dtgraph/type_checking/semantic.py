import re

from .expression_parser import parser, ASTTransformer
from .ast_nodes import BooleanLiteral, ComparisonExpression, Literal, LogicalExpression, PropertyAccess, FunctionCall, BinaryExpression, UnaryExpression


class SemanticAnalyzer:

    def __init__(self, env):
        self.env = env

    def analyze(self, rule_dict):

        for c in rule_dict.get("constructors", []):

            labels = c.get("labels")
            if not labels:
                continue

            for prop in c.get("properties", []):
                key = prop["key"]
                raw_value = prop["value"].strip()

                # Build AST
                ast = parse_expression(raw_value)

                prop["ast"] = ast

                ## Translate to cypher
                prop["value"] = to_cypher(ast)

                print("AST:")
                print_ast(ast)

                # Type check
                if key not in self.env.target:
                    raise Exception(f"Unknown target property: {key}")

                expected = self.env.target[key]
                actual = self.infer_type(ast)

                expected_types = expected if isinstance(expected, list) else [expected]

                def format_types(types):
                    if len(types) == 1:
                        return types[0]
                    return " or ".join(types)

                if not any(t in expected_types for t in actual):
                    raise Exception(
                        f"Type mismatch for '{key}': expected {format_types(expected_types)}, got {format_types(actual)}"
                    )

    # Type inference
    def infer_type(self, node):

        if isinstance(node, Literal):
            return [node.type]

        if isinstance(node, PropertyAccess):
            if node.prop not in self.env.source:
                raise Exception(f"Unknown source property: {node.prop}")
            t = self.env.source[node.prop]
            return t if isinstance(t, list) else [t]

        if isinstance(node, FunctionCall):

            if node.name not in self.env.functions:
                raise Exception(f"Unknown function '{node.name}'")

            func = self.env.functions[node.name]

            if len(node.args) != len(func["inputs"]):
                raise Exception(
                    f"Function '{node.name}' expects {len(func['inputs'])} arguments"
                )

            for arg, expected in zip(node.args, func["inputs"]):
                actual = self.infer_type(arg)

                expected_types = expected if isinstance(expected, list) else [expected]

                if not any(t in expected_types for t in actual):
                    raise Exception(
                        f"Function '{node.name}' expected {expected_types}, got {actual}"
                    )

            out = func["output"]
            return out if isinstance(out, list) else [out]
        
        #### New blocks for expressions
        if isinstance(node, BinaryExpression):

            left_types = self.infer_type(node.left)
            right_types = self.infer_type(node.right)

            result = []

            for l in left_types:
                for r in right_types:

                    if node.operator in ["+", "-", "*", "/"]:

                        if l == "integer" and r == "integer":
                            result.append("integer")

                        elif node.operator == "+" and l == "string" and r == "string":
                            result.append("string")

                        else:
                            raise Exception(
                            f"Invalid operation: {l} {node.operator} {r}"
                            )

            if not result:
                raise Exception(
                    f"Could not infer type for operation: {left_types} {node.operator} {right_types}"
                )

            return list(set(result))
        
        if isinstance(node, BooleanLiteral):
            return ["boolean"]
        
        if isinstance(node, UnaryExpression):

            operand = self.infer_type(node.operand)

            if node.operator == "-" and "integer" in operand:
                return ["integer"]

            if node.operator == "NOT" and "boolean" in operand:
                return ["boolean"]

            raise Exception(f"Invalid unary operation: {node.operator} {operand}")
        
        if isinstance(node, ComparisonExpression):

            left = self.infer_type(node.left)
            right = self.infer_type(node.right)

            for l in left:
                for r in right:

                    if l == r:

                        if node.operator in ["==", "!="]:
                            return ["boolean"]

                        if l == "integer" and node.operator in [">", "<", ">=", "<="]:
                            return ["boolean"]

            raise Exception(
                f"Invalid comparison: cannot apply '{node.operator}' to {left} and {right}"
            )
        
        if isinstance(node, LogicalExpression):

            left = self.infer_type(node.left)
            right = self.infer_type(node.right)

            if all(t == "boolean" for t in left) and all(t == "boolean" for t in right):
                return ["boolean"]

            raise Exception(f"Logical operations require boolean operands, got {left} and {right}")

        raise Exception("Unknown AST node")

def parse_expression(expr: str):
    expr = expr.strip()

    try:
        tree = parser.parse(expr)
        return ASTTransformer().transform(tree)
    except Exception:
        return legacy_parse_expression(expr)

def legacy_parse_expression(expr: str):
    expr = expr.strip()

    # String
    if expr.startswith('"') and expr.endswith('"'):
        return Literal(expr, "string")

    # Integer
    if expr.isdigit():
        return Literal(expr, "integer")

    # Function call
    match = re.match(r"(\w+)\((.*)\)", expr)
    if match:
        name = match.group(1)
        args_str = match.group(2)
        args = split_args(args_str)
        return FunctionCall(name, [parse_expression(a) for a in args])

    # Property access
    if "." in expr:
        var, prop = expr.split(".", 1)
        return PropertyAccess(var.strip(), prop.strip())

    raise Exception(f"Unknown expression: {expr}")


def split_args(args_str):
    # simple version (can improve later)
    return [a.strip() for a in args_str.split(",") if a.strip()]


def to_cypher(node):

    if isinstance(node, Literal):
        if node.type == "string":
            return f'"{node.value}"'
        return str(node.value)

    if isinstance(node, PropertyAccess):
        return f"{node.var}.{node.prop}"

    if isinstance(node, FunctionCall):
        args = ", ".join([to_cypher(arg) for arg in node.args])
        return f"{node.name}({args})"

    if isinstance(node, BinaryExpression):
        left = to_cypher(node.left)
        right = to_cypher(node.right)
        return f"({left} {node.operator} {right})"

    if isinstance(node, UnaryExpression):
        operand = to_cypher(node.operand)

        if node.operator == "-":
            return f"(-{operand})"

        if node.operator == "NOT":
            return f"(NOT ({operand}))"

    if isinstance(node, ComparisonExpression):
        left = to_cypher(node.left)
        right = to_cypher(node.right)

        operator_map = {
            "==": "=",
            "!=": "<>"
        }

        operator = operator_map.get(node.operator, node.operator)
        return f"({left} {operator} {right})"

    if isinstance(node, LogicalExpression):
        left = to_cypher(node.left)
        right = to_cypher(node.right)
        return f"({left} {node.operator} {right})"

    if isinstance(node, BooleanLiteral):
        return "true" if node.value else "false"

    raise Exception(f"Unknown node type: {type(node)}")


def print_ast(node, level=0):
    indent = "    " * level
    prefix = "└── " if level > 0 else ""

    if isinstance(node, Literal):
        print(f"{indent}{prefix}Literal")
        print(f"{indent}    ├── value: {node.value}")
        print(f"{indent}    └── type: {node.type}")

    elif isinstance(node, PropertyAccess):
        print(f"{indent}{prefix}PropertyAccess")
        print(f"{indent}    ├── var: {node.var}")
        print(f"{indent}    └── prop: {node.prop}")

    elif isinstance(node, FunctionCall):
        print(f"{indent}{prefix}FunctionCall: {node.name}")
        for arg in node.args:
            print_ast(arg, level + 1)

    elif isinstance(node, BinaryExpression):
        print(f"{indent}{prefix}BinaryExpression: {node.operator}")
        print_ast(node.left, level + 1)
        print_ast(node.right, level + 1)

    elif isinstance(node, ComparisonExpression):
        print(f"{indent}{prefix}ComparisonExpression: {node.operator}")
        print_ast(node.left, level + 1)
        print_ast(node.right, level + 1)


    elif isinstance(node, LogicalExpression):
        print(f"{indent}{prefix}LogicalExpression: {node.operator}")
        print_ast(node.left, level + 1)
        print_ast(node.right, level + 1)

    elif isinstance(node, UnaryExpression):
        print(f"{indent}{prefix}UnaryExpression: {node.operator}")
        print_ast(node.operand, level + 1)

    elif isinstance(node, BooleanLiteral):
        print(f"{indent}{prefix}BooleanLiteral")
        print(f"{indent}    └── value: {node.value}")

    else:
        print(f"{indent}{prefix}UnknownNode")
