from type_checking.pipeline import TypeCheckingPipeline
from dtgraph.exceptions import CompileError

def check_types(rules, env):

    pipeline = TypeCheckingPipeline(env)

    try:
        pipeline.run(rules)

    except Exception as e:
        msg = str(e)

        lines = msg.split("\n")
        filtered = [line.strip(" -") for line in lines if line.strip().startswith("-")]

        reason = filtered[0] if filtered else msg

        raise CompileError(f"\nType checking failed:\n\nReason: {reason}")

