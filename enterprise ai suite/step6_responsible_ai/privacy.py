import re

def redact_emails(text):
    return re.sub(r'[\w\.-]+@[\w\.-]+', '[email]', text)

def redact_phone_numbers(text):
    return re.sub(r'\+?\d[\d\-\(\) ]{7,}\d', '[phone]', text)

def apply_privacy(text):
    text = redact_emails(text)
    text = redact_phone_numbers(text)
    return text
