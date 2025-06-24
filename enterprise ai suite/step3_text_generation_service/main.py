from fastapi import FastAPI, Request
from pydantic import BaseModel
from generator import generate_text
from filter import is_safe, censor_content
from monitor import log_usage

app = FastAPI(title="Text Generation API")

class PromptRequest(BaseModel):
    prompt: str
    user: str = "anonymous"

@app.post("/generate")
def generate(prompt_data: PromptRequest):
    prompt = prompt_data.prompt
    user = prompt_data.user

    if not is_safe(prompt):
        return {"error": "Prompt contains unsafe content."}

    response = generate_text(prompt)
    censored_response = censor_content(response)
    log_usage(prompt, censored_response, user)

    return {"response": censored_response}
