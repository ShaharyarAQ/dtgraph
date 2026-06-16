import re

def extract_function_calls_from_lhs(lhs: str, known_functions):
    calls = []

    i = 0
    while i < len(lhs):
        match = re.search(r"\b[a-zA-Z_][a-zA-Z0-9_.]*\s*\(", lhs[i:])

        if not match:
            break

        start = i + match.start()
        name_start = start
        paren_start = i + match.end() - 1

        name = lhs[name_start:paren_start].strip()

        # Skip Cypher clauses/pattern syntax accidentally matched
        if name.upper() in {"MATCH", "OPTIONAL", "WHERE", "WITH", "RETURN", "LIMIT", "ORDER", "BY"}:
            i = paren_start + 1
            continue

        if len(name) == 1 and name.islower():
            i = paren_start + 1
            continue

        if name not in known_functions:
            raise Exception(f"Unknown LHS function '{name}'")

        depth = 0
        end = paren_start

        while end < len(lhs):
            ch = lhs[end]

            if ch == "(":
                depth += 1
            elif ch == ")":
                depth -= 1

                if depth == 0:
                    calls.append(lhs[name_start:end + 1].strip())
                    break

            end += 1

        i = end + 1

    return calls


def extract_lhs_function_assignments(lhs: str):
    assignments = []

    with_matches = re.findall(
        r"\bWITH\b\s+(.*?)(?=\bWHERE\b|\bRETURN\b|\bMATCH\b|\bOPTIONAL MATCH\b|\bLIMIT\b|$)",
        lhs,
        flags=re.IGNORECASE | re.DOTALL,
    )

    for with_body in with_matches:
        parts = split_top_level_commas(with_body)

        for part in parts:
            part = part.strip()

            match = re.match(
                r"(.+?)\s+AS\s+([a-zA-Z_][a-zA-Z0-9_]*)$",
                part,
                flags=re.IGNORECASE,
            )

            if not match:
                continue

            expr = match.group(1).strip()
            var_name = match.group(2).strip()

            # only validate function captures
            if "(" in expr and ")" in expr:
                assignments.append((expr, var_name))

    return assignments


def split_top_level_commas(text):
    parts = []
    current = []
    depth = 0
    in_string = False

    for ch in text:
        if ch == '"':
            in_string = not in_string

        elif not in_string:
            if ch in "([{":
                depth += 1
            elif ch in ")]}":
                depth -= 1
            elif ch == "," and depth == 0:
                parts.append("".join(current).strip())
                current = []
                continue

        current.append(ch)

    if current:
        parts.append("".join(current).strip())

    return parts