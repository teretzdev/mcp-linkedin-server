#!/usr/bin/env python3
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
import threading
import shutil
import json
import centralized_logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Configure logging
logger = centralized_logging.get_logger("auto_startup")

class AutoStartup:
    def __init__(self):
        # Unique port ranges for each service
        self.service_port_ranges = {
            'api_bridge': list(range(8001, 8011)),
            'mcp_backend': list(range(8101, 8111)),
            'llm_controller': list(range(8201, 8211)),
            'react_frontend': list(range(3000, 3010)),
        }
        self.services = {
            'api_bridge': {'script': 'api_bridge.py', 'process': None, 'port': None},
            'mcp_backend': {'script': 'linkedin_browser_mcp.py', 'process': None, 'port': None},
            'llm_controller': {'script': 'llm_controller.py', 'process': None, 'port': None},
            'react_frontend': {'script': 'npm start', 'process': None, 'port': None},
        }
        self.max_port_attempts = 10
        self.ports_file = Path(__file__).parent / 'service_ports.json'
        self.load_ports()
        
    def load_ports(self):
        if self.ports_file.exists():
            try:
                with open(self.ports_file, 'r') as f:
                    self.saved_ports = json.load(f)
            except Exception:
                self.saved_ports = {}
        else:
            self.saved_ports = {}

    def save_ports(self):
        ports = {svc: info['port'] for svc, info in self.services.items() if info['port']}
        with open(self.ports_file, 'w') as f:
            json.dump(ports, f, indent=2)

    def check_port_available(self, port: int) -> bool:
        """Check if a port is available"""
        try:
            import socket
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', port))
                return True
        except OSError:
            return False
    
    def find_unique_available_port(self, port_range, service_name):
        # Try to use the last saved port if available and free
        last_port = self.saved_ports.get(service_name)
        if last_port and self.check_port_available(last_port):
            return last_port
        for port in port_range:
            if self.check_port_available(port):
                return port
        raise RuntimeError(f"No available port found in range {port_range}")
    
    def kill_process_on_port(self, port: int) -> bool:
        """Kill any process using the specified port - Windows compatible"""
        try:
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    # Windows-compatible way to get connections
                    if hasattr(proc, 'connections'):
                        connections = proc.connections()
                        for conn in connections:
                            if hasattr(conn, 'laddr') and hasattr(conn.laddr, 'port') and conn.laddr.port == port:
                                logger.log_info(f"Killing process {proc.info['pid']} on port {port}")
                                proc.terminate()
                                proc.wait(timeout=5)
                                return True
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.TimeoutExpired, AttributeError):
                    continue
            return False
        except Exception as e:
            logger.log_error(f"Error killing process on port {port}: {e}")
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
            logger.log_info(f"PATH: {os.environ.get('PATH')}")
            logger.log_info(f"node path: {node_path}")
            logger.log_info(f"npm path: {npm_path}")
            # Try node -v
            node_ok = False
            npm_ok = False
            if node_path:
                result = subprocess.run([node_path, '--version'], capture_output=True, text=True, timeout=10)
                logger.log_info(f"node -v output: {result.stdout.strip()} (rc={result.returncode})")
                node_ok = result.returncode == 0
            if npm_path:
                result = subprocess.run([npm_path, '--version'], capture_output=True, text=True, timeout=10)
                logger.log_info(f"npm -v output: {result.stdout.strip()} (rc={result.returncode})")
                npm_ok = result.returncode == 0
            if node_ok and npm_ok:
                logger.log_info("Node.js and npm are properly installed and available in PATH.")
                return True
            else:
                logger.log_error("Node.js or npm not found or not working. Please check your PATH and try opening a new terminal window.")
                logger.log_error(f"PATH: {os.environ.get('PATH')}")
                return False
        except (subprocess.TimeoutExpired, FileNotFoundError, Exception) as e:
            logger.log_error(f"Node.js or npm not found. Please install Node.js from https://nodejs.org/ or check your PATH. Error: {e}")
            logger.log_error(f"PATH: {os.environ.get('PATH')}")
            return False

    def install_npm_dependencies(self) -> bool:
        """Install npm dependencies if node_modules doesn't exist"""
        if not Path('node_modules').exists():
            logger.log_info("Installing npm dependencies...")
            try:
                result = subprocess.run(['npm', 'install'], capture_output=True, text=True, timeout=300)
                if result.returncode == 0:
                    logger.log_info("Successfully installed npm dependencies")
                    return True
                else:
                    logger.log_error(f"Failed to install npm dependencies: {result.stderr}")
                    return False
            except (subprocess.TimeoutExpired, FileNotFoundError):
                logger.log_error("Failed to run npm install")
                return False
        return True

    def create_env_if_missing(self) -> bool:
        """Create .env file if it doesn't exist"""
        if not Path('.env').exists():
            logger.log_info("Creating .env file...")
            try:
                result = subprocess.run([sys.executable, 'create_env.py'], 
                                      capture_output=True, text=True, timeout=30)
                if result.returncode == 0:
                    logger.log_info("Successfully created .env file")
                    return True
                else:
                    logger.log_error(f"Failed to create .env file: {result.stderr}")
                    return False
            except subprocess.TimeoutExpired:
                logger.log_error("Timeout creating .env file")
                return False
        return True
    
    def is_service_healthy(self, port, health_path="/health"):
        try:
            url = f"http://localhost:{port}{health_path}"
            resp = requests.get(url, timeout=2)
            if resp.status_code == 200 and (resp.json().get("status") == "ok" or resp.text == "ok"):
                return True
        except Exception:
            pass
        return False

    def start_python_service(self, script: str, service_name: str):
        port_range = self.service_port_ranges[service_name]
        port = self.find_unique_available_port(port_range, service_name)
        self.services[service_name]['port'] = port
        self.save_ports()
        # Health check before killing/restarting
        if self.is_service_healthy(port):
            logger.log_info(f"{service_name} already running and healthy on port {port}, reusing.")
            return None  # Do not restart
        self.kill_process_on_port(port)
        time.sleep(1)
        logger.log_info(f"Starting {service_name} on port {port}...")
        try:
            process = subprocess.Popen(
                [sys.executable, script, f"--port={port}"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8',
                errors='replace'
            )
            self.services[service_name]['process'] = process
            # Log output in real time
            def log_output(stream, log_func):
                for line in iter(stream.readline, ''):
                    log_func(f"[{service_name}] {line.strip()}")
            threading.Thread(target=log_output, args=(process.stdout, logger.log_info), daemon=True).start()
            threading.Thread(target=log_output, args=(process.stderr, logger.log_error), daemon=True).start()
            return process
        except Exception as e:
            logger.log_error(f"Error starting {service_name}: {e}")
            self.services[service_name]['process'] = None
            return None
    
    def start_react_frontend(self):
        port_range = self.service_port_ranges['react_frontend']
        port = self.find_unique_available_port(port_range, 'react_frontend')
        self.services['react_frontend']['port'] = port
        self.save_ports()
        # Health check before killing/restarting
        if self.is_service_healthy(port):
            logger.log_info(f"React frontend already running and healthy on port {port}, reusing.")
            self.open_browser(f"http://localhost:{port}")
            return None  # Do not restart
        self.kill_process_on_port(port)
        time.sleep(1)
        logger.log_info(f"Starting React frontend on port {port}...")
        
        # Use the new start_auto script if available
        start_auto_script = Path(__file__).parent / 'start_auto.py'
        if start_auto_script.exists():
            logger.log_info("Using start_auto script for React frontend...")
            try:
                process = subprocess.Popen(
                    [sys.executable, str(start_auto_script)],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                self.services['react_frontend']['process'] = process
                self.save_ports()
                self.open_browser(f"http://localhost:{port}")
                return process
            except Exception as e:
                logger.log_error(f"Error starting React frontend with start_auto script: {e}")
                self.services['react_frontend']['process'] = None
                return None
        
        # Fallback to direct npm start
        react_app_dir = Path(__file__).parent  # Use root directory
        package_json = react_app_dir / 'package.json'
        if not package_json.exists():
            logger.log_error(f"No package.json found in {react_app_dir}")
            return None
        npm_path = shutil.which('npm')
        if not npm_path:
            logger.log_error("Could not find 'npm' in PATH.")
            return None
        env = os.environ.copy()
        env['PORT'] = str(port)
        try:
            process = subprocess.Popen(
                [npm_path, 'start'],
                cwd=str(react_app_dir),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=env
            )
            self.services['react_frontend']['process'] = process
            self.save_ports()
            self.open_browser(f"http://localhost:{port}")
            return process
        except Exception as e:
            logger.log_error(f"Error starting React frontend: {e}")
            self.services['react_frontend']['process'] = None
            return None
    
    def open_browser(self, url: str):
        """Open browser with the application"""
        try:
            import webbrowser
            webbrowser.open(url)
            logger.log_info(f"Opened browser to {url}")
        except Exception as e:
            logger.log_error(f"Error opening browser: {e}")
    
    def cleanup_on_exit(self):
        """Cleanup function to terminate all processes"""
        logger.log_info("Cleaning up processes...")
        for service_name, service_info in self.services.items():
            if service_info['process'] and service_info['process'].poll() is None:
                try:
                    service_info['process'].terminate()
                    service_info['process'].wait(timeout=5)
                    logger.log_info(f"Terminated {service_name}")
                except subprocess.TimeoutExpired:
                    service_info['process'].kill()
                    logger.log_info(f"Killed {service_name}")
                except Exception as e:
                    logger.log_error(f"Error terminating {service_name}: {e}")
    
    def restart_api_bridge(self):
        """Gracefully restart the API bridge process"""
        svc = self.services['api_bridge']
        proc = svc.get('process')
        if proc and proc.poll() is None:
            logger.log_info("[Auto] Stopping API bridge for restart...")
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except Exception:
                proc.kill()
        # Start new process
        logger.log_info("[Auto] Restarting API bridge...")
        new_proc = subprocess.Popen([sys.executable, svc['script']], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        svc['process'] = new_proc
        # Wait for service to be ready
        if self.wait_for_service(f"http://localhost:{svc['port']}/health", timeout=30):
            logger.log_info("[Auto] API bridge restarted successfully.")
        else:
            logger.log_error("[Auto] API bridge failed to restart.")

    def run_resume_upload_tests(self):
        logger.log_info("[Auto] Running resume upload tests...")
        result = subprocess.run([sys.executable, "test_resume_upload.py"])
        if result.returncode == 0:
            logger.log_info("[Auto] ✅ All resume upload tests passed.")
        else:
            logger.log_error("[Auto] ❌ Some resume upload tests failed.")

    def run(self):
        """Main startup sequence"""
        try:
            logger.log_info("Starting LinkedIn Job Hunter - Automated Mode")
            
            # Check Node.js installation
            if not self.check_node_installation():
                logger.log_error("Node.js installation check failed")
                return False
            
            # Install npm dependencies
            if not self.install_npm_dependencies():
                logger.log_error("Failed to install npm dependencies")
                return False
            
            # Create .env if missing
            if not self.create_env_if_missing():
                logger.log_error("Failed to create .env file")
                return False
            
            # Start services in order
            services_started = []
            
            # 1. Start API Bridge
            self.services['api_bridge']['process'] = self.start_python_service('api_bridge_with_database.py', 'api_bridge')
            if self.services['api_bridge']['process']:
                services_started.append('api_bridge')
            
            # 2. Start MCP Backend
            self.services['mcp_backend']['process'] = self.start_python_service('linkedin_browser_mcp.py', 'mcp_backend')
            if self.services['mcp_backend']['process']:
                services_started.append('mcp_backend')
            
            # 3. Start LLM Controller
            self.services['llm_controller']['process'] = self.start_python_service('llm_controller.py', 'llm_controller')
            if self.services['llm_controller']['process']:
                services_started.append('llm_controller')
            
            # 4. Start React Frontend
            self.services['react_frontend']['process'] = self.start_react_frontend()
            if self.services['react_frontend']['process']:
                services_started.append('react_frontend')
            
            # Check if all services started
            if len(services_started) == len(self.services):
                logger.log_info("All services started successfully!")
                for svc, info in self.services.items():
                    logger.log_info(f"{svc} running on port {info['port']}")
                logger.log_info(f"Dashboard: http://localhost:{self.services['react_frontend']['port']}")
                logger.log_info(f"API Bridge: http://localhost:{self.services['api_bridge']['port']}")
                logger.log_info("Press Ctrl+C to stop all services")
                
                # Keep running until interrupted
                try:
                    while True:
                        time.sleep(1)
                        # Check if any service died
                        for service_name, service_info in self.services.items():
                            if service_info['process'] and service_info['process'].poll() is not None:
                                logger.log_error(f"{service_name} has stopped unexpectedly")
                                return False
                except KeyboardInterrupt:
                    logger.log_info("Received interrupt signal")
                    return True
            else:
                logger.log_error(f"Only {len(services_started)}/{len(self.services)} services started")
                return False
                
        except Exception as e:
            logger.log_error(f"Startup failed: {e}")
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
            logger.log_info(f"[Auto] Detected change in {event.src_path}, restarting API bridge and running tests...")
            self.restart_api_bridge()
            self.run_tests()

def watch_backend_and_test(restart_api_bridge, run_tests):
    event_handler = BackendChangeHandler(restart_api_bridge, run_tests)
    observer = Observer()
    observer.schedule(event_handler, path='.', recursive=True)
    observer.start()
    logger.log_info("[Auto] Watching for backend code changes. Press Ctrl+C to stop.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

def main():
    """Main entry point"""
    startup = AutoStartup()
    results = {}
    # Start API Bridge
    results['api_bridge'] = startup.start_python_service('api_bridge_with_database.py', 'api_bridge')
    # Start MCP Backend
    results['mcp_backend'] = startup.start_python_service('linkedin_browser_mcp.py', 'mcp_backend')
    # Start LLM Controller
    results['llm_controller'] = startup.start_python_service('llm_controller.py', 'llm_controller')
    # Start React Frontend
    results['react_frontend'] = startup.start_react_frontend()
    print("\nService startup summary:")
    for svc, proc in results.items():
        port = startup.services[svc]['port']
        status = "reused" if proc is None else ("started" if proc else "failed")
        print(f"- {svc} on port {port}: {status}")
    print("\nYou can refer to service_ports.json for the current port assignments.")

if __name__ == "__main__":
    main() 