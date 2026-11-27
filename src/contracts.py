#an output contract bundles everything that depends on the answer type:
#the prompt template of every role and the parser for the FINAL line

from dataclasses import dataclass
from typing import Callable

from src import prompts as P
from src.code_eval import passes
from src.parsing import (parse_final_numeric, parse_final_mcq, parse_final_code,
                         truncate_report, truncate_code_report)

def exact_match(answer: str | None, item: dict) -> bool:
    """QA scoring: the canonical answer string equals the gold one."""
    return answer is not None and answer == item["gold"]

@dataclass(frozen=True)
class Contract:
    name: str
    parse: Callable[[str], str | None]
    worker: str
    worker_format: str
    personas: list[tuple[str, str]]
    critic: str
    synthesizer: str
    refiner: str
    duelist: str
    duelist_bye: str
    planner: str
    plan_solver: str
    manager: str
    correct: Callable[[str | None, dict], bool] = exact_match #is this parsed answer right for this item?
    max_tokens: int = 1024      #generation cap per call
    report_tokens: int = 120    #cap on each parent report shown downstream
    truncate: Callable[[str, int], str] = truncate_report

    def clip(self, report: str) -> str:
        """Truncate one parent report to this contract's cap."""
        return self.truncate(report, self.report_tokens)

#integer answers: GSM8K, GSMHard
NUMERIC = Contract(
    name="numeric", parse=parse_final_numeric,
    worker=P.WORKER_NUMERIC, worker_format=P.WORKER_FORMAT_NUMERIC, personas=P.PERSONAS_NUMERIC,
    critic=P.CRITIC_NUMERIC, synthesizer=P.SYNTHESIZER_NUMERIC, refiner=P.REFINER_NUMERIC,
    duelist=P.DUELIST_NUMERIC, duelist_bye=P.DUELIST_BYE_NUMERIC,
    planner=P.PLANNER_NUMERIC, plan_solver=P.PLAN_SOLVER_NUMERIC, manager=P.MANAGER_NUMERIC,
)

#option letters A-D: ARC-Challenge, GPQA, MMLU
MCQ = Contract(
    name="mcq", parse=parse_final_mcq,
    worker=P.WORKER_MCQ, worker_format=P.WORKER_FORMAT_MCQ, personas=P.PERSONAS_MCQ,
    critic=P.CRITIC_MCQ, synthesizer=P.SYNTHESIZER_MCQ, refiner=P.REFINER_MCQ,
    duelist=P.DUELIST_MCQ, duelist_bye=P.DUELIST_BYE_MCQ,
    planner=P.PLANNER_MCQ, plan_solver=P.PLAN_SOLVER_MCQ, manager=P.MANAGER_MCQ,
)

#Python functions scored by execution: HumanEval with HumanEval+ tests.
#Distinct correct programs are different strings, so answers are never compared to each other.
CODE = Contract(
    name="code", parse=parse_final_code,
    worker=P.WORKER_CODE, worker_format=P.WORKER_FORMAT_CODE, personas=P.PERSONAS_CODE,
    critic=P.CRITIC_CODE, synthesizer=P.SYNTHESIZER_CODE, refiner=P.REFINER_CODE,
    duelist=P.DUELIST_CODE, duelist_bye=P.DUELIST_BYE_CODE,
    planner=P.PLANNER_CODE, plan_solver=P.PLAN_SOLVER_CODE, manager=P.MANAGER_CODE,
    correct=lambda answer, item: passes(item, answer),
    max_tokens=2048, report_tokens=512, truncate=truncate_code_report,
)
