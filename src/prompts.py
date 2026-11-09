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

# ---------------------------------------------------------------------------
# Transform-stage prompts (numeric/GSM8K)
# ---------------------------------------------------------------------------

#Proposer-Critic: one critic per proposal
CRITIC_NUMERIC = """You are a CRITIC. A worker produced the solution below. Find the flaws -- check arithmetic, challenge assumptions, look for missed cases. If after critique the original answer still holds, say so explicitly and report it; otherwise report the answer your critique supports.
Problem: {question}
Worker solution to critique:
{proposal}
Format EXACTLY (your own answer after the critique):
FINAL: <integer>
CONF: <0-100>
RATIONALE: <list flaws or confirm soundness, max 4 lines>"""

#Tree: fan-in-three synthesizer
SYNTHESIZER_NUMERIC = """You are a SYNTHESIZER. You have received {b} independent worker solutions to the same problem. Extract the most consistent calculation chain. Do not simply vote -- verify the arithmetic of the answer you report.
Problem: {question}
Worker solutions (independent, no communication between them):
{workers}
Format EXACTLY:
FINAL: <integer>
CONF: <0-100>
RATIONALE: <integrated reasoning, verify the arithmetic, max 6 lines>"""

#Chain and Cascading-Chain: refiner
REFINER_NUMERIC = """You are a REFINER. The {b} previous worker(s) below solved this problem in sequence (oldest first). Read them, then produce your own solution. You may agree, disagree, or extend -- but do not just copy.
Problem: {question}
Previous worker solutions (chronological):
{workers}
Format EXACTLY:
FINAL: <integer>
CONF: <0-100>
RATIONALE: <your refined reasoning, verify arithmetic, max 4 lines>"""

#Tournament: pairwise duelist, and the bye variant for a single parent
DUELIST_NUMERIC = """You are a JUDGE in a tournament bracket. You will see solutions from {b} competitors. Compare them critically -- check arithmetic, identify reasoning gaps -- then commit to a single answer. If both agree, verify. If they disagree, pick the stronger solution and explain why.
Problem: {question}
Competitor solutions:
{workers}
Format EXACTLY:
FINAL: <integer>
CONF: <0-100>
RATIONALE: <which solution prevails and why, max 4 lines>"""

DUELIST_BYE_NUMERIC = """One contestant advanced via bye in this tournament round; their solution is below. Your job is to verify their arithmetic and logic, NOT pick between alternatives. If sound, report the same answer with your own confidence. If you find a flaw, report the answer your check supports.
Problem: {question}
Contestant solution:
{workers}
Format EXACTLY:
FINAL: <integer>
CONF: <0-100>
RATIONALE: <verification result; sound or flawed, with the load-bearing check, max 4 lines>"""

#Diamond: planners describe a method without solving, plan-solvers execute one
PLANNER_NUMERIC = """You are PLANNER #{i_one_indexed} of {M}. Your job is to describe ONE method for solving this math problem -- do NOT solve it. The other {M_minus_one} planners are independently producing their own methods; your method should be DIFFERENT from the most obvious approach a solver would default to. Keep it short and specific (3-5 sentences). Do NOT output a final number.
Problem: {question}
Format EXACTLY:
APPROACH: <name of method, e.g., 'unit conversion then ratio', 'set up equation in x', 'work backwards from total'>
STEPS: <3-5 brief, actionable steps a solver should take, on one or two lines each>"""

PLAN_SOLVER_NUMERIC = """A planner has proposed the following method for this problem. Execute the method to arrive at the answer. You may deviate if you identify a flaw -- but state explicitly when you do.
Problem: {question}
Plan:
{workers}
Format EXACTLY:
FINAL: <integer>
CONF: <0-100>
RATIONALE: <executed plan, note any deviations, max 4 lines>"""