import json
import os

from src.architectures import ARCHITECTURES
from src.load_data import load_gsm8k

N_ITEMS = 20
os.makedirs("results", exist_ok=True)
items = load_gsm8k(N_ITEMS)

configs = [("star", 3), ("star", 5)]

with open("results/gsm8k_dev.jsonl", "w") as f:
    for arch, n in configs:
        run_fn = ARCHITECTURES[arch]
        correct = covered = 0
        for it in items:
            res = run_fn(it["question"], n, it["item_id"])
            res["gold"] = it["gold"]
            res["Y"] = int(res["final_answer"] == it["gold"])
            res["O"] = int(any(a == it["gold"] for a in res["worker_answers"]))
            correct += res["Y"]
            covered += res["O"]
            f.write(json.dumps(res) + "\n")
        print(f"{arch} N={n}: Y={correct/len(items):.2f}  O={covered/len(items):.2f}")