#!/usr/bin/env python3
"""
Test script to demonstrate port conflict resolution
"""

import time
import subprocess
import threading
from start_frontend_auto import find_available_port, kill_process_on_port

def test_port_conflict_resolution():
    print("🧪 Testing Port Conflict Resolution")
    print("=" * 50)
    
    # Test 1: Find available port
    print("\n1. Testing port availability detection...")
    port = find_available_port(3000, 5)
    print(f"✅ Found available port: {port}")
    
    # Test 2: Kill processes on specific ports
    print("\n2. Testing process termination on ports...")
    for test_port in [3000, 3001, 3002]:
        kill_process_on_port(test_port)
        print(f"✅ Checked port {test_port}")
    
    # Test 3: Simulate multiple React starts
    print("\n3. Testing multiple React app starts...")
    
    def start_react_on_port(port_num):
        """Start a React app on a specific port"""
        try:
            env = os.environ.copy()
            env['PORT'] = str(port_num)
            process = subprocess.Popen(
                ['npm', 'start'],
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            print(f"🚀 Started React on port {port_num} (PID: {process.pid})")
            return process
        except Exception as e:
            print(f"❌ Failed to start on port {port_num}: {e}")
            return None
    
    # Start multiple React instances in threads
    processes = []
    threads = []
    
    for i in range(3):
        port = 3000 + i
        thread = threading.Thread(target=lambda p=port: start_react_on_port(p))
        threads.append(thread)
        thread.start()
        time.sleep(2)  # Give each process time to start
    
    print("\n⏳ Waiting for processes to start...")
    time.sleep(5)
    
    # Check what's running
    print("\n📊 Current React processes:")
    try:
        result = subprocess.run(['netstat', '-ano'], capture_output=True, text=True)
        lines = result.stdout.split('\n')
        for line in lines:
            if ':300' in line and 'LISTENING' in line:
                print(f"  {line.strip()}")
    except Exception as e:
        print(f"Error checking processes: {e}")
    
    # Cleanup
    print("\n🧹 Cleaning up test processes...")
    for port in [3000, 3001, 3002]:
        kill_process_on_port(port)
    
    print("\n✅ Port conflict resolution test completed!")

if __name__ == "__main__":
    import os
    test_port_conflict_resolution() 