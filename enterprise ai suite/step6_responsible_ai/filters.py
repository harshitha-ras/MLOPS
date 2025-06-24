def is_safe_prompt(prompt: str) -> bool:
    blacklist = ["hate", "kill", "attack"]
    return not any(word in prompt.lower() for word in blacklist)
