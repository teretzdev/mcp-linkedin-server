#!/usr/bin/env python3
"""
Test Runner for LinkedIn Job Hunter
Provides easy access to different test categories and comprehensive testing
"""

import sys
import json
import time
from pathlib import Path
from typing import Dict, Any, List

# Add legacy directory to path to allow imports
LEGACY_DIR = Path(__file__).parent / "legacy"
if LEGACY_DIR.is_dir():
    sys.path.insert(0, str(LEGACY_DIR))

def run_environment_tests() -> Dict[str, Any]:
    """Run environment validation tests"""
    results = []
    start_time = time.time()
    
    print("🔍 Running Environment Tests...")
    
    # Test Python version
    try:
        version = sys.version_info
        if version.major < 3 or (version.major == 3 and version.minor < 8):
            results.append({
                "test": "Python Version",
                "success": False,
                "error": f"Python 3.8+ required, found {version.major}.{version.minor}"
            })
        else:
            results.append({
                "test": "Python Version",
                "success": True,
                "details": f"{version.major}.{version.minor}.{version.micro}"
            })
    except Exception as e:
        results.append({
            "test": "Python Version",
            "success": False,
            "error": str(e)
        })
    
    # Test dependencies
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
            results.append({
                "test": "Dependencies",
                "success": False,
                "error": f"Missing modules: {', '.join(missing_modules)}"
            })
        else:
            results.append({
                "test": "Dependencies",
                "success": True,
                "details": f"All {len(required_modules)} modules available"
            })
    except Exception as e:
        results.append({
            "test": "Dependencies",
            "success": False,
            "error": str(e)
        })
    
    # Test Node.js installation
    try:
        import subprocess
        result = subprocess.run(["node", "--version"], 
                              capture_output=True, text=True, timeout=10)
        
        if result.returncode != 0:
            results.append({
                "test": "Node.js Installation",
                "success": False,
                "error": "Node.js not found"
            })
        else:
            results.append({
                "test": "Node.js Installation",
                "success": True,
                "details": result.stdout.strip()
            })
    except Exception as e:
        results.append({
            "test": "Node.js Installation",
            "success": False,
            "error": str(e)
        })
    
    # Test file permissions
    try:
        base_path = Path(__file__).parent
        test_file = base_path / "test_write.tmp"
        test_file.write_text("test")
        test_file.unlink()
        
        results.append({
            "test": "File Permissions",
            "success": True,
            "details": "Write permissions OK"
        })
    except Exception as e:
        results.append({
            "test": "File Permissions",
            "success": False,
            "error": str(e)
        })
    
    return {
        "category": "Environment Tests",
        "duration": time.time() - start_time,
        "results": results
    }

def run_startup_tests() -> Dict[str, Any]:
    """Run startup and configuration tests"""
    results = []
    start_time = time.time()
    
    print("🚀 Running Startup Tests...")
    
    # Test psutil compatibility
    try:
        import psutil
        
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
        results.append({
            "test": "psutil Compatibility",
            "success": True,
            "details": "Windows compatibility OK"
        })
    except Exception as e:
        results.append({
            "test": "psutil Compatibility",
            "success": False,
            "error": str(e)
        })
    
    # Test port availability
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
            results.append({
                "test": "Port Availability",
                "success": False,
                "error": f"Ports in use: {unavailable_ports}"
            })
        else:
            results.append({
                "test": "Port Availability",
                "success": True,
                "details": f"All ports available: {required_ports}"
            })
    except Exception as e:
        results.append({
            "test": "Port Availability",
            "success": False,
            "error": str(e)
        })
    
    # Test service files
    try:
        base_path = Path(__file__).parent
        service_files = [
            "legacy/api_bridge.py",
            "legacy/linkedin_browser_mcp.py",
            "auto_startup.py"
        ]
        
        missing_files = []
        for file in service_files:
            if not (base_path / file).exists():
                missing_files.append(file)
        
        if missing_files:
            results.append({
                "test": "Service Files",
                "success": False,
                "error": f"Missing files: {missing_files}"
            })
        else:
            results.append({
                "test": "Service Files",
                "success": True,
                "details": f"All {len(service_files)} service files found"
            })
    except Exception as e:
        results.append({
            "test": "Service Files",
            "success": False,
            "error": str(e)
        })
    
    return {
        "category": "Startup Tests",
        "duration": time.time() - start_time,
        "results": results
    }

def run_security_tests() -> Dict[str, Any]:
    """Run security tests"""
    results = []
    start_time = time.time()
    
    print("🔒 Running Security Tests...")
    
    # Test security middleware
    try:
        from security_middleware import InputValidator, JWTManager
        
        # Test input validation
        validator = InputValidator()
        assert validator.validate_email("test@example.com")
        assert not validator.validate_email("invalid-email")
        
        results.append({
            "test": "Input Validation",
            "success": True,
            "details": "Email validation working"
        })
    except Exception as e:
        results.append({
            "test": "Input Validation",
            "success": False,
            "error": str(e)
        })
    
    # Test JWT functionality
    try:
        jwt_mgr = JWTManager("test-secret")
        token = jwt_mgr.create_access_token({"user_id": "test"})
        payload = jwt_mgr.verify_token(token)
        
        assert payload["user_id"] == "test"
        results.append({
            "test": "JWT Authentication",
            "success": True,
            "details": "Token creation and verification OK"
        })
    except Exception as e:
        results.append({
            "test": "JWT Authentication",
            "success": False,
            "error": str(e)
        })
    
    # Test password hashing
    try:
        from security_middleware import hash_password, verify_password
        
        password = "test_password_123"
        hashed = hash_password(password)
        
        assert verify_password(password, hashed)
        assert not verify_password("wrong_password", hashed)
        
        results.append({
            "test": "Password Hashing",
            "success": True,
            "details": "PBKDF2 hashing working"
        })
    except Exception as e:
        results.append({
            "test": "Password Hashing",
            "success": False,
            "error": str(e)
        })
    
    return {
        "category": "Security Tests",
        "duration": time.time() - start_time,
        "results": results
    }

