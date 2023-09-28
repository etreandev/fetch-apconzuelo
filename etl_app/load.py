from typing import List, Dict, Any, Optional
from datetime import datetime
import psycopg2
from psycopg2.extras import execute_values

# Function to insert records into the 'user_logins' table in the Postgres database
def load_messages(messages, connection_params):
    # SQL query to insert records into the 'user_logins' table
    insert_query = """
    INSERT INTO user_logins (
        user_id,
        device_type,
        masked_ip,
        masked_device_id,
        locale,
        app_version,
        create_date
    ) VALUES %s;
""" 

    # Connect to the Postgres database
    with psycopg2.connect(**connection_params) as conn:
        with conn.cursor() as cur:
            # Execute the insert query with the records as tuples
            execute_values(cur, insert_query, messages)
        # Commit the transaction
        conn.commit()
