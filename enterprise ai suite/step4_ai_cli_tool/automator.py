from cli import run_prompt

def run_batch(file_path):
    try:
        with open(file_path, "r") as f:
            prompts = f.readlines()
        for prompt in prompts:
            print(f"\nPrompt: {prompt.strip()}")
            run_prompt(prompt.strip())
    except Exception as e:
        from handler import handle_error
        handle_error("Batch automation failed", str(e))
