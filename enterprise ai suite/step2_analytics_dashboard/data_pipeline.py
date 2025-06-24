import json
import random
from datetime import datetime, timedelta

def simulate_metrics(num_days=7):
    data = []
    for i in range(num_days):
        day = datetime.now() - timedelta(days=i)
        messages = random.randint(10, 50)
        users = random.randint(3, 10)
        latency = round(random.uniform(0.2, 1.0), 2)
        data.append({
            "date": day.strftime("%Y-%m-%d"),
            "messages_sent": messages,
            "active_users": users,
            "avg_latency": latency
        })
    return data[::-1]

def save_metrics(filepath="metrics.json"):
    metrics = simulate_metrics()
    with open(filepath, "w") as f:
        json.dump(metrics, f, indent=2)

def load_metrics(filepath="metrics.json"):
    with open(filepath) as f:
        return json.load(f)
