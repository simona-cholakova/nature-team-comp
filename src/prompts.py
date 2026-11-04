WORKER_NUMERIC = """Solve this math problem step by step. Be concise.
                    Problem: {question}
                    Format EXACTLY (answer and confidence FIRST, then reasoning):
                    FINAL: <integer>
                    CONF: <0-100>
                    RATIONALE: <brief reasoning, max 4 lines>"""

MANAGER_NUMERIC = """You are the FINAL ADJUDICATOR. You will see {m} downstream reports 
                    (workers, refiners, duelists, plan-solvers, synthesizers, or critcs depending on the team structure).
                    You are explicitly empowered to OVERRIDE the majority if their arithmetic is wrong. Be skeptical. Re-derive if needed.
                    Problem: {question}
                    Downstream reports: {reports}
                    Format EXACTLY:
                    FINAL: <integer>
                    CONF: <0-100>
                    RATIONALE: <audit-style reasoning, identify any computational errors, max 6 lines>"""