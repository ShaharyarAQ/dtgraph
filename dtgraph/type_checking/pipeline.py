from .semantic import SemanticAnalyzer


class TypeCheckingPipeline:

    def __init__(self, env):
        self.analyzer = SemanticAnalyzer(env)

    def run(self, rules):

        for rule in rules:

            if not hasattr(rule, "_dict") or rule._dict is None:
                raise Exception("Invalid rule: missing parsed structure")

            print("\n--- Checking Rule ---")
            # print(rule)
            print(rule._dict)
            self.analyzer.analyze(rule._dict)

        print("\n Type checking passed\n")
        return rules