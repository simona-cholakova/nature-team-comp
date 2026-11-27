#this script loads each benchmark as a list of {"item_id", "question", "gold"} items

import random

from datasets import Dataset, load_dataset

from src.contracts import NUMERIC, MCQ, CODE

LETTERS = "ABCD"
MMLU_HARD_SUBJECTS = ["college_mathematics", "college_physics", "econometrics",
                      "formal_logic", "professional_accounting"]

def _mcq_question(stem: str, options: list[str]) -> str:
    """The stem followed by the four lettered options, one per line."""
    return stem.strip() + "\n" + "\n".join(f"{l}) {str(o).strip()}" for l, o in zip(LETTERS, options))

def _load(path: str, name: str | None, split: str) -> Dataset:
    ds = load_dataset(path, name, split=split)
    assert isinstance(ds, Dataset)
    return ds

def load_gsm8k(n_items: int | None = None) -> list[dict]:
    """GSM8K test set (1,319 items)."""
    items = []
    for i, row in enumerate(_load("openai/gsm8k", "main", "test")):
        gold = row["answer"].split("####")[-1].strip().replace(",", "")
        items.append({"item_id": f"gsm8k-{i}", "question": row["question"], "gold": gold})
    return items[:n_items]

def load_gsmhard(n_items: int | None = None) -> list[dict]:
    """GSM-Hard, kept to the items whose target is an integer (1,017 of 1,319),
       because the numeric contract scores integer strings."""
    items = []
    for i, row in enumerate(_load("reasoning-machines/gsm-hard", None, "train")):
        target = row["target"]
        if abs(target - round(target)) >= 1e-9:
            continue
        items.append({"item_id": f"gsmhard-{i}", "question": row["input"], "gold": str(round(target))})
    return items[:n_items]

def load_arc(n_items: int | None = None) -> list[dict]:
    """ARC-Challenge test set, kept to the four-option items (1,165 of 1,172).
       Options labeled 1-4 are relabeled A-D."""
    items = []
    for row in _load("allenai/ai2_arc", "ARC-Challenge", "test"):
        labels = row["choices"]["label"]
        if len(labels) != 4:
            continue
        gold = LETTERS[labels.index(row["answerKey"])]
        items.append({"item_id": f"arc-{row['id']}",
                      "question": _mcq_question(row["question"], row["choices"]["text"]),
                      "gold": gold})
    return items[:n_items]

def load_mmlu_hard(n_items: int | None = None) -> list[dict]:
    """The five hard MMLU subjects, test split (724 items). With n_items the subset is
       drawn round-robin so that every subject is represented."""
    per_subject = []
    for subject in MMLU_HARD_SUBJECTS:
        per_subject.append([
            {"item_id": f"mmlu-{subject}-{i}",
             "question": _mcq_question(row["question"], row["choices"]),
             "gold": LETTERS[row["answer"]],
             "subject": subject}
            for i, row in enumerate(_load("cais/mmlu", subject, "test"))
        ])
    if n_items is None:
        return [it for subject_items in per_subject for it in subject_items]
    items = []
    depth = 0
    while len(items) < n_items and any(depth < len(s) for s in per_subject):
        items.extend(s[depth] for s in per_subject if depth < len(s))
        depth += 1
    return items[:n_items]

def load_gpqa(n_items: int | None = None) -> list[dict]:
    """GPQA Diamond (198 items). The dataset is gated: accept its terms on the Hugging Face
       page and log in (`hf auth login`) first. The dataset lists the correct answer
       first, so the options are shuffled with a fixed per-item seed."""
    items = []
    for i, row in enumerate(_load("Idavidrein/gpqa", "gpqa_diamond", "train")):
        options = [row["Correct Answer"], row["Incorrect Answer 1"],
                   row["Incorrect Answer 2"], row["Incorrect Answer 3"]]
        order = list(range(4))
        random.Random(f"gpqa-{i}").shuffle(order)
        items.append({"item_id": f"gpqa-{i}",
                      "question": _mcq_question(row["Question"], [options[j] for j in order]),
                      "gold": LETTERS[order.index(0)]})
    return items[:n_items]

def load_humaneval(n_items: int | None = None) -> list[dict]:
    """HumanEval (164 problems) with both test suites: the original base tests and the
       HumanEval+ tests. There is no gold string; a candidate is scored by running both."""
    base = _load("openai/openai_humaneval", None, "test")
    plus = {row["task_id"]: row for row in _load("evalplus/humanevalplus", None, "test")}
    items = []
    for row in base:
        number = row["task_id"].split("/")[-1]
        plus_row = plus[row["task_id"]]
        plus_test = plus_row["test"]
        if number == "32":
            #The published HumanEval+ check for find_zero is unusable: it unpacks the
            #candidate's float result, so every program fails, and with the arguments put in
            #the intended order the reference solution itself still fails 3 of its 886 inputs.
            #This one problem is therefore scored on the base tests only.
            plus_test = "def check(candidate):\n    pass\n"
        items.append({
            "item_id": f"humaneval-{number}",
            "question": "Complete the following Python function.\n" + plus_row["prompt"].rstrip(),
            "gold": None,
            "prompt": plus_row["prompt"],
            "entry_point": row["entry_point"],
            "base_test": row["test"],
            "plus_test": plus_test,
            "canonical_solution": plus_row["canonical_solution"],
        })
    return items[:n_items]

#task name -> (loader, output contract)
TASKS: dict[str, tuple] = {
    "gsm8k": (load_gsm8k, NUMERIC),
    "gsmhard": (load_gsmhard, NUMERIC),
    "arc": (load_arc, MCQ),
    "gpqa": (load_gpqa, MCQ),
    "mmlu_hard": (load_mmlu_hard, MCQ),
    "humaneval": (load_humaneval, CODE),
}
