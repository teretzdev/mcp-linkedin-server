#!/usr/bin/env python3
"""
User Story Test Runner
Executes comprehensive tests for the login, job search, and Easy Apply user story
"""

import subprocess
import sys
import os
import time
from pathlib import Path

def run_tests_with_pytest(test_file, markers=None, verbose=True):
    """Run tests using pytest with specified markers"""
    cmd = [
        sys.executable, "-m", "pytest",
        test_file,
        "-v" if verbose else "",
        "--tb=short",
        "--strict-markers"
    ]
    
    if markers:
        cmd.extend(["-m", markers])
    
    # Remove empty strings
    cmd = [arg for arg in cmd if arg]
    
    print(f"Running: {' '.join(cmd)}")
    print("=" * 60)
    
    try:
        result = subprocess.run(cmd, capture_output=False, text=True)
        return result.returncode == 0
    except Exception as e:
        print(f"Error running tests: {e}")
        return False

def run_specific_story_tests():
    """Run tests for specific user story components"""
    test_file = "user_story_tests.py"
    
    if not Path(test_file).exists():
        print(f"Error: Test file {test_file} not found!")
        return False
    
    print("🧪 User Story Test Suite")
    print("=" * 60)
    
    # Test categories
    test_categories = [
        ("Authentication", "auth"),
        ("Job Search", "search"),
        ("Easy Apply", "easy_apply"),
        ("Application Tracking", "tracking"),
        ("End-to-End", "e2e"),
        ("Performance", "performance"),
        ("Security", "security")
    ]
    
    results = {}
    
    for category, marker in test_categories:
        print(f"\n📋 Running {category} Tests...")
        print("-" * 40)
        
        success = run_tests_with_pytest(test_file, f"user_story and {marker}")
        results[category] = success
        
        if success:
            print(f"✅ {category} tests passed")
        else:
            print(f"❌ {category} tests failed")
    
    # Run all user story tests together
    print(f"\n🚀 Running All User Story Tests...")
    print("-" * 40)
    
    all_success = run_tests_with_pytest(test_file, "user_story")
    results["All Tests"] = all_success
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    for category, success in results.items():
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{category:20} {status}")
    
    return all_success

def run_quick_smoke_tests():
    """Run quick smoke tests for basic functionality"""
    print("🔥 Quick Smoke Tests")
    print("=" * 40)
    
    test_file = "user_story_tests.py"
    
    # Run basic configuration and utility tests
    cmd = [
        sys.executable, "-m", "pytest",
        test_file,
        "-k", "test_user_story_configuration or test_mock_context",
        "-v"
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=False, text=True)
        return result.returncode == 0
    except Exception as e:
        print(f"Error running smoke tests: {e}")
        return False

def check_environment():
    """Check if required environment is set up"""
    print("🔍 Environment Check")
    print("=" * 40)
    
    checks = {
        "Python Version": f"{sys.version_info.major}.{sys.version_info.minor}",
        "Test File Exists": Path("user_story_tests.py").exists(),
        "API Bridge Exists": Path("api_bridge.py").exists(),
        "LinkedIn MCP Exists": Path("linkedin_browser_mcp.py").exists(),
        "Requirements File": Path("requirements.txt").exists(),
        "Package.json": Path("package.json").exists()
    }
    
    for check, value in checks.items():
        status = "✅" if value else "❌"
        print(f"{check:25} {status} {value}")
    
    return all(checks.values())

def main():
    """Main test runner"""
    print("🎯 LinkedIn Job Hunter - User Story Test Runner")
    print("=" * 60)
    
    # Check environment
    if not check_environment():
        print("\n❌ Environment check failed. Please ensure all required files exist.")
        return 1
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "smoke":
            success = run_quick_smoke_tests()
        elif command == "all":
            success = run_specific_story_tests()
        elif command == "auth":
            success = run_tests_with_pytest("user_story_tests.py", "user_story and auth")
        elif command == "search":
            success = run_tests_with_pytest("user_story_tests.py", "user_story and search")
        elif command == "easy-apply":
            success = run_tests_with_pytest("user_story_tests.py", "user_story and easy_apply")
        elif command == "e2e":
            success = run_tests_with_pytest("user_story_tests.py", "user_story and e2e")
        elif command == "performance":
            success = run_tests_with_pytest("user_story_tests.py", "user_story and performance")
        elif command == "security":
            success = run_tests_with_pytest("user_story_tests.py", "user_story and security")
        else:
            print(f"Unknown command: {command}")
            print("Available commands: smoke, all, auth, search, easy-apply, e2e, performance, security")
            return 1
    else:
        # Default: run all tests
        success = run_specific_story_tests()
    
    print(f"\n{'🎉 All tests passed!' if success else '💥 Some tests failed!'}")
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main()) 