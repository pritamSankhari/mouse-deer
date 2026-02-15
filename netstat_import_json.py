import mysql.connector
import json
import uuid
from datetime import datetime
import sys
import requests


# ----------------------------
# Load DB config
# ----------------------------
def load_config(path="myconfig/dbconfig.json"):
    with open(path, "r") as file:
        return json.load(file)


# ----------------------------
# Load JSON data
# ----------------------------
def load_json(file_path):
    with open(file_path, "r") as f:
        data = json.load(f)

    if not isinstance(data, list) or not data:
        raise ValueError("Invalid or empty JSON file")

    return data


# ----------------------------
# DB Connection
# ----------------------------
def get_connection(config):
    return mysql.connector.connect(
        host=config["host"],
        user=config["username"],
        password=config["password"],
        database=config["database"]
    )


# ----------------------------
# Extract IP from address
# ----------------------------
def extract_ip(address):
    if not address:
        return None

    ip = address.split(":")[0]

    if ip.startswith("127.") or ip.startswith("0.0.0.0"):
        return None

    return ip


# ----------------------------
# Get IP Info from API
# ----------------------------
def get_ip_info(ip):
    try:
        response = requests.get(f"http://ip-api.com/json/{ip}", timeout=5)
        data = response.json()

        if data["status"] == "success":
            return {
                "country": data.get("country"),
                "isp": data.get("isp"),
                "org": data.get("org")
            }
    except Exception:
        return None

    return None


# ----------------------------
# Store IP Intelligence
# ----------------------------
def store_ip_intelligence(cursor, ip, snapshot_id):
    # Check if exists
    cursor.execute("SELECT id FROM ip_intelligence WHERE ip_address=%s AND snapshot_id=%s", (ip, snapshot_id))
    if cursor.fetchone():
        return

    info = get_ip_info(ip)

    if info:
        sql = """
            INSERT INTO ip_intelligence
            (ip_address, country, isp, org, snapshot_id)
            VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(sql, (
            ip,
            info["country"],
            info["isp"],
            info["org"],
            snapshot_id         
        ))
        print(f"IP Enriched: {ip} ({info['country']})")


# ----------------------------
# Main
# ----------------------------
def main():
    config = load_config()
    file_name = input("Enter JSON file name: ")
    netstat_data = load_json(file_name)

    snapshot_id = str(uuid.uuid4())
    snapshot_time = datetime.now()
    total_records = len(netstat_data)

    try:
        conn = get_connection(config)
        cursor = conn.cursor()
        conn.start_transaction()

        # Insert snapshot
        cursor.execute("""
            INSERT INTO netstat_snapshots
            (snapshot_id, created_at, total_records)
            VALUES (%s, %s, %s)
        """, (snapshot_id, snapshot_time, total_records))

        # Insert logs
        log_sql = """
            INSERT INTO netstat_logs
            (snapshot_id, protocol, local_address, foreign_address, state, pid)
            VALUES (%s, %s, %s, %s, %s, %s)
        """

        values = []
        unique_ips = set()

        for entry in netstat_data:
            foreign_address = entry.get("foreign_address")
            ip = extract_ip(foreign_address)

            if ip:
                unique_ips.add(ip)

            values.append((
                snapshot_id,
                entry.get("protocol"),
                entry.get("local_address"),
                foreign_address,
                entry.get("state"),
                entry.get("pid")
            ))

        cursor.executemany(log_sql, values)

        # Enrich IPs
        for ip in unique_ips:
            store_ip_intelligence(cursor, ip, snapshot_id)

        conn.commit()

        print("================================")
        print("Snapshot ID:", snapshot_id)
        print("Logs Inserted:", len(values))
        print("Unique External IPs:", len(unique_ips))
        print("================================")

    except Exception as e:
        conn.rollback()
        print("Error:", e)

    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()
            print("Connection closed.")


if __name__ == "__main__":
    main()
