from ctransformers import AutoModelForCausalLM
import os

MODEL_FILE = "tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf"
MODEL_PATH = os.path.join("models", MODEL_FILE)

llm = AutoModelForCausalLM.from_pretrained(
    MODEL_PATH,
    model_type="llama",         # or "mistral", "phi" if using different model
    local_files_only=True
)

def run_llm(prompt: str) -> str:
    result = llm(prompt, max_new_tokens=50)
    if isinstance(result, str):
        return result
    else:
        return "".join(result)
