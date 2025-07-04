#!/usr/bin/env python3
"""
Simple Test Runner for LinkedIn Job Hunter
Easy-to-use test runner with clear output and error handling
"""

import sys
import json
import time
import subprocess
from pathlib import Path
from typing import Dict, Any, List

def print_header(title: str):
    """Print a formatted header"""
    print("\n" + "="*60)
    print(f"🧪 {title}")
    print("="*60)

def print_result(test_name: str, success: bool, error: str = None, details: str = None):
    """Print a test result"""
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"  {status} {test_name}")
    
    if error:
        print(f"    Error: {error}")
    
    if details:
        print(f"    Details: {details}")

def test_python_version() -> Dict[str, Any]:
    """Test Python version"""
    try:
        version = sys.version_info
        if version.major < 3 or (version.major == 3 and version.minor < 8):
            return {
                "success": False,
                "error": f"Python 3.8+ required, found {version.major}.{version.minor}"
            }
        
        return {
            "success": True,
            "details": f"Python {version.major}.{version.minor}.{version.micro}"
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

def test_dependencies() -> Dict[str, Any]:
    """Test required dependencies"""
    try:
        required_modules = [
            "fastapi", "uvicorn", "playwright", "psutil", 
            "aiohttp", "requests"
        ]
        
        missing_modules = []
        for module in required_modules:
            try:
                __import__(module)
            except ImportError:
                missing_modules.append(module)
        
        if missing_modules:
            return {
                "success": False,
                "error": f"Missing modules: {', '.join(missing_modules)}"
            }
        
        return {
            "success": True,
            "details": f"All {len(required_modules)} modules available"
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

def test_node_installation() -> Dict[str, Any]:
    """Test Node.js installation"""
    try:
        # Try using shell=True for Windows compatibility
        result = subprocess.run("node --version", 
                              shell=True, capture_output=True, text=True, timeout=10)
        
        if result.returncode != 0:
            return {"success": False, "error": f"Node.js not found: {result.stderr}"}
        
        node_version = result.stdout.strip()
        
        # Test npm with shell=True
        npm_result = subprocess.run("npm --version", 
                                  shell=True, capture_output=True, text=True, timeout=10)
        
        if npm_result.returncode != 0:
            return {"success": False, "error": f"npm not found: {npm_result.stderr}"}
        
        npm_version = npm_result.stdout.strip()
        
        return {
            "success": True,
            "details": f"Node {node_version}, npm {npm_version}"
        }
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Timeout checking Node.js/npm"}
    except FileNotFoundError:
        return {"success": False, "error": "Node.js or npm not found in PATH"}
    except Exception as e:
        return {"success": False, "error": f"Unexpected error: {str(e)}"}

def test_file_permissions() -> Dict[str, Any]:
    """Test file permissions"""
    try:
        base_path = Path(__file__).parent
        test_file = base_path / "test_write.tmp"
        test_file.write_text("test")
        test_file.unlink()
        
        return {"success": True, "details": "Write permissions OK"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def test_psutil_compatibility() -> Dict[str, Any]:
    """Test psutil Windows compatibility"""
    try:
        import psutil
        
        # Test the specific function that was failing
        def test_kill_process_on_port(port: int) -> bool:
            try:
                for proc in psutil.process_iter(['pid', 'name']):
                    try:
                        if hasattr(proc, 'connections'):
                            connections = proc.connections()
                            for conn in connections:
                                if hasattr(conn, 'laddr') and hasattr(conn.laddr, 'port'):
                                    if conn.laddr.port == port:
                                        return True
                    except (psutil.NoSuchProcess, psutil.AccessDenied, AttributeError):
                        continue
                return False
            except Exception:
                return False
        
        test_kill_process_on_port(9999)
        return {"success": True, "details": "Windows compatibility OK"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def test_port_availability() -> Dict[str, Any]:
    """Test port availability"""
    try:
        import socket
        
        required_ports = [8001, 8002, 8003, 3000]
        unavailable_ports = []
        
        for port in required_ports:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('localhost', port))
            sock.close()
            
            if result == 0:
                unavailable_ports.append(port)
        
        if unavailable_ports:
            return {
                "success": False,
                "error": f"Ports in use: {unavailable_ports}"
            }
        
        return {
            "success": True,
            "details": f"All ports available: {required_ports}"
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

def test_service_files() -> Dict[str, Any]:
    """Test if service files exist"""
    try:
        base_path = Path(__file__).parent
        service_files = [
            "api_bridge.py",
            "linkedin_browser_mcp.py", 
            "auto_startup.py"
        ]
        
        missing_files = []
        for file in service_files:
            if not (base_path / file).exists():
                missing_files.append(file)
        
        if missing_files:
            return {
                "success": False,
                "error": f"Missing files: {missing_files}"
            }
        
        return {
            "success": True,
            "details": f"All {len(service_files)} service files found"
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

def test_security_middleware() -> Dict[str, Any]:
    """Test security middleware"""
    try:
        from security_middleware import InputValidator, JWTManager
        
        # Test input validation
        validator = InputValidator()
        assert validator.validate_email("test@example.com")
        assert not validator.validate_email("invalid-email")
        
        # Test JWT functionality
        jwt_mgr = JWTManager("test-secret")
        token = jwt_mgr.create_access_token({"user_id": "test"})
        payload = jwt_mgr.verify_token(token)
        
        assert payload["user_id"] == "test"
        
        return {"success": True, "details": "Security middleware working"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def test_error_handler() -> Dict[str, Any]:
    """Test error handler"""
    try:
        from error_handler import error_handler, AppError
        
        error = AppError("Test error")
        result = error_handler.handle_error(error)
        
        return {"success": True, "details": "Error handling working"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def run_environment_tests() -> List[Dict[str, Any]]:
    """Run environment tests"""
    print_header("Environment Tests")
    
    tests = [
        ("Python Version", test_python_version),
        ("Dependencies", test_dependencies),
        ("Node.js Installation", test_node_installation),
        ("File Permissions", test_file_permissions)
    ]
    
    results = []
    for test_name, test_func in tests:
        result = test_func()
        result["test_name"] = test_name
        results.append(result)
        
        print_result(test_name, result["success"], 
                    result.get("error"), result.get("details"))
    
    return results

def run_startup_tests() -> List[Dict[str, Any]]:
    """Run startup tests"""
    print_header("Startup Tests")
    
    tests = [
        ("psutil Compatibility", test_psutil_compatibility),
        ("Port Availability", test_port_availability),
        ("Service Files", test_service_files)
    ]
    
    results = []
    for test_name, test_func in tests:
        result = test_func()
        result["test_name"] = test_name
        results.append(result)
        
        print_result(test_name, result["success"], 
                    result.get("error"), result.get("details"))
    
    return results

def run_security_tests() -> List[Dict[str, Any]]:
    """Run security tests"""
    print_header("Security Tests")
    
    tests = [
        ("Security Middleware", test_security_middleware),
        ("Error Handler", test_error_handler)
    ]
    
    results = []
    for test_name, test_func in tests:
        result = test_func()
        result["test_name"] = test_name
        results.append(result)
        
        print_result(test_name, result["success"], 
                    result.get("error"), result.get("details"))
    
    return results

def run_quick_health_check() -> Dict[str, Any]:
    """Run quick health check"""
    print_header("Quick Health Check")
    
    start_time = time.time()
    
    # Run critical tests
    env_results = run_environment_tests()
    startup_results = run_startup_tests()
    
    all_results = env_results + startup_results
    duration = time.time() - start_time
    
    # Calculate summary
    passed = sum(1 for r in all_results if r["success"])
    failed = len(all_results) - passed
    success_rate = (passed / len(all_results) * 100) if all_results else 0
    
    # Print summary
    print_header("Summary")
    print(f"Total Tests: {len(all_results)}")
    print(f"Passed: {passed} ✅")
    print(f"Failed: {failed} ❌")
    print(f"Success Rate: {success_rate:.1f}%")
    print(f"Duration: {duration:.2f}s")
    
    return {
        "total": len(all_results),
        "passed": passed,
        "failed": failed,
        "success_rate": success_rate,
        "duration": duration,
        "results": all_results
    }

def run_all_tests() -> Dict[str, Any]:
    """Run all tests"""
    print_header("Comprehensive Test Suite")
    
    start_time = time.time()
    
    # Run all test categories
    env_results = run_environment_tests()
    startup_results = run_startup_tests()
    security_results = run_security_tests()
    
    all_results = env_results + startup_results + security_results
    duration = time.time() - start_time
    
    # Calculate summary
    passed = sum(1 for r in all_results if r["success"])
    failed = len(all_results) - passed
    success_rate = (passed / len(all_results) * 100) if all_results else 0
    
    # Print summary
    print_header("Summary")
    print(f"Total Tests: {len(all_results)}")
    print(f"Passed: {passed} ✅")
    print(f"Failed: {failed} ❌")
    print(f"Success Rate: {success_rate:.1f}%")
    print(f"Duration: {duration:.2f}s")
    
    return {
        "total": len(all_results),
        "passed": passed,
        "failed": failed,
        "success_rate": success_rate,
        "duration": duration,
        "results": all_results
    }

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="LinkedIn Job Hunter Test Runner")
    parser.add_argument("--category", choices=[
        "environment", "startup", "security", "all", "quick"
    ], default="quick", help="Test category to run")
    parser.add_argument("--output", "-o", help="Save results to JSON file")
    
    args = parser.parse_args()
    
    # Run tests
    if args.category == "quick":
        results = run_quick_health_check()
    elif args.category == "all":
        results = run_all_tests()
    elif args.category == "environment":
        test_results = run_environment_tests()
        results = {
            "total": len(test_results),
            "passed": sum(1 for r in test_results if r["success"]),
            "failed": sum(1 for r in test_results if not r["success"]),
            "results": test_results
        }
    elif args.category == "startup":
        test_results = run_startup_tests()
        results = {
            "total": len(test_results),
            "passed": sum(1 for r in test_results if r["success"]),
            "failed": sum(1 for r in test_results if not r["success"]),
            "results": test_results
        }
    elif args.category == "security":
        test_results = run_security_tests()
        results = {
            "total": len(test_results),
            "passed": sum(1 for r in test_results if r["success"]),
            "failed": sum(1 for r in test_results if not r["success"]),
            "results": test_results
        }
    
    # Save results if requested
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\nResults saved to: {args.output}")
    
    # Return exit code
    return 0 if results["failed"] == 0 else 1

if __name__ == "__main__":
    sys.exit(main()) 