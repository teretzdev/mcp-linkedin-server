# User Story Testing Guide

## Overview
This guide provides comprehensive instructions for testing the complete user journey from LinkedIn login through job search to Easy Apply functionality.

## 📋 Test Coverage

### User Story Components Tested

1. **Authentication (Story 1)**
   - Login form rendering
   - Credential validation
   - Secure credential storage
   - LinkedIn authentication
   - Session management

2. **Job Search (Story 2)**
   - Search form functionality
   - Filter application
   - Job result display
   - Easy Apply indicators
   - Job saving functionality

3. **Easy Apply (Story 3)**
   - Application form rendering
   - AI-powered answer generation
   - Form validation
   - Application submission
   - Success confirmation

4. **Application Tracking (Story 4)**
   - Applications dashboard
   - Saved jobs management
   - Job recommendations
   - Status tracking

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pytest
- FastAPI TestClient
- Required project dependencies

### Running Tests

#### 1. Quick Smoke Tests
```bash
python run_user_story_tests.py smoke
```
Runs basic configuration and utility tests to verify environment setup.

#### 2. All User Story Tests
```bash
python run_user_story_tests.py all
```
Runs the complete test suite for all user story components.

#### 3. Specific Component Tests
```bash
# Authentication tests only
python run_user_story_tests.py auth

# Job search tests only
python run_user_story_tests.py search

# Easy Apply tests only
python run_user_story_tests.py easy-apply

# End-to-end tests only
python run_user_story_tests.py e2e

# Performance tests only
python run_user_story_tests.py performance

# Security tests only
python run_user_story_tests.py security
```

#### 4. Direct pytest Commands
```bash
# Run all user story tests
pytest user_story_tests.py -m user_story -v

# Run specific category
pytest user_story_tests.py -m "user_story and auth" -v

# Run with coverage
pytest user_story_tests.py -m user_story --cov=. --cov-report=html
```

## 📊 Test Categories

### Authentication Tests (`@pytest.mark.auth`)
- **TC-AUTH-001:** Login form rendering
- **TC-AUTH-002:** Credential validation
- **TC-AUTH-003:** Loading states
- **TC-AUTH-004:** Success/error messages
- **TC-AUTH-005:** Password masking

### Job Search Tests (`@pytest.mark.search`)
- **TC-SEARCH-001:** Search form rendering
- **TC-SEARCH-002:** Query input handling
- **TC-SEARCH-003:** Filter application
- **TC-SEARCH-004:** Job result display
- **TC-SEARCH-005:** Easy Apply badge display
- **TC-SEARCH-006:** Empty results handling
- **TC-SEARCH-007:** Job saving functionality
- **TC-SEARCH-008:** Search loading states

### Easy Apply Tests (`@pytest.mark.easy_apply`)
- **TC-EASY-APPLY-001:** Form rendering with questions
- **TC-EASY-APPLY-002:** Job details display
- **TC-EASY-APPLY-003:** Progress bar functionality
- **TC-EASY-APPLY-004:** AI answer generation
- **TC-EASY-APPLY-005:** Manual answer entry
- **TC-EASY-APPLY-006:** Form validation
- **TC-EASY-APPLY-007:** Application submission
- **TC-EASY-APPLY-008:** Success confirmation

### Application Tracking Tests (`@pytest.mark.tracking`)
- **TC-TRACKING-001:** Applications dashboard
- **TC-TRACKING-002:** Saved jobs management
- **TC-TRACKING-003:** Job recommendations
- **TC-TRACKING-004:** Status tracking

### End-to-End Tests (`@pytest.mark.e2e`)
- **TC-E2E-001:** Complete workflow
- **TC-E2E-002:** Error recovery
- **TC-E2E-003:** Alternative paths
- **TC-E2E-004:** Session persistence
- **TC-E2E-005:** Data consistency

### Performance Tests (`@pytest.mark.performance`)
- **TC-PERF-001:** Job search response time
- **TC-PERF-002:** Easy Apply submission time
- **TC-PERF-003:** Concurrent user handling
- **TC-PERF-004:** Memory usage optimization
- **TC-PERF-005:** API rate limiting

### Security Tests (`@pytest.mark.security`)
- **TC-SEC-001:** Credential encryption
- **TC-SEC-002:** Session management
- **TC-SEC-003:** XSS prevention
- **TC-SEC-004:** CSRF protection
- **TC-SEC-005:** Input validation
- **TC-SEC-006:** API authentication
- **TC-SEC-007:** Data privacy compliance

## 🔧 Test Configuration

### Test Data
The tests use a standardized test configuration defined in `USER_STORY_CONFIG`:

