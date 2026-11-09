from src.common import make_seed, call_many, format_reports
from src.parsing import parse_final_numeric
from src.llm import call_llm
from src.prompts import WORKER_NUMERIC, DUELIST_NUMERIC, MANAGER_NUMERIC

def run(question: str, n: int, item_id: str, run_id: int = 0,
        base_seed: int = 42) -> dict:
    """Run the Tournament architecture on a numeric question.
       L = n//2 workers, L-1 duels and a separate manager, so 2L calls (n=30 -> 30).
       The manager sees only the winner of the final duel."""
    assert n >= 2, "Tournament needs at least 1 worker + 1 manager"
    n_workers = n // 2

    #Tier 1: independent workers. L proposals. Generate stage.
    worker_prompt = WORKER_NUMERIC.format(question=question)
    jobs = [
        (worker_prompt, make_seed(base_seed, run_id, n, "tournament", item_id, "worker", i))
        for i in range(n_workers)
    ]
    worker_outputs = call_many(jobs)
    worker_answers = [parse_final_numeric(o) for o in worker_outputs]

    #Bracket: duelists compare two reports each, an odd one out advances without a call
    current = worker_outputs
    duel_outputs = []
    round_i = 0
    while len(current) > 1:
        round_jobs = [
            (DUELIST_NUMERIC.format(b=2, question=question, workers=format_reports(current[j:j + 2])),
             make_seed(base_seed, run_id, n, "tournament", item_id, "duel", f"{round_i}-{j // 2}"))
            for j in range(0, len(current) - 1, 2)
        ]
        advanced = call_many(round_jobs)
        duel_outputs.append(list(advanced))
        if len(current) % 2:
            advanced.append(current[-1])
        current = advanced
        round_i += 1
    winner = current[0] #the bracket winner (with n=2/3 there are no duels: the lone worker)

    #Tier 3: a separate manager that sees only the bracket winner
    manager_prompt = MANAGER_NUMERIC.format(
        m = 1,
        question = question,
        reports = format_reports([winner])
    )
    manager_seed = make_seed(base_seed, run_id, n, "tournament", item_id, "manager", 0)
    manager_output = call_llm(manager_prompt, seed=manager_seed)

    return {
        "architecture": "tournament",
        "n": n,
        "item_id": item_id,
        "run_id": run_id,
        "worker_outputs": worker_outputs,
        "worker_answers": worker_answers,
        "duel_outputs": duel_outputs, #per round; the last round holds the bracket winner
        "manager_output": manager_output,
        "final_answer": parse_final_numeric(manager_output), #manager's answer
    }
