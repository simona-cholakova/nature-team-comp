from src.common import make_seed, call_many, format_reports
from src.parsing import parse_final_numeric
from src.llm import call_llm
from src.prompts import WORKER_NUMERIC, SYNTHESIZER_NUMERIC, MANAGER_NUMERIC

def _shape(n: int) -> tuple[int, int, int]:
    """Return (workers, fan-in-3 synthesizers, extra synthesizers) filling n calls.
       Complete triples feed a synthesizer and orphan workers feed the manager directly.
       A few budgets (n=4, 20, ...) leave one call over, spent on a synthesizer
       over two orphans."""
    n_workers = max(l for l in range(1, n) if l + l // 3 + 1 <= n)
    n_syn = n_workers // 3
    spare = n - 1 - n_workers - n_syn
    return n_workers, n_syn, spare

def run(question: str, n: int, item_id: str, run_id: int = 0,
        base_seed: int = 42) -> dict:
    """Run the Tree architecture on a numeric question.
       Workers are merged by fan-in-three synthesizers; the manager reads the
       syntheses plus any orphan workers (n=30 -> L=22, 7 syntheses, 1 orphan)."""
    assert n >= 2, "Tree needs at least 1 worker + 1 manager"
    n_workers, n_syn, spare = _shape(n)

    #Tier 1: independent workers. L proposals. Generate stage.
    worker_prompt = WORKER_NUMERIC.format(question=question)
    jobs = [
        (worker_prompt, make_seed(base_seed, run_id, n, "tree", item_id, "worker", i))
        for i in range(n_workers)
    ]
    worker_outputs = call_many(jobs)
    worker_answers = [parse_final_numeric(o) for o in worker_outputs]

    #Tier 2: synthesizers over consecutive groups of three (the spare one covers the last two orphans)
    groups = [worker_outputs[3 * i:3 * i + 3] for i in range(n_syn)]
    orphans = worker_outputs[3 * n_syn:]
    if spare:
        groups.append(orphans)
        orphans = []
    synth_jobs = [
        (SYNTHESIZER_NUMERIC.format(b=len(g), question=question, workers=format_reports(g)),
         make_seed(base_seed, run_id, n, "tree", item_id, "synthesizer", i))
        for i, g in enumerate(groups)
    ]
    synth_outputs = call_many(synth_jobs)

    #Tier 3: the manager reads the syntheses and any orphan workers
    manager_inputs = synth_outputs + orphans
    manager_prompt = MANAGER_NUMERIC.format(
        m = len(manager_inputs),
        question = question,
        reports = format_reports(manager_inputs)
    )
    manager_seed = make_seed(base_seed, run_id, n, "tree", item_id, "manager", 0)
    manager_output = call_llm(manager_prompt, seed=manager_seed)

    return {
        "architecture": "tree",
        "n": n,
        "item_id": item_id,
        "run_id": run_id,
        "worker_outputs": worker_outputs,
        "worker_answers": worker_answers,
        "synthesizer_outputs": synth_outputs,
        "manager_output": manager_output,
        "final_answer": parse_final_numeric(manager_output), #manager's answer
    }
