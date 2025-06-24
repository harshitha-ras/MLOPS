import argparse
import requests

parser = argparse.ArgumentParser()
parser.add_argument("--prompt", required=True, help="Enter the prompt for LLM")
parser.add_argument("--user", default="cli_user", help="Username to track usage")
args = parser.parse_args()

print(f"User: {args.user}")
print(f"Prompt: {args.prompt}")

response = requests.post("http://127.0.0.1:8000/generate", json={
    "prompt": args.prompt,
    "user": args.user
})

if response.status_code == 200:
    print("LLM Response:", response.json()["response"])
else:
    print("Error occurred:", response.text)
