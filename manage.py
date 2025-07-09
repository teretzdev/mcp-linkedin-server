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
import socket

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

def kill_process_on_port(port: int):
    """Find and kill any process listening on the given port."""
    logger.log_info(f"Checking for and terminating any existing process on port {port}...")
    killed = False
    for proc in psutil.process_iter(['pid', 'name', 'connections']):
        try:
            for conn in proc.info['connections']:
                if conn.status == psutil.CONN_LISTEN and conn.laddr.port == port:
                    logger.log_info(f"  -> Found existing process '{proc.info['name']}' (PID: {proc.info['pid']}) on port {port}. Terminating.")
                    proc.kill()
                    proc.wait(timeout=3) # Wait for termination
                    logger.log_info(f"  -> Process terminated.")
                    killed = True
        except (psutil.NoSuchProcess, psutil.AccessDenied, KeyError, psutil.TimeoutExpired) as e:
            logger.log_warning(f"  -> Could not terminate process on port {port}: {e}")
            continue
    if not killed:
        logger.log_info(f"  -> Port {port} is already clean.")


def start_enhanced_backend():
    """Starts the enhanced FastAPI backend server as a background process."""
    port = port_manager.get_last_assigned_port('enhanced_backend') or 8101
    kill_process_on_port(port) # Ensure port is free
    cmd = [sys.executable, 'enhanced-mcp-server/scripts/start_enhanced_mcp_server.py']
    
    logger.log_info("\n[STARTING] Enhanced Backend Server in the background...")
    
    # Log backend output for debugging
    os.makedirs('logs', exist_ok=True)
    stdout_log = open('logs/backend_stdout.log', 'w')
    stderr_log = open('logs/backend_stderr.log', 'w')
    
    # Use Popen for non-blocking background process
    subprocess.Popen(cmd, shell=False, stdout=stdout_log, stderr=stderr_log)
    
    # Health Check
    logger.log_info(f"Waiting for Enhanced Backend to be ready on port {port}...")
    time.sleep(5) # Give it a moment to start
    max_retries = 5
    for i in range(max_retries):
        try:
            resp = requests.get(f"http://localhost:{port}/health", timeout=5)
            if resp.status_code == 200:
                logger.log_info(f"[SUCCESS] Enhanced Backend is running and healthy on port {port}.")
                input("\nPress Enter to return to the menu...")
                return
        except requests.ConnectionError:
            logger.log_info(f"Attempt {i+1}/{max_retries}: Backend not ready yet, retrying in 3 seconds...")
            time.sleep(3)
    
    logger.log_error("[FAIL] Enhanced Backend failed to start or respond to health check.")
    input("\nPress Enter to return to the menu...")


def trigger_enhanced_automation():
    """Triggers the job application automation on the enhanced backend."""
    port = port_manager.get_last_assigned_port('enhanced_backend') or 8101
    url = f"http://localhost:{port}/run-automation"
    logger.log_info(f"\n[TRIGGERING] Job Automation via POST to {url}")
    try:
        response = requests.post(url, timeout=10) # 10-second timeout for the request itself
        if response.status_code == 200:
            logger.log_info("[SUCCESS] Automation task started successfully on the backend.")
            logger.log_info("Check the backend server logs for progress.")
        else:
            logger.log_error(f"[ERROR] Failed to trigger automation. Backend responded with status {response.status_code}.")
            logger.log_error(f"Response: {response.text}")
    except requests.RequestException as e:
        logger.log_error(f"[ERROR] Could not connect to the Enhanced Backend at {url}.")
        logger.log_error(f"Please ensure the backend service is started. Details: {e}")
    input("\nPress Enter to return to the menu...")


def start_all_enhanced():
    """Starts both the Enhanced Backend and the Frontend."""
    logger.log_info("Starting all enhanced services...")
    start_enhanced_backend()
    start_frontend()


def start_all():
    # Use port_manager to get last assigned port
    port = port_manager.get_last_assigned_port('api_bridge') or 8002
    kill_process_on_port(port) # Ensure port is free
    run_command([sys.executable, 'start_auto.py'], check_port=port, service_name='Backend API')

