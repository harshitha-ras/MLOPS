BANNED_KEYWORDS = ["kill", "bomb", "attack", "hate", "racist", "violence", "sex", "nsfw", "drugs"]

def is_safe(content: str) -> bool:
    lower = content.lower()
    return not any(bad_word in lower for bad_word in BANNED_KEYWORDS)

def censor_content(content: str) -> str:
    for bad in BANNED_KEYWORDS:
        content = content.replace(bad, "***")
    return content
