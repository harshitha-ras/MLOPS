import re

BLOCKED_KEYWORDS = [
    "kill", "violence", "bomb", "assassinate", "drugs", "nsfw",
    "suicide", "hate", "abuse", "self-harm"
]

def is_safe(text: str) -> bool:
    lowered = text.lower()
    return not any(bad in lowered for bad in BLOCKED_KEYWORDS)

def sanitize(text: str) -> str:
    for bad in BLOCKED_KEYWORDS:
        text = re.sub(bad, "[filtered]", text, flags=re.IGNORECASE)
    return text