def start_frontend():
    port = port_manager.get_last_assigned_port('react_frontend') or 3000
    kill_process_on_port(port) # Ensure port is free
    max_retries = 3
    attempt = 0
    while attempt < max_retries:
        # NOTE: shell=True is often needed on Windows for .cmd files like npm
        run_command(['npm', 'start'], shell=True, check_port=port, service_name='React Frontend', max_retries=1)
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
    """Starts the legacy backend API server, ensuring the port is free first."""
    port = 8001
    logger.log_info(f"Preparing to start legacy backend on port {port}...")

    max_port_retries = 5
    is_free = False
    for i in range(max_port_retries):
        logger.log_info(f"Attempt {i+1}/{max_port_retries} to clear and verify port {port}...")
        kill_process_on_port(port)
        time.sleep(2)  # Give the OS a moment to release the socket.

        # Verify the port is actually free by trying to bind to it repeatedly.
        verification_retries = 5
        for j in range(verification_retries):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind(('127.0.0.1', port))
                logger.log_info(f"Port {port} is confirmed to be free.")
                is_free = True
                break  # Exit verification loop
            except OSError:
                logger.log_warning(f"Port {port} still in use, retrying verification in 1 second...")
                time.sleep(1)
        
        if is_free:
            break # Exit main retry loop

    if not is_free:
        logger.log_error(f"Failed to free port {port} after multiple attempts. Aborting backend start.")
        return

    run_command([sys.executable, 'api_bridge_with_database.py'], service_name="Backend API (Legacy)")


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

def run_apply_to_jobs():
    run_command([sys.executable, 'apply_to_jobs.py'])

def job_automation_menu():
    """Provides a menu to run specific phases of the AI Job Automation."""
    while True:
        choice = questionary.select(
            "AI Job Automation Menu:",
            choices=[
                "1. Run Recon Phase (Find Jobs)",
                "2. Run Application Phase (Apply to Jobs)",
                "Back to Main Menu"
            ],
            pointer="=>"
        ).ask()

        if choice is None:
            break
        elif choice.startswith("1."):
            run_command([sys.executable, 'ai_job_automation.py', 'start_recon'])
        elif choice.startswith("2."):
            run_command([sys.executable, 'ai_job_automation.py', 'start_easyapply'])
        elif choice.startswith("Back"):
            break

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
        os.system('cls' if os.name == 'nt' else 'clear')
        choice = questionary.select(
            "MCP-LinkedIn Main Menu",
            choices=[
                "1. Start All Services (Enhanced)",
                "2. Start All Services (Legacy)",
                "3. Start Frontend Only",
                "4. Start Backend Only (Enhanced)",
                "5. Start Backend Only (Legacy)",
                "6. AI Job Automation",
                "7. Trigger Enhanced Automation",
                "8. Port Management",
                "9. Cleanup Ports",
                "10. Run Tests",
                "Exit"
            ],
            pointer="=>"
        ).ask()

        if choice is None or choice == "Exit":
            break
        elif choice.startswith("1."):
            start_all_enhanced()
        elif choice.startswith("2."):
            start_all()
        elif choice.startswith("3."):
            start_frontend()
        elif choice.startswith("4."):
            start_enhanced_backend()
        elif choice.startswith("5."):
            start_backend()
        elif choice.startswith("6."):
            job_automation_menu()
        elif choice.startswith("7."):
            trigger_enhanced_automation()
        elif choice.startswith("8."):
            port_management_menu()
        elif choice.startswith("9."):
            cleanup_ports()
        elif choice.startswith("10."):
            run_tests()
        else:
            logger.log_info("Invalid choice.")
    logger.log_info("Exiting.")

def main():
    """Main entry point"""
    if len(sys.argv) > 1:
        command = sys.argv[1]
        logger.log_info(f"Executing non-interactive command: {command}")
        if command == "start_backend":
            start_backend()
        elif command == "run_recon":
            run_command([sys.executable, 'ai_job_automation.py', 'start_recon'])
        # Add other non-interactive commands here
        else:
            logger.log_error(f"Unknown command: {command}")
            sys.exit(1)
        logger.log_info(f"Command '{command}' finished.")
    else:
        main_menu()

if __name__ == '__main__':
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        logger.log_info("\nExiting gracefully.")
        sys.exit(0)
    except Exception as e:
        logger.log_error(f"An unexpected error occurred: {e}", exc_info=True)
        sys.exit(1) 