from datetime import datetime

def log_event(sender, receiver, message):
    with open("security/audit_logs.txt", "a") as f:
        f.write(f"{datetime.utcnow()} | {sender} -> {receiver}: {message}\n")
