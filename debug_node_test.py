#!/usr/bin/env python3
"""
Debug script for Node.js test issue
"""

import subprocess
import sys
import os

def test_node_detection():
    """Test Node.js detection"""
    print("Testing Node.js detection...")
    
    # Test 1: Direct command
    print("\n1. Testing direct command:")
    try:
        result = subprocess.run(["node", "--version"], 
                              capture_output=True, text=True, timeout=10)
        print(f"   Return code: {result.returncode}")
        print(f"   Output: {result.stdout.strip()}")
        print(f"   Error: {result.stderr.strip()}")
        print(f"   Success: {result.returncode == 0}")
    except Exception as e:
        print(f"   Exception: {e}")
    
    # Test 2: Check PATH
    print("\n2. Checking PATH:")
    path = os.environ.get('PATH', '')
    print(f"   PATH contains 'node': {'node' in path.lower()}")
    
    # Test 3: Try with shell=True
    print("\n3. Testing with shell=True:")
    try:
        result = subprocess.run("node --version", 
                              shell=True, capture_output=True, text=True, timeout=10)
        print(f"   Return code: {result.returncode}")
        print(f"   Output: {result.stdout.strip()}")
        print(f"   Error: {result.stderr.strip()}")
        print(f"   Success: {result.returncode == 0}")
    except Exception as e:
        print(f"   Exception: {e}")
    
    # Test 4: Check if node is in PATH
    print("\n4. Checking if node is executable:")
    try:
        import shutil
        node_path = shutil.which("node")
        print(f"   Node path: {node_path}")
        print(f"   Node found: {node_path is not None}")
    except Exception as e:
        print(f"   Exception: {e}")

if __name__ == "__main__":
    test_node_detection() 