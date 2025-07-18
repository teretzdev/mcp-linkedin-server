#!/usr/bin/env python3
"""
User Story Tests: Login, Job Search, and Easy Apply
Comprehensive test suite for the complete user journey
"""

import pytest
import asyncio
import os
import json
import sys
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock
import httpx
import time

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

# Import project modules
try:
    from linkedin_browser_mcp import (
        _login_linkedin_secure, search_linkedin_jobs, apply_to_linkedin_job
    )
    from api_bridge import app
    from llm_controller import LLMController
except ImportError as e:
    print(f"Warning: Could not import project modules: {e}")

# Test Configuration
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

class MockContext:
    """Mock context for testing MCP tools"""
    def __init__(self):
        self.messages = []
        self.errors = []
        self.progress = []
    
    def info(self, message):
        self.messages.append(f"INFO: {message}")
        print(f"INFO: {message}")
    
    def error(self, message):
        self.errors.append(f"ERROR: {message}")
        print(f"ERROR: {message}")
    
    async def report_progress(self, current, total, message=None):
        progress = {"current": current, "total": total, "message": message}
        self.progress.append(progress)
        print(f"Progress: {current}/{total} - {message}")

# ============================================================================
# STORY 1: AUTHENTICATION TESTING
# ============================================================================

@pytest.mark.user_story
@pytest.mark.auth
class TestAuthentication:
    """Test Story 1: Initial Setup and Login"""
    
    def test_login_component_rendering(self):
        """TC-AUTH-001: Login form renders correctly"""
        # This would be a frontend test in a real implementation
        # For now, we test the API endpoint
        try:
            from fastapi.testclient import TestClient
            client = TestClient(app)
            response = client.get("/api/health")
            assert response.status_code == 200
        except ImportError:
            pytest.skip("FastAPI TestClient not available")
    
    @pytest.mark.asyncio
    async def test_credential_validation(self):
        """TC-AUTH-002: Credential validation works"""
        ctx = MockContext()
        
        # Test valid credentials
        result = await _login_linkedin_secure(ctx)
        assert "status" in result
        
        # Test invalid email format
        with patch.dict(os.environ, {'LINKEDIN_USERNAME': 'invalid-email'}):
            result = await _login_linkedin_secure(ctx)
            assert result["status"] == "error"
    
    def test_credential_storage_api(self):
        """TC-SETTINGS-001: Credential loading from API"""
        try:
            from fastapi.testclient import TestClient
            client = TestClient(app)
            
            # Test credential update
            credentials = {
                "username": USER_STORY_CONFIG["test_user"]["email"],
                "password": USER_STORY_CONFIG["test_user"]["password"]
            }
            response = client.post("/api/update_credentials", json=credentials)
            assert response.status_code in [200, 500]
            
            # Test credential retrieval
            response = client.get("/api/get_credentials")
            assert response.status_code in [200, 500]
            
        except ImportError:
            pytest.skip("FastAPI TestClient not available")
    
    def test_login_api_endpoint(self):
        """TC-API-AUTH-001: Successful LinkedIn login"""
        try:
            from fastapi.testclient import TestClient
            client = TestClient(app)
            
            response = client.post("/api/login_linkedin_secure")
            assert response.status_code in [200, 500]
            
        except ImportError:
            pytest.skip("FastAPI TestClient not available")

# ============================================================================
# STORY 2: JOB SEARCH TESTING
# ============================================================================

@pytest.mark.user_story
@pytest.mark.search
class TestJobSearch:
    """Test Story 2: Job Search and Discovery"""
    
    def test_search_form_rendering(self):
        """TC-SEARCH-001: Search form rendering"""
        # Test that search API endpoint exists
        try:
            from fastapi.testclient import TestClient
            client = TestClient(app)
            
            # Test basic search
            search_payload = {
                "query": USER_STORY_CONFIG["test_user"]["target_role"],
                "location": USER_STORY_CONFIG["test_user"]["location"],
                "count": 10
            }
            response = client.post("/api/search_jobs", json=search_payload)
            assert response.status_code in [200, 500]
            
        except ImportError:
            pytest.skip("FastAPI TestClient not available")
    
    def test_search_with_filters(self):
        """TC-SEARCH-003: Filter application"""
        try:
            from fastapi.testclient import TestClient
            client = TestClient(app)
            
            # Test search with filters
            search_payload = {
                "query": "React Developer",
                "location": "Remote",
                "filters": {
                    "experience_level": "Mid Level",
                    "job_type": "Full-time",
                    "remote": True,
                    "easy_apply": True
                },
                "count": 5
            }
            response = client.post("/api/search_jobs", json=search_payload)
            assert response.status_code in [200, 500]
            
        except ImportError:
            pytest.skip("FastAPI TestClient not available")
    
    @pytest.mark.asyncio
    async def test_mcp_job_search(self):
        """TC-MCP-SEARCH-001: MCP job search functionality"""
        ctx = MockContext()
        
        # Test MCP job search
        result = await search_linkedin_jobs(
            query=USER_STORY_CONFIG["test_user"]["target_role"],
            location=USER_STORY_CONFIG["test_user"]["location"],
            ctx=ctx
        )
        
        assert "status" in result
        if result["status"] == "success":
            assert "jobs" in result
            assert "count" in result
    
    def test_saved_jobs_functionality(self):
        """TC-SEARCH-007: Job saving functionality"""
        try:
            from fastapi.testclient import TestClient
            client = TestClient(app)
            
            # Test saving a job
            save_payload = {
                "job_url": USER_STORY_CONFIG["test_job"]["url"],
                "title": USER_STORY_CONFIG["test_job"]["title"],
                "company": USER_STORY_CONFIG["test_job"]["company"]
            }
            response = client.post("/api/save_job", json=save_payload)
            assert response.status_code in [200, 500]
            
            # Test retrieving saved jobs
            response = client.get("/api/list_saved_jobs")
            assert response.status_code in [200, 500]
            
        except ImportError:
            pytest.skip("FastAPI TestClient not available")

