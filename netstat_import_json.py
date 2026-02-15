import mysql.connector
import json
import uuid
from datetime import datetime

# Load credentials from JSON
with open("myconfig/dbconfig.json", "r") as file:
    config = json.load(file)


import_file_name = input("Enter the JSON file name to import (e.g., files/filename.json): ")


# Load JSON data    
with open(import_file_name) as f:
    netstat_data = json.load(f)



# Generate unique snapshot ID
snapshot_id = str(uuid.uuid4())
    
try:
    conn = mysql.connector.connect(
        host=config["host"],
        user=config["username"],
        password=config["password"],
        database=config["database"]
    )

    if conn.is_connected():
        print("DB Connected successfully!")
        
        cursor = conn.cursor()

        sql = """
            INSERT INTO netstat_logs 
            (snapshot_id, protocol, local_address, foreign_address, state, pid)
            VALUES (%s, %s, %s, %s, %s, %s)
        """

        values_list = [
            (
                snapshot_id,
                entry.get("protocol"),
                entry.get("local_address"),
                entry.get("foreign_address"),
                entry.get("state"),
                entry.get("pid")
            )
            for entry in netstat_data
        ]

        cursor.executemany(sql, values_list)
        conn.commit()

        print(f"Inserted {cursor.rowcount} records")
        print(f"Snapshot ID: {snapshot_id}")

except mysql.connector.Error as e:
    print("Db Error:", e)

finally:
    if 'conn' in locals() and conn.is_connected():
        conn.close()
        print("Connection closed.")    