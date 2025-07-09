import json
import os
from pathlib import Path
from typing import Optional
import socket

PORT_ASSIGNMENTS_FILE = Path("port_assignments.json")

def find_available_port(start_port: int, host: str = '127.0.0.1') -> int:
    """Finds an available TCP port on the host, starting from start_port."""
    port = start_port
    while True:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex((host, port)) != 0:
                return port
            port += 1

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

# Renaming for clarity and to match usage
def assign_port(service_name: str, port: int):
    """Saves the port assignment for a given service."""
    save_port_assignment(service_name, port)

# Example usage:
# new_port = find_available_port(8000)
# assign_port('api_bridge', new_port)
# last_port = get_last_assigned_port('api_bridge') 