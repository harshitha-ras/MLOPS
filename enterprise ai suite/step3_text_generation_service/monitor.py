import json
from datetime import datetime

LOG_FILE = "usage_metrics.txt"

def log_usage(prompt: str, output: str, user: str = "anonymous"):
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "user": user,
        "prompt": prompt,
        "response": output
    }
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")
