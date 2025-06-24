from datetime import datetime

def handle_error(context, error):
    timestamp = datetime.utcnow().isoformat()
    print(f"[{timestamp}] ERROR in {context}: {error}")
    with open("error.log", "a") as f:
        f.write(f"[{timestamp}] {context}: {error}\n")
