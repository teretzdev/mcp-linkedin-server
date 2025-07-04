# 🧪 Testing Guide - LinkedIn Job Hunter

## 🧪 Overview

This guide explains how to use the comprehensive test suite for the LinkedIn Job Hunter application. The test suite covers environment validation, startup issues, security, integration, and end-to-end testing with automated test execution and detailed reporting.

## 🚀 Quick Start

### Run Quick Health Check
```bash
# Basic health check (recommended for first run)
python test_runner.py --category quick

# Or use the comprehensive test framework
python test_framework.py --quick
```

### Run All Tests
```bash
# Run all test categories
python test_runner.py --category all

# Or use the comprehensive framework
python test_framework.py --category all --verbose
```

### Automated Testing
```bash
# Run tests with automatic fixes
python test_runner.py --auto-fix

# Run tests and generate report
python test_runner.py --category all --report
```

## 📋 Test Categories

### 1. Environment Tests
Validates the basic environment setup and dependencies.

**Tests:**
- Python version compatibility (3.8+)
- Required dependencies installation
- Node.js and npm availability
- File permissions and access
- Environment variables configuration
- Virtual environment activation

**Run:**
```bash
python test_runner.py --category environment
```

**Example Output:**
```
✅ Python Version: 3.9.7 (Compatible)
✅ Required Dependencies: All installed
✅ Node.js: v16.15.0 (Compatible)
✅ npm: 8.5.5 (Available)
✅ Environment Variables: Configured
✅ File Permissions: Valid
```

### 2. Startup Tests
Tests the critical startup functionality and Windows compatibility.

**Tests:**
- psutil Windows compatibility (fixes the startup error)
- Port availability (8001, 8002, 8003, 3000)
- Service file existence and permissions
- Configuration loading and validation
- Process management capabilities
- Service startup sequence

**Run:**
```bash
python test_runner.py --category startup
```

**Example Output:**
```
✅ psutil Windows Compatibility: Fixed
✅ Port 8001: Available
✅ Port 8002: Available
✅ Port 3000: Available
✅ Service Files: All present
✅ Configuration: Valid
```

### 3. Security Tests
Validates security implementations and protection mechanisms.

**Tests:**
- JWT authentication functionality
- Password hashing and verification
- Input validation and sanitization
- Rate limiting implementation
- Security headers configuration
- Error handling security
- XSS and SQL injection prevention

**Run:**
```bash
python test_runner.py --category security
```

**Example Output:**
```
✅ JWT Authentication: Working
✅ Password Hashing: Secure
✅ Input Validation: Comprehensive
✅ Rate Limiting: Active
✅ Security Headers: Configured
✅ Error Handling: Secure
```

### 4. Integration Tests
Tests component interactions and service communication.

**Tests:**
- MCP client functionality
- API bridge integration
- Database connectivity and operations
- Service communication protocols
- Error propagation handling
- Data flow validation

**Run:**
```bash
python test_framework.py --category integration
```

### 5. API Tests
Tests API endpoints and response handling.

**Tests:**
- Authentication endpoints
- Job search endpoints
- Application tracking endpoints
- Automation endpoints
- Error response handling
- Rate limiting enforcement

**Run:**
```bash
python test_framework.py --category api
```

### 6. Performance Tests
Tests performance characteristics and resource usage.

**Tests:**
- Response times under load
- Concurrent request handling
- Memory usage monitoring
- CPU utilization tracking
- Database query performance
- Browser automation efficiency

**Run:**
```bash
python test_framework.py --category performance
```

### 7. End-to-End Tests
Tests complete user workflows and real-world scenarios.

**Tests:**
- User journey (login → search → apply → track)
- Automation workflow validation
- Error recovery scenarios
- Cross-browser compatibility
- Mobile responsiveness

**Run:**
```bash
python test_framework.py --category e2e
```

## 🔧 Test Configuration

### Test Configuration File
The test suite uses `test_config.json` for configuration:

```json
{
  "test_configuration": {
    "environment": {
      "python_min_version": "3.8.0",
      "required_modules": ["fastapi", "uvicorn", "playwright", "psutil", "PyJWT"],
      "required_ports": [8001, 8002, 8003, 3000],
      "node_min_version": "16.0.0",
      "npm_min_version": "8.0.0"
    },
    "performance": {
      "max_response_time": 5.0,
      "max_memory_usage": 512,
      "max_cpu_usage": 80,
      "concurrent_requests": 10
    },
    "security": {
      "password_min_length": 8,
      "rate_limit_requests": 100,
      "jwt_expire_minutes": 30,
      "max_login_attempts": 5
    },
    "automation": {
      "browser_timeout": 30,
      "page_load_timeout": 10,
      "retry_attempts": 3,
      "screenshot_on_failure": true
    }
  }
}
```

### Environment-Specific Testing
```bash
# Development testing
python test_runner.py --environment development

# Production testing
python test_runner.py --environment production

# Staging testing
python test_runner.py --environment staging
```

## 📊 Understanding Test Results

### Test Result Format
```json
{
  "test_name": "Python Version Check",
  "category": "environment",
  "success": true,
  "details": "Python 3.9.7",
  "error": null,
  "duration": 0.05,
  "timestamp": "2024-01-15T10:30:15Z"
}
```

### Summary Format
```json
{
  "total_tests": 25,
  "passed": 23,
  "failed": 2,
  "skipped": 0,
  "success_rate": 92.0,
  "total_duration": 15.23,
  "categories": {
    "environment": {"total": 6, "passed": 6, "failed": 0},
    "startup": {"total": 5, "passed": 5, "failed": 0},
    "security": {"total": 8, "passed": 7, "failed": 1},
    "integration": {"total": 6, "passed": 5, "failed": 1}
  }
}
```

