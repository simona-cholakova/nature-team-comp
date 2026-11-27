#this script decides whether a candidate program is correct by running the benchmark's tests

#NOTE: candidates are model-written code. Each one runs in a separate Python process with a
#time limit, a memory limit, an empty working directory and a stripped environment. That stops
#runaway programs, but it is not a security sandbox (no filesystem or network isolation). The
#paper runs candidates inside the EvalPlus sandbox.

import hashlib
import os
import resource
import subprocess
import sys
import tempfile
import threading

TIMEOUT_S = 60          #wall-clock limit per test suite
MEMORY_BYTES = 4 * 2**30  #address-space limit per process

_cache: dict[str, bool] = {}
_lock = threading.Lock()

def _limits() -> None:
    """Applied inside the child process just before it starts."""
    resource.setrlimit(resource.RLIMIT_AS, (MEMORY_BYTES, MEMORY_BYTES))
    resource.setrlimit(resource.RLIMIT_CPU, (TIMEOUT_S, TIMEOUT_S))
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
    os.setsid()

def run_program(program: str, timeout: float = TIMEOUT_S) -> bool:
    """Run a Python program in a fresh process. True when it exits cleanly in time."""
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "program.py")
        with open(path, "w") as f:
            f.write(program)
        try:
            proc = subprocess.run(
                [sys.executable, "-I", path], cwd=tmp, env={"PATH": os.defpath},
                stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                timeout=timeout, preexec_fn=_limits,
            )
        except subprocess.TimeoutExpired:
            return False
        return proc.returncode == 0

def passes(item: dict, code: str | None) -> bool:
    """True when the candidate passes BOTH the base HumanEval tests and the HumanEval+ tests.
       The task prompt is put in front of the candidate so that its imports and helper
       functions are available; the candidate's own definition then replaces the stub."""
    if not code:
        return False
    key = hashlib.md5((item["item_id"] + "\0" + code).encode()).hexdigest()
    with _lock:
        if key in _cache:
            return _cache[key]
    header = item["prompt"] + "\n    pass\n\n" + code + "\n\n"
    call = f"\n\ncheck({item['entry_point']})\n"
    ok = all(run_program(header + item[suite] + call) for suite in ("base_test", "plus_test"))
    with _lock:
        _cache[key] = ok
    return ok
