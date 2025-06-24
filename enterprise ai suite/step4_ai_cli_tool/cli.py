import argparse
import requests
from handler import handle_error

API_URL = "http://localhost:8000/generate"

def run_prompt(prompt, user="cli"):
    try:
        response = requests.post(API_URL, json={"prompt": prompt, "user": user})
        data = response.json()
        if "response" in data:
            print("\n🧠 AI Response:\n", data["response"])
        elif "error" in data:
            print("\n⚠️ Error:", data["error"])
    except Exception as e:
        handle_error("CLI request failed", str(e))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AI Text Generator CLI Tool")
    parser.add_argument("--prompt", type=str, help="Prompt text to send to the AI", required=True)
    parser.add_argument("--user", type=str, default="cli", help="User ID (for logging)")
    args = parser.parse_args()

    run_prompt(args.prompt, args.user)
