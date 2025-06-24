from fastapi import FastAPI
from pydantic import BaseModel

from model_runner import run_llm
from cache import get_cached, set_cached
from step6_responsible_ai.filters import is_safe, sanitize
from step6_responsible_ai.privacy import apply_privacy
from step6_responsible_ai.auditor import log_interaction

app = FastAPI(title="Local LLM API (Secure + Auditable)")

class Prompt(BaseModel):
    prompt: str

@app.post("/generate")
def generate(req: Prompt):
    prompt = req.prompt.strip()

    # 1. Safety check
    if not is_safe(prompt):
        log_interaction("api", prompt, "Unsafe prompt blocked", False)
        return {"error": "Unsafe prompt content detected."}

    # 2. Cache check
    cached = get_cached(prompt)
    if cached:
        log_interaction("api", prompt, cached, True)
        return {"response": cached, "cached": True}

    # 3. Run LLM
    raw_response = run_llm(prompt)

    # 4. Sanitize output
    safe_response = sanitize(raw_response)
    safe_response = apply_privacy(safe_response)

    # 5. Cache and log
    set_cached(prompt, safe_response)
    log_interaction("api", prompt, safe_response, True)

    return {"response": safe_response, "cached": False}
