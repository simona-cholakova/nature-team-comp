#this script turns the model's output into clean answer

import re

_FINAL = re.compile(r"FINAL:\s*\$?\s*(-?[\d,]*\.?\d+)") #extracts the final numerical answer from the model's output

def parse_final_numeric(text: str) -> str | None:
    """Extract the FINAL answer and canonicalize to an integer string."""
    m = _FINAL.search(text or "")
    if not m:
        return None
    num = m.group(1).replace(",","") #remove commas
    try:
        val = float(num)
    except ValueError:
        return None
    return str(int(val)) if val == int(val) else None

def truncate_report(text: str, max_tokens: int = 120) -> str:
    """Truncate the report to a maximum number of tokens."""
    words = text.split()
    return " ".join(words[:max_tokens])



_FINAL_MCQ = re.compile(r"FINAL:\s*[\(\[<]?\s*([A-Da-d])\b") #extracts the final option letter from the model's output

def parse_final_mcq(text: str) -> str | None:
    """Extract the FINAL answer and canonicalize to an option letter A-D."""
    m = _FINAL_MCQ.search(text or "")
    return m.group(1).upper() if m else None

_FENCE = re.compile(r"```[ \t]*(?:python|py)?[ \t]*\r?\n(.*?)(?:```|\Z)", re.S | re.I) #a fenced code block (the closing fence may be cut off)

def parse_final_code(text: str) -> str | None:
    """Extract the candidate program: the first fenced block that holds a function definition."""
    blocks = [b.rstrip() + "\n" for b in _FENCE.findall(text or "") if b.strip()]
    for block in blocks:
        if re.search(r"^\s*def\s+\w+\s*\(", block, re.M):
            return block
    return None

def truncate_code_report(text: str, max_tokens: int = 512) -> str:
    """Truncate to a maximum number of tokens while keeping newlines and indentation,
       which truncate_report would flatten and which Python code depends on."""
    words = list(re.finditer(r"\S+", text))
    if len(words) <= max_tokens:
        return text
    return text[:words[max_tokens - 1].end()]
