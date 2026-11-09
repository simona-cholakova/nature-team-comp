# ---------------------------------------------------------------------------
# Worker prompts (numeric/GSM8K)
# ---------------------------------------------------------------------------

#The part every worker shares: the problem plus the strict output contract
WORKER_FORMAT_NUMERIC = """Problem: {question}
Format EXACTLY (answer and confidence FIRST, then reasoning):
FINAL: <integer>
CONF: <0-100>
RATIONALE: <brief reasoning, max 4 lines>"""

#Star's default leading directive
WORKER_DIRECTIVE_DEFAULT = "Solve this math problem step by step. Be concise."

#Star's full worker prompt = default directive + shared format block
WORKER_NUMERIC = WORKER_DIRECTIVE_DEFAULT + "\n" + WORKER_FORMAT_NUMERIC

#Persona-Star: six leading directives, cycled by worker index
PERSONAS_NUMERIC = [
    ("forward",
     "Solve this math problem by working FORWARD from the given values step by step. Be concise."),
    ("backward",
     "Solve this math problem by working BACKWARDS: propose a plausible numerical answer, "
     "then check whether it satisfies every constraint in the problem. Adjust until consistent. "
     "Be concise."),
    ("decomposer",
     "Solve this math problem by first DECOMPOSING it into a sequence of simpler subproblems. "
     "Solve each subproblem in order; the answer to the last yields the final answer. Be concise."),
    ("stepback",
     "Solve this math problem by first STEPPING BACK: identify the general method, formula, "
     "or theorem this problem requires, then apply it to the specific numbers. Be concise."),
    ("conservative",
     "Solve this math problem CONSERVATIVELY: commit only after at least two independent "
     "verification passes (e.g. dimensional check, sanity bound, alternative derivation) agree "
     "on the answer. Report low CONF when checks disagree. Be concise."),
    ("contrarian",
     "Solve this math problem as a CONTRARIAN. Arrive at an obvious answer, then deliberately "
     "attempt to find an error in your reasoning. If you find a real flaw, revise; otherwise "
     "report the original answer and note that your attempted falsification failed. Be concise."),
]

# ---------------------------------------------------------------------------
# Manager prompt (all topologies)
# ---------------------------------------------------------------------------

MANAGER_NUMERIC = """You are the FINAL ADJUDICATOR. You will see {m} downstream reports (workers, refiners, duelists, plan-solvers, synthesizers, or critics depending on the team structure). You are explicitly empowered to OVERRIDE the majority if their arithmetic is wrong. Be skeptical. Re-derive if needed.
Problem: {question}
Downstream reports:
{reports}
Format EXACTLY:
FINAL: <integer>
CONF: <0-100>
RATIONALE: <audit-style reasoning, identify any computational errors, max 6 lines>"""