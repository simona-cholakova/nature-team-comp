from datasets import Dataset, load_dataset


def load_gsm8k(n_items: int | None = None) -> list[dict]:
    ds = load_dataset("openai/gsm8k", "main", split="test")
    assert isinstance(ds, Dataset)
    items = []
    for i, row in enumerate(ds):
        gold = row["answer"].split("####")[-1].strip().replace(",", "")
        items.append({"item_id": f"gsm8k-{i}", "question": row["question"], "gold": gold})
        if n_items and len(items) >= n_items:
            break
    return items