import json
from datetime import datetime

def log_audit(prompt: str, response: str, user: str):
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "user": user,
        "prompt": prompt,
        "response": response
    }
    with open("audit_log.jsonl", "a") as f:
        f.write(json.dumps(entry) + "\n")
