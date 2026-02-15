import json

def parse_netstat_file(file_path):
    data = []

    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    for line in lines:
        line = line.strip()

        # Skip headers or empty lines
        if not line or line.startswith("Active") or line.startswith("Proto"):
            continue

        parts = line.split()

        # Handle TCP lines (with State column)
        if parts[0] == "TCP":
            if len(parts) >= 5:
                entry = {
                    "protocol": parts[0],
                    "local_address": parts[1],
                    "foreign_address": parts[2],
                    "state": parts[3],
                    "pid": parts[4]
                }
                data.append(entry)

        # Handle UDP lines (no State column)
        elif parts[0] == "UDP":
            if len(parts) >= 4:
                entry = {
                    "protocol": parts[0],
                    "local_address": parts[1],
                    "foreign_address": parts[2],
                    "state": None,
                    "pid": parts[3]
                }
                data.append(entry)

    return data


# === Usage ===
file_path = input("file name: ")
parsed_data = parse_netstat_file(file_path)

# Convert to JSON
json_output = json.dumps(parsed_data, indent=4)

# Save to file
with open("data/netstat.json", "w", encoding="utf-8") as f:
    f.write(json_output)

print("✅ Converted successfully to netstat.json")
