from fastapi import FastAPI
import httpx
from cachetools import LRUCache
import time
import hashlib
import threading
import psutil
import os

# Metrics storage
metrics = {
    "total_requests": 0,
    "cache_hits": 0,
    "cache_misses": 0,
    "total_latency": 0.0,  # Sum of all response times
}
metrics_lock = threading.Lock()


app = FastAPI()
OLLAMA_URL = "http://localhost:11434/api/generate"
cache = LRUCache(maxsize=100)

def generate_cache_key(prompt: str) -> str:
    """Generate a cache key from the prompt"""
    return hashlib.md5(prompt.encode()).hexdigest()

# ADD THIS ROOT ENDPOINT
@app.get("/")
async def root():
    return {"message": "LLM API is running", "endpoints": ["/generate", "/health"]}

@app.post("/generate")
async def generate(request_data: dict):
    import time
    start = time.time()
    prompt = request_data.get("prompt", "")
    cache_key = generate_cache_key(prompt)
    
    with metrics_lock:
        metrics["total_requests"] += 1

    cached_result = cache.get(cache_key)
    if cached_result is not None:
        duration = time.time() - start
        with metrics_lock:
            metrics["cache_hits"] += 1
            metrics["total_latency"] += duration
        print(f"Cache HIT - Request took {duration:.4f} seconds")
        return cached_result

    # Not in cache
    payload = {"model": "tinyllama", "prompt": prompt, "stream": False}
    async with httpx.AsyncClient() as client:
        resp = await client.post(OLLAMA_URL, json=payload)
        result = resp.json()
        cache[cache_key] = result
        duration = time.time() - start
        with metrics_lock:
            metrics["cache_misses"] += 1
            metrics["total_latency"] += duration
        print(f"Cache MISS - Request took {duration:.4f} seconds")
        return result


@app.get("/health")
async def health():
    return {"status": "healthy", "cache_size": len(cache)}


@app.get("/metrics")
async def get_metrics():
    with metrics_lock:
        total = metrics["total_requests"]
        avg_latency = metrics["total_latency"] / total if total > 0 else 0.0
        process = psutil.Process(os.getpid())
        mem_mb = process.memory_info().rss / 1024 / 1024
        return {
            "total_requests": metrics["total_requests"],
            "cache_hits": metrics["cache_hits"],
            "cache_misses": metrics["cache_misses"],
            "average_latency_seconds": round(avg_latency, 4),
            "memory_usage_mb": round(mem_mb, 2),
        }
