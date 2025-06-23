from fastapi import FastAPI, HTTPException, Request, Depends, status
from fastapi.security.api_key import APIKeyHeader, APIKey
from pydantic import BaseModel, Field
from transformers import pipeline, set_seed
from typing import Dict
import time
import logging

# --- Configuration ---
API_KEY = "9d207bf0-10f5-4d8f-a479-22ff5aeff8d1"  # Replace with a secure key!
UNSAFE_WORDS = {"hate", "violence", "kill", "nsfw", "sex"}  # Example filter
RATE_LIMIT = 5  # requests per minute per IP

# --- Logging setup ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("api_logger")

# --- App and Models ---
app = FastAPI(
    title="Text Generation API",
    description="A generative AI API with content filtering, monitoring, and security.",
    version="1.0"
)

class Prompt(BaseModel):
    text: str = Field(..., example="Once upon a time", description="Input prompt for text generation")
    max_length: int = Field(50, example=100, description="Maximum output length")

class GenerationResponse(BaseModel):
    generated_text: str

# --- Security: API Key Auth ---
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)
def get_api_key(api_key_header: str = Depends(api_key_header)):
    if api_key_header == API_KEY:
        return api_key_header
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API Key"
        )

# --- Security: Rate Limiting ---
request_counts: Dict[str, list] = {}

def rate_limiter(request: Request):
    ip = request.client.host
    now = time.time()
    window = 60  # seconds
    if ip not in request_counts:
        request_counts[ip] = []
    # Remove outdated requests
    request_counts[ip] = [t for t in request_counts[ip] if now - t < window]
    if len(request_counts[ip]) >= RATE_LIMIT:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Try again later."
        )
    request_counts[ip].append(now)

# --- Load Model ---
generator = pipeline("text-generation", model="distilgpt2")
set_seed(20)

# --- Usage Metrics ---
metrics = {
    "total_requests": 0,
    "blocked_requests": 0,
    "successful_requests": 0
}

# --- Content Filtering ---
def is_safe(text: str) -> bool:
    lower = text.lower()
    return not any(word in lower for word in UNSAFE_WORDS)

# --- Middleware for Monitoring ---
@app.middleware("http")
async def log_requests(request: Request, call_next):
    metrics["total_requests"] += 1
    logger.info(f"Request: {request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"Response status: {response.status_code}")
    return response

# --- API Endpoints ---

@app.post(
    "/generate",
    response_model=GenerationResponse,
    summary="Generate text",
    description="Generates text using DistilGPT2 model. Requires API Key.",
    responses={
        200: {"description": "Successful generation"},
        400: {"description": "Content blocked by safety filter"},
        401: {"description": "Invalid or missing API Key"},
        429: {"description": "Rate limit exceeded"},
        500: {"description": "Generation error"}
    }
)
def generate(
    prompt: Prompt,
    request: Request,
    api_key: APIKey = Depends(get_api_key)
):
    # Rate limiting
    rate_limiter(request)

    # Generate text
    try:
        results = generator(prompt.text, max_length=prompt.max_length, num_return_sequences=1)
        generated = results[0]["generated_text"]
    except Exception as e:
        logger.error(f"Generation error: {e}")
        raise HTTPException(status_code=500, detail="Model error: " + str(e))

    # Content filtering
    if not is_safe(generated):
        metrics["blocked_requests"] += 1
        logger.warning("Blocked unsafe content")
        raise HTTPException(status_code=400, detail="Generated content blocked by safety filter.")

    metrics["successful_requests"] += 1
    return GenerationResponse(generated_text=generated)

@app.get(
    "/metrics",
    summary="Get API usage metrics",
    description="Returns basic usage metrics for the API. Requires API Key."
)
def get_metrics(api_key: APIKey = Depends(get_api_key)):
    return metrics

@app.get(
    "/docs",
    include_in_schema=False
)
def custom_docs_redirect():
    return {"message": "Go to /docs for API documentation."}

# --- Run with: uvicorn script_name:app --reload ---
