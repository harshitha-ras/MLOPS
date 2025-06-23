from airflow import DAG
from airflow.operators.python import PythonOperator, ShortCircuitOperator
from datetime import datetime
import subprocess
import os

def git_pull_latest():
    repo_dir = os.path.dirname(__file__)
    
    # Replace with your actual Bitbucket username and app password
    username = "JesseFWarren"
    app_password = "ATBBJuYZswqDt3e2WaW8NWjuAPrkB66ABB0C"
    
    remote_url = f"https://{username}:{app_password}@bitbucket.org/dentsply/insightsfactory.git"
    
    # Reset remote to include credentials just for this pull
    subprocess.run(["git", "-C", repo_dir, "remote", "set-url", "origin", remote_url], check=True)
    subprocess.run(["git", "-C", repo_dir, "pull"], check=True)

def new_data_available():
    base_dir = os.path.dirname(__file__)
    files_to_check = [
        os.path.join(base_dir, "Ticket Details.xlsx"),
        os.path.join(base_dir, "Device List.xlsx")
    ]

    today = datetime.today().date()

    for filepath in files_to_check:
        if not os.path.exists(filepath):
            print(f"Missing file: {filepath}")
            return False
        
        mod_date = datetime.fromtimestamp(os.path.getmtime(filepath)).date()
        print(f"{os.path.basename(filepath)} last modified: {mod_date}")

        if mod_date != today:
            return False

    return True

def run_clean_and_merge():
    subprocess.run(["python", "datacleaning.py"], check=True)

def run_load_to_postgres():
    subprocess.run(["python", "db.py"], check=True)

with DAG("customer_etl_pipeline",
         start_date=datetime(2025, 3, 31),
         schedule_interval="@daily",  # change for testing
         catchup=False) as dag:

    pull_repo = PythonOperator(
        task_id="pull_latest_repo",
        python_callable=git_pull_latest
    )

    check_data = ShortCircuitOperator(
        task_id="check_new_data",
        python_callable=new_data_available
    )

    clean_merge = PythonOperator(
        task_id="clean_and_merge",
        python_callable=run_clean_and_merge
    )

    load_postgres = PythonOperator(
        task_id="load_to_postgres",
        python_callable=run_load_to_postgres
    )

    pull_repo >> check_data >> clean_merge >> load_postgres