from pyparsing import *

# Some voluntary differences with Cypher's syntax: https://neo4j.com/docs/cypher-manual/current/syntax/naming/
#   - We require variables to begin with a lowercase character.
#   - We require node labels and relationship types to start with an uppercase character.
#   - We disallow underscores in node labels, relationship types, property names, variables. (Hint: use camelCase)
#   - There is no support for undirected edges.

COMMA, COLON, LPAR, RPAR, LBRACE, RBRACE, EQUAL = map(Suppress, ",:(){}=")

#constant = Combine(Literal('"') + Word(alphanums) + Literal('"'))
constant = QuotedString('"', unquoteResults=False)
# freevar = Word(alphas.lower(), alphanums+"_")
freevar = Word(alphas.lower() + "_", alphanums + "_") ## Supporting _ as skolem
attribute = Word(alphas, alphanums+"_")
accesskey = Combine(freevar + Literal('.') + attribute)
label = Word(alphas.upper(), alphanums+"_")

# IDElement = (constant | accesskey | freevar | label)

SkolemRef = Group(LPAR + freevar + RPAR)
IDElement = (constant | accesskey | SkolemRef | freevar | label)

# As list of constant or accesskey expressions:
#ConstExpression = DelimitedList(accesskey | constant, delim="+")
# Or, flatened ConstExpression:
# ConstExpression = Combine((accesskey | constant) + ZeroOrMore("+" + (accesskey | constant)), adjacent=False, joinString=" ")

### Accpeting more types of properties in RHS
ConstExpression = Combine(SkipTo(Regex(r",|\}"), include=False))

PropertyElement = Group(attribute('key') + EQUAL + ConstExpression('value'))

IDTuple = LPAR + Optional(DelimitedList(IDElement, allow_trailing_delim=True), default=[])('ids') + RPAR
Labels = DelimitedList(label, allow_trailing_delim=True)('labels')
PropertyList = LBRACE + DelimitedList(PropertyElement, allow_trailing_delim=True)('properties') + RBRACE

ContentConstructor = Optional(freevar('alias') + EQUAL) + IDTuple + COLON + Optional(Labels) + Optional(PropertyList) 
NodeConstructor = LPAR + (ContentConstructor | freevar('alias')) + RPAR
RightEdgeConstructor = Group(NodeConstructor)('src') + Suppress('-[') + Group(ContentConstructor)('edge') + Suppress(']->') + Group(NodeConstructor)('tgt')
LeftEdgeConstructor = Group(NodeConstructor)('tgt') + Suppress('<-[') + Group(ContentConstructor)('edge') + Suppress(']-') + Group(NodeConstructor)('src')
EdgeConstructor = RightEdgeConstructor | LeftEdgeConstructor

Constructor = EdgeConstructor | NodeConstructor
# RightHandSide = DelimitedList(Group(Constructor), allow_trailing_delim=True)('constructors')

#### Extension ####
statement_delimiter = Suppress(",") | Suppress(";")

RightHandSide = DelimitedList(Group(Constructor),delim=statement_delimiter,allow_trailing_delim=True)('constructors')

##################

middle_delimiter = Keyword('=>') | CaselessKeyword('GENERATE')
RuleParser = SkipTo(middle_delimiter)('lhs') + middle_delimiter + RightHandSide
