from dtgraph.exceptions import CompileError

class Compiler:
    # def __init__(self, database, with_diagnose = True, explain = False, profile = False):
    #     self._database = database
    #     self._with_diagnose = with_diagnose
    #     self._explain = explain
    #     self._profile = profile


    def __init__(self, database, env=None, type_strict=False, with_diagnose=True, explain=False, profile=False):
        self._database = database
        self._env = env
        self._type_strict = type_strict
        self._with_diagnose = with_diagnose
        self._explain = explain
        self._profile = profile

    def compile(self, dict) -> str:
        """Compiles a rule.

        Raises a CompileError if something went wrong.

        Parameters
        ----------
        dict : dict
            A string describing the rule as an executable openCypher script.

        Returns:
        --------
        str
            An openCypher script implementing the transformation described by the input dictionary.
        """
        aliases = []
        missing_aliases = []
        script = "" 
        if self._explain:
            script += "EXPLAIN "
        if self._profile:
            script += "PROFILE "
        script += dict['lhs'].strip() + "\n"
        # handle first the node constructors; including node constructors found in edge constructors
        for constructor in dict.get('constructors'):
            src, tgt = constructor.get('src'), constructor.get('tgt')
            if(src):
                script += self._process_node_constructor(src, aliases, missing_aliases)
                script += self._process_node_constructor(tgt, aliases, missing_aliases)
            else:
                script += self._process_node_constructor(constructor, aliases, missing_aliases)
        if missing_aliases:
            raise CompileError("The following aliases are not defined: " + ",".join(missing_aliases))
        # handle edge constructors
        for constructor in dict.get('constructors'):
            src, edge, tgt = constructor.get('src'), constructor.get('edge'), constructor.get('tgt')
            if edge:
                script += self._process_edge_constructor(edge, aliases, src.get('alias'), tgt.get('alias'))
        return script

    def _process_edge_constructor(self, edge, aliases: list[str], src_alias: str, tgt_alias: str) -> str:
        alias = edge.get('alias')
        ids = edge.get('ids')
        script = ""
        if alias:
            raise CompileError("Using alias in edge constructor is forbidden.")
        alias = f"x_{len(aliases)}"
        aliases.append(alias)
        edge['alias'] = alias
        labels = edge.get('labels')
        properties = edge.get('properties')
        if labels is None or len(labels) != 1:
            raise CompileError("Relationships should be of only one type in openCypher.")
        script += f'MERGE ({src_alias})-[{alias}:{labels[0]} {{\n    ' 
        # idsE = [labels[0]]
        # idsE.extend(ids)
        # idsE.extend([src_alias, tgt_alias])

        idsE = [labels[0]]

        if ids:
            idsE.extend(ids)
        else:
            # fallback to structural identity
            idsE.extend([src_alias, tgt_alias])

        script += self._process_ids(idsE)
        script += f' \n}}]->({tgt_alias})\n'
        script += self._process_properties(alias, labels, properties, setLabels=False)
        return script

    def _process_node_constructor(self, node, aliases: list[str], missing_aliases: list[str]) -> str:
        alias = node.get('alias')
        ids = node.get('ids')
        script = ""
        if alias and ids is None:
            # this is when an alias is referenced; for flexibility, we allow an alias to be referenced before its definition
            if alias not in aliases and alias not in missing_aliases:
                missing_aliases.append(alias)
        else:
            if alias:
                if alias in aliases:
                    raise CompileError("Redefinition of the following alias: " + alias)
                aliases.append(alias)
                if alias in missing_aliases:
                    missing_aliases.remove(alias)
            else:
                alias = f"x_{len(aliases)}"
                aliases.append(alias)
                node['alias'] = alias
            labels = node.get('labels')
            properties = node.get('properties')
            script += f'MERGE ({alias}:_dummy {{\n    '
            script += self._process_ids(ids)
            script += f' \n}})\n'
            script += self._process_properties(alias, labels, properties)
        return script

    def _process_ids(self, ids: list[str]) -> str:
        script = f'_id: "("'
        if ids:
            script += ' + '
        script += f'{ """ + "," + """.join(map(self._wrap_id, ids)) } + ")"'
        return script

    # def _wrap_id(self, id: str) -> str:
    #     # id[0].islower() rules out both Labels and "constants"; the last check rules out access.keys
    #     if id[0].islower() and '.' not in id:
    #         return ("element" if self._database == "neo4j" else "") + "ID(" + id + ")"
    #     # labels should get enclosed into quotes; we add leading and trailing colons for labels
    #     elif id[0].isupper():
    #         return '":' + id + ':"'
    #     else:
    #         return id

    def _wrap_id(self, id) -> str:

        if id == "_":
            if self._database == "neo4j":
                return "randomUUID()"
            else:
                return "uuid()"
        
        if isinstance(id, list):
            ref = id[0]
            return ref + "._id"
        if id[0].islower() and '.' not in id:
            return ("element" if self._database == "neo4j" else "") + "ID(" + id + ")"
        elif id[0].isupper():
            return '":' + id + ':"'
        else:
            return id

    def _process_properties(self, alias: str, labels: list[str], properties: list[dict[str, str]], setLabels: bool = True) -> str:
        script = ""
        if (setLabels and labels) or properties:
            script += f'ON CREATE\n'
            if setLabels and labels:
                script += f'    SET { ",".join([alias + ":" + l for l in labels]) }'
            if properties:
                if setLabels and labels:
                    script += ",\n        "
                else:
                    script += f'    SET '
                script += ",\n        ".join([alias + "." + p['key'] + " = " + p['value'] for p in properties])
            script += "\nON MATCH\n"
            if setLabels and labels:
                script += f'    SET { ",".join([alias + ":" + l for l in labels]) }'
            if properties:
                if setLabels and labels:
                    script += ",\n        "
                else:
                    script += f'    SET '
                script += ",\n        ".join([self._conflict_detection(alias, p) for p in properties])
            script += "\n"

        # centralize information about the conflicts on this given element to allow fast lookup by diagnose()
        if(properties and self._with_diagnose):
            script += "FOREACH (i in CASE WHEN " + " OR ".join([self._list_cd(alias, p) for p in properties]) 
            script += " THEN [1] else [] END | "
            # if this is a node, add a specific label
            if setLabels:
                script += "SET " + alias + ":_hasConflict"
            # if this is an edge, add a specific attribute
            else:
                script += "SET " + alias + "._hasConflict = True"
            script += ")\n"

        return script

    def _list_cd(self, alias: str, p: dict[str, str]) -> str:
        return (
            alias + "." + p['key'] + ' = "Conflict Detected!"' 
        )

    # def _conflict_detection(self, alias: str, p: dict[str, str]) -> str:
    #     return (
    #         alias + "." + p['key'] + " = \n        CASE\n            WHEN " 
    #         + alias + "." + p['key'] + " <> " + p['value'] 
    #         + ' THEN\n                "Conflict Detected!"\n            ELSE\n                ' 
    #         + p["value"] + "\n        END"
    #     )

    def _parse_type(self, type_str: str):

        if isinstance(type_str, list):
            # assume union of scalar types
            return "scalar", type_str
    
        if not type_str:
            return "scalar", None

        if type_str.startswith("bag["):
            return "bag", type_str[4:-1]

        if type_str.startswith("set["):
            return "set", type_str[4:-1]

        return "scalar", type_str

    def _conflict_detection(self, alias: str, p: dict[str, str]) -> str:

        value = p["value"].strip()
        key = p["key"]

        # Default DTGraph behavior
        if not self._type_strict or not self._env:
            return (
                alias + "." + key + " = \n        CASE\n            WHEN "
                + alias + "." + key + " <> " + value
                + ' THEN\n                "Conflict Detected!"\n            ELSE\n                '
                + value + "\n        END"
            )

        # Type strict mode
        type_str = self._env.target.get(key)

        from dtgraph.exceptions import CompileError

        # Checking if property exists
        if not type_str:
            raise CompileError(f"Unknown target property '{key}' in strict mode")

        kind, inner = self._parse_type(type_str)

        # Collection types (bag/set)
        if kind in ["bag", "set"]:

            # Must be a list
            if not (value.startswith("[") and value.endswith("]")):
                raise CompileError(
                    f"Property '{key}' expects a collection ({kind}[{inner}]) but got scalar value '{value}'"
                )

            # NULL-safe transformation
            inner_expr = value[1:-1].strip()
            safe_value = (
                "CASE WHEN " + inner_expr + " IS NULL THEN [] ELSE [" + inner_expr + "] END"
            )

            # BAG → append (allow duplicates)
            if kind == "bag":
                return (
                    alias + "." + key + " = \n        CASE\n"
                    "            WHEN " + alias + "." + key + " IS NULL THEN " + safe_value + "\n"
                    "            ELSE " + alias + "." + key + " + " + safe_value + "\n"
                    "        END"
                )

            # SET → append + deduplicate
            if kind == "set":
                return (
                    alias + "." + key + " = \n        CASE\n"
                    "            WHEN " + alias + "." + key + " IS NULL THEN " + safe_value + "\n"
                    "            ELSE REDUCE(acc = " + alias + "." + key + ", x IN " + safe_value + " |\n"
                    "                CASE WHEN x IN acc THEN acc ELSE acc + x END)\n"
                    "        END"
                )

        # SCALAR → always conflict (NO merge)
        return (
            alias + "." + key + " = \n        CASE\n            WHEN "
            + alias + "." + key + " <> " + value
            + ' THEN\n                "Conflict Detected!"\n            ELSE\n                '
            + value + "\n        END"
        )

if __name__ == "__main__":
    from dtgraph import Rule
    dico = Rule.from_ascii('''
        MATCH (n) 
        RETURN n
        => (("c", v.fff, w) : Dummy),
        (x = (n) : Person {
            name = "SK1(" + n.name + ")",
            city = "test"
        })-[(): Knows]->(y = (n) : Person {
            name = "SK2(" + n.name + ")" 
        }), 
        (x)-[(v) : Likes {
            since = "01/01/1970"
        }]->(y),
        (() : Test)
    ''')._dict
    compiler = Compiler("neo4j")
    print(compiler.compile(dico))

    # because dico is modified in place during the compilation step, 
    # we need to create a new dictionary
    dico = Rule.from_ascii('''
        MATCH (n) 
        RETURN n
        => (("c", v.fff, w) : Dummy),
        (x = (n) : Person {
            name = "SK1(" + n.name + ")",
            city = "test"
        })-[(): Knows]->(y = (n) : Person {
            name = "SK2(" + n.name + ")" 
        }), 
        (x)-[(v) : Likes {
            since = "01/01/1970"
        }]->(y),
        (() : Test)
    ''')._dict
    compiler = Compiler("memgraph")
    print(compiler.compile(dico))