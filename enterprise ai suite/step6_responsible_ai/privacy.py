import re

def mask_sensitive_data(text: str) -> str:
    text = re.sub(r"\b\d{12}\b", "[MASKED-AADHAAR]", text)
    text = re.sub(r"\b\d{10}\b", "[MASKED-PHONE]", text)
    return text
