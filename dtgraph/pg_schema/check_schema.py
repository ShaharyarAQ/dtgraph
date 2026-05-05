from dtgraph.exceptions import CompileError
from pg_schema.precheck import precheck_rule


def check_schema(rules, schema):

    all_passed = True

    for rule in rules:

        if not hasattr(rule, "_dict") or rule._dict is None:
            raise Exception("Invalid rule: missing parsed structure")

        print("\n--- Checking Rule ---")
        print(rule)

        try:
            precheck_rule(rule._dict, schema)

        except Exception as e:
            all_passed = False

            print("\nRULE FAILED:")
            print(rule)

            msg = str(e)
            lines = msg.split("\n")

            filtered = [
                line.strip(" -") for line in lines if line.strip().startswith("-")
            ]

            reason = filtered[0] if filtered else msg

            print("Reason:", reason)

    if not all_passed:
        raise CompileError("\nSchema conformance failed for one or more rules")

    print("\nAll rules conform to provided schema\n")