import re

from .expression_parser import parser, ASTTransformer
from .ast_nodes import (
    BooleanLiteral,
    ComparisonExpression,
    ListExpression,
    Literal,
    LogicalExpression,
    PropertyAccess,
    FunctionCall,
    BinaryExpression,
    UnaryExpression,
    Variable,
)


def is_compatible(actual, expected):

    # exact match
    if actual == expected:
        return True

    # bag/set compatibility
    if actual.startswith(("bag[", "set[")) and expected.startswith(("bag[", "set[")):
        actual_inner = actual[actual.find("[") + 1 : -1]
        expected_inner = expected[expected.find("[") + 1 : -1]

        return actual_inner == expected_inner

    return False


class SemanticAnalyzer:

    def __init__(self, env):
        self.env = env

    def analyze(self, rule_dict):

        for c in rule_dict.get("constructors", []):

            objs = []

            if "edge" in c:
                objs.extend([c["src"], c["edge"], c["tgt"]])

            else:
                objs.append(c)

            for obj in objs:
                labels = obj.get("labels")
                if not labels:
                    continue

                for prop in obj.get("properties", []):
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

                    expected_types = (
                        expected if isinstance(expected, list) else [expected]
                    )

                    def format_types(types):
                        if len(types) == 1:
                            return types[0]
                        return " or ".join(types)

                    # if not any(t in expected_types for t in actual):
                    if not any(
                        is_compatible(a, e) for a in actual for e in expected_types
                    ):
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

                # if not any(t in expected_types for t in actual):
                #     raise Exception(
                #         f"Function '{node.name}' expected {expected_types}, got {actual}"
                #     )

                if not any(is_compatible(a, e) for a in actual for e in expected_types):
                    raise Exception(
                        f"Function '{node.name}' expected {expected_types}, got {actual}"
                    )

            out = func["output"]
            return out if isinstance(out, list) else [out]

        #### New blocks for expressions

        if isinstance(node, Variable):
            if node.name not in self.env.variables:
                raise Exception(f"Unknown variable: {node.name}")
            t = self.env.variables[node.name]
            return t if isinstance(t, list) else [t]

        if isinstance(node, BinaryExpression):

            left_types = self.infer_type(node.left)
            right_types = self.infer_type(node.right)

            result = []

            for l in left_types:
                for r in right_types:

                    # if node.operator in ["+", "-", "*", "/"]:

                    #     if l == "integer" and r == "integer":
                    #         result.append("integer")

                    #     elif node.operator == "+" and l == "string" and r == "string":
                    #         result.append("string")

                    #     else:
                    #         raise Exception(
                    #         f"Invalid operation: {l} {node.operator} {r}"
                    #         )

                    if node.operator in ["+", "-", "*", "/"]:

                        # numeric operations
                        if l in ["integer", "float"] and r in ["integer", "float"]:
                            if l == "float" or r == "float":
                                result.append("float")
                            else:
                                result.append("integer")

                        # string concatenation
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

        # if isinstance(node, UnaryExpression):

        #     operand = self.infer_type(node.operand)

        #     if node.operator == "-" and "integer" in operand:
        #         return ["integer"]

        #     if node.operator == "NOT" and "boolean" in operand:
        #         return ["boolean"]

        #     raise Exception(f"Invalid unary operation: {node.operator} {operand}")

        if isinstance(node, UnaryExpression):

            operand = self.infer_type(node.operand)

            # Numeric negation
            if node.operator == "-" and any(t in ["integer", "float"] for t in operand):
                return operand

            # Logical negation
            if node.operator == "NOT" and "boolean" in operand:
                return ["boolean"]

            raise Exception(f"Invalid unary operation: {node.operator} {operand}")

        if isinstance(node, ComparisonExpression):

            left = self.infer_type(node.left)
            right = self.infer_type(node.right)

            for l in left:
                for r in right:

                    # if l == r:
                    if l == r or (
                        l in ["integer", "float"] and r in ["integer", "float"]
                    ):

                        if node.operator in ["==", "!="]:
                            return ["boolean"]

                        # if l == "integer" and node.operator in [">", "<", ">=", "<="]:
                        #     return ["boolean"]

                        if node.operator in [">", "<", ">=", "<="]:
                            if l in ["integer", "float"] and r in ["integer", "float"]:
                                return ["boolean"]

            raise Exception(
                f"Invalid comparison: cannot apply '{node.operator}' to {left} and {right}"
            )

        if isinstance(node, LogicalExpression):

            left = self.infer_type(node.left)
            right = self.infer_type(node.right)

            if all(t == "boolean" for t in left) and all(t == "boolean" for t in right):
                return ["boolean"]

            raise Exception(
                f"Logical operations require boolean operands, got {left} and {right}"
            )

        if isinstance(node, ListExpression):

            if not node.elements:
                return ["list"]

            element_types = []
            for el in node.elements:
                element_types.extend(self.infer_type(el))

            element_types = list(set(element_types))

            result = []
            for t in element_types:
                result.append(f"set[{t}]")
                result.append(f"bag[{t}]")

            return result

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

    if isinstance(node, Variable):
        return node.name

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

        operator_map = {"==": "=", "!=": "<>"}

        operator = operator_map.get(node.operator, node.operator)
        return f"({left} {operator} {right})"

    if isinstance(node, LogicalExpression):
        left = to_cypher(node.left)
        right = to_cypher(node.right)
        return f"({left} {node.operator} {right})"

    if isinstance(node, BooleanLiteral):
        return "true" if node.value else "false"

    if isinstance(node, ListExpression):
        elements = ", ".join([to_cypher(e) for e in node.elements])
        return f"[{elements}]"

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

    elif isinstance(node, ListExpression):
        print(f"{indent}{prefix}ListExpression")
        for el in node.elements:
            print_ast(el, level + 1)

    elif isinstance(node, Variable):
        print(f"{indent}{prefix}Variable")
        print(f"{indent}    └── name: {node.name}")

    else:
        print(f"{indent}{prefix}UnknownNode")


