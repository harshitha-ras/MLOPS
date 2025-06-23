import os
import json
import yaml
import subprocess
import argparse
import logging
import glob

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def load_customer_config(customer_id):
    config_path = f"configs/{customer_id}.yaml"
    
    if not os.path.exists(config_path):
        logging.error(f"Configuration file not found: {config_path}")
        return None
    
    with open(config_path, 'r') as file:
        try:
            return yaml.safe_load(file)
        except yaml.YAMLError as e:
            logging.error(f"Error parsing YAML configuration: {e}")
            return None

def list_available_customers():
    config_files = glob.glob("configs/*.yaml")
    customers = []
    
    for config_file in config_files:
        customer_id = os.path.basename(config_file).replace('.yaml', '')
        # Load the config to get the name
        with open(config_file, 'r') as file:
            try:
                config = yaml.safe_load(file)
                customers.append((customer_id, config.get('name', customer_id)))
            except yaml.YAMLError:
                customers.append((customer_id, customer_id))
    
    return customers

def run_pipeline(customer_id):    
    customer = load_customer_config(customer_id)
    if not customer:
        return False
    
    logging.info(f"Running pipeline for {customer['name']}")
    
    for step in customer["steps"]:
        output = step["args"].get("output")
        if output:
            output_dir = os.path.dirname(output)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir, exist_ok=True)
    
    for i, step in enumerate(customer["steps"]):
        script = step["script"]
        args = step["args"].copy()  
        
        # Handle special case for metrics - TODO: update so this isn't needed
        if "metrics" in args and isinstance(args["metrics"], dict):
            args["metrics"] = json.dumps(args["metrics"])
            logging.info("Converted metrics dictionary to JSON string")
        
        cmd = ["python", script]
        for arg_name, arg_value in args.items():
            if len(arg_name) == 1:
                cmd.append(f"-{arg_name}")
            else:
                cmd.append(f"--{arg_name}")
            
            if arg_value is not None:
                cmd.append(str(arg_value))
        
        cmd_str = " ".join(cmd)
        
        logging.info(f"Step {i+1}: Executing: {cmd_str}")
        try:
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            logging.info(f"Step {i+1}: Completed successfully")
            if result.stdout.strip():
                logging.info(f"Output: {result.stdout.strip()}")
        except subprocess.CalledProcessError as e:
            logging.error(f"Step {i+1}: Failed with error code {e.returncode}")
            logging.error(f"Error output: {e.stderr}")
            return False
            
    logging.info(f"Pipeline completed for {customer['name']}")
    return True

def display_customers():
    customers = list_available_customers()
    
    if not customers:
        print("No customer configurations found in configs/ directory")
        return
    
    print("\nAvailable customers:")
    for customer_id, name in customers:
        print(f"  - {customer_id}: {name}")
    print("\nUse --customer <id> to run a specific customer pipeline")

def main():
    """Main entry point for the pipeline"""
    parser = argparse.ArgumentParser(description="Run pipeline for specific customer")
    
    parser.add_argument("--customer", "-c", type=str,
                        help="Customer ID to run pipeline for")
    
    parser.add_argument("--list", "-l", action="store_true",
                        help="List all available customers")
    
    args = parser.parse_args()
    
    if args.list:
        display_customers()
        return
    
    if args.customer:
        run_pipeline(args.customer)
    else:
        parser.print_help()
        display_customers()

if __name__ == "__main__":
    main()