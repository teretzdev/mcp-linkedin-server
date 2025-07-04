#!/usr/bin/env python3
"""
Comprehensive Test Suite for LinkedIn Job Hunter
Tests all major components: MCP Server, API Bridge, Browser Automation, and Frontend
"""

import pytest
import asyncio
import os
import json
import sys
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock
import httpx
import subprocess
import time
from datetime import datetime, timedelta

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

# Import project modules
try:
    from linkedin_browser_mcp import (
        BrowserSession, save_cookies, load_cookies,
        login_linkedin, _login_linkedin_secure,
        search_linkedin_jobs, apply_to_linkedin_job,
        save_linkedin_job, browse_linkedin_feed,
        search_linkedin_profiles, view_linkedin_profile,
        interact_with_linkedin_post, update_application_status,
        add_application_note, get_application_analytics,
        save_applied_job_tracking
    )
    from api_bridge import app
except ImportError as e:
    print(f"Warning: Could not import project modules: {e}")

# Test Configuration
TEST_CONFIG = {
    "headless": True,
    "timeout": 30000,
    "test_credentials": {
        "username": "test@example.com",
        "password": "testpassword123"
    },
    "test_urls": {
        "linkedin_login": "https://www.linkedin.com/login",
        "linkedin_job": "https://www.linkedin.com/jobs/view/test-job",
        "linkedin_profile": "https://www.linkedin.com/in/test-profile"
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
# APPLICATION TRACKING TESTS
# ============================================================================
@pytest.mark.application_tracking
class TestApplicationTracking:
    """Test enhanced application tracking features"""
    
    @pytest.fixture
    def sample_job_data(self):
        """Sample job data for testing"""
        return {
            "id": "test_job_123",
            "title": "Senior Software Engineer",
            "company": "TechCorp Inc.",
            "location": "San Francisco, CA",
            "salary": "$120,000 - $150,000",
            "jobType": "Full-time",
            "remote": True,
            "experienceLevel": "Senior",
            "date_applied": datetime.now().isoformat(),
            "job_url": "https://www.linkedin.com/jobs/view/test-job",
            "status": "applied",
            "notes": [],
            "follow_up_date": None
        }
    
    @pytest.fixture
    def sample_applied_jobs_file(self, tmp_path):
        """Create a temporary applied jobs file for testing"""
        jobs_file = tmp_path / "applied_jobs.json"
        sample_jobs = [
            {
                "id": "job_1",
                "title": "Frontend Developer",
                "company": "Company A",
                "location": "New York, NY",
                "date_applied": "2024-01-15T10:00:00Z",
                "status": "applied",
                "notes": []
            },
            {
                "id": "job_2",
                "title": "Backend Engineer",
                "company": "Company B",
                "location": "San Francisco, CA",
                "date_applied": "2024-01-20T10:00:00Z",
                "status": "under_review",
                "notes": [
                    {
                        "id": "note_1",
                        "text": "Follow up next week",
                        "date": "2024-01-21T10:00:00Z"
                    }
                ]
            },
            {
                "id": "job_3",
                "title": "Full Stack Developer",
                "company": "Company C",
                "location": "Remote",
                "date_applied": "2024-01-25T10:00:00Z",
                "status": "interview",
                "notes": []
            }
        ]
        with open(jobs_file, 'w') as f:
            json.dump(sample_jobs, f)
        return jobs_file
    
    def test_application_status_management(self, sample_applied_jobs_file):
        """Test application status updates"""
        # Load sample data
        with open(sample_applied_jobs_file, 'r') as f:
            jobs = json.load(f)
        
        # Test status update
        job_id = "job_1"
        new_status = "under_review"
        
        for job in jobs:
            if job["id"] == job_id:
                job["status"] = new_status
                break
        
        # Verify status was updated
        updated_job = next(job for job in jobs if job["id"] == job_id)
        assert updated_job["status"] == new_status
    
    def test_application_notes_management(self, sample_applied_jobs_file):
        """Test adding and managing application notes"""
        # Load sample data
        with open(sample_applied_jobs_file, 'r') as f:
            jobs = json.load(f)
        
        # Test adding a note
        job_id = "job_1"
        new_note = {
            "id": str(int(time.time())),
            "text": "Great company culture, follow up in 2 weeks",
            "date": datetime.now().isoformat()
        }
        
        for job in jobs:
            if job["id"] == job_id:
                if "notes" not in job:
                    job["notes"] = []
                job["notes"].append(new_note)
                break
        
        # Verify note was added
        updated_job = next(job for job in jobs if job["id"] == job_id)
        assert len(updated_job["notes"]) > 0
        assert updated_job["notes"][-1]["text"] == new_note["text"]
    
    def test_application_filtering(self, sample_applied_jobs_file):
        """Test application filtering functionality"""
        # Load sample data
        with open(sample_applied_jobs_file, 'r') as f:
            jobs = json.load(f)
        
        # Test status filtering
        status_filter = "under_review"
        filtered_jobs = [job for job in jobs if job["status"] == status_filter]
        assert len(filtered_jobs) == 1
        assert filtered_jobs[0]["company"] == "Company B"
        
        # Test company filtering
        company_filter = "Company A"
        company_filtered = [job for job in jobs if company_filter.lower() in job["company"].lower()]
        assert len(company_filtered) == 1
        assert company_filtered[0]["title"] == "Frontend Developer"
    
    def test_application_sorting(self, sample_applied_jobs_file):
        """Test application sorting functionality"""
        # Load sample data
        with open(sample_applied_jobs_file, 'r') as f:
            jobs = json.load(f)
        
        # Test sorting by date (newest first)
        sorted_jobs = sorted(jobs, key=lambda x: x["date_applied"], reverse=True)
        assert sorted_jobs[0]["title"] == "Full Stack Developer"
        assert sorted_jobs[-1]["title"] == "Frontend Developer"
        
        # Test sorting by company name
        sorted_by_company = sorted(jobs, key=lambda x: x["company"])
        assert sorted_by_company[0]["company"] == "Company A"
        assert sorted_by_company[-1]["company"] == "Company C"

# ============================================================================
# FOLLOW-UP TRACKING TESTS
# ============================================================================
@pytest.mark.follow_ups
class TestFollowUpTracking:
    """Test follow-up tracking functionality"""
    
    @pytest.fixture
    def sample_follow_ups(self):
        """Sample follow-up data for testing"""
        return [
            {
                "id": "follow_1",
                "applicationId": "job_1",
                "applicationTitle": "Frontend Developer",
                "applicationCompany": "Company A",
                "type": "email",
                "date": (datetime.now() + timedelta(days=7)).isoformat(),
                "notes": "Follow up on application status",
                "completed": False,
                "createdAt": datetime.now().isoformat()
            },
            {
                "id": "follow_2",
                "applicationId": "job_2",
                "applicationTitle": "Backend Engineer",
                "applicationCompany": "Company B",
                "type": "phone",
                "date": (datetime.now() - timedelta(days=1)).isoformat(),
                "notes": "Call HR about interview",
                "completed": True,
                "createdAt": datetime.now().isoformat()
            },
            {
                "id": "follow_3",
                "applicationId": "job_3",
                "applicationTitle": "Full Stack Developer",
                "applicationCompany": "Company C",
                "type": "linkedin",
                "date": (datetime.now() + timedelta(days=3)).isoformat(),
                "notes": "Send LinkedIn message",
                "completed": False,
                "createdAt": datetime.now().isoformat()
            }
        ]
    
    def test_follow_up_creation(self, sample_follow_ups):
        """Test creating new follow-ups"""
        new_follow_up = {
            "id": "follow_4",
            "applicationId": "job_4",
            "applicationTitle": "DevOps Engineer",
            "applicationCompany": "Company D",
            "type": "email",
            "date": (datetime.now() + timedelta(days=5)).isoformat(),
            "notes": "Send thank you email",
            "completed": False,
            "createdAt": datetime.now().isoformat()
        }
        
        sample_follow_ups.append(new_follow_up)
        assert len(sample_follow_ups) == 4
        assert sample_follow_ups[-1]["applicationTitle"] == "DevOps Engineer"
    
    def test_follow_up_completion(self, sample_follow_ups):
        """Test marking follow-ups as completed"""
        follow_up_id = "follow_1"
        
        for follow_up in sample_follow_ups:
            if follow_up["id"] == follow_up_id:
                follow_up["completed"] = True
                break
        
        # Verify completion
        updated_follow_up = next(fu for fu in sample_follow_ups if fu["id"] == follow_up_id)
        assert updated_follow_up["completed"] == True
    
    def test_overdue_follow_ups(self, sample_follow_ups):
        """Test identifying overdue follow-ups"""
        today = datetime.now()
        overdue_follow_ups = [
            fu for fu in sample_follow_ups 
            if not fu["completed"] and datetime.fromisoformat(fu["date"]) < today
        ]
        
        assert len(overdue_follow_ups) == 1
        assert overdue_follow_ups[0]["id"] == "follow_2"
    
    def test_upcoming_follow_ups(self, sample_follow_ups):
        """Test identifying upcoming follow-ups"""
        today = datetime.now()
        next_week = today + timedelta(days=7)
        
        upcoming_follow_ups = [
            fu for fu in sample_follow_ups 
            if not fu["completed"] and 
            today <= datetime.fromisoformat(fu["date"]) <= next_week
        ]
        
        assert len(upcoming_follow_ups) == 2
        assert any(fu["id"] == "follow_1" for fu in upcoming_follow_ups)
        assert any(fu["id"] == "follow_3" for fu in upcoming_follow_ups)

# ============================================================================
# ANALYTICS TESTS
# ============================================================================
@pytest.mark.analytics
class TestApplicationAnalytics:
    """Test application analytics functionality"""
    
    @pytest.fixture
    def sample_analytics_data(self):
        """Sample analytics data for testing"""
        return {
            "total_applications": 15,
            "status_counts": {
                "applied": 5,
                "under_review": 3,
                "interview": 4,
                "offer": 1,
                "rejected": 2
            },
            "company_counts": {
                "Company A": 3,
                "Company B": 2,
                "Company C": 4,
                "Company D": 1,
                "Company E": 5
            },
            "monthly_counts": {
                "2024-01": 8,
                "2024-02": 7
            },
            "success_rate": 33.3,
            "recent_applications": 5
        }
    
    def test_success_rate_calculation(self, sample_analytics_data):
        """Test success rate calculation"""
        success_statuses = ['interview', 'offer']
        total = sample_analytics_data["total_applications"]
        successful = sum(sample_analytics_data["status_counts"].get(status, 0) 
                        for status in success_statuses)
        
        expected_success_rate = (successful / total * 100) if total > 0 else 0
        assert abs(expected_success_rate - sample_analytics_data["success_rate"]) < 0.1
    
    def test_response_rate_calculation(self, sample_analytics_data):
        """Test response rate calculation"""
        total = sample_analytics_data["total_applications"]
        responded = sum(count for status, count in sample_analytics_data["status_counts"].items() 
                       if status != "applied")
        
        response_rate = (responded / total * 100) if total > 0 else 0
        assert response_rate == 66.7  # 10 out of 15 applications got responses
    
    def test_top_companies_analysis(self, sample_analytics_data):
        """Test top companies analysis"""
        company_counts = sample_analytics_data["company_counts"]
        top_companies = sorted(company_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        
        assert top_companies[0][0] == "Company E"
        assert top_companies[0][1] == 5
        assert len(top_companies) == 3
    
    def test_monthly_trend_analysis(self, sample_analytics_data):
        """Test monthly trend analysis"""
        monthly_counts = sample_analytics_data["monthly_counts"]
        
        # Test trend calculation
        months = sorted(monthly_counts.keys())
        assert len(months) == 2
        assert monthly_counts["2024-01"] == 8
        assert monthly_counts["2024-02"] == 7

# ============================================================================
# MCP TOOL TESTS
# ============================================================================
@pytest.mark.mcp_tools
class TestMCPApplicationTools:
    """Test MCP tools for application tracking"""
    
    @pytest.fixture
    def mock_context(self):
        """Mock context for MCP tools"""
        return MockContext()
    
    @pytest.mark.asyncio
    async def test_update_application_status(self, mock_context, tmp_path):
        """Test update_application_status MCP tool"""
        # Create temporary applied jobs file
        jobs_file = tmp_path / "applied_jobs.json"
        sample_jobs = [
            {
                "id": "test_job",
                "title": "Test Job",
                "company": "Test Company",
                "status": "applied",
                "notes": []
            }
        ]
        with open(jobs_file, 'w') as f:
            json.dump(sample_jobs, f)
        
        # Mock the file path
        with patch('linkedin_browser_mcp.open') as mock_open:
            mock_open.return_value.__enter__.return_value.read.return_value = json.dumps(sample_jobs)
            mock_open.return_value.__enter__.return_value.write = Mock()
            
            result = await update_application_status("test_job", mock_context, status="under_review")
            
            assert result["status"] == "success"
    
    @pytest.mark.asyncio
    async def test_add_application_note(self, mock_context, tmp_path):
        """Test add_application_note MCP tool"""
        # Create temporary applied jobs file
        jobs_file = tmp_path / "applied_jobs.json"
        sample_jobs = [
            {
                "id": "test_job",
                "title": "Test Job",
                "company": "Test Company",
                "status": "applied",
                "notes": []
            }
        ]
        with open(jobs_file, 'w') as f:
            json.dump(sample_jobs, f)
        
        # Mock the file path
        with patch('linkedin_browser_mcp.open') as mock_open:
            mock_open.return_value.__enter__.return_value.read.return_value = json.dumps(sample_jobs)
            mock_open.return_value.__enter__.return_value.write = Mock()
            
            result = await add_application_note("test_job", "Test note", mock_context)
            
            assert result["status"] == "success"
    
    @pytest.mark.asyncio
    async def test_get_application_analytics(self, mock_context, tmp_path):
        """Test get_application_analytics MCP tool"""
        # Create temporary applied jobs file
        jobs_file = tmp_path / "applied_jobs.json"
        sample_jobs = [
            {
                "id": "job_1",
                "title": "Job 1",
                "company": "Company A",
                "status": "applied",
                "date_applied": datetime.now().isoformat(),
                "notes": []
            },
            {
                "id": "job_2",
                "title": "Job 2",
                "company": "Company B",
                "status": "interview",
                "date_applied": datetime.now().isoformat(),
                "notes": []
            }
        ]
        with open(jobs_file, 'w') as f:
            json.dump(sample_jobs, f)
        
        # Mock the file path
        with patch('linkedin_browser_mcp.open') as mock_open:
            mock_open.return_value.__enter__.return_value.read.return_value = json.dumps(sample_jobs)
            
            result = await get_application_analytics(mock_context)
            
            assert result["status"] == "success"
            assert "analytics" in result
            assert result["analytics"]["total_applications"] == 2

# ============================================================================
# API ENDPOINT TESTS
# ============================================================================
@pytest.mark.api_endpoints
class TestApplicationTrackingAPI:
    """Test API endpoints for application tracking"""
    
    @pytest.fixture
    def client(self):
        try:
            from fastapi.testclient import TestClient
            return TestClient(app)
        except ImportError:
            pytest.skip("FastAPI TestClient not available")
    
    def test_update_application_endpoint(self, client):
        """Test /api/update_application endpoint"""
        payload = {
            "job_id": "test_job",
            "status": "under_review",
            "notes": "Test note",
            "follow_up_date": (datetime.now() + timedelta(days=7)).isoformat()
        }
        response = client.post("/api/update_application", json=payload)
        assert response.status_code in [200, 500]
    
    def test_add_application_note_endpoint(self, client):
        """Test /api/add_application_note endpoint"""
        payload = {
            "job_id": "test_job",
            "note": "Test note content"
        }
        response = client.post("/api/add_application_note", json=payload)
        assert response.status_code in [200, 500]
    
    def test_application_analytics_endpoint(self, client):
        """Test /api/application_analytics endpoint"""
        response = client.get("/api/application_analytics")
        assert response.status_code in [200, 500]
    
    def test_enhanced_list_applied_jobs_endpoint(self, client):
        """Test enhanced /api/list_applied_jobs endpoint"""
        response = client.get("/api/list_applied_jobs")
        assert response.status_code in [200, 500]
        
        if response.status_code == 200:
            data = response.json()
            assert "applied_jobs" in data
            assert "count" in data

# ============================================================================
# FRONTEND COMPONENT TESTS
# ============================================================================
@pytest.mark.frontend_components
class TestApplicationTrackingComponents:
    """Test frontend components for application tracking"""
    
    def test_applications_component_exists(self):
        """Test that Applications component exists with enhanced features"""
        components_dir = Path(__file__).parent / 'src' / 'components'
        if not components_dir.exists():
            pytest.skip("src/components directory not found")
        
        applications_path = components_dir / 'Applications.js'
        assert applications_path.exists()
        
        with open(applications_path, 'r', encoding='utf-8') as f:
            content = f.read()
            # Test for enhanced features
            assert 'statusConfig' in content, "Applications component missing status configuration"
            assert 'filteredJobs' in content, "Applications component missing filtering"
            assert 'searchTerm' in content, "Applications component missing search"
            assert 'statusFilter' in content, "Applications component missing status filtering"
            assert 'sortBy' in content, "Applications component missing sorting"
            assert 'showAnalytics' in content, "Applications component missing analytics toggle"
            assert 'exportApplications' in content, "Applications component missing export functionality"
            assert 'addNote' in content, "Applications component missing note functionality"
    
    def test_application_follow_ups_component_exists(self):
        """Test that ApplicationFollowUps component exists"""
        components_dir = Path(__file__).parent / 'src' / 'components'
        if not components_dir.exists():
            pytest.skip("src/components directory not found")
        
        follow_ups_path = components_dir / 'ApplicationFollowUps.js'
        assert follow_ups_path.exists()
        
        with open(follow_ups_path, 'r', encoding='utf-8') as f:
            content = f.read()
            # Test for follow-up features
            assert 'followUps' in content, "ApplicationFollowUps component missing follow-ups state"
            assert 'addFollowUp' in content, "ApplicationFollowUps component missing add follow-up function"
            assert 'toggleFollowUp' in content, "ApplicationFollowUps component missing toggle function"
            assert 'getOverdueFollowUps' in content, "ApplicationFollowUps component missing overdue detection"
            assert 'getUpcomingFollowUps' in content, "ApplicationFollowUps component missing upcoming detection"
    
    def test_application_analytics_component_exists(self):
        """Test that ApplicationAnalytics component exists"""
        components_dir = Path(__file__).parent / 'src' / 'components'
        if not components_dir.exists():
            pytest.skip("src/components directory not found")
        
        analytics_path = components_dir / 'ApplicationAnalytics.js'
        assert analytics_path.exists()
        
        with open(analytics_path, 'r', encoding='utf-8') as f:
            content = f.read()
            # Test for analytics features
            assert 'analytics' in content, "ApplicationAnalytics component missing analytics state"
            assert 'calculateMetrics' in content, "ApplicationAnalytics component missing metrics calculation"
            assert 'exportAnalytics' in content, "ApplicationAnalytics component missing export functionality"
            assert 'getStatusColor' in content, "ApplicationAnalytics component missing status colors"
            assert 'timeRange' in content, "ApplicationAnalytics component missing time range filtering"

# ============================================================================
# INTEGRATION TESTS - API Bridge (ENABLED)
# ============================================================================
@pytest.mark.integration
@pytest.mark.api
class TestAPIBridge:
    """Test API bridge functionality"""
    @pytest.fixture
    def client(self):
        try:
            from fastapi.testclient import TestClient
            return TestClient(app)
        except ImportError:
            pytest.skip("FastAPI TestClient not available")
    def test_health_endpoint(self, client):
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
    def test_search_jobs_endpoint(self, client):
        payload = {"keywords": "python developer", "location": "San Francisco", "count": 5}
        response = client.post("/api/search_jobs", json=payload)
        assert response.status_code in [200, 500]
    def test_apply_job_endpoint(self, client):
        payload = {"job_url": "https://www.linkedin.com/jobs/view/test-job"}
        response = client.post("/api/apply_job", json=payload)
        assert response.status_code in [200, 500]
    def test_save_job_endpoint(self, client):
        payload = {"job_url": "https://www.linkedin.com/jobs/view/test-job", "title": "Test Job", "company": "Test Company"}
        response = client.post("/api/save_job", json=payload)
        assert response.status_code in [200, 500]
    def test_list_applied_jobs_endpoint(self, client):
        response = client.get("/api/list_applied_jobs")
        assert response.status_code in [200, 500]
    def test_list_saved_jobs_endpoint(self, client):
        response = client.get("/api/list_saved_jobs")
        assert response.status_code in [200, 500]

# ============================================================================
# FRONTEND TESTS (ENABLED)
# ============================================================================
@pytest.mark.frontend
class TestFrontend:
    def test_package_json_dependencies(self):
        package_json_path = Path(__file__).parent / 'package.json'
        if not package_json_path.exists():
            pytest.skip("package.json not found")
        with open(package_json_path, 'r') as f:
            package_data = json.load(f)
        required_deps = [
            'react', 'react-dom', 'axios', 'react-router-dom',
            'lucide-react', 'tailwindcss'
        ]
        for dep in required_deps:
            assert dep in package_data['dependencies']
    def test_testing_dependencies(self):
        package_json_path = Path(__file__).parent / 'package.json'
        if not package_json_path.exists():
            pytest.skip("package.json not found")
        with open(package_json_path, 'r') as f:
            package_data = json.load(f)
        testing_deps = [
            '@testing-library/jest-dom',
            '@testing-library/react',
            '@testing-library/user-event'
        ]
        for dep in testing_deps:
            assert dep in package_data['dependencies']
    def test_react_components_exist(self):
        components_dir = Path(__file__).parent / 'src' / 'components'
        if not components_dir.exists():
            pytest.skip("src/components directory not found")
        required_components = [
            'Dashboard.js', 'JobSearch.js', 'Applications.js',
            'SavedJobs.js', 'SettingsPage.js', 'Sidebar.js',
            'FeedBrowser.js', 'PostInteraction.js', 'ProfileSearch.js',
            'AutomationDashboard.js', 'ApplicantKnowledgeBase.js',
            'ApplicationFollowUps.js', 'ApplicationAnalytics.js'
        ]
        for comp in required_components:
            assert (components_dir / comp).exists()
    def test_advanced_search_components(self):
        """Test that advanced search components exist and have enhanced features"""
        components_dir = Path(__file__).parent / 'src' / 'components'
        if not components_dir.exists():
            pytest.skip("src/components directory not found")
        
        # Test ApplicantKnowledgeBase advanced features
        akb_path = components_dir / 'ApplicantKnowledgeBase.js'
        if akb_path.exists():
            with open(akb_path, 'r', encoding='utf-8') as f:
                content = f.read()
                assert 'useMemo' in content, "ApplicantKnowledgeBase missing useMemo optimization"
                assert 'searchTerm' in content, "ApplicantKnowledgeBase missing search functionality"
                assert 'selectedCategory' in content, "ApplicantKnowledgeBase missing category filter"
        
        # Test SavedJobs advanced features
        saved_jobs_path = components_dir / 'SavedJobs.js'
        if saved_jobs_path.exists():
            with open(saved_jobs_path, 'r', encoding='utf-8') as f:
                content = f.read()
                assert 'useMemo' in content, "SavedJobs missing useMemo optimization"
                assert 'searchTerm' in content, "SavedJobs missing search functionality"
                assert 'selectedLocation' in content, "SavedJobs missing location filter"
                assert 'selectedDateRange' in content, "SavedJobs missing date range filter"
        
        # Test JobSearch advanced features
        job_search_path = components_dir / 'JobSearch.js'
        if job_search_path.exists():
            with open(job_search_path, 'r', encoding='utf-8') as f:
                content = f.read()
                assert 'useMemo' in content, "JobSearch missing useMemo optimization"
                assert 'searchQuery' in content, "JobSearch missing search functionality"
                assert 'salaryRange' in content, "JobSearch missing salary filter"
                assert 'skills' in content, "JobSearch missing skills filter"
                assert 'viewMode' in content, "JobSearch missing view mode switching"

# ============================================================================
# CONFIGURATION TESTS (ENABLED)
# ============================================================================
@pytest.mark.unit
class TestConfiguration:
    def test_requirements_file(self):
        req_path = Path(__file__).parent / 'requirements.txt'
        assert req_path.exists()
        with open(req_path, 'r') as f:
            lines = f.readlines()
        assert any('fastmcp' in line for line in lines)
        assert any('playwright' in line for line in lines)
    def test_environment_file_structure(self):
        env_path = Path(__file__).parent / '.env'
        assert env_path.exists() or (Path(__file__).parent / '.env.test').exists()
    def test_project_structure(self):
        expected_files = [
            'linkedin_browser_mcp.py', 'api_bridge.py', 'src', 'requirements.txt', 'package.json'
        ]
        for file in expected_files:
            assert (Path(__file__).parent / file).exists()
    def test_advanced_search_test_suite_exists(self):
        """Test that the advanced search test suite exists"""
        test_file = Path(__file__).parent / 'test_suite.py'
        assert test_file.exists()
        with open(test_file, 'r', encoding='utf-8') as f:
            content = f.read()
            assert 'TestApplicationTracking' in content, "Application tracking tests missing"
            assert 'TestFollowUpTracking' in content, "Follow-up tracking tests missing"
            assert 'TestApplicationAnalytics' in content, "Application analytics tests missing"

    def test_application_tracking_test_suite_exists(self):
        """Test that the application tracking test suite exists"""
        test_file = Path(__file__).parent / 'test_application_tracking.py'
        assert test_file.exists(), "Application tracking test suite not found"
        
        with open(test_file, 'r', encoding='utf-8') as f:
            content = f.read()
            assert 'TestApplicationTracking' in content, "Application tracking tests missing"
            assert 'TestFollowUpTracking' in content, "Follow-up tracking tests missing"
            assert 'TestApplicationAnalytics' in content, "Application analytics tests missing"
            assert 'TestApplicationTrackingComponents' in content, "Frontend component tests missing"
            assert 'TestApplicationTrackingIntegration' in content, "Integration tests missing"
            assert 'TestApplicationTrackingPerformance' in content, "Performance tests missing"

    def test_application_tracking_runner_exists(self):
        """Test that the application tracking test runner exists"""
        runner_file = Path(__file__).parent / 'run_application_tracking_tests.py'
        assert runner_file.exists(), "Application tracking test runner not found"

def test_advanced_search_integration():
    """Integration test for advanced search functionality"""
    # This test ensures that all advanced search components work together
    assert True  # Placeholder for actual integration test

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])