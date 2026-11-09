from src.common import make_seed, call_many, format_reports
from src.parsing import parse_final_numeric, truncate_report
from src.llm import call_llm
from src.prompts import WORKER_NUMERIC, CRITIC_NUMERIC, MANAGER_NUMERIC

def run(question: str, n: int, item_id: str, run_id: int = 0,
        base_seed: int = 42) -> dict:
    """Run the Proposer-Critic architecture on a numeric question.
       (n-1)//2 proposer-critic pairs; when n-1 is odd one proposal is left unpaired
       and goes straight to the manager (L = ceil((n-1)/2))."""
    assert n >= 2, "Proposer-Critic needs at least 1 worker + 1 manager"
    n_pairs = (n - 1) // 2
    n_free = (n - 1) % 2
    n_workers = n_pairs + n_free

    #Tier 1: independent proposers. L proposals. Generate stage.
    worker_prompt = WORKER_NUMERIC.format(question=question)
    jobs = [
        (worker_prompt, make_seed(base_seed, run_id, n, "proposer_critic", item_id, "worker", i))
        for i in range(n_workers)
    ]
    worker_outputs = call_many(jobs)
    worker_answers = [parse_final_numeric(o) for o in worker_outputs]

    #Tier 2: each critic sees exactly one (truncated) proposal. The last proposal is unpaired when n-1 is odd.
    critic_jobs = [
        (CRITIC_NUMERIC.format(question=question, proposal=truncate_report(worker_outputs[i])),
         make_seed(base_seed, run_id, n, "proposer_critic", item_id, "critic", i))
        for i in range(n_pairs)
    ]
    critic_outputs = call_many(critic_jobs)

    #Tier 3: the manager reads the critics plus the unpaired proposal, if any
    manager_inputs = critic_outputs + worker_outputs[n_pairs:]
    manager_prompt = MANAGER_NUMERIC.format(
        m = len(manager_inputs),
        question = question,
        reports = format_reports(manager_inputs)
    )
    manager_seed = make_seed(base_seed, run_id, n, "proposer_critic", item_id, "manager", 0)
    manager_output = call_llm(manager_prompt, seed=manager_seed)

    return {
        "architecture": "proposer_critic",
        "n": n,
        "item_id": item_id,
        "run_id": run_id,
        "worker_outputs": worker_outputs,
        "worker_answers": worker_answers,
        "critic_outputs": critic_outputs,
        "manager_output": manager_output,
        "final_answer": parse_final_numeric(manager_output), #manager's answer
    }
