grammar = r"""
?start: expr

?expr: or_expr

?or_expr: or_expr "OR" and_expr   -> or_op
        | and_expr

?and_expr: and_expr "AND" comp_expr -> and_op
         | comp_expr

?comp_expr: arith_expr (COMP_OP arith_expr)? -> compare

?arith_expr: arith_expr "+" term   -> add
           | arith_expr "-" term   -> sub
           | term

?term: term "*" factor -> mul
     | term "/" factor -> div
     | factor

?factor: "-" factor    -> neg
       | atom
       | "(" expr ")"

?atom: NUMBER           -> number
     | STRING           -> string
     | "true"          -> true
     | "false"         -> false
     | NAME "." NAME    -> property
     | NAME "(" args ")" -> function

?args: expr ("," expr)*

COMP_OP: ">" | "<" | ">=" | "<=" | "==" | "!="

%import common.CNAME -> NAME
%import common.NUMBER
%import common.ESCAPED_STRING -> STRING
%import common.WS
%ignore WS
"""


from lark import Lark, Transformer
from .ast_nodes import (
    Literal,
    PropertyAccess,
    FunctionCall,
    BinaryExpression,
    UnaryExpression,
    ComparisonExpression,
    LogicalExpression,
    BooleanLiteral
)

parser = Lark(grammar, parser="lalr")


class ASTTransformer(Transformer):

    def number(self, items):
        return Literal(str(items[0]), "integer")

    def string(self, items):
        return Literal(str(items[0])[1:-1], "string")

    def property(self, items):
        return PropertyAccess(str(items[0]), str(items[1]))

    def function(self, items):
        name = str(items[0])

        if len(items) > 1:
            args = items[1]
            if not isinstance(args, list):
                args = [args]
        else:
            args = []

        return FunctionCall(name, args)

    def args(self, items):
        return list(items)

    def add(self, items):
        return BinaryExpression(items[0], "+", items[1])

    def sub(self, items):
        return BinaryExpression(items[0], "-", items[1])

    def mul(self, items):
        return BinaryExpression(items[0], "*", items[1])

    def div(self, items):
        return BinaryExpression(items[0], "/", items[1])
    

    def neg(self, items):
        return UnaryExpression("-", items[0])

    def true(self, _):
        return BooleanLiteral(True)

    def false(self, _):
        return BooleanLiteral(False)

    def compare(self, items):
        if len(items) == 1:
            return items[0]
        return ComparisonExpression(items[0], items[1].value, items[2])

    def and_op(self, items):
        return LogicalExpression(items[0], "AND", items[1])

    def or_op(self, items):
        return LogicalExpression(items[0], "OR", items[1])