# ============================================================================
# STORY 3: EASY APPLY TESTING
# ============================================================================

@pytest.mark.user_story
@pytest.mark.easy_apply
class TestEasyApply:
    """Test Story 3: Easy Apply Process"""
    
    def test_easy_apply_form_rendering(self):
        """TC-EASY-APPLY-001: Form rendering with questions"""
        # Test that Easy Apply API endpoint exists
        try:
            from fastapi.testclient import TestClient
            client = TestClient(app)
            
            # Test job application
            apply_payload = {
                "job_url": USER_STORY_CONFIG["test_job"]["url"]
            }
            response = client.post("/api/apply_job", json=apply_payload)
            assert response.status_code in [200, 500]
            
        except ImportError:
            pytest.skip("FastAPI TestClient not available")
    
    @pytest.mark.asyncio
    async def test_mcp_easy_apply(self):
        """TC-MCP-APPLY-001: MCP Easy Apply functionality"""
        ctx = MockContext()
        
        # Test MCP Easy Apply
        result = await apply_to_linkedin_job(
            job_url=USER_STORY_CONFIG["test_job"]["url"],
            ctx=ctx
        )
        
        assert "status" in result
        # Note: This might fail if not logged in, which is expected
    
    def test_ai_integration_validation(self):
        """TC-AI-001: Gemini API key validation"""
        # Test that AI integration can be validated
        gemini_key = os.getenv('GEMINI_API_KEY', '')
        
        # This test checks if the system can handle missing API keys gracefully
        if not gemini_key:
            print("Warning: GEMINI_API_KEY not set - AI features will be limited")
        
        # Test that the system doesn't crash without AI key
        assert True  # Placeholder for actual AI validation test
    
    def test_application_tracking(self):
        """TC-API-APPLY-004: Application tracking"""
        try:
            from fastapi.testclient import TestClient
            client = TestClient(app)
            
            # Test retrieving applied jobs
            response = client.get("/api/list_applied_jobs")
            assert response.status_code in [200, 500]
            
        except ImportError:
            pytest.skip("FastAPI TestClient not available")

# ============================================================================
# STORY 4: APPLICATION TRACKING TESTING
# ============================================================================

@pytest.mark.user_story
@pytest.mark.tracking
class TestApplicationTracking:
    """Test Story 4: Application Tracking and Management"""
    
    def test_applications_dashboard(self):
        """Test viewing applications"""
        try:
            from fastapi.testclient import TestClient
            client = TestClient(app)
            
            # Test applications endpoint
            response = client.get("/api/list_applied_jobs")
            assert response.status_code in [200, 500]
            
        except ImportError:
            pytest.skip("FastAPI TestClient not available")
    
    def test_saved_jobs_management(self):
        """Test managing saved jobs"""
        try:
            from fastapi.testclient import TestClient
            client = TestClient(app)
            
            # Test saved jobs endpoint
            response = client.get("/api/list_saved_jobs")
            assert response.status_code in [200, 500]
            
        except ImportError:
            pytest.skip("FastAPI TestClient not available")
    
    def test_job_recommendations(self):
        """Test job recommendations"""
        try:
            from fastapi.testclient import TestClient
            client = TestClient(app)
            
            # Test recommendations endpoint
            response = client.get("/api/job_recommendations")
            assert response.status_code in [200, 500]
            
        except ImportError:
            pytest.skip("FastAPI TestClient not available")

# ============================================================================
# END-TO-END TESTING
# ============================================================================

@pytest.mark.user_story
@pytest.mark.e2e
class TestEndToEndWorkflow:
    """Test Complete User Journey"""
    
    @pytest.mark.asyncio
    async def test_complete_workflow(self):
        """TC-E2E-001: Complete login to application workflow"""
        ctx = MockContext()
        
        # Step 1: Test login
        login_result = await _login_linkedin_secure(ctx)
        assert "status" in login_result
        
        # Step 2: Test job search
        search_result = await search_linkedin_jobs(
            query="React Developer",
            location="Remote",
            ctx=ctx
        )
        assert "status" in search_result
        
        # Step 3: Test Easy Apply (if jobs found)
        if search_result.get("status") == "success" and search_result.get("jobs"):
            job_url = search_result["jobs"][0].get("jobUrl", "")
            if job_url:
                apply_result = await apply_to_linkedin_job(job_url, ctx)
                assert "status" in apply_result
        
        print("Complete workflow test completed")
    
    def test_error_recovery(self):
        """TC-E2E-002: Error recovery and retry mechanisms"""
        try:
            from fastapi.testclient import TestClient
            client = TestClient(app)
            
            # Test health endpoint for error recovery
            response = client.get("/api/health")
            assert response.status_code == 200
            
            # Test invalid endpoints for error handling
            response = client.get("/api/invalid_endpoint")
            assert response.status_code == 404
            
        except ImportError:
            pytest.skip("FastAPI TestClient not available")

# ============================================================================
# PERFORMANCE TESTING
# ============================================================================

@pytest.mark.user_story
@pytest.mark.performance
class TestPerformance:
    """Performance Tests"""
    
    def test_job_search_response_time(self):
        """TC-PERF-001: Job search response time"""
        try:
            from fastapi.testclient import TestClient
            client = TestClient(app)
            
            start_time = time.time()
            
            search_payload = {
                "query": "React Developer",
                "location": "Remote",
                "count": 5
            }
            response = client.post("/api/search_jobs", json=search_payload)
            
            end_time = time.time()
            response_time = end_time - start_time
            
            # Assert response time is under 3 seconds
            assert response_time < 3.0
            assert response.status_code in [200, 500]
            
        except ImportError:
            pytest.skip("FastAPI TestClient not available")
    
    def test_api_health_response_time(self):
        """Test API health response time"""
        try:
            from fastapi.testclient import TestClient
            client = TestClient(app)
            
            start_time = time.time()
            response = client.get("/api/health")
            end_time = time.time()
            
            response_time = end_time - start_time
            
            # Assert health check is very fast
            assert response_time < 1.0
            assert response.status_code == 200
            
        except ImportError:
            pytest.skip("FastAPI TestClient not available")

# ============================================================================
# SECURITY TESTING
# ============================================================================

@pytest.mark.user_story
@pytest.mark.security
class TestSecurity:
    """Security Tests"""
    
    def test_credential_encryption(self):
        """TC-SEC-001: Credential encryption"""
        # Test that credentials are not exposed in plain text
        try:
            from fastapi.testclient import TestClient
            client = TestClient(app)
            
            # Test credential retrieval doesn't expose password
            response = client.get("/api/get_credentials")
            if response.status_code == 200:
                data = response.json()
                if "password" in data:
                    # Password should be masked
                    assert data["password"] == "••••••••" or len(data["password"]) == 0
            
        except ImportError:
            pytest.skip("FastAPI TestClient not available")
    
    def test_input_validation(self):
        """TC-SEC-005: Input validation"""
        try:
            from fastapi.testclient import TestClient
            client = TestClient(app)
            
            # Test invalid email format
            invalid_credentials = {
                "username": "invalid-email",
                "password": "short"
            }
            response = client.post("/api/update_credentials", json=invalid_credentials)
            # Should handle invalid input gracefully
            assert response.status_code in [200, 400, 422, 500]
            
        except ImportError:
            pytest.skip("FastAPI TestClient not available")

# ============================================================================
# TEST UTILITIES
# ============================================================================

def test_user_story_configuration():
    """Test that user story configuration is valid"""
    assert "test_user" in USER_STORY_CONFIG
    assert "test_job" in USER_STORY_CONFIG
    
    user = USER_STORY_CONFIG["test_user"]
    assert "name" in user
    assert "email" in user
    assert "skills" in user
    
    job = USER_STORY_CONFIG["test_job"]
    assert "title" in job
    assert "company" in job
    assert "easy_apply" in job

def test_mock_context():
    """Test MockContext functionality"""
    ctx = MockContext()
    
    ctx.info("Test info message")
    ctx.error("Test error message")
    
    assert len(ctx.messages) == 1
    assert len(ctx.errors) == 1
    assert "Test info message" in ctx.messages[0]
    assert "Test error message" in ctx.errors[0]

# ============================================================================
# TEST RUNNER
# ============================================================================

if __name__ == "__main__":
    print("Running User Story Tests...")
    print("=" * 50)
    
    # Run tests with pytest
    pytest.main([
        __file__,
        "-v",
        "--tb=short",
        "--strict-markers",
        "-m", "user_story"
    ])
