#!/usr/bin/env python3
"""
LinkedIn MCP Frontend Auto-Start Script
Automatically finds available ports and handles conflicts gracefully
"""

import os
import sys
import time
import socket
import subprocess
import psutil
import json
import shutil
from pathlib import Path

def check_dependencies():
    """Check if all required dependencies are available"""
    print("🔍 Checking dependencies...")
    
    # Check Node.js and npm
    node_path = shutil.which('node')
    npm_path = shutil.which('npm')
    
    if not node_path:
        print("❌ Node.js not found. Please install Node.js from https://nodejs.org/")
        return False
    
    if not npm_path:
        print("❌ npm not found. Please install npm or check your PATH")
        return False
    
    print(f"✅ Node.js found: {node_path}")
    print(f"✅ npm found: {npm_path}")
    return True

def install_npm_dependencies():
    """Install npm dependencies if needed"""
    if not Path('node_modules').exists():
        print("📦 Installing npm dependencies...")
        try:
            result = subprocess.run(['npm', 'install'], 
                                  capture_output=True, text=True, timeout=300)
            if result.returncode == 0:
                print("✅ npm dependencies installed successfully")
                return True
            else:
                print(f"❌ Failed to install npm dependencies: {result.stderr}")
                return False
        except Exception as e:
            print(f"❌ Error installing dependencies: {e}")
            return False
    else:
        print("✅ npm dependencies already installed")
        return True

def find_available_port(start_port=3000, max_attempts=10):
    """Find an available port starting from start_port"""
    for i in range(max_attempts):
        port = start_port + i
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', port))
                return port
        except OSError:
            continue
    return None

def kill_process_on_port(port):
    """Kill any process running on the specified port"""
    try:
        for conn in psutil.net_connections():
            if hasattr(conn, 'laddr') and conn.laddr and hasattr(conn.laddr, 'port'):
                if conn.laddr.port == port and conn.status == 'LISTEN':
                    try:
                        process = psutil.Process(conn.pid)
                        print(f"Killing process on port {port}: {process.name()} (PID: {process.pid})")
                        process.terminate()
                        process.wait(timeout=5)
                    except (psutil.NoSuchProcess, psutil.TimeoutExpired):
                        try:
                            process.kill()
                        except psutil.NoSuchProcess:
                            pass
                    except Exception as e:
                        print(f"Error killing process on port {port}: {e}")
    except Exception as e:
        print(f"Error checking port {port}: {e}")

def start_react_app(port):
    """Start the React app on the specified port"""
    try:
        # Set environment variable
        env = os.environ.copy()
        env['PORT'] = str(port)
        
        print(f"Starting React app on port {port}...")
        
        # Start the React app
        process = subprocess.Popen(
            ['npm', 'start'],
            env=env,
            cwd=os.getcwd(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait a moment to see if it starts successfully
        time.sleep(3)
        
        if process.poll() is None:
            print(f"✅ React app started successfully on http://localhost:{port}")
            
            # Save the port information for other scripts
            port_info = {
                'frontend_port': port,
                'frontend_url': f'http://localhost:{port}',
                'started_at': time.strftime('%Y-%m-%d %H:%M:%S')
            }
            
            with open('service_ports.json', 'w') as f:
                json.dump(port_info, f, indent=2)
            
            return process
        else:
            stdout, stderr = process.communicate()
            print(f"❌ Failed to start React app: {stderr}")
            return None
            
    except Exception as e:
        print(f"❌ Error starting React app: {e}")
        return None

def main():
    print("🚀 Starting LinkedIn MCP Frontend Only...")
    print()
    
    # Check dependencies
    if not check_dependencies():
        print("\n❌ Dependency check failed. Please install required dependencies.")
        sys.exit(1)
    
    # Install npm dependencies
    if not install_npm_dependencies():
        print("\n❌ Failed to install npm dependencies.")
        sys.exit(1)
    
    # Kill existing processes on common React ports
    print("🔍 Checking for existing React processes...")
    for port in range(3000, 3006):
        kill_process_on_port(port)
    
    # Find available port
    print("🔍 Finding available port...")
    available_port = find_available_port(3000, 10)
    
    if not available_port:
        print("❌ No available ports found in range 3000-3009")
        sys.exit(1)
    
    print(f"✅ Found available port: {available_port}")
    
    # Start React app
    process = start_react_app(available_port)
    
    if process:
        print()
        print(f"🌐 React app is running on: http://localhost:{available_port}")
        print("📝 Press Ctrl+C to stop the server")
        print()
        
        try:
            # Keep the process running
            process.wait()
        except KeyboardInterrupt:
            print("\n🛑 Stopping React app...")
            process.terminate()
            process.wait()
            print("✅ React app stopped")
    else:
        print("❌ Failed to start React app")
        sys.exit(1)

if __name__ == "__main__":
    main() 