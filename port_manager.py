import json
import os
from pathlib import Path
from typing import Optional

PORT_ASSIGNMENTS_FILE = Path("port_assignments.json")

def load_port_assignments():
    if PORT_ASSIGNMENTS_FILE.exists():
        try:
            with open(PORT_ASSIGNMENTS_FILE, 'r') as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_port_assignment(service_name: str, port: int):
    assignments = load_port_assignments()
    assignments[service_name] = port
    with open(PORT_ASSIGNMENTS_FILE, 'w') as f:
        json.dump(assignments, f, indent=2)

def get_last_assigned_port(service_name: str) -> Optional[int]:
    assignments = load_port_assignments()
    return assignments.get(service_name)

# Example usage:
# save_port_assignment('api_bridge', 8002)
# last_port = get_last_assigned_port('api_bridge') 