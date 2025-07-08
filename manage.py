#!/usr/bin/env python3
"""
Unified CLI Menu for LinkedIn MCP Project
Use arrow keys to select actions. Replaces batch files for startup and management.
"""
import subprocess
import sys
import questionary
import os
import psutil
import port_manager
import datetime
import time
import requests
import centralized_logging

logger = centralized_logging.get_logger("manage")

def run_command(cmd, shell=False, check_port=None, service_name=None, max_retries=3):
    logger.log_info(f"\n[RUNNING] {cmd}\n{'='*40}")
    attempt = 0
    while attempt < max_retries:
        try:
            result = subprocess.run(cmd, shell=shell, check=True)
            health_ok = True
            if check_port and service_name:
                # Confirm service is running and healthy
                import socket
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                try:
                    s.settimeout(3)
                    s.connect(('localhost', check_port))
                    logger.log_info(f"[SUCCESS] {service_name} is running and accepting connections on port {check_port}.")
                    # Extended health check for Backend API
                    if service_name == 'Backend API':
                        try:
                            resp = requests.get(f"http://localhost:{check_port}/health", timeout=3)
                            if resp.status_code == 200 and (resp.json().get("status") == "ok" or resp.text == "ok"):
                                logger.log_info(f"[HEALTHY] {service_name} passed /health check.")
                            else:
                                logger.log_error(f"[ERROR] {service_name} /health endpoint did not return healthy status.")
                                health_ok = False
                        except Exception as e:
                            logger.log_error(f"[ERROR] {service_name} /health check failed: {e}")
                            health_ok = False
                except Exception as e:
                    logger.log_error(f"[ERROR] {service_name} did not start correctly on port {check_port}: {e}")
                    health_ok = False
                finally:
                    s.close()
            if health_ok:
                break
            else:
                attempt += 1
                if attempt < max_retries:
                    logger.log_info(f"[RETRY] Attempting to restart {service_name} (attempt {attempt+1}/{max_retries})...")
                    time.sleep(2)
                else:
                    logger.log_error(f"[FAIL] {service_name} failed health checks after {max_retries} attempts.")
        except subprocess.CalledProcessError as e:
            logger.log_error(f"[ERROR] Command failed: {e}")
            attempt += 1
            if attempt < max_retries:
                logger.log_info(f"[RETRY] Attempting to restart {service_name} (attempt {attempt+1}/{max_retries})...")
                time.sleep(2)
            else:
                logger.log_error(f"[FAIL] {service_name} failed to start after {max_retries} attempts.")
    input("\nPress Enter to return to the menu...")

def start_all():
    # Use port_manager to get last assigned port
    port = port_manager.get_last_assigned_port('api_bridge') or 8002
    run_command([sys.executable, 'start_auto.py'], check_port=port, service_name='Backend API')

def start_frontend():
    port = port_manager.get_last_assigned_port('react_frontend') or 3000
    max_retries = 3
    attempt = 0
    while attempt < max_retries:
        run_command(['npm', 'start'], check_port=port, service_name='React Frontend', max_retries=1)
        # Health check: port open and HTTP 200
        import socket
        import requests
        import time
        port_ok = False
        http_ok = False
        content_ok = False
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.settimeout(3)
            s.connect(('localhost', port))
            port_ok = True
        except Exception as e:
            logger.log_error(f"[ERROR] React Frontend did not open port {port}: {e}")
        finally:
            s.close()
        if port_ok:
            try:
                resp = requests.get(f"http://localhost:{port}", timeout=5)
                if resp.status_code == 200:
                    http_ok = True
                    # Check for expected content
                    if ('You can now view' in resp.text) or ('Compiled successfully!' in resp.text):
                        content_ok = True
                        logger.log_info(f"[HEALTHY] React Frontend is running and serving expected content on port {port}.")
                        break
                    else:
                        logger.log_warning(f"[WARNING] React Frontend HTTP 200 but expected content not found.")
                else:
                    logger.log_error(f"[ERROR] React Frontend HTTP status: {resp.status_code}")
            except Exception as e:
                logger.log_error(f"[ERROR] React Frontend HTTP check failed: {e}")
        attempt += 1
        if attempt < max_retries:
            logger.log_info(f"[RETRY] Attempting to restart React Frontend (attempt {attempt+1}/{max_retries})...")
            time.sleep(2)
        else:
            logger.log_error(f"[FAIL] React Frontend failed health checks after {max_retries} attempts.")
    input("\nPress Enter to return to the menu...")

