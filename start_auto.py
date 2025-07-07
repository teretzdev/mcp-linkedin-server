#!/usr/bin/env python3
"""
LinkedIn MCP Server - Auto Startup Entry Point
Main entry point for starting all services with intelligent port management
"""

import os
import sys
import time
import subprocess
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
    import socket
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
        import psutil
        for conn in psutil.net_connections():
            if hasattr(conn, 'laddr') and conn.laddr and hasattr(conn.laddr, 'port'):
                if conn.laddr.port == port and conn.status == 'LISTEN':
                    try:
                        process = psutil.Process(conn.pid)
                        print(f"🔄 Killing process on port {port}: {process.name()} (PID: {process.pid})")
                        process.terminate()
                        process.wait(timeout=5)
                    except (psutil.NoSuchProcess, psutil.TimeoutExpired):
                        try:
                            process.kill()
                        except psutil.NoSuchProcess:
                            pass
                    except Exception as e:
                        print(f"⚠️ Error killing process on port {port}: {e}")
    except Exception as e:
        print(f"⚠️ Error checking port {port}: {e}")

def kill_all_required_ports():
    """Kill all processes on required ports before starting services"""
    required_ports = [8001, 8101, 8201, 3000]
    print("\n🔪 Killing all processes on required ports:", required_ports)
    for port in required_ports:
        kill_process_on_port(port)
    print("✅ All required ports are now free.")

def start_react_app(port):
    """Start the React app on the specified port"""
    try:
        # Set environment variable
        env = os.environ.copy()
        env['PORT'] = str(port)
        
        print(f"🚀 Starting React app on port {port}...")
        
        # Get npm path
        npm_path = shutil.which('npm')
        if not npm_path:
            print("❌ npm not found in PATH")
            return None
        
        print(f"📦 Using npm: {npm_path}")
        
        # Start the React app
        process = subprocess.Popen(
            [npm_path, 'start'],
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
            
            # Save the port information
            port_info = {
                'api_bridge': 8001,
                'mcp_backend': 8101,
                'llm_controller': 8201,
                'react_frontend': port,
                'frontend_port': port,
                'frontend_url': f'http://localhost:{port}',
                'started_at': time.strftime('%Y-%m-%d %H:%M:%S')
            }
            
            with open('service_ports.json', 'w') as f:
                import json
                json.dump(port_info, f, indent=2)
            
            return process
        else:
            stdout, stderr = process.communicate()
            print(f"❌ Failed to start React app: {stderr}")
            return None
            
    except Exception as e:
        print(f"❌ Error starting React app: {e}")
        return None

def start_api_bridge():
    """Start the API bridge service"""
    try:
        print("🚀 Starting API Bridge...")
        
        # Check if api_bridge_with_database.py exists
        api_script = 'api_bridge_with_database.py'
        if not Path(api_script).exists():
            api_script = 'api_bridge.py'
        
        if not Path(api_script).exists():
            print(f"❌ API bridge script not found")
            return None
        
        print(f"📄 Using API script: {api_script}")
        
        process = subprocess.Popen(
            [sys.executable, api_script],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        time.sleep(2)
        if process.poll() is None:
            print("✅ API Bridge started successfully")
            return process
        else:
            stdout, stderr = process.communicate()
            print(f"❌ Failed to start API Bridge: {stderr}")
            return None
            
    except Exception as e:
        print(f"❌ Error starting API Bridge: {e}")
        return None

def open_browser(url):
    """Open browser with the application"""
    try:
        import webbrowser
        webbrowser.open(url)
        print(f"🌐 Opened browser to {url}")
    except Exception as e:
        print(f"⚠️ Error opening browser: {e}")

def main():
    """Main startup sequence"""
    print("🚀 LinkedIn MCP Server - Auto Startup")
    print("=" * 50)
    
    # Kill all required ports before anything else
    kill_all_required_ports()
    
    # Check dependencies
    if not check_dependencies():
        print("\n❌ Dependency check failed. Please install required dependencies.")
        return False
    
    # Install npm dependencies
    if not install_npm_dependencies():
        print("\n❌ Failed to install npm dependencies.")
        return False
    
    # Find available port
    print("\n🔍 Finding available port...")
    available_port = find_available_port(3000, 10)
    
    if not available_port:
        print("❌ No available ports found in range 3000-3009")
        return False
    
    print(f"✅ Found available port: {available_port}")
    
    # Start API Bridge in background
    api_process = start_api_bridge()
    
    # Start React app
    react_process = start_react_app(available_port)
    
    if react_process:
        print()
        print(f"🌐 React app is running on: http://localhost:{available_port}")
        print("📝 Press Ctrl+C to stop the server")
        print()
        
        # Open browser
        open_browser(f"http://localhost:{available_port}")
        
        try:
            # Keep the process running
            react_process.wait()
        except KeyboardInterrupt:
            print("\n🛑 Stopping React app...")
            react_process.terminate()
            react_process.wait()
            print("✅ React app stopped")
            
            # Also stop API bridge if running
            if api_process and api_process.poll() is None:
                print("🛑 Stopping API Bridge...")
                api_process.terminate()
                api_process.wait()
                print("✅ API Bridge stopped")
    else:
        print("❌ Failed to start React app")
        return False
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n🛑 Startup interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1) 