```python
USER_STORY_CONFIG = {
    "test_user": {
        "name": "Sarah Chen",
        "email": "sarah.chen@test.com",
        "password": "testpassword123",
        "experience": "4 years",
        "skills": ["React", "JavaScript", "Node.js"],
        "target_role": "Senior React Developer",
        "location": "Remote"
    },
    "test_job": {
        "title": "Senior React Developer",
        "company": "TechCorp Inc.",
        "location": "San Francisco, CA",
        "salary": "$120,000 - $150,000",
        "easy_apply": True,
        "url": "https://www.linkedin.com/jobs/view/test-senior-react"
    }
}
```

### Mock Context
Tests use a `MockContext` class to simulate MCP tool context:

```python
class MockContext:
    def __init__(self):
        self.messages = []
        self.errors = []
        self.progress = []
    
    def info(self, message):
        self.messages.append(f"INFO: {message}")
    
    def error(self, message):
        self.errors.append(f"ERROR: {message}")
    
    async def report_progress(self, current, total, message=None):
        self.progress.append({"current": current, "total": total, "message": message})
```

## 📈 Test Metrics

### Success Criteria
- **Unit Tests:** >90% code coverage
- **Integration Tests:** >80% API coverage
- **E2E Tests:** 100% critical path coverage
- **Test Execution Time:** <10 minutes for full suite
- **Test Reliability:** >95% pass rate

### Performance Benchmarks
- **Job Search Response Time:** <3 seconds
- **Easy Apply Submission Time:** <30 seconds
- **API Health Check:** <1 second
- **Concurrent User Handling:** 10+ simultaneous users

## 🐛 Troubleshooting

### Common Issues

#### 1. Import Errors
```
Warning: Could not import project modules: No module named 'linkedin_browser_mcp'
```
**Solution:** Ensure all project dependencies are installed:
```bash
pip install -r requirements.txt
```

#### 2. FastAPI TestClient Not Available
```
pytest.skip("FastAPI TestClient not available")
```
**Solution:** Install FastAPI testing dependencies:
```bash
pip install fastapi[testing]
```

#### 3. MCP Tool Failures
```
ERROR: Not logged in. Please run login_linkedin tool first
```
**Solution:** This is expected behavior when not authenticated. Tests handle this gracefully.

#### 4. Environment Variables Missing
```
Warning: GEMINI_API_KEY not set - AI features will be limited
```
**Solution:** Set required environment variables:
```bash
export GEMINI_API_KEY="your-api-key"
export LINKEDIN_USERNAME="your-email"
export LINKEDIN_PASSWORD="your-password"
```

### Debug Mode
Run tests with verbose output for debugging:
```bash
pytest user_story_tests.py -m user_story -v -s
```

### Test Isolation
Each test class is isolated and can be run independently:
```bash
pytest user_story_tests.py::TestAuthentication -v
pytest user_story_tests.py::TestJobSearch -v
pytest user_story_tests.py::TestEasyApply -v
```

## 🔄 Continuous Integration

### GitHub Actions Example
```yaml
name: User Story Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install fastapi[testing]
      - name: Run user story tests
        run: python run_user_story_tests.py all
      - name: Generate coverage report
        run: |
          pytest user_story_tests.py -m user_story --cov=. --cov-report=xml
```

### Pre-commit Hooks
Add to `.pre-commit-config.yaml`:
```yaml
repos:
  - repo: local
    hooks:
      - id: user-story-tests
        name: User Story Tests
        entry: python run_user_story_tests.py smoke
        language: system
        pass_filenames: false
```

## 📝 Test Maintenance

### Adding New Tests
1. Create test method in appropriate test class
2. Add test case ID and description
3. Update test documentation
4. Add to test runner if needed

### Updating Test Data
1. Modify `USER_STORY_CONFIG` for new test scenarios
2. Update mock data as needed
3. Ensure test data is realistic and comprehensive

### Test Case Management
- Use consistent naming: `TC-{CATEGORY}-{NUMBER}`
- Include clear descriptions
- Add appropriate markers
- Document expected behavior

## 🎯 Best Practices

### Test Design
- **Isolation:** Each test should be independent
- **Clarity:** Test names should describe the scenario
- **Completeness:** Cover happy path and error cases
- **Maintainability:** Use helper functions and fixtures

### Test Execution
- **Fast:** Unit tests should run quickly
- **Reliable:** Tests should be deterministic
- **Comprehensive:** Cover all critical paths
- **Informative:** Provide clear failure messages

### Test Data
- **Realistic:** Use realistic test data
- **Secure:** Never use real credentials
- **Comprehensive:** Cover edge cases
- **Maintainable:** Centralize test data

## 📚 Additional Resources

- [pytest Documentation](https://docs.pytest.org/)
- [FastAPI Testing Guide](https://fastapi.tiangolo.com/tutorial/testing/)
- [MCP Testing Best Practices](https://modelcontextprotocol.io/docs/testing)
- [LinkedIn API Documentation](https://developer.linkedin.com/)

This testing guide ensures comprehensive coverage of the user story and helps maintain high quality standards throughout the development lifecycle. 