def start_backend():
    # Use port_manager to get last assigned port
    port = port_manager.get_last_assigned_port('api_bridge') or 8002
    run_command([sys.executable, 'api_bridge_with_database.py'], check_port=port, service_name='Backend API')

def cleanup_ports():
    """Kill processes on commonly used ports (3000, 8001, 8002, 8101)"""
    ports = [3000, 8001, 8002, 8101]
    logger.log_info(f"\n[INFO] Cleaning up ports: {ports}")
    for port in ports:
        killed = False
        for proc in psutil.process_iter(['pid', 'name', 'connections']):
            try:
                for conn in proc.info['connections']:
                    if conn.status == psutil.CONN_LISTEN and conn.laddr.port == port:
                        logger.log_info(f"Killing process {proc.info['name']} (PID: {proc.info['pid']}) on port {port}")
                        proc.kill()
                        killed = True
            except (psutil.NoSuchProcess, psutil.AccessDenied, KeyError):
                continue
        if not killed:
            logger.log_info(f"[INFO] Port {port} is clean")
    logger.log_info("[SUCCESS] Port cleanup complete!\n")
    input("Press Enter to return to the menu...")

def run_tests():
    run_command(['run_tests.bat'], shell=True)

def run_job_automation():
    run_command([sys.executable, 'ai_job_automation.py'])

def port_management_menu():
    assignments = port_manager.load_port_assignments()
    logger.log_info("\n[Port Assignments]")
    for svc, port in assignments.items():
        logger.log_info(f"  {svc}: {port}")
        # Check if port is in use
        in_use = False
        for proc in psutil.process_iter(['pid', 'name', 'connections', 'cmdline', 'create_time']):
            try:
                for conn in proc.info['connections']:
                    if conn.status == psutil.CONN_LISTEN and conn.laddr.port == port:
                        start_time = datetime.datetime.fromtimestamp(proc.info['create_time']).strftime('%Y-%m-%d %H:%M:%S') if proc.info.get('create_time') else 'N/A'
                        cmdline = ' '.join(proc.info.get('cmdline', []))
                        logger.log_info(f"    [IN USE] by {proc.info['name']} (PID: {proc.info['pid']})")
                        logger.log_info(f"      Started: {start_time}")
                        logger.log_info(f"      Cmdline: {cmdline}")
                        in_use = True
                        # Offer to kill
                        confirm = input(f"    Kill this process? (y/N): ").strip().lower()
                        if confirm == 'y':
                            proc.kill()
                            logger.log_info("    Process killed.")
            except (psutil.NoSuchProcess, psutil.AccessDenied, KeyError):
                continue
        if not in_use:
            logger.log_info("    [FREE]")
    input("\nPress Enter to return to the menu...")

def main_menu():
    while True:
        choice = questionary.select(
            "Select an action:",
            choices=[
                "Start ALL (Auto Startup)",
                "Start Frontend Only",
                "Start Backend Only",
                "Cleanup Ports",
                "Run Tests",
                "Run Job Application Automation",
                "Port Management & Cleanup",
                "Exit"
            ]
        ).ask()
        if choice == "Start ALL (Auto Startup)":
            start_all()
        elif choice == "Start Frontend Only":
            start_frontend()
        elif choice == "Start Backend Only":
            start_backend()
        elif choice == "Cleanup Ports":
            cleanup_ports()
        elif choice == "Run Tests":
            run_tests()
        elif choice == "Run Job Application Automation":
            run_job_automation()
        elif choice == "Port Management & Cleanup":
            port_management_menu()
        elif choice == "Exit":
            logger.log_info("Goodbye!")
            break

if __name__ == "__main__":
    main_menu() 