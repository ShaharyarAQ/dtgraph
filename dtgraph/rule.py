"""Property Graph transformation rule.

This module contains the `Rule` class for representation of a declarative
property graph transformation rule.
"""

from dtgraph.parser import RuleParser, RightHandSide
from dtgraph.compiler import Compiler
from dtgraph.exceptions import RuleInitializationError


###########################################
import re


def should_expand(ascii: str) -> bool:
    
    match = re.search(r"\bGENERATE\b|=>", ascii)
    if not match:
        return False

    rhs = ascii.split(match.group(0), 1)[1]

    if rhs.count("->") + rhs.count("<-") > 1:
        return True

    if "<-" in rhs:
        return True

    return False

def expand_pattern(ascii_str: str) -> str:

    match = re.search(r"\bGENERATE\b|=>", ascii_str)
    if not match:
        return ascii_str
    
    delimiter = match.group(0)
    lhs, rhs = ascii_str.split(delimiter, 1)

    if '->' not in rhs and '<-' not in rhs:
        return ascii_str

    NODE_PATTERN = r"\((?:[^()]*|\([^()]*\))*\)"
    EDGE_PATTERN = r"-\[[^\]]+\]->|<-\[[^\]]+\]-"

    chain_pattern = re.compile(
        rf"({NODE_PATTERN}(?:\s*(?:{EDGE_PATTERN})\s*{NODE_PATTERN})+)"
    )

    def extract_alias(node: str):
        match = re.match(r"\(\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*=", node)
        return match.group(1) if match else None

    def expand_chain(chain: str) -> str:

        # Extract tokens
        tokens = re.findall(rf"{NODE_PATTERN}|{EDGE_PATTERN}", chain)

        nodes = []
        edges = []

        for t in tokens:
            if t.startswith("("):
                nodes.append(t.strip())
            else:
                edges.append(t.strip())

        result = []
        seen_aliases = set()

        for i in range(len(edges)):
            edge = edges[i]

            src = nodes[i]
            tgt = nodes[i + 1]

            # Extract aliases
            src_alias = extract_alias(src)
            tgt_alias = extract_alias(tgt)


            # source node
            if src_alias:
                if src_alias in seen_aliases:
                    src = f"({src_alias})"
                else:
                    seen_aliases.add(src_alias)

            # target node
            if tgt_alias:
                if tgt_alias in seen_aliases:
                    tgt = f"({tgt_alias})"
                else:
                    seen_aliases.add(tgt_alias)

            # Build edges
            if edge.startswith("-["):  # forward →
                result.append(f"{src}{edge}{tgt}")

            else:  # backward <-
                rel = re.search(r"\[[^\]]+\]", edge).group(0)
                result.append(f"{tgt}-{rel}->{src}")

        return ", ".join(result)

    # Apply expansion
    rhs = chain_pattern.sub(lambda m: expand_chain(m.group(0)), rhs)

    # Reconstruct rule
    return lhs + delimiter + rhs

###########################################


class Rule(object):
    """Class representing a declarative transformation rule.

    (TODO long description for this class)

    Methods
    -------
    apply_on(graph)
        Execute the query on the Neo4jGraph.
    """

    _dict = None
    _compiled = None

    # def __init__(self, ascii=None, raw=None, lhs=None, rhs=None):
    def __init__(self, ascii=None, raw=None, lhs=None, rhs=None , env=None, type_strict=False):
        """Initializes a rule.

        The type of operation is defined by which arguments are provided.
        If an invalid combination of arguments is provided, raises an RuleInitializationError exception.
        Supported combinations: raw; lhs + rhs; lhs + ascii; ascii.

        Parameters
        ----------
        ascii : str
            A string representing the rhs of the rule in ASCII-art style if `lhs` is provided.
            If `lhs` is not provided, its contains a representation of the entire rule in ASCII-art style.
            In any case, it will be processed by the DSL, and an openCypher script will be obtained
            from it.
        raw : str
            A string describing the rule as an executable openCypher script.
        lhs : str
            A string describing the lhs of the rule as an executable openCypher script.
        rhs : str
            A string describing the rhs of the rule in openCypher.
        """

        self._env = env
        self._type_strict = type_strict

        if raw:
            self._compiled = raw
        elif lhs and rhs:
            self._compiled = f"{lhs}\n{rhs}"
        elif lhs and ascii:
            rhs_dict = RightHandSide.parseString(ascii, parseAll=True).asDict()
            self._dict = {"lhs": lhs, "constructors": rhs_dict["constructors"]}
        # elif ascii:
        #     self._dict = RuleParser.parseString(ascii, parseAll=True).asDict()
        # elif ascii:
        #     ascii = expand_pattern(ascii)
        #     self._dict = RuleParser.parseString(ascii, parseAll=True).asDict()
        elif ascii:
            if should_expand(ascii):
                ascii = expand_pattern(ascii)

            self._dict = RuleParser.parseString(ascii, parseAll=True).asDict()
        else:
            raise RuleInitializationError("Invalid set of parameters.")

    @classmethod
    def from_ascii(cls, ascii, lhs=None):
        """Creates a rule object from an ASCII representation."""
        if lhs:
            return cls(lhs=lhs, ascii=ascii)
        else:
            return cls(ascii=ascii)

    @classmethod
    def from_raw(cls, raw):
        """Creates a rule object from a raw representation."""
        return cls(raw=raw)

    def _compile(
        self, database="neo4j", with_diagnose=True, explain=False, profile=False
    ):
        # the compilation step is not idempotent
        if self._compiled is None:
            # compiler = Compiler(
            #     database, with_diagnose=with_diagnose, explain=explain, profile=profile
            # )

            env = getattr(self, "_env", None)
            type_strict = getattr(self, "_type_strict", False)

            # Type checking (if enabled)
            # if env and type_strict:
            #     if self._dict is None:
            #         raise Exception("Cannot type check rule without parsed structure")

            #     from type_checking.pipeline import TypeCheckingPipeline
            #     from dtgraph.exceptions import CompileError

            #     pipeline = TypeCheckingPipeline(env)
                

            #     try:
            #         pipeline.run([self])
            #     except Exception as e:
            #         msg = str(e)
            #         lines = msg.split("\n")
            #         filtered = [line.strip(" -") for line in lines if line.strip().startswith("-")]

            #         reason = filtered[0] if filtered else msg

            #         raise CompileError(
            #             f"\nType checking failed for rule:\n{self}\n\nReason: {reason}"
            #         )


            compiler = Compiler(
            database,
            env=self._env if hasattr(self, "_env") else None,
            type_strict=self._type_strict if hasattr(self, "_type_strict") else False,
            with_diagnose=with_diagnose,
            explain=explain,
            profile=profile
            )
            
            self._compiled = compiler.compile(self._dict)

    def apply_on(self, graph, with_diagnose=True, explain=False, profile=False) -> int:
        """
        Applies the rule on the given graph, in the context of a graph transformation scenario.

        Parameters
        ----------
        graph : dtgraph.backend.neo4j.graph.Neo4jGraph
            Graph to be transformed by the rule.
        """
        if self._compiled is None:
            self._compile(
                graph.database,
                with_diagnose=with_diagnose,
                explain=explain,
                profile=profile,
            )
        summary = graph.exec_rule(self._compiled, stats=True)
        return summary.result_available_after, summary

    def __str__(self):
        repr = ""
        if self._compiled:
            repr += "Compiled:\n" + self._compiled + "\n"
        if self._dict:
            repr += "Source dictionary:\n" + str(self._dict)
        return repr
