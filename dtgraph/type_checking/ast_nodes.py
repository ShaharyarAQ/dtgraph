class Node:
    pass

class Literal(Node):
    def __init__(self, value, type_):
        self.value = value
        self.type = type_

class PropertyAccess(Node):
    def __init__(self, var, prop):
        self.var = var
        self.prop = prop

class FunctionCall(Node):
    def __init__(self, name, args):
        self.name = name
        self.args = args

class BinaryExpression(Node):
    def __init__(self, left, operator, right):
        self.left = left
        self.operator = operator
        self.right = right

class UnaryExpression(Node):
    def __init__(self, operator, operand):
        self.operator = operator
        self.operand = operand

class ComparisonExpression(Node):
    def __init__(self, left, operator, right):
        self.left = left
        self.operator = operator
        self.right = right

class LogicalExpression(Node):
    def __init__(self, left, operator, right):
        self.left = left
        self.operator = operator
        self.right = right

class BooleanLiteral(Node):
    def __init__(self, value):
        self.value = value
        self.type = "boolean"

class ListExpression(Node):
    def __init__(self, elements):
        self.elements = elements

class Variable(Node):
    def __init__(self, name):
        self.name = name