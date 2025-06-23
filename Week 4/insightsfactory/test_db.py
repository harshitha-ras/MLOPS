import psycopg2

DB_CONFIG = {
    "dbname": "postgres",
    "user": "dbadmin",
    "password": "Pooh@2828JF",
    "host": "mydb-capstone-v14.postgres.database.azure.com",
    "port": "5432",
    "sslmode": "require"
}

def test_connection():
    """Test connection to PostgreSQL and check the merged_data table."""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()

        cur.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'merged_data'
            );
        """)
        table_exists = cur.fetchone()[0]

        if not table_exists:
            print("Table 'merged_data' does NOT exist.")
        else:
            print("Table 'merged_data' exists. Fetching first 10 rows...")

            cur.execute("SELECT * FROM merged_data LIMIT 10;")
            rows = cur.fetchall()

            if not rows:
                print("Table is empty.")
            else:
                for row in rows:
                    print(row)

        cur.close()
        conn.close()
        print("Database connection closed.")

    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    test_connection()
