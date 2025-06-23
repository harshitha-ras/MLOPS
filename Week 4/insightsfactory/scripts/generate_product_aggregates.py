import pandas as pd
import numpy as np
import argparse
import json
import os

from db_helpers import create_view, get_db_connection
from setup_customer_tables import get_customer_id

# metrics expects format like: {'device_age': [('avg_age', 'mean'), ('max_age', 'max')]}
# where you have a column along with the aggregations that you want
def analyze_metrics(df, group_by='device_alias', metrics=None):

    grouped = df.groupby(group_by)
    
    result = pd.DataFrame(index=grouped.groups.keys())
    result.index.name = group_by
    result = result.reset_index()
    
    for col, operations in metrics.items():
        for operation in operations:
            # it expects tuples here but the input format made it a list, maybe a better way of going about this
            if isinstance(operation, (list, tuple)) and len(operation) == 2:
                name, func = operation
                
                if isinstance(func, str):
                    # can add arbitrary named functions here for customizability, although 
                    # most of the general ones already exist
                    if func == 'count_distinct':
                        temp_result = grouped[col].nunique()
                    else:
                        temp_result = grouped[col].agg(func)
                else:
                    temp_result = grouped[col].agg(func)
                
                result[name] = temp_result.values
    
    # Round numeric columns
    for col in result.columns:
        if result[col].dtype in [np.float64, np.float32]:
            result[col] = result[col].round(2)
    
    return result

def load_data(date_from=None, 
              date_to=None, input_table='merged_data'):
    """
    Load data from either a CSV file or database table
    """
    # Read from database
    try:
        query = f"SELECT * FROM {input_table}"
        
        # Add date filtering if provided
        date_filters = []
        params = []
        
        if date_from:
            date_filters.append("created_date >= %s")
            params.append(date_from)
            
        if date_to:
            date_filters.append("created_date <= %s")
            params.append(date_to)
            
        if date_filters:
            query += " AND " + " AND ".join(date_filters)
        
        # Read into pandas DataFrame
        conn = get_db_connection()
        df = pd.read_sql_query(query, conn, params=params)
        conn.close()
            
        return df
        
    except Exception as e:
        print(f"Error reading data: {e}")
        raise

def save_metrics_to_db(customer_id, results_df):
    """
    Save metrics results to the customer_metrics table
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # todo should prob change this to an updated at
        cursor.execute(
            "DELETE FROM customer_metrics WHERE customer_id = %s",
            [customer_id]
        )
        
        rows_inserted = 0
        for _, row in results_df.iterrows():
            device_alias = row['device_alias']
            
            metrics_dict = {col: row[col] for col in results_df.columns if col != 'device_alias'}
            
            cursor.execute(
                """
                INSERT INTO customer_metrics 
                (customer_id, device_alias, metrics, created_at) 
                VALUES (%s, %s, %s, CURRENT_TIMESTAMP)
                """,
                [customer_id, device_alias, json.dumps(metrics_dict)]
            )
            rows_inserted += 1
            
        cursor.execute(
            """
            UPDATE customers 
            SET updated_at = CURRENT_TIMESTAMP 
            WHERE id = %s
            """,
            [customer_id]
        )
        
        conn.commit()
        print(f"Saved {rows_inserted} rows")
        return rows_inserted
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Error saving metrics: {e}")
        raise
    finally:
        if conn:
            cursor.close()
            conn.close()

def create_customer_metrics_view(customer_id, output, metrics_list):
    """
    Create a view for a specific customer's metrics
    """
    # Format customer name for view name (lowercase, no spaces)
    view_name = f"{output.lower().replace(' ', '_')}"
    
    metric_selections = []
    for metric in metrics_list:
        metric_selections.append(f"(metrics->>'{metric}')::numeric AS {metric}")
    
    select_query = f"""
    SELECT 
        id,
        customer_id,
        device_alias,
        created_at,
        {', '.join(metric_selections)}
    FROM customer_metrics
    WHERE customer_id = {customer_id}
    """
    
    return create_view(view_name, select_query)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run product analysis')
    
    parser.add_argument('--input_table', type=str, 
                        help='Input table name')
    
    parser.add_argument('--customer_id', type=str,
                        help='Customer ID')
    
    parser.add_argument('--metrics', '-m', type=str,
                        help='JSON string with metrics specification')
    
    parser.add_argument('--output_table', '-o', type=str, 
                        help='Name to save output metrics table view')
    
    parser.add_argument('--from_date', type=str, help='Start date for filtering data (format: YYYY-MM-DD)')
    parser.add_argument('--to_date', type=str, help='End date for filtering data (format: YYYY-MM-DD)')

    args = parser.parse_args()

    df = load_data(args.from_date, args.to_date, args.input_table)
    
    metrics = None

    if args.metrics:
        try:
            # some formatting issues here, this resolves for nowbut will adjust later
            metrics_str = args.metrics
            if metrics_str.startswith('"') and metrics_str.endswith('"'):
                metrics_str = metrics_str[1:-1]
            elif metrics_str.startswith("'") and metrics_str.endswith("'"):
                metrics_str = metrics_str[1:-1]
            
            metrics = json.loads(metrics_str)
        except json.JSONDecodeError as e:
            print(f"JSON Error: {str(e)}")
            exit(1)
    
    if metrics is None:
        print(f"No metrics to aggregate over: {str(e)}")
        exit(1)

    results = analyze_metrics(df, 'device_alias', metrics)
    metric_columns = [col for col in results.columns if col != 'device_alias']
    
    customer_id = get_customer_id(args.customer_id)
    if not customer_id:
        print(f"Could not find customer with ID {args.customer_id}")
        customer_name = f"customer_{args.customer_id}"

    save_metrics_to_db(customer_id, results)
    view_name = create_customer_metrics_view(customer_id, args.output_table, metric_columns)