import os
import pandas as pd
import psycopg2
import json

# maybe we should move to an env file or something at some point
DB_CONFIG = {
    "dbname": "postgres",
    "user": "dbadmin",
    "password": "Pooh@2828JF",
    "host": "mydb-capstone-v14.postgres.database.azure.com",
    "port": "5432",
    "sslmode": "require"
}

def get_db_connection():
    """
    Create and return a database connection
    """
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        print(f"Database connection error: {e}")
        raise

def execute_query(query, params=None):
    """
    Execute a database query to our shared DB
    """
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        
        if query.strip().upper().startswith(('SELECT', 'SHOW', 'DESCRIBE')):
            result = cursor.fetchall()
            return result
        else:
            conn.commit()
            return cursor.rowcount
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Query execution error: {e}")
        raise
    finally:
        if conn:
            cursor.close()
            conn.close()

def create_table(table_name, columns_definition, drop_if_exists=False):
    """
    Create a table with the specified structure
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        # for refreshing the table
        if drop_if_exists:
            cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
        
        create_query = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            {columns_definition}
        )
        """
        cursor.execute(create_query)
        conn.commit()
        print(f"Table {table_name} created successfully.")
        return True
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Error creating table {table_name}: {e}")
        raise
    finally:
        if conn:
            cursor.close()
            conn.close()

def create_view(view_name, select_query, replace_if_exists=True):
    """
    Create a view for the specified query
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        create_or_replace = "CREATE OR REPLACE" if replace_if_exists else "CREATE"
        
        create_query = f"""
        {create_or_replace} VIEW {view_name} AS
        {select_query}
        """
        cursor.execute(create_query)
        conn.commit()
        print(f"View {view_name} created successfully.")
        return True
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Error creating view {view_name}: {e}")
        raise
    finally:
        if conn:
            cursor.close()
            conn.close()


def insert_dataframe(df, table_name, if_exists='append', chunk_size=1000):
    """
    Insert a pandas DataFrame into a PostgreSQL table
    """
    try:
        conn = get_db_connection()
        
        # Replace empty strings with None
        df = df.replace(r'^\s*$', None, regex=True)
        
        # Convert any datetime columns to proper format
        datetime_cols = df.select_dtypes(include=['datetime64']).columns
        for col in datetime_cols:
            df[col] = pd.to_datetime(df[col], errors='coerce')
            df[col] = df[col].apply(lambda x: x.strftime("%Y-%m-%d %H:%M:%S") if pd.notna(x) else None)
        
        # Use pandas' to_sql for insertion
        df.to_sql(
            name=table_name,
            con=conn.connection,
            if_exists=if_exists,
            index=False,
            chunksize=chunk_size
        )
        
        row_count = len(df)
        print(f"Inserted {row_count} rows into {table_name}")
        return row_count
    except Exception as e:
        print(f"Error inserting data: {e}")
        raise
    finally:
        if conn:
            conn.close()

def bulk_insert_csv(file_path, table_name, delimiter=','):
    """
    Bulk insert of CSV file
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        with open(file_path, 'r') as f:
            header = next(f).strip().split(delimiter)
            columns = ','.join(header)
            f.seek(0)
            cursor.copy_expert(
                f"COPY {table_name}({columns}) FROM STDIN WITH CSV HEADER DELIMITER '{delimiter}'",
                f
            )
        
        conn.commit()
        print(f"Bulk inserted data from {file_path} into {table_name}")
        return True
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Error bulk inserting data: {e}")
        raise
    finally:
        if conn:
            cursor.close()
            conn.close()