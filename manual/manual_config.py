import os
import json

def process_manual_connections(connections, base_dir=None):
    """
    Takes a list of database connection dictionaries and writes them
    as a structured JSON config to the user's Desktop.

    Parameters:
    - connections (list): List of dictionaries with DB connection info
    - base_dir (str, optional): Override path for output (used for testing)

    Returns:
    - dict: status, message, and path to the generated config
    """
    structured = []

    for conn in connections:
        structured.append({
            "id": conn.get("connName", "").replace(" ", "_").lower(),
            "software": conn.get("softwareTool", ""),
            "name": conn.get("connName", ""),
            "driver": conn.get("dbType", ""),
            "configuration": {
                "host": conn.get("host", ""),
                "port": int(conn.get("port", 0)),
                "database": conn.get("dbName", ""),
                "user": conn.get("username", ""),
                "password": conn.get("password", "")
            }
        })

    # Determine output location
    if base_dir:
        output_path = os.path.join(base_dir, "db_config.json")
    else:
        desktop = os.path.join(os.path.expanduser("~"), "Desktop")
        os.makedirs(desktop, exist_ok=True)
        output_path = os.path.join(desktop, "db_config.json")

    # Write JSON to file
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(structured, f, indent=2)

    return {
        "status": "success",
        "message": f"Config created on Desktop with {len(structured)} connection(s).",
        "path": output_path
    }
