import subprocess
import sys
import os
import time
import requests
import psutil
import logging

# --- Configuration ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
ENHANCED_BACKEND_PORT = 8101
REACT_FRONTEND_PORT = 3000
BACKEND_HEALTH_ENDPOINT = f"http://localhost:{ENHANCED_BACKEND_PORT}/health"
AUTOMATION_TRIGGER_ENDPOINT = f"http://localhost:{ENHANCED_BACKEND_PORT}/run-automation"

def cleanup_ports():
    """Kills any processes listening on the backend or frontend ports."""
    ports_to_clean = [ENHANCED_BACKEND_PORT, REACT_FRONTEND_PORT]
    logging.info(f"--- Cleaning up ports: {ports_to_clean} ---")
    for port in ports_to_clean:
        for proc in psutil.process_iter(['pid', 'name', 'connections']):
            try:
                for conn in proc.info['connections']:
                    if conn.status == psutil.CONN_LISTEN and conn.laddr.port == port:
                        logging.info(f"Found process {proc.info['name']} (PID: {proc.info['pid']}) on port {port}. Terminating.")
                        proc.kill()
            except (psutil.NoSuchProcess, psutil.AccessDenied, KeyError):
                continue
    logging.info("--- Port cleanup complete ---")

def start_backend():
    """Starts the enhanced backend server as a background process and waits for it to be healthy."""
    logging.info("--- Starting Enhanced Backend Server ---")
    backend_cmd = [sys.executable, 'enhanced-mcp-server/scripts/start_enhanced_mcp_server.py']
    
    # Log backend output for debugging if needed
    os.makedirs('logs', exist_ok=True)
    stdout_log = open('logs/backend_stdout.log', 'w')
    stderr_log = open('logs/backend_stderr.log', 'w')
    
    subprocess.Popen(backend_cmd, stdout=stdout_log, stderr=stderr_log, creationflags=subprocess.CREATE_NEW_CONSOLE)
    
    logging.info("Waiting for backend to become healthy...")
    max_retries = 15
    for i in range(max_retries):
        try:
            response = requests.get(BACKEND_HEALTH_ENDPOINT, timeout=3)
            # The health check in server.py needs to be implemented to return a simple 200 OK
            if response.status_code == 200:
                logging.info("✅ Backend is healthy!")
                return True
        except requests.ConnectionError:
            pass
        logging.info(f"Attempt {i+1}/{max_retries}: Backend not ready yet, waiting...")
        time.sleep(2)
        
    logging.error("❌ Backend failed to start in time. Check logs/backend_stderr.log for errors.")
    return False

def start_frontend():
    """Starts the React frontend."""
    logging.info("--- Starting React Frontend ---")
    # Using shell=True for 'npm' on Windows, and CREATE_NEW_CONSOLE to detach it.
    subprocess.Popen(['npm', 'start'], shell=True, creationflags=subprocess.CREATE_NEW_CONSOLE)
    logging.info("✅ Frontend process launched. It will open in a new window.")
    # We don't wait for the frontend to be "healthy" as it has its own window and logs.

def trigger_automation():
    """Sends a request to the backend to start the job automation process."""
    logging.info("--- Triggering Job Application Automation ---")
    try:
        # Increased timeout to 120 seconds to allow for browser setup
        response = requests.post(AUTOMATION_TRIGGER_ENDPOINT, timeout=120)
        # 202 means the request was accepted and is being processed in the background.
        if response.status_code == 200 or response.status_code == 202:
            logging.info("✅ Automation successfully triggered on the backend.")
            logging.info("The browser window will now open for login if required.")
        else:
            logging.error(f"❌ Failed to trigger automation. Backend responded with status {response.status_code}: {response.text}")
    except requests.RequestException as e:
        logging.error(f"❌ Could not connect to the backend to trigger automation: {e}")

def main():
    """The main orchestration function."""
    cleanup_ports()
    
    if not start_backend():
        sys.exit(1) # Exit if backend fails to start

    start_frontend()
    
    # Give frontend a moment to get going before triggering the automation
    # that might open a browser.
    time.sleep(5) 
    
    trigger_automation()
    
    logging.info("\n--- MCP Startup Complete ---")
    logging.info("Backend is running in the background.")
    logging.info("Frontend is running in its own console window.")
    logging.info("Automation is running. Check the browser and backend logs for progress.")

if __name__ == "__main__":
    main() 