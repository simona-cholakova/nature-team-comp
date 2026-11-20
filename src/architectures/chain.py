from src.common import make_seed, format_reports
from src.parsing import parse_final_numeric
from src.llm import call_llm
from src.prompts import WORKER_NUMERIC, REFINER_NUMERIC, MANAGER_NUMERIC

def run_chain(question: str, n: int, item_id: str, run_id: int, base_seed: int,
              window: int, name: str) -> dict:
    """Shared body of Chain and Cascading-Chain: one worker, then n-2 refiners that each
       read the `window` most recent reports. The manager reads all n-1 reports (L = 1)."""
    assert n >= 2, "Chain needs at least 1 worker + 1 manager"

    #Tier 1: a single worker. L = 1 proposal. Generate stage.
    worker_seed = make_seed(base_seed, run_id, n, name, item_id, "worker", 0)
    reports = [call_llm(WORKER_NUMERIC.format(question=question), seed=worker_seed)]

    #Tier 2: serial refiners, each building on the most recent reports
    for i in range(n - 2):
        seen = reports[-window:]
        prompt = REFINER_NUMERIC.format(b=len(seen), question=question, workers=format_reports(seen))
        reports.append(call_llm(prompt, seed=make_seed(base_seed, run_id, n, name, item_id, "refiner", i)))

    #Tier 3: the manager reads the complete sequence
    manager_prompt = MANAGER_NUMERIC.format(
        m = len(reports),
        question = question,
        reports = format_reports(reports)
    )
    manager_seed = make_seed(base_seed, run_id, n, name, item_id, "manager", 0)
    manager_output = call_llm(manager_prompt, seed=manager_seed)

    return {
        "architecture": name,
        "n": n,
        "item_id": item_id,
        "run_id": run_id,
        "worker_outputs": reports[:1],
        "worker_answers": [parse_final_numeric(reports[0])],
        "refiner_outputs": reports[1:],
        "manager_output": manager_output,
        "final_answer": parse_final_numeric(manager_output), #manager's answer
    }

def run(question: str, n: int, item_id: str, run_id: int = 0,
        base_seed: int = 42) -> dict:
    """Run the Chain architecture: each refiner sees only the immediately preceding report."""
    return run_chain(question, n, item_id, run_id, base_seed, window=1, name="chain")
