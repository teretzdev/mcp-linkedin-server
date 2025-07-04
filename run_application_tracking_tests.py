#!/usr/bin/env python3
"""
Application Tracking Test Runner
Run comprehensive tests for enhanced application tracking features
"""

import subprocess
import sys
import os
from pathlib import Path

def run_application_tracking_tests():
    """Run all application tracking tests"""
    print("🚀 Running Application Tracking Test Suite")
    print("=" * 50)
    
    # Test categories to run
    test_categories = [
        "application_tracking",
        "follow_ups", 
        "analytics",
        "frontend_components",
        "integration",
        "performance"
    ]
    
    total_tests = 0
    passed_tests = 0
    failed_tests = 0
    
    for category in test_categories:
        print(f"\n📋 Running {category.replace('_', ' ').title()} Tests...")
        print("-" * 40)
        
        try:
            # Run tests for this category
            result = subprocess.run([
                sys.executable, "-m", "pytest", 
                "test_application_tracking.py",
                "-m", category,
                "-v",
                "--tb=short"
            ], capture_output=True, text=True, cwd=Path(__file__).parent)
            
            # Parse results
            output_lines = result.stdout.split('\n')
            for line in output_lines:
                if '::' in line and 'PASSED' in line:
                    passed_tests += 1
                    total_tests += 1
                    print(f"✅ {line.split('::')[1].split(' ')[0]}")
                elif '::' in line and 'FAILED' in line:
                    failed_tests += 1
                    total_tests += 1
                    print(f"❌ {line.split('::')[1].split(' ')[0]}")
                elif '::' in line and 'ERROR' in line:
                    failed_tests += 1
                    total_tests += 1
                    print(f"💥 {line.split('::')[1].split(' ')[0]}")
            
            if result.stderr:
                print(f"⚠️  Warnings: {result.stderr}")
                
        except Exception as e:
            print(f"❌ Error running {category} tests: {e}")
            failed_tests += 1
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {failed_tests}")
    
    if total_tests > 0:
        success_rate = (passed_tests / total_tests) * 100
        print(f"Success Rate: {success_rate:.1f}%")
        
        if success_rate >= 90:
            print("🎉 Excellent! Application tracking features are working well!")
        elif success_rate >= 80:
            print("👍 Good! Most application tracking features are working.")
        elif success_rate >= 70:
            print("⚠️  Fair. Some application tracking features need attention.")
        else:
            print("🚨 Poor. Application tracking features need significant work.")
    
    return failed_tests == 0

def run_specific_test(test_name):
    """Run a specific test by name"""
    print(f"🎯 Running specific test: {test_name}")
    
    try:
        result = subprocess.run([
            sys.executable, "-m", "pytest", 
            "test_application_tracking.py",
            "-k", test_name,
            "-v",
            "--tb=long"
        ], cwd=Path(__file__).parent)
        
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error running test {test_name}: {e}")
        return False

def run_component_tests():
    """Run tests for specific components"""
    components = {
        "applications": "TestApplicationTracking",
        "follow_ups": "TestFollowUpTracking", 
        "analytics": "TestApplicationAnalytics",
        "frontend": "TestApplicationTrackingComponents",
        "integration": "TestApplicationTrackingIntegration",
        "performance": "TestApplicationTrackingPerformance"
    }
    
    print("🔧 Running Component Tests")
    print("=" * 40)
    
    for component, test_class in components.items():
        print(f"\n📦 Testing {component} component...")
        success = run_specific_test(test_class)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {component} component")

def main():
    """Main test runner"""
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "all":
            success = run_application_tracking_tests()
            sys.exit(0 if success else 1)
        elif command == "components":
            run_component_tests()
        elif command == "help":
            print("""
Application Tracking Test Runner

Usage:
  python run_application_tracking_tests.py [command]

Commands:
  all         - Run all application tracking tests
  components  - Run tests for specific components
  help        - Show this help message

Examples:
  python run_application_tracking_tests.py all
  python run_application_tracking_tests.py components
            """)
        else:
            # Try to run as specific test name
            success = run_specific_test(command)
            sys.exit(0 if success else 1)
    else:
        # Default: run all tests
        success = run_application_tracking_tests()
        sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 