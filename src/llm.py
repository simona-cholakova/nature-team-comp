#in this script we have code that talks to the model

from openai import OpenAI

BASE_URL = "http://localhost:11434/v1"
MODEL = "qwen2.5:1.5b"

_client = OpenAI(
    base_url = BASE_URL,
    api_key = "ollama"
)

def call_llm(prompt: str, temperature: float = 0.4, top_p: float = 0.95,
             max_tokens: int = 1024, seed: int | None = None) -> str:
    """
    Calls the LLM with the given prompt and parameters.

    Args:
        prompt (str): The prompt to send to the model.
        temperature (float): Sampling temperature. Default is 0.4.
        top_p (float): Nucleus sampling parameter. Default is 0.95.
        max_tokens (int): Maximum number of tokens to generate. Default is 1024.
        seed (int | None): Optional seed for reproducibility.

    Returns:
        str: The generated text from the model.
    """
    response = _client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature,
        top_p=top_p,
        max_tokens=max_tokens,
        seed=seed
    )
    
    content = response.choices[0].message.content

    return content or ""

