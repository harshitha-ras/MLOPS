import random

def generate_text(prompt: str) -> str:
    # Simulated output — replace with LLM later
    samples = [
        f"{prompt}... and then it happened unexpectedly.",
        f"{prompt} leads to a surprising result.",
        f"{prompt} is the start of something amazing."
    ]
    return random.choice(samples)