### Exit Codes
- `0`: All tests passed
- `1`: Some tests failed
- `2`: Configuration error
- `3`: Environment setup failed

## 🚨 Common Test Failures and Solutions

### 1. Python Version Error
**Error:** `Python 3.8+ required, found 3.7.x`
**Solution:** Upgrade Python to 3.8 or higher
```bash
# Check current version
python --version

# Download and install Python 3.8+ from python.org
```

### 2. Missing Dependencies
**Error:** `Missing modules: fastapi, playwright, PyJWT`
**Solution:** Install missing dependencies
```bash
# Install all dependencies
pip install -r requirements.txt

# Install specific missing packages
pip install fastapi playwright PyJWT
```

### 3. Node.js Not Found
**Error:** `Node.js not found or version incompatible`
**Solution:** Install or update Node.js
```bash
# Check current version
node --version
npm --version

# Download from https://nodejs.org/
# Install Node.js 16+ and npm
```

### 4. Ports in Use
**Error:** `Ports in use: [8001, 8002]`
**Solution:** Stop services using those ports
```bash
# Find processes using ports
netstat -ano | findstr :8001
netstat -ano | findstr :8002

# Kill processes (replace PID with actual process ID)
taskkill /PID <PID> /F

# Or use automated port management
python test_runner.py --auto-fix
```

### 5. psutil Compatibility Error
**Error:** `invalid attr name 'connections'`
**Solution:** This is now automatically fixed in the codebase
```bash
# The fix is already implemented
# Run tests to verify
python test_runner.py --category startup
```

### 6. JWT Module Missing
**Error:** `ModuleNotFoundError: No module named 'PyJWT'`
**Solution:** Install PyJWT
```bash
pip install PyJWT
```

## 🔄 Automated Testing Features

### Auto-Fix Capability
The test suite can automatically fix common issues:

```bash
# Run tests with automatic fixes
python test_runner.py --auto-fix

# Fix specific issues
python test_runner.py --fix-ports
python test_runner.py --fix-dependencies
python test_runner.py --fix-configuration
```

### Continuous Integration
```yaml
# .github/workflows/test.yml
name: Test Suite
on: [push, pull_request]
jobs:
  test:
    runs-on: windows-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.9'
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        npm install
    - name: Run tests
      run: python test_runner.py --category all --report
```

### Test Reporting
```bash
# Generate detailed report
python test_runner.py --category all --report --format html

# Generate JSON report
python test_runner.py --category all --report --format json

# Generate summary report
python test_runner.py --category all --report --format summary
```

## 🧪 Advanced Testing

### Load Testing
```bash
# Run load tests
python test_runner.py --category performance --load-test

# Custom load parameters
python test_runner.py --category performance --load-test --users 50 --duration 300
```

### Security Penetration Testing
```bash
# Run security penetration tests
python test_runner.py --category security --penetration-test

# Run specific security tests
python test_runner.py --category security --test xss
python test_runner.py --category security --test sql-injection
```

### Browser Compatibility Testing
```bash
# Test multiple browsers
python test_runner.py --category e2e --browsers chrome,firefox,edge

# Test mobile browsers
python test_runner.py --category e2e --mobile
```

## 📈 Test Metrics and Analytics

### Performance Metrics
- **Test Execution Time**: Track how long tests take to run
- **Success Rate**: Monitor test pass/fail ratios
- **Resource Usage**: Track memory and CPU usage during tests
- **Coverage**: Measure code coverage by tests

### Test Analytics Dashboard
```bash
# Generate analytics dashboard
python test_analytics.py --generate-dashboard

# View test trends
python test_analytics.py --trends --days 30

# Export test metrics
python test_analytics.py --export --format csv
```

## 🔧 Custom Test Development

### Creating Custom Tests
```python
# custom_test.py
from test_framework import BaseTest

class CustomTest(BaseTest):
    def test_custom_functionality(self):
        """Test custom functionality"""
        # Test implementation
        result = self.custom_function()
        self.assertIsNotNone(result)
        self.assertEqual(result.status, "success")
    
    def custom_function(self):
        # Custom test logic
        return {"status": "success"}
```

### Test Hooks
```python
# test_hooks.py
def before_test(test_name):
    """Run before each test"""
    print(f"Starting test: {test_name}")

def after_test(test_name, result):
    """Run after each test"""
    print(f"Completed test: {test_name} with result: {result}")
```

## 🚀 Test Optimization

### Parallel Testing
```bash
# Run tests in parallel
python test_runner.py --parallel --workers 4

# Parallel testing with specific categories
python test_runner.py --category environment,startup --parallel
```

### Test Caching
```bash
# Enable test caching
python test_runner.py --cache

# Clear test cache
python test_runner.py --clear-cache
```

### Selective Testing
```bash
# Run only failed tests
python test_runner.py --failed-only

# Run tests matching pattern
python test_runner.py --pattern "security"

# Skip specific tests
python test_runner.py --skip "performance"
```

## 📚 Additional Resources

### Test Documentation
- [Test Framework API](docs/test-framework-api.md)
- [Custom Test Development](docs/custom-tests.md)
- [Performance Testing Guide](docs/performance-testing.md)
- [Security Testing Guide](docs/security-testing.md)

### External Testing Tools
- [Playwright Testing](https://playwright.dev/python/docs/intro)
- [Pytest Framework](https://docs.pytest.org/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)

---

**Remember**: Regular testing ensures your application remains stable and secure. Run tests frequently and address failures promptly. 