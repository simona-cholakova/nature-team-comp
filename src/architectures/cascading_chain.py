from src.architectures.chain import run_chain

WINDOW = 5 #how many preceding reports each refiner can read

def run(question: str, n: int, item_id: str, run_id: int = 0,
        base_seed: int = 42) -> dict:
    """Run the Cascading-Chain architecture: Chain, but each refiner sees up to the
       five most recent reports. The manager still sees the complete sequence."""
    return run_chain(question, n, item_id, run_id, base_seed, window=WINDOW, name="cascading_chain")
