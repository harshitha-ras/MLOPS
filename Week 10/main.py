from fastapi import FastAPI, HTTPException, Request, Depends
from pydantic import BaseModel
from transformers.pipelines import pipeline
from transformers.trainer_utils import set_seed
import os

app = FastAPI()
API_KEY = os.getenv("SECRET_API_KEY", "your_secure_key_here")
print("Loaded API key:", API_KEY)

def api_key_auth(request: Request):
    print("Incoming X-API-Key:", request.headers.get("x-api-key"))
    if request.headers.get("x-api-key") != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return True

class Prompt(BaseModel):
    text: str
    max_length: int = 50

generator = pipeline("text-generation", model="distilgpt2")
set_seed(20)

@app.post("/generate")
def generate(prompt: Prompt, request: Request, auth: bool = Depends(api_key_auth)):
    try:
        results = generator(prompt.text, max_length=prompt.max_length, num_return_sequences=1)
        if results and isinstance(results, list) and "generated_text" in results[0]:
            return {"generated_text": results[0]["generated_text"]}
        else:
            raise HTTPException(status_code=500, detail="Model did not return generated text.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
