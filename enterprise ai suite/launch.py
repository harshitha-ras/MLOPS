import subprocess
import threading
import os

def run_fastapi():
    subprocess.run(["uvicorn", "step5_local_llm_service.main:app", "--host", "127.0.0.1", "--port", "8000"])

def run_streamlit():
    env = os.environ.copy()
    env["PYTHONPATH"] = os.getcwd()
    subprocess.run(["streamlit", "run", "step1_secure_chat/app.py"], env=env)


def run_cli():
    subprocess.run(["python", "step4_ai_cli_tool/cli.py", "--prompt", "Hello", "--user", "cli_user"])

if __name__ == "__main__":
    print("[*] Launching SmartEnterprise AI Suite...")

    t1 = threading.Thread(target=run_fastapi)
    t2 = threading.Thread(target=run_streamlit)
    t3 = threading.Thread(target=run_cli)

    t1.start()
    t2.start()
    t3.start()

    t1.join()
    t2.join()
    t3.join()
