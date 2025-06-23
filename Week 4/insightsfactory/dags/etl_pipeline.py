from airflow import DAG
from airflow.operators.python import PythonOperator, ShortCircuitOperator
from airflow.operators.bash import BashOperator
from datetime import datetime
import subprocess
import os
import logging
from airflow import Dataset
from dotenv import load_dotenv
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from scripts.db_helpers import execute_query
load_dotenv()  # Load variables from .env file, just need to add in a variable for BITBUCKET_ACCESS_TOKEN, which you can generate from bitbucket

REPO_OWNER = 'dentsply'
REPO_NAME = 'insightsfactory' 
PERSONAL_ACCESS_TOKEN = os.getenv("BITBUCKET_ACCESS_TOKEN")
CLONE_PATH = '/opt/airflow/repo' 

# Ensure logging is configured
logging.basicConfig(level=logging.INFO)

# Define the merged data dataset
merged_data = Dataset("postgres://airflow/airflow/public/merged_data")

def clone_or_pull_repo():
    """
    Clone or pull a private repository using a personal access token
    """
    # Construct the repository URL with token
    repo_url = f'https://x-token-auth:{PERSONAL_ACCESS_TOKEN}@bitbucket.org/{REPO_OWNER}/{REPO_NAME}.git'
    
    logging.info(f"Checking repository at {CLONE_PATH}")
    
    try:
        if not os.path.exists(CLONE_PATH):
            # Repository doesn't exist, clone it
            logging.info(f"Cloning private repository")
            subprocess.run([
                'git', 'clone', repo_url, CLONE_PATH
            ], check=True)
            
            # Additionally pull LFS files
            logging.info("Fetching LFS files")
            subprocess.run([
                'git', '-C', CLONE_PATH, 'lfs', 'pull'
            ], check=True)
            
        else:
            # Repository exists, pull latest changes
            logging.info("Pulling latest changes")
            subprocess.run([
                'git', '-C', CLONE_PATH, 'pull'
            ], check=True)

            logging.info("Fetching LFS files")
            subprocess.run([
                'git', '-C', CLONE_PATH, 'lfs', 'pull'
            ], check=True)

        # List contents to verify
        logging.info("Repository contents:")
        subprocess.run(['ls', '-la', CLONE_PATH], check=True)

    except subprocess.CalledProcessError as e:
        logging.error(f"Git operation failed: {e}")
        raise

def new_data_available():
    """
    Check if new data files are available and up to date.
    Return True if either file is more recent than the last database update.
    """
    # Use the cloned repository path as the base directory
    files_to_check = [
        os.path.join(CLONE_PATH, "Ticket Details.xlsx"),
        os.path.join(CLONE_PATH, "Device List.xlsx")
    ]

    MAX_UPDATED_AT_QUERY = """
    SELECT 
        MAX(updated_at) AS latest_update
    FROM customers
    """
    result = execute_query(MAX_UPDATED_AT_QUERY)
    latest_update = result[0][0] if result else None
    logging.info(f"Last modified in db: {latest_update}")
    
    new_data_found = False
    
    for filepath in files_to_check:
        logging.info(f"Checking file: {filepath}")
        
        if not os.path.exists(filepath):
            logging.error(f"Missing file: {filepath}")
            return False
        
        mod_date = datetime.fromtimestamp(os.path.getmtime(filepath))
        logging.info(f"{os.path.basename(filepath)} last modified: {mod_date}")

        if latest_update is None or mod_date > latest_update:
            logging.info(f"File {filepath} has new data")
            new_data_found = True
    
    return new_data_found

def run_clean_and_merge():    
    """
    Run the data cleaning and merging script from the cloned repo
    """
    subprocess.run(
        ["python",  "scripts/datacleaning.py"], 
        check=True)

def run_load_to_postgres():
    """
    Run the script to load data to PostgreSQL from the cloned repo
    """
    
    subprocess.run(
        ["python", "scripts/db.py"], 
        check=True
    )

# Install dependencies task - can move into the docker setup
install_dependencies = BashOperator(
    task_id='install_dependencies',
    bash_command='pip install openpyxl'
)

# Create the DAG
with DAG(
    "customer_etl_pipeline",
    start_date=datetime(2025, 3, 31),
    schedule_interval='*/5 * * * *',  #make this lower for demos
    catchup=False
) as dag:
    # Clone or pull repository task
    clone_pull_task = PythonOperator(
        task_id='clone_or_pull_private_repository',
        python_callable=clone_or_pull_repo
    )

    # Check for new data
    check_data = ShortCircuitOperator(
        task_id="check_new_data",
        python_callable=new_data_available
    )

    # Clean and merge data
    clean_merge = PythonOperator(
        task_id="clean_and_merge",
        python_callable=run_clean_and_merge
    )

    # Load data to PostgreSQL
    load_postgres = PythonOperator(
        task_id="load_to_postgres",
        python_callable=run_load_to_postgres,
        outlets=[merged_data]  
    )

    install_dependencies >> clone_pull_task >> check_data >> clean_merge >> load_postgres