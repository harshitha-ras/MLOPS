Enterprise AI Suite
=========================
An enterprise-grade, fully local AI platform built with open-source tools.
Designed for responsible AI use, real-time interaction, and end-to-end traceability.

--------------------------
System Components
--------------------------

1. Secure Chat UI (Streamlit)
   - Role-based login system
   - Multi-user real-time chat interface
   - Sends prompts to local LLM backend

2. Local LLM Service (FastAPI + ctransformers)
   - Uses TinyLlama 1.1B GGUF model
   - CPU-only
   - Caching, filtering, privacy, and audit logging enabled

3. CLI Tool
   - Terminal-based access to LLM
   - Reuses the same API backend
   - Fully auditable

4. Analytics Dashboard
   - Visualizes system usage
   - Parses audit logs in real-time
   - Shows safe vs unsafe prompt metrics

5. Responsible AI Layer
   - Prompt filtering + content sanitization
   - Privacy redaction (emails, phone numbers)
   - JSONL audit logging for every interaction

--------------------------
How to Run Everything
--------------------------

0. Prerequisites:
   - Python 3.8+
   - `pip install -r step5_local_llm_service/requirements.txt`
   - Download GGUF model file:
     → Place it in `step5_local_llm_service/models/`

1. Launch entire system:
   > python launch.py

   - This runs:
     - LLM API backend
     - Chat UI in browser
     - CLI tool in terminal

2. Access UI:
   - Chat App: http://localhost:8501
   - CLI: Type prompts directly in terminal
   - API Docs (Optional): http://localhost:8000/docs

--------------------------
Directory Overview
--------------------------

smartenterprise_ai_suite/
├── step1_secure_chat/           # Chat UI
├── step2_analytics_dashboard/   # Usage visualization
├── step3_textgen_api/           # (Mock legacy)
├── step4_cli_tool/              # CLI interface
├── step5_local_llm_service/     # API + LLM (ctransformers)
├── step6_responsible_ai/        # Filters, audits, privacy
├── launch.py                    # System launcher
└── README.txt                   # (This file)

--------------------------
Model Info
--------------------------

- Model: TinyLlama-1.1B-Chat-v1.0.Q4_K_M.gguf
- Format: GGUF (CPU-only)
- Inference Library: `ctransformers`
- Approx Size: 420MB
- Response Speed: ~5–10 tokens/sec

--------------------------
Responsible AI Features
--------------------------

- Unsafe prompt blocking
- Output sanitization
- PII redaction
- Full audit logging
- Local-only inference
- Dashboard for transparency

--------------------------
License / Usage: MIT
--------------------------

This project is for educational and internal enterprise use only.
All models and libraries used are open-source and self-hosted.

Ensure responsible and lawful usage in accordance with AI safety best practices.

--------------------------
Author: Harshitha Rasamsetty
--------------------------
