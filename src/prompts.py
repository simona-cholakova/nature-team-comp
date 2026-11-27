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

# ---------------------------------------------------------------------------
# Multiple-choice contract (ARC, GPQA, MMLU)
# ---------------------------------------------------------------------------
#{question} holds the stem followed by the lettered options, one per line.
#The paper prints only the multiple-choice worker verbatim and states that every other role
#differs from its numeric template "only in the task noun and the format block", so the
#remaining multiple-choice templates are derived from the numeric ones by that rule.

def _to_mcq(template: str) -> str:
    """Numeric template -> multiple-choice template (task noun + format block)."""
    return (template
            .replace("Problem: {question}", "Question: {question}")
            .replace("FINAL: <integer>", "FINAL: <A, B, C, or D>")
            .replace("this math problem", "this multiple-choice question")
            .replace("final number", "final answer"))

WORKER_FORMAT_MCQ = _to_mcq(WORKER_FORMAT_NUMERIC)
WORKER_DIRECTIVE_MCQ = "Answer the multiple-choice question. Be concise."
WORKER_MCQ = WORKER_DIRECTIVE_MCQ + "\n" + WORKER_FORMAT_MCQ
PERSONAS_MCQ = [(name, _to_mcq(directive)) for name, directive in PERSONAS_NUMERIC]

MANAGER_MCQ = _to_mcq(MANAGER_NUMERIC)
CRITIC_MCQ = _to_mcq(CRITIC_NUMERIC)
SYNTHESIZER_MCQ = _to_mcq(SYNTHESIZER_NUMERIC)
REFINER_MCQ = _to_mcq(REFINER_NUMERIC)
DUELIST_MCQ = _to_mcq(DUELIST_NUMERIC)
DUELIST_BYE_MCQ = _to_mcq(DUELIST_BYE_NUMERIC)
PLANNER_MCQ = _to_mcq(PLANNER_NUMERIC)
PLAN_SOLVER_MCQ = _to_mcq(PLAN_SOLVER_NUMERIC)


# ---------------------------------------------------------------------------
# Code contract (HumanEval)
# ---------------------------------------------------------------------------
#{question} holds a one-line instruction and the function signature + docstring.
#The paper prints the code worker and the six code personas verbatim. For the other roles it
#only says "the code template uses the code contract", so those templates are the numeric
#ones reworded for code, ending in the code format block.

CODE_FORMAT = """CONF: <0-100>
SOLUTION:
```python
<full function definition here>
```"""

#The code worker has no leading directive, so it is also the shared format block
WORKER_FORMAT_CODE = "{question}\nFormat EXACTLY:\n" + CODE_FORMAT
WORKER_CODE = WORKER_FORMAT_CODE

#Persona-Star on code: six coding strategies, cycled by worker index
PERSONAS_CODE = [
    ("forward",
     "Approach: implement the function FORWARD -- translate the spec directly into code, "
     "handling each requirement in the order it appears in the signature and docstring."),
    ("backward",
     "Approach: work BACKWARD from the examples -- figure out the expected output for the "
     "docstring's example inputs first, then write code that reproduces them and generalizes "
     "to the rest."),
    ("decomposer",
     "Approach: DECOMPOSE the task into 2-3 smaller steps (helper computations or sub-cases), "
     "solve each, then compose them into the final function."),
    ("stepback",
     "Approach: STEP BACK first -- name the general algorithm or data structure this calls for "
     "(sorting, hashing, a counter, two pointers, dynamic programming, ...), then implement "
     "that approach."),
    ("conservative",
     "Approach: code CONSERVATIVELY -- handle edge cases explicitly (empty input, zero, "
     "negatives, boundaries), mentally run the docstring examples before committing, and "
     "report lower CONF if any case is uncertain."),
    ("contrarian",
     "Approach: as a CONTRARIAN, write the obvious implementation, then deliberately hunt for "
     "the input that breaks it (off-by-one, empty case, aliasing, overflow). If you find one, "
     "fix it; otherwise keep it and note the attack that failed."),
]

MANAGER_CODE = """You are the FINAL ADJUDICATOR. You will see {m} downstream reports (workers, refiners, duelists, plan-solvers, synthesizers, or critics depending on the team structure). You are explicitly empowered to OVERRIDE the majority if their code is wrong. Be skeptical. Re-implement if needed.
Task:
{question}
Downstream reports:
{reports}
Format EXACTLY:
""" + CODE_FORMAT

CRITIC_CODE = """You are a CRITIC. A worker produced the solution below. Find the flaws -- check the logic, challenge assumptions, look for missed cases. If after critique the original solution still holds, say so explicitly and report it; otherwise report the solution your critique supports.
Task:
{question}
Worker solution to critique:
{proposal}
Format EXACTLY (your own solution after the critique):
""" + CODE_FORMAT

SYNTHESIZER_CODE = """You are a SYNTHESIZER. You have received {b} independent worker solutions to the same task. Extract the most consistent implementation. Do not simply vote -- verify the logic of the solution you report.
Task:
{question}
Worker solutions (independent, no communication between them):
{workers}
Format EXACTLY:
""" + CODE_FORMAT

REFINER_CODE = """You are a REFINER. The {b} previous worker(s) below solved this task in sequence (oldest first). Read them, then produce your own solution. You may agree, disagree, or extend -- but verify the code you report.
Task:
{question}
Previous worker solutions (chronological):
{workers}
Format EXACTLY:
""" + CODE_FORMAT

DUELIST_CODE = """You are a JUDGE in a tournament bracket. You will see solutions from {b} competitors. Compare them critically -- check the logic, identify missed cases -- then commit to a single solution. If both agree, verify. If they disagree, pick the stronger solution or repair it.
Task:
{question}
Competitor solutions:
{workers}
Format EXACTLY:
""" + CODE_FORMAT

DUELIST_BYE_CODE = """One contestant advanced via bye in this tournament round; their solution is below. Your job is to verify their code and logic, NOT pick between alternatives. If sound, report the same solution with your own confidence. If you find a flaw, report the solution your check supports.
Task:
{question}
Contestant solution:
{workers}
Format EXACTLY:
""" + CODE_FORMAT

PLANNER_CODE = """You are PLANNER #{i_one_indexed} of {M}. Your job is to describe ONE method for implementing this function -- do NOT implement it. The other {M_minus_one} planners are independently producing their own methods; your method should be DIFFERENT from the most obvious approach a solver would default to. Keep it short and specific (3-5 sentences). Do NOT write any code.
Task:
{question}
Format EXACTLY:
APPROACH: <name of method, e.g., 'sort then scan', 'hash-map counter', 'recursion on the suffix'>
STEPS: <3-5 brief, actionable steps a solver should take, on one or two lines each>"""

PLAN_SOLVER_CODE = """A planner has proposed the following method for this task. Execute the method to implement the function. You may deviate if you identify a flaw -- but note it in a code comment when you do.
Task:
{question}
Plan:
{workers}
Format EXACTLY:
""" + CODE_FORMAT
