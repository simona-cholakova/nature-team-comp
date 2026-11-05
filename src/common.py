import hashlib
from concurrent.futures import ThreadPoolExecutor

from src.llm import call_llm
from src.parsing import truncate_report

MAX_WORKERS = 8 #how many requests are in flight at once

def make_seed(*parts) -> int:
    """Deterministic seed from any combination of identifying parts."""
    key = "|".join(str(p) for p in parts)
    return int(hashlib.md5(key.encode()).hexdigest(), 16) % (2**31)

def call_many(jobs: list[tuple[str, int]]) -> list[str]:
    """Run (prompt, seed) pairs in parallel. Results keep the input order."""
    def _one(job: tuple[str, int]) -> str:
        prompt, seed = job
        return call_llm(prompt, seed=seed)

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        return list(pool.map(_one, jobs))

def format_reports(outputs: list[str], max_tokens: int = 120) -> str:
    """Label each upstream output 'Report i' and truncate it, for a downstream prompt."""
    return "\n\n".join(
        f"Report {i + 1}:\n{truncate_report(o, max_tokens)}"
        for i, o in enumerate(outputs)
    )