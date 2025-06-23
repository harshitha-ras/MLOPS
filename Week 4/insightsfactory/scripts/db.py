import psycopg2
import pandas as pd
from io import StringIO

DB_CONFIG = {
    "dbname": "postgres",
    "user": "dbadmin",
    "password": "Pooh@2828JF",
    "host": "mydb-capstone-v14.postgres.database.azure.com",
    "port": "5432",
    "sslmode": "require"
}

def create_table():
    """Drops and creates the merged table in PostgreSQL."""
    query = """
    DROP TABLE IF EXISTS merged_data;
    
    CREATE TABLE merged_data (
        transaction_number VARCHAR(100) PRIMARY KEY,
        product_key VARCHAR(100),
        device_alias VARCHAR(200),
        fix_flag VARCHAR(255),
        record_type VARCHAR(255),
        oob_or_not VARCHAR(255),
        oob_status VARCHAR(255),
        created_date TIMESTAMP,
        solved_at_date TIMESTAMP,
        days_to_resolve BIGINT,
        days_to_resolve_bucket VARCHAR(255),
        category_level1 VARCHAR(255),
        category_level2 VARCHAR(255),
        category_level3 VARCHAR(255),
        category_level4 VARCHAR(255),
        estimated_installation_date TIMESTAMP,
        device_age BIGINT
    )"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        cur.execute(query)
        conn.commit()
        cur.close()
        conn.close()
        print("Table created successfully.")
    except Exception as e:
        print("Error creating table:", e)

def insert_data(data_path):
    """Inserts cleaned merged CSV data into PostgreSQL."""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        df = pd.read_csv(data_path)
        
        df.columns = [col.lower().replace(" ", "_") for col in df.columns]

        df.replace(r'^\s*$', None, regex=True, inplace=True)

        datetime_columns = ["created_date", "solved_at_date", "estimated_installation_date"]
        for col in datetime_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors="coerce")
                df[col] = df[col].apply(lambda x: x.strftime("%Y-%m-%d %H:%M:%S") if pd.notna(x) else None)

        columns = ", ".join(df.columns)
        values = ", ".join(["%s" for _ in df.columns])
        insert_query = f"INSERT INTO merged_data ({columns}) VALUES ({values}) ON CONFLICT DO NOTHING"
        
        for row in df.itertuples(index=False, name=None):
            cur.execute(insert_query, tuple(row))
        
        conn.commit()
        cur.close()
        conn.close()
        print("Data inserted into merged_data successfully.")
    except Exception as e:
        print("Error inserting data:", e)

def insert_data_with_copy(data_path):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        df = pd.read_csv(data_path)
        
        buffer = StringIO()
        df.to_csv(buffer, header=False, index=False, sep=',', na_rep='\\N')
        buffer.seek(0)
        
        cur.copy_expert(f"COPY merged_data ({','.join(df.columns)}) FROM STDIN WITH CSV", buffer)
        
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    create_table()
    insert_data_with_copy("Cleaned_Merged_Data.csv")
