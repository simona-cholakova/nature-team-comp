from src.common import make_seed
from src.llm import call_llm
from src.parsing import parse_final_numeric
from src.prompts import WORKER_NUMERIC


def run(question: str, n: int, item_id: str, run_id: int = 0,
        base_seed: int = 42) -> dict:
    """Single worker baseline (N=1). The n argument is ignored, kept so all
    architectures share one signature."""
    seed = make_seed(base_seed, run_id, 1, "single", item_id, "worker", 0)
    out = call_llm(WORKER_NUMERIC.format(question=question), seed=seed)
    answer = parse_final_numeric(out)
    return {
        "architecture": "single",
        "n": 1,
        "item_id": item_id,
        "run_id": run_id,
        "worker_outputs": [out],
        "worker_answers": [answer],
        "manager_output": None,
        "final_answer": answer,
    }