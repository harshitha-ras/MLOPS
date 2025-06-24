import json
from datetime import datetime

AUDIT_LOG = "audit_log.jsonl"

def log_interaction(source: str, prompt: str, response: str, safe: bool):
    record = {
        "timestamp": datetime.utcnow().isoformat(),
        "source": source,             # e.g., cli, ui, api
        "prompt": prompt,
        "response": response,
        "safe": safe
    }
    with open(AUDIT_LOG, "a") as f:
        f.write(json.dumps(record) + "\n")
