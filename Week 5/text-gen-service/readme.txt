Generative AI Text Generation API
A secure, monitored, and content-filtered API for text generation using a state-of-the-art language model.

Table of Contents
Overview

Features

Setup

API Key & Security

API Endpoints

POST /generate

GET /metrics

Usage Examples

Content Filtering

Usage Monitoring

API Documentation

Notes & Recommendations

Overview
This project provides a RESTful API for generating text using the DistilGPT2 language model. The API includes:

Content filtering for safety

Usage monitoring and metrics

API key authentication and rate limiting

Auto-generated interactive API documentation

Features
Text Generation: Generate text from prompts using a modern transformer model.

Content Filtering: Blocks unsafe or inappropriate content.

Usage Monitoring: Tracks total, successful, and blocked requests.

Security: API key authentication and per-IP rate limiting.

Documentation: Interactive OpenAPI docs at /docs.

Setup
Clone the repository:

bash
git clone <your-repo-url>
cd <your-project-folder>
Install dependencies:

bash
pip install fastapi uvicorn transformers
Configure your API key:

Open main.py.

Set a secure value for the API_KEY variable:

python
API_KEY = "your-own-secret-key"
Run the API server:

bash
uvicorn main:app --reload
Access the API docs:
Open http://localhost:8000/docs in your browser.

API Key & Security
API Key: All endpoints require the X-API-Key header.

Rate Limiting: Each IP is limited to 5 requests per minute to /generate.

Change the API Key: Edit the API_KEY variable in main.py to your own secure string.

API Endpoints
POST /generate
Generate text from a prompt.

URL: /generate

Method: POST

Headers:

Content-Type: application/json

X-API-Key: <your-api-key>

Request Body:

json
{
  "text": "Your prompt here",
  "max_length": 50
}
text (string, required): The prompt for text generation.

max_length (int, optional): Maximum length of output (default: 50).

Responses:

200 OK:

json
{
  "generated_text": "Generated text here..."
}
400 Bad Request: Content blocked by safety filter.

401 Unauthorized: Invalid or missing API key.

429 Too Many Requests: Rate limit exceeded.

500 Internal Server Error: Generation error.

GET /metrics
Get API usage metrics.

URL: /metrics

Method: GET

Headers:

X-API-Key: <your-api-key>

Response:

json
{
  "total_requests": 10,
  "blocked_requests": 2,
  "successful_requests": 8
}
Usage Examples
Generate Text with cURL:

bash
curl -X POST "http://localhost:8000/generate" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-own-secret-key" \
  -d '{"text": "Once upon a time", "max_length": 50}'
Get Metrics with cURL:

bash
curl -X GET "http://localhost:8000/metrics" \
  -H "X-API-Key: your-own-secret-key"
Content Filtering
The API checks generated text for unsafe or inappropriate words.

If unsafe content is detected, the response is blocked and a 400 error is returned.

The filter is basic (keyword-based) but can be extended with more advanced models.

Usage Monitoring
The API tracks:

total_requests: All requests received.

blocked_requests: Requests blocked due to unsafe content.

successful_requests: Requests that returned generated text.

Metrics are available at the /metrics endpoint.

API Documentation
Interactive Docs: http://localhost:8000/docs

OpenAPI Schema: http://localhost:8000/openapi.json

The docs include all endpoints, parameters, and example requests/responses.

Notes & Recommendations
Production Use: For real-world deployment, use HTTPS, store API keys securely, and consider persistent logging.

Content Filtering: For advanced content moderation, integrate third-party APIs or machine learning classifiers.

Scalability: For high-traffic scenarios, use a database for metrics and a distributed rate limiter.