from ctransformers import AutoModelForCausalLM
from step5_local_llm_service.config import MODEL_PATH

def run_llm(prompt: str) -> str:
    llm = AutoModelForCausalLM.from_pretrained(
        model_path_or_repo_id=MODEL_PATH,
        model_type="llama",     # or try "llama" vs "llama-cpp"
        max_new_tokens=256
    )
    result = llm(prompt)
    return result if isinstance(result, str) else "".join(result)