### LHS validation for properties and variables
def add_validation(rule_dict):

    props = set()
    vars = set()

    # Extract dependencies from AST
    for c in rule_dict.get("constructors", []):

        objs = []

        if "edge" in c:
            objs.extend([c["src"], c["edge"], c["tgt"]])
        else:
            objs.append(c)

        for obj in objs:
            if not obj.get("labels"):
                continue

            for prop in obj.get("properties", []):
                ast = prop.get("ast") or parse_expression(prop["value"].strip())
                extract_dependencies(ast, props, vars)

    # Build conditions
    conditions = set()

    for var, prop in props:
        conditions.add(f"{var}.{prop} IS NOT NULL")

    for v in vars:
        conditions.add(f"{v} IS NOT NULL")

    if not conditions:
        return props, vars

    # Inject into LHS
    lhs = rule_dict["lhs"]

    existing_conditions = set()

    if "WHERE" in lhs:
        before_where, after_where = lhs.split("WHERE", 1)

        # Split existing conditions safely
        existing_conditions = set(
            [c.strip() for c in after_where.split("AND") if c.strip()]
        )

        new_conditions = conditions - existing_conditions

        if new_conditions:
            updated_where = after_where.strip() + " AND " + " AND ".join(sorted(new_conditions))
        else:
            updated_where = after_where.strip()

        lhs = before_where.strip() + "\nWHERE " + updated_where

    else:
        lhs = lhs.strip() + "\nWHERE " + " AND ".join(sorted(conditions))

    rule_dict["lhs"] = lhs
    print("Updated LHS:\n", rule_dict["lhs"])
    return props, vars

def extract_dependencies(node, props, vars):

    if isinstance(node, PropertyAccess):
        props.add((node.var, node.prop))

    elif isinstance(node, Variable):
        vars.add(node.name)

    elif isinstance(node, FunctionCall):
        for arg in node.args:
            extract_dependencies(arg, props, vars)

    elif isinstance(node, BinaryExpression):
        extract_dependencies(node.left, props, vars)
        extract_dependencies(node.right, props, vars)

    elif isinstance(node, UnaryExpression):
        extract_dependencies(node.operand, props, vars)

    elif isinstance(node, ComparisonExpression):
        extract_dependencies(node.left, props, vars)
        extract_dependencies(node.right, props, vars)

    elif isinstance(node, LogicalExpression):
        extract_dependencies(node.left, props, vars)
        extract_dependencies(node.right, props, vars)

    elif isinstance(node, ListExpression):
        for el in node.elements:
            extract_dependencies(el, props, vars)
