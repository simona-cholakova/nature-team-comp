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


