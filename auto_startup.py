THIS SHOULD BE A LINTER ERROR#!/usr/bin/env python3
"""
Automated Startup Script for LinkedIn Job Hunter
Handles all manual intervention scenarios automatically
"""

import os
import sys
import time
import subprocess
import requests
import psutil
import signal
from pathlib import Path
from typing import List, Optional, Tuple
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import threading
import shutil

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('startup.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AutoStartup:
    def __init__(self):
        self.services = {
            'api_bridge': {'port': 8001, 'script': 'api_bridge.py', 'process': None},
            'mcp_backend': {'port': 8002, 'script': 'linkedin_browser_mcp.py', 'process': None},
            'llm_controller': {'port': 8003, 'script': 'llm_controller.py', 'process': None},
            'react_frontend': {'port': 3000, 'script': 'npm start', 'process': None}
        }
        self.max_port_attempts = 10
        
    def check_port_available(self, port: int) -> bool:
        """Check if a port is available"""
        try:
            import socket
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', port))
                return True
        except OSError:
            return False
    
    def find_available_port(self, start_port: int) -> int:
        """Find the next available port starting from start_port"""
        port = start_port
        attempts = 0
        
        while attempts < self.max_port_attempts:
            if self.check_port_available(port):
                return port
            port += 1
            attempts += 1
            
        raise RuntimeError(f"Could not find available port starting from {start_port}")
    
    def kill_process_on_port(self, port: int) -> bool:
        """Kill any process using the specified port - cross-platform."""
        try:
            for conn in psutil.net_connections(kind='inet'):
                if conn.laddr.port == port and conn.status == psutil.CONN_LISTEN:
                    try:
                        proc = psutil.Process(conn.pid)
                        logger.info(f"Killing process {proc.pid} ({proc.name()}) on port {port}")
                        proc.terminate()
                        proc.wait(timeout=5)
                        return True
                    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.TimeoutExpired) as e:
                        logger.warning(f"Failed to kill process {conn.pid} on port {port}: {e}")
                        continue
            return False
        except Exception as e:
            logger.error(f"Error killing process on port {port}: {e}")
            return False
    
    def wait_for_service(self, url: str, timeout: int = 30) -> bool:
        """Wait for a service to be ready"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                response = requests.get(url, timeout=2)
                if response.status_code == 200:
                    return True
            except requests.RequestException:
                pass
            time.sleep(1)
        return False
    
    def check_node_installation(self) -> bool:
        """Check if Node.js and npm are installed"""
        try:
            node_path = shutil.which('node')
            npm_path = shutil.which('npm')
            logger.info(f"PATH: {os.environ.get('PATH')}")
            logger.info(f"node path: {node_path}")
            logger.info(f"npm path: {npm_path}")
            # Try node -v
            node_ok = False
            npm_ok = False
            if node_path:
                result = subprocess.run([node_path, '--version'], capture_output=True, text=True, timeout=10)
                logger.info(f"node -v output: {result.stdout.strip()} (rc={result.returncode})")
                node_ok = result.returncode == 0
            if npm_path:
                result = subprocess.run([npm_path, '--version'], capture_output=True, text=True, timeout=10)
                logger.info(f"npm -v output: {result.stdout.strip()} (rc={result.returncode})")
                npm_ok = result.returncode == 0
            if node_ok and npm_ok:
                logger.info("Node.js and npm are properly installed and available in PATH.")
                return True
            else:
                logger.error("Node.js or npm not found or not working. Please check your PATH and try opening a new terminal window.")
                logger.error(f"PATH: {os.environ.get('PATH')}")
                return False
        except (subprocess.TimeoutExpired, FileNotFoundError, Exception) as e:
            logger.error(f"Node.js or npm not found. Please install Node.js from https://nodejs.org/ or check your PATH. Error: {e}")
            logger.error(f"PATH: {os.environ.get('PATH')}")
            return False

    def install_npm_dependencies(self) -> bool:
        """Install npm dependencies if node_modules doesn't exist"""
        if not Path('node_modules').exists():
            logger.info("Installing npm dependencies...")
            try:
                result = subprocess.run(['npm', 'install'], capture_output=True, text=True, timeout=300)
                if result.returncode == 0:
                    logger.info("Successfully installed npm dependencies")
                    return True
                else:
                    logger.error(f"Failed to install npm dependencies: {result.stderr}")
                    return False
            except (subprocess.TimeoutExpired, FileNotFoundError):
                logger.error("Failed to run npm install")
                return False
        return True

    def create_env_if_missing(self) -> bool:
        """Create .env file if it doesn't exist"""
        if not Path('.env').exists():
            logger.info("Creating .env file...")
            try:
                result = subprocess.run([sys.executable, 'create_env.py'], 
                                      capture_output=True, text=True, timeout=30)
                if result.returncode == 0:
                    logger.info("Successfully created .env file")
                    return True
                else:
                    logger.error(f"Failed to create .env file: {result.stderr}")
                    return False
            except subprocess.TimeoutExpired:
                logger.error("Timeout creating .env file")
                return False
        return True
    
    def start_python_service(self, service_name: str, script: str, port: int) -> Optional[subprocess.Popen]:
        """Start a Python service"""
        try:
            # Kill any existing process on the port
            self.kill_process_on_port(port)
            time.sleep(1)
            
            # Start the service
            logger.info(f"Starting {service_name} on port {port}...")
            process = subprocess.Popen(
                [sys.executable, script],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # Wait for service to be ready
            if self.wait_for_service(f"http://localhost:{port}/health", timeout=30):
                logger.info(f"{service_name} started successfully")
                return process
            else:
                logger.error(f"{service_name} failed to start")
                process.terminate()
                return None
                
        except Exception as e:
            logger.error(f"Error starting {service_name}: {e}")
            return None
    
    def start_react_frontend(self, port: int) -> Optional[subprocess.Popen]:
        """Start React frontend with automatic port selection"""
        try:
            # Find available port
            actual_port = self.find_available_port(port)
            if actual_port != port:
                logger.info(f"Port {port} in use, using port {actual_port}")
            
            # Kill any existing process on the port
            self.kill_process_on_port(actual_port)
            time.sleep(1)
            
            # Set environment variable
            env = os.environ.copy()
            env['PORT'] = str(actual_port)
            
            logger.info(f"Starting React frontend on port {actual_port}...")
            process = subprocess.Popen(
                ['npm', 'start', '--', '--port', str(actual_port)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=env,
                bufsize=1,
                universal_newlines=True
            )
            
            # Wait for React to be ready
            if self.wait_for_service(f"http://localhost:{actual_port}", timeout=60):
                logger.info(f"React frontend started successfully on port {actual_port}")
                return process
            else:
                logger.error("React frontend failed to start")
                stdout, stderr = process.communicate()
                logger.error(f"STDOUT: {stdout}")
                logger.error(f"STDERR: {stderr}")
                process.terminate()
                return None
                
        except Exception as e:
            logger.error(f"Error starting React frontend: {e}")
            return None
    
    def open_browser(self, url: str):
        """Open browser with the application"""
        logger.info(f"Dashboard is available at: {url}")
        # try:
        #     import webbrowser
        #     webbrowser.open(url)
        #     logger.info(f"Opened browser to {url}")
        # except Exception as e:
        #     logger.error(f"Error opening browser: {e}")
    
    def cleanup_on_exit(self):
        """Cleanup function to terminate all processes"""
        logger.info("Cleaning up processes...")
        for service_name, service_info in self.services.items():
            if service_info['process'] and service_info['process'].poll() is None:
                try:
                    service_info['process'].terminate()
                    service_info['process'].wait(timeout=5)
                    logger.info(f"Terminated {service_name}")
                except subprocess.TimeoutExpired:
                    service_info['process'].kill()
                    logger.info(f"Killed {service_name}")
                except Exception as e:
                    logger.error(f"Error terminating {service_name}: {e}")
    
    def restart_api_bridge(self):
        """Gracefully restart the API bridge process"""
        svc = self.services['api_bridge']
        proc = svc.get('process')
        if proc and proc.poll() is None:
            logger.info("[Auto] Stopping API bridge for restart...")
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except Exception:
                proc.kill()
        # Start new process
        logger.info("[Auto] Restarting API bridge...")
        new_proc = subprocess.Popen([sys.executable, svc['script']], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        svc['process'] = new_proc
        # Wait for service to be ready
        if self.wait_for_service(f"http://localhost:{svc['port']}/health", timeout=30):
            logger.info("[Auto] API bridge restarted successfully.")
        else:
            logger.error("[Auto] API bridge failed to restart.")

    def run_resume_upload_tests(self):
        logger.info("[Auto] Running resume upload tests...")
        result = subprocess.run([sys.executable, "test_resume_upload.py"])
        if result.returncode == 0:
            logger.info("[Auto] ✅ All resume upload tests passed.")
        else:
            logger.error("[Auto] ❌ Some resume upload tests failed.")

    def run(self):
        """Main startup sequence"""
        try:
            logger.info("Starting LinkedIn Job Hunter - Automated Mode")
            
            # Check Node.js installation
            if not self.check_node_installation():
                logger.error("Node.js installation check failed")
                return False
            
            # Install npm dependencies
            if not self.install_npm_dependencies():
                logger.error("Failed to install npm dependencies")
                return False
            
            # Create .env if missing
            if not self.create_env_if_missing():
                logger.error("Failed to create .env file")
                return False
            
            # Start services in order
            services_started = []
            
            # 1. Start API Bridge
            self.services['api_bridge']['process'] = self.start_python_service(
                'API Bridge', 'api_bridge.py', 8001
            )
            if self.services['api_bridge']['process']:
                services_started.append('api_bridge')
            
            # 2. Start MCP Backend
            self.services['mcp_backend']['process'] = self.start_python_service(
                'MCP Backend', 'linkedin_browser_mcp.py', 8002
            )
            if self.services['mcp_backend']['process']:
                services_started.append('mcp_backend')
            
            # 3. Start LLM Controller
            self.services['llm_controller']['process'] = self.start_python_service(
                'LLM Controller', 'llm_controller.py', 8003
            )
            if self.services['llm_controller']['process']:
                services_started.append('llm_controller')
            
            # 4. Start React Frontend
            self.services['react_frontend']['process'] = self.start_react_frontend(3000)
            if self.services['react_frontend']['process']:
                services_started.append('react_frontend')
                # Open browser
                self.open_browser("http://localhost:3000")
            
            # Check if all services started
            if len(services_started) == len(self.services):
                logger.info("All services started successfully!")
                logger.info("Dashboard: http://localhost:3000")
                logger.info("API Bridge: http://localhost:8001")
                logger.info("Press Ctrl+C to stop all services")
                
                # Keep running until interrupted
                try:
                    while True:
                        time.sleep(1)
                        # Check if any service died
                        for service_name, service_info in self.services.items():
                            if service_info['process'] and service_info['process'].poll() is not None:
                                logger.error(f"{service_name} has stopped unexpectedly")
                                return False
                except KeyboardInterrupt:
                    logger.info("Received interrupt signal")
                    return True
            else:
                logger.error(f"Only {len(services_started)}/{len(self.services)} services started")
                return False
                
        except Exception as e:
            logger.error(f"Startup failed: {e}")
            return False
        finally:
            self.cleanup_on_exit()

# Backend file watcher
class BackendChangeHandler(FileSystemEventHandler):
    def __init__(self, restart_api_bridge, run_tests):
        self.restart_api_bridge = restart_api_bridge
        self.run_tests = run_tests

    def on_modified(self, event):
        if event.is_directory:
            return
        path_str = str(event.src_path)
        if path_str.endswith('.py'):
            logger.info(f"[Auto] Detected change in {event.src_path}, restarting API bridge and running tests...")
            self.restart_api_bridge()
            self.run_tests()

def watch_backend_and_test(restart_api_bridge, run_tests):
    event_handler = BackendChangeHandler(restart_api_bridge, run_tests)
    observer = Observer()
    observer.schedule(event_handler, path='.', recursive=True)
    observer.start()
    logger.info("[Auto] Watching for backend code changes. Press Ctrl+C to stop.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

def main():
    """Main entry point"""
    startup = AutoStartup()
    
    # Set up signal handlers for graceful shutdown
    def signal_handler(signum, frame):
        logger.info("Received shutdown signal")
        startup.cleanup_on_exit()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    startup.run()  # This starts all services as before

    # Start backend watcher in a background thread
    watch_thread = threading.Thread(target=watch_backend_and_test, args=(startup.restart_api_bridge, startup.run_resume_upload_tests))
    watch_thread.daemon = True
    watch_thread.start()

    # Keep main thread alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("[Auto] Shutting down...")
        startup.cleanup_on_exit()

if __name__ == "__main__":
    main() 