Overview
This guide documents the deployment of a local open-source LLM (TinyLlama) using Ollama, wrapped with a FastAPI server, with in-memory caching and performance metrics collection. It covers setup, API usage, caching, metrics, and troubleshooting for local development and assignment submission.

Table of Contents
1. Prerequisites

2. Environment Setup

3. Model Deployment with Ollama

4. API Wrapper with FastAPI

5. Caching Implementation

6. Performance Metrics

7. API Endpoints & Usage

8. Testing the API

9. Troubleshooting

10. Summary Table



Prerequisites
Windows, macOS, or Linux machine

Python 3.8+ installed

Internet connection


Environment Setup
1. Install Ollama

On Windows: Download and install from Ollama's website.

On macOS/Linux:

curl https://ollama.ai/install.sh | sh


2. Install Python Packages

pip install fastapi uvicorn httpx cachetools psutil


3. Verify Installations

- Ollama:
ollama --version


- Python
python --version



Model Deployment with Ollama
1. Pull the TinyLlama Model
ollama pull tinyllama

2. Start Ollama Server

ollama serve

Keep this terminal open and running.

API Wrapper with FastAPI
1. Clone this repo
git clone <github link>

2. Run the API Server
uvicorn main:app --reload

The API will be available at http://localhost:8000.

Caching Implementation
The code uses an in-memory LRU cache (100 entries) to store prompt-response pairs.

Cache key is an MD5 hash of the prompt.

Cache hits and misses are tracked in the /metrics endpoint.

Performance Metrics
total_requests: Number of /generate requests served

cache_hits: Number of requests served from cache

cache_misses: Number of requests that required LLM inference

average_latency_seconds: Average time per request

memory_usage_mb: Current memory usage of the API process

Access metrics at: http://localhost:8000/metrics



Metrics obtained while testing:

{"total_requests":4,"cache_hits":1,"cache_misses":2,"average_latency_seconds":0.6271,"memory_usage_mb":49.85}

API Endpoints & Usage

![alt text](<API Endpoints.png>)

The prompt in the prompt.json file can be changed.

After changing, run this command in a separate terminal: 

curl.exe -X POST "http://localhost:8000/generate" -H "Content-Type: application/json" -d '@prompt.json'


Testing the API
First request to a new prompt: should be a cache miss (slower).

Repeat the same prompt: should be a cache hit (faster).

Check /metrics: verify that total_requests, cache_hits, and cache_misses update as expected.

Try different prompts to test cache and LLM response variety.

Summary Table

![alt text](<Summary Table.png>)

References
Ollama documentation and API reference

FastAPI official documentation

Community guides on cURL and PowerShell JSON handling