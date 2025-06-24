from fastapi import FastAPI, Request
from pydantic import BaseModel
from step5_local_llm_service.model_runner import run_llm
from step5_local_llm_service.cache import get_cached, set_cached

app = FastAPI()

class PromptRequest(BaseModel):
    prompt: str
    user: str

@app.post("/generate")
def generate(data: PromptRequest):
    prompt, user = data.prompt, data.user
    cached = get_cached(prompt)
    if cached:
        return {"response": cached, "cached": True}
    response = run_llm(prompt)
    set_cached(prompt, response)
    return {"response": response}
