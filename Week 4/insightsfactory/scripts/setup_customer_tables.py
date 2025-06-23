from db_helpers import create_table, execute_query, get_db_connection

def setup_customer_tables():
    """
    Set up the main customer tables in the database
    """
    create_table(
        "customers",
        """
        id SERIAL PRIMARY KEY,
        name VARCHAR(255) NOT NULL UNIQUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        """,
        drop_if_exists=False
    )
    
    create_table(
        "customer_metrics",
        """
        id SERIAL PRIMARY KEY,
        customer_id INTEGER NOT NULL,
        device_alias VARCHAR(255),
        metrics JSONB NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (customer_id) REFERENCES customers(id)
        """,
        drop_if_exists=False
    )
    
    print("All customer tables created successfully")

def setup_customer(customer_name):
    """
    Complete setup for a customer
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Insert customer if not exists
        cursor.execute(
            """
            INSERT INTO customers (name)
            VALUES (%s)
            ON CONFLICT (name) DO NOTHING
            RETURNING id
            """,
            [customer_name]
        )
        
        result = cursor.fetchone()
        if result:
            customer_id = result[0]
        else:
            # Get ID if customer already existed
            cursor.execute("SELECT id FROM customers WHERE name = %s", [customer_name])
            customer_id = cursor.fetchone()[0]
        
        conn.commit()
        
        print(f"Customer {customer_name} (ID: {customer_id}) setup complete")
        return customer_id
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Error setting up customer: {e}")
        raise
    finally:
        if conn:
            cursor.close()
            conn.close()

def get_customer_id(customer_name):
    """
    Get customer id from the customers table
    """
    print(customer_name)
    try:
        result = execute_query(
            "SELECT id FROM customers WHERE name = %s",
            params=[customer_name],
        )
        return result[0][0] if result else None
    except Exception as e:
        print(f"Error getting customer id: {e}")
        return None
          
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Customer database management utility')
    
    parser.add_argument('--command', choices=['setup', 'add_customer'], 
                        help='Command to execute')
    parser.add_argument('--name', help='Customer name')
    
    args = parser.parse_args()
    
    if args.command == 'setup':
        setup_customer_tables()
    
    elif args.command == 'add_customer':
        if not args.name:
            print("Error: --name is required for add_customer command")
            parser.print_help()
            exit(1)
        setup_customer(args.name)
    
    else:
        parser.print_help()