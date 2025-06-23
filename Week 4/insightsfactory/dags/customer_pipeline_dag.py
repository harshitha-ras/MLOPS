# dags/customer_pipeline_dag.py
import logging
import os
import yaml
import json
from datetime import datetime, timedelta
from pathlib import Path

from airflow import DAG, Dataset
from airflow.operators.python import PythonOperator
from airflow.models import Variable
from airflow.utils.task_group import TaskGroup


merged_data = Dataset("postgres://airflow/airflow/public/merged_data")

default_args = {
    'owner': 'analytics',
    'depends_on_past': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    'start_date': datetime(2023, 1, 1),
}

# Path to customer configs
CONFIGS_DIR = Path(os.environ.get('CONFIGS_DIR', 'configs'))

def load_customer_config(customer_id):
    """Load a customer's configuration from YAML file"""
    config_path = CONFIGS_DIR / f"{customer_id}.yaml"
    
    if not config_path.exists():
        raise ValueError(f"Configuration file not found: {config_path}")
    
    with open(config_path, 'r') as file:
        try:
            return yaml.safe_load(file)
        except yaml.YAMLError as e:
            raise ValueError(f"Error parsing YAML configuration: {e}")

def run_script(script_path, script_args=None, **kwargs):
    """Run a Python script with explicitly provided arguments"""
    import subprocess
    import logging
    
    cmd = ["python", script_path]
    
    # Only use arguments explicitly passed in script_args
    if script_args:
        for arg_name, arg_value in script_args.items():
            if arg_value is None:
                continue
            
            # Handle dictionary arguments by converting to JSON
            if isinstance(arg_value, dict):
                arg_value = json.dumps(arg_value)
                logging.info(f"Converted {arg_name} dictionary to JSON string")
            
            # Handle output directory creation
            if arg_name == "output" and arg_value:
                output_dir = os.path.dirname(str(arg_value))
                if output_dir and not os.path.exists(output_dir):
                    os.makedirs(output_dir, exist_ok=True)
            
            # Add argument to command
            if len(arg_name) == 1:
                cmd.append(f"-{arg_name}")
            else:
                cmd.append(f"--{arg_name}")
            
            cmd.append(str(arg_value))
    
    cmd_str = " ".join(cmd)
    logging.info(f"Executing: {cmd_str}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        logging.info(f"Script completed successfully")
        if result.stdout.strip():
            logging.info(f"Output: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        logging.error(f"Script failed with error code {e.returncode}")
        logging.error(f"Error output: {e.stderr}")
        raise Exception(f"Script execution failed: {e.stderr}")

def list_customer_configs():
    """List all available customer config files"""
    return [f.stem for f in CONFIGS_DIR.glob("*.yaml")]

def create_customer_dag(customer_id):
    """Create a DAG for a specific customer based on their config"""
    try:
        customer_config = load_customer_config(customer_id)
        customer_name = customer_config.get('name', customer_id)
        
        dag = DAG(
            dag_id=f'customer_pipeline_{customer_id}',
            default_args=default_args,
            description=f'Pipeline for {customer_name}',
            schedule=[merged_data],  # This will run when merged_data is updated
            catchup=False,
            tags=['customer_pipeline', customer_id],
        )
        
        with dag:
            previous_task = None
            
            # Create a task for each step in the pipeline
            for i, step in enumerate(customer_config["steps"]):
                step_id = f"step_{i+1}"
                script = step["script"]
                
                task = PythonOperator(
                    task_id=step_id,
                    python_callable=run_script,
                    op_kwargs={
                        'script_path': script,
                        'script_args': step["args"],  # Pass args under a separate parameter
                    },
                )
                
                if previous_task:
                    previous_task >> task
                    
                previous_task = task
                
        return dag
    except Exception as e:
        logging.error(f"Failed to create DAG for customer {customer_id}: {str(e)}")
        return None

# Separate dag for each customer
for customer_id in list_customer_configs():
    dag_id = f'customer_pipeline_{customer_id}'
    globals()[dag_id] = create_customer_dag(customer_id)