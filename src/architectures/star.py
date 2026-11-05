from src.common import make_seed, call_many, format_reports
from src.parsing import parse_final_numeric, truncate_report
from src.llm import call_llm
from src.prompts import WORKER_NUMERIC, MANAGER_NUMERIC

def run(question: str, n: int, item_id: str, run_id: int = 0,
        base_seed: int = 42) -> dict:
    """Run the STAR architecture on a numeric question.
       n-1 independent workers feed one manager (L = n-1)."""
    assert n >= 2, "Star needs at least 1 worker + 1 manager"
    n_workers = n - 1

    #Tier 1: independent workers. L proposals. Generate stage.
    worker_prompt = WORKER_NUMERIC.format(question=question)
    jobs = [
        (worker_prompt, make_seed(base_seed, run_id, n, "star", item_id, "worker", i))
        for i in range(n_workers)
    ]
    worker_outputs = call_many(jobs)
    worker_answers = [parse_final_numeric(o) for o in worker_outputs]

    #Tier 2: the manager reads all (truncated) worker reports
    manager_prompt = MANAGER_NUMERIC.format(
        m = n_workers,
        question = question,
        reports = format_reports(worker_outputs) #we do not use worker_answers here, because we want the manager to see the full reasoning of each worker
    )
    manager_seed = make_seed(base_seed, run_id, n, "star", item_id, "manager", 0)
    manager_output = call_llm(manager_prompt, seed=manager_seed)

    return {
        "architecture": "star",
        "n": n,
        "item_id": item_id,
        "run_id": run_id,
        "worker_outputs": worker_outputs,
        "worker_answers": worker_answers,
        "manager_output": manager_output,
        "final_answer": parse_final_numeric(manager_output), #manager's answer
    }