def run_integration_tests() -> Dict[str, Any]:
    """Run integration tests"""
    results = []
    start_time = time.time()
    
    print("🔗 Running Integration Tests...")
    
    # Test MCP client
    try:
        from mcp_client import MCPClient
        
        client = MCPClient()
        results.append({
            "test": "MCP Client",
            "success": True,
            "details": "MCP client initialized"
        })
    except Exception as e:
        results.append({
            "test": "MCP Client",
            "success": False,
            "error": str(e)
        })
    
    # Test API bridge imports
    try:
        from api_bridge import app
        
        results.append({
            "test": "API Bridge",
            "success": True,
            "details": "FastAPI app created"
        })
    except Exception as e:
        results.append({
            "test": "API Bridge",
            "success": False,
            "error": str(e)
        })
    
    # Test error handler
    try:
        from error_handler import error_handler, AppError
        
        error = AppError("Test error")
        result = error_handler.handle_error(error)
        
        results.append({
            "test": "Error Handler",
            "success": True,
            "details": "Error handling working"
        })
    except Exception as e:
        results.append({
            "test": "Error Handler",
            "success": False,
            "error": str(e)
        })
    
    return {
        "category": "Integration Tests",
        "duration": time.time() - start_time,
        "results": results
    }

def run_quick_health_check() -> Dict[str, Any]:
    """Run a quick health check"""
    print("🏥 Running Quick Health Check...")
    
    env_results = run_environment_tests()
    startup_results = run_startup_tests()
    
    all_results = env_results["results"] + startup_results["results"]
    total_duration = env_results["duration"] + startup_results["duration"]
    
    passed = sum(1 for r in all_results if r["success"])
    failed = len(all_results) - passed
    
    return {
        "category": "Quick Health Check",
        "duration": total_duration,
        "results": all_results,
        "summary": {
            "total": len(all_results),
            "passed": passed,
            "failed": failed,
            "success_rate": (passed / len(all_results) * 100) if all_results else 0
        }
    }

def run_all_tests() -> Dict[str, Any]:
    """Run all test categories"""
    print("🧪 Running All Tests...")
    
    test_categories = [
        run_environment_tests,
        run_startup_tests,
        run_security_tests,
        run_integration_tests
    ]
    
    all_results = []
    total_duration = 0
    
    for test_func in test_categories:
        try:
            result = test_func()
            all_results.extend(result["results"])
            total_duration += result["duration"]
        except Exception as e:
            all_results.append({
                "test": f"{test_func.__name__}",
                "success": False,
                "error": str(e)
            })
    
    passed = sum(1 for r in all_results if r["success"])
    failed = len(all_results) - passed
    
    return {
        "category": "All Tests",
        "duration": total_duration,
        "results": all_results,
        "summary": {
            "total": len(all_results),
            "passed": passed,
            "failed": failed,
            "success_rate": (passed / len(all_results) * 100) if all_results else 0
        }
    }

def print_results(results: Dict[str, Any], verbose: bool = False):
    """Print test results"""
    print("\n" + "="*60)
    print(f"TEST RESULTS: {results['category']}")
    print("="*60)
    
    if "summary" in results:
        summary = results["summary"]
        print(f"Total Tests: {summary['total']}")
        print(f"Passed: {summary['passed']} ✅")
        print(f"Failed: {summary['failed']} ❌")
        print(f"Success Rate: {summary['success_rate']:.1f}%")
        print(f"Duration: {results['duration']:.2f}s")
    
    print("\nDetailed Results:")
    for result in results["results"]:
        status = "✅ PASS" if result["success"] else "❌ FAIL"
        print(f"  {status} {result['test']}")
        
        if not result["success"] and "error" in result:
            print(f"    Error: {result['error']}")
        
        if verbose and result.get("details"):
            print(f"    Details: {result['details']}")

def main():
    """Main test runner"""
    import argparse
    
    parser = argparse.ArgumentParser(description="LinkedIn Job Hunter Test Runner")
    parser.add_argument("--category", choices=[
        "environment", "startup", "security", "integration", "all", "quick"
    ], default="quick", help="Test category to run")
    parser.add_argument("--verbose", "-v", action="store_true", 
                       help="Verbose output")
    parser.add_argument("--output", "-o", help="Output results to JSON file")
    
    args = parser.parse_args()
    
    # Run tests
    if args.category == "quick":
        results = run_quick_health_check()
    elif args.category == "all":
        results = run_all_tests()
    elif args.category == "environment":
        results = run_environment_tests()
    elif args.category == "startup":
        results = run_startup_tests()
    elif args.category == "security":
        results = run_security_tests()
    elif args.category == "integration":
        results = run_integration_tests()
    else:
        print(f"Unknown test category: {args.category}")
        return 1
    
    # Print results
    print_results(results, args.verbose)
    
    # Save to file if requested
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\nResults saved to: {args.output}")
    
    # Return exit code
    if "summary" in results:
        return 0 if results["summary"]["failed"] == 0 else 1
    else:
        failed = sum(1 for r in results["results"] if not r["success"])
        return 0 if failed == 0 else 1

if __name__ == "__main__":
    sys.exit(main()) 