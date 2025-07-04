#!/usr/bin/env python3
"""
Test script to verify startup fixes
"""

import sys
import subprocess
import time
from pathlib import Path

def test_psutil_fix():
    """Test the psutil Windows compatibility fix"""
    print("🧪 Testing psutil Windows compatibility fix...")
    
    try:
        from auto_startup import AutoStartup
        startup = AutoStartup()
        
        # Test the kill_process_on_port function
        result = startup.kill_process_on_port(9999)  # Use a port that shouldn't be in use
        print(f"✅ psutil fix test passed: {result}")
        return True
    except Exception as e:
        print(f"❌ psutil fix test failed: {e}")
        return False

def test_node_check():
    """Test Node.js installation check"""
    print("🧪 Testing Node.js installation check...")
    
    try:
        from auto_startup import AutoStartup
        startup = AutoStartup()
        
        # Test the check_node_installation function
        result = startup.check_node_installation()
        print(f"✅ Node.js check test passed: {result}")
        return True
    except Exception as e:
        print(f"❌ Node.js check test failed: {e}")
        return False

def test_env_creation():
    """Test environment file creation"""
    print("🧪 Testing environment file creation...")
    
    try:
        from auto_startup import AutoStartup
        startup = AutoStartup()
        
        # Test the create_env_if_missing function
        result = startup.create_env_if_missing()
        print(f"✅ Environment creation test passed: {result}")
        return True
    except Exception as e:
        print(f"❌ Environment creation test failed: {e}")
        return False

def test_port_availability():
    """Test port availability check"""
    print("🧪 Testing port availability check...")
    
    try:
        from auto_startup import AutoStartup
        startup = AutoStartup()
        
        # Test the check_port_available function
        result = startup.check_port_available(9999)
        print(f"✅ Port availability test passed: {result}")
        return True
    except Exception as e:
        print(f"❌ Port availability test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("🧪 Testing Startup Fixes")
    print("=" * 60)
    
    tests = [
        ("psutil Windows Compatibility", test_psutil_fix),
        ("Node.js Installation Check", test_node_check),
        ("Environment File Creation", test_env_creation),
        ("Port Availability Check", test_port_availability)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Print summary
    print("\n" + "=" * 60)
    print("📋 TEST RESULTS")
    print("=" * 60)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:<30} {status}")
        if result:
            passed += 1
    
    print("=" * 60)
    print(f"Results: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("\n🎉 All startup fixes are working!")
        print("\nYou can now try running:")
        print("python auto_startup.py")
    else:
        print("\n⚠️ Some tests failed. Please check the errors above.")
    
    return passed == len(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 