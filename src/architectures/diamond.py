from src.common import make_seed, call_many, format_reports
from src.parsing import parse_final_numeric
from src.llm import call_llm
from src.prompts import PLANNER_NUMERIC, PLAN_SOLVER_NUMERIC, MANAGER_NUMERIC

def run(question: str, n: int, item_id: str, run_id: int = 0,
        base_seed: int = 42) -> dict:
    """Run the Diamond architecture on a numeric question.
       max(1, n//5) planners describe methods without answering; the remaining calls are
       plan-conditioned solvers spread evenly over the plans (L = n - planners - 1)."""
    assert n >= 3, "Diamond needs at least 1 planner + 1 solver + 1 manager"
    n_planners = max(1, n // 5)
    n_solvers = n - n_planners - 1

    #Tier 1: planners. They are forbidden to answer, so they are not part of L.
    planner_jobs = [
        (PLANNER_NUMERIC.format(i_one_indexed=i + 1, M=n_planners, M_minus_one=n_planners - 1, question=question),
         make_seed(base_seed, run_id, n, "diamond", item_id, "planner", i))
        for i in range(n_planners)
    ]
    planner_outputs = call_many(planner_jobs)

    #Tier 2: plan-conditioned solvers. L proposals. Generate stage.
    solver_jobs = [
        (PLAN_SOLVER_NUMERIC.format(question=question, workers=format_reports([planner_outputs[i % n_planners]])),
         make_seed(base_seed, run_id, n, "diamond", item_id, "solver", i))
        for i in range(n_solvers)
    ]
    worker_outputs = call_many(solver_jobs)
    worker_answers = [parse_final_numeric(o) for o in worker_outputs]

    #Tier 3: the manager sees every solver
    manager_prompt = MANAGER_NUMERIC.format(
        m = n_solvers,
        question = question,
        reports = format_reports(worker_outputs)
    )
    manager_seed = make_seed(base_seed, run_id, n, "diamond", item_id, "manager", 0)
    manager_output = call_llm(manager_prompt, seed=manager_seed)

    return {
        "architecture": "diamond",
        "n": n,
        "item_id": item_id,
        "run_id": run_id,
        "planner_outputs": planner_outputs,
        "worker_outputs": worker_outputs,
        "worker_answers": worker_answers,
        "manager_output": manager_output,
        "final_answer": parse_final_numeric(manager_output), #manager's answer
    }
