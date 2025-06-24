import subprocess
import threading
import time
import webbrowser

def run_streamlit_chat():
    subprocess.run(["streamlit", "run", "step1_secure_chat/app.py"])

def run_streamlit_dashboard():
    subprocess.run(["streamlit", "run", "step2_analytics_dashboard/app.py"])

def run_llm_backend():
    subprocess.run(["uvicorn", "step5_local_llm_service.main:app", "--host", "127.0.0.1", "--port", "8000"])

def run_cli_tool():
    subprocess.run(["python", "step4_cli_tool/cli.py"])

if __name__ == "__main__":
    print("[*] Launching SmartEnterprise AI Suite...")

    # LLM API server
    threading.Thread(target=run_llm_backend, daemon=True).start()
    time.sleep(2)

    # Streamlit Chat UI
    threading.Thread(target=run_streamlit_chat).start()

    # CLI Tool (optional)
    threading.Thread(target=run_cli_tool).start()

    # Optional: auto-launch dashboard
    # threading.Thread(target=run_streamlit_dashboard).start()

    # Auto-open chat interface
    time.sleep(3)
    webbrowser.open("http://localhost:8501")

    print("[*] All systems running. Press Ctrl+C to stop.")
