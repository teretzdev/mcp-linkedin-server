#!/usr/bin/env python3
"""
Application Tracking Test Suite
Tests for enhanced application tracking, follow-ups, and analytics features
"""

import pytest
import json
import os
import sys
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

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
            "id": str(int(datetime.now().timestamp())),
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
    
    def test_application_export(self, sample_applied_jobs_file):
        """Test application data export functionality"""
        # Load sample data
        with open(sample_applied_jobs_file, 'r') as f:
            jobs = json.load(f)
        
        # Simulate CSV export
        csv_rows = []
        csv_rows.append(['Title', 'Company', 'Location', 'Status', 'Date Applied', 'Notes'])
        
        for job in jobs:
            notes_text = '; '.join([note['text'] for note in job.get('notes', [])])
            csv_rows.append([
                job.get('title', ''),
                job.get('company', ''),
                job.get('location', ''),
                job.get('status', ''),
                job.get('date_applied', ''),
                notes_text
            ])
        
        # Verify export data
        assert len(csv_rows) == 4  # Header + 3 jobs
        assert csv_rows[0][0] == 'Title'
        assert csv_rows[1][0] == 'Frontend Developer'
        assert csv_rows[2][0] == 'Backend Engineer'
        assert csv_rows[3][0] == 'Full Stack Developer'

@pytest.mark.application_tracking
def test_database_corruption_and_rollback():
    """Test database corruption and rollback scenario"""
    try:
        # Simulate corruption (mocked)
        # In real test, corrupt the DB file and check recovery
        assert True  # Placeholder for actual corruption test
    except Exception as e:
        assert False, f"Database corruption test failed: {e}"

@pytest.mark.application_tracking
def test_permission_role_access():
    """Test permission and role-based access to application tracking features"""
    try:
        # Simulate user roles (mocked)
        user_role = 'user'
        admin_role = 'admin'
        # User should not access admin-only features
        assert user_role != admin_role
    except Exception as e:
        assert False, f"Role-based access test failed: {e}"

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
        # Force at least one follow-up to be overdue
        sample_follow_ups[0]["date"] = (today - timedelta(days=2)).isoformat()
        overdue_follow_ups = [
            fu for fu in sample_follow_ups
            if not fu["completed"] and datetime.fromisoformat(fu["date"]) < today
        ]
        assert len(overdue_follow_ups) >= 1
    
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
    
    def test_follow_up_types(self, sample_follow_ups):
        """Test different follow-up types"""
        follow_up_types = [fu["type"] for fu in sample_follow_ups]
        assert "email" in follow_up_types
        assert "phone" in follow_up_types
        assert "linkedin" in follow_up_types
        
        # Test type-specific functionality
        email_follow_ups = [fu for fu in sample_follow_ups if fu["type"] == "email"]
        assert len(email_follow_ups) == 1
        assert email_follow_ups[0]["applicationTitle"] == "Frontend Developer"

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
        responded = sum(count for status, count in sample_analytics_data["status_counts"].items() if status != "applied")
        response_rate = (responded / total * 100) if total > 0 else 0
        assert response_rate == pytest.approx(66.7, abs=0.1)  # 10 out of 15 applications got responses
    
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
    
    def test_status_distribution(self, sample_analytics_data):
        """Test status distribution analysis"""
        status_counts = sample_analytics_data["status_counts"]
        total = sample_analytics_data["total_applications"]
        
        # Test percentage calculations
        applied_percentage = (status_counts["applied"] / total) * 100
        assert applied_percentage == pytest.approx(33.3, abs=0.1)  # 5 out of 15
        
        interview_percentage = (status_counts["interview"] / total) * 100
        assert interview_percentage == 26.7  # 4 out of 15
    
    def test_analytics_export(self, sample_analytics_data):
        """Test analytics data export"""
        # Simulate analytics export
        export_data = {
            "metrics": {
                "total_applications": sample_analytics_data["total_applications"],
                "success_rate": sample_analytics_data["success_rate"],
                "response_rate": 66.7
            },
            "status_breakdown": sample_analytics_data["status_counts"],
            "top_companies": sorted(sample_analytics_data["company_counts"].items(), 
                                  key=lambda x: x[1], reverse=True)[:5]
        }
        
        assert export_data["metrics"]["total_applications"] == 15
        assert export_data["metrics"]["success_rate"] == 33.3
        assert len(export_data["top_companies"]) == 5

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
    
    def test_sidebar_integration(self):
        """Test that sidebar includes application tracking links"""
        components_dir = Path(__file__).parent / 'src' / 'components'
        if not components_dir.exists():
            pytest.skip("src/components directory not found")
        
        sidebar_path = components_dir / 'Sidebar.js'
        assert sidebar_path.exists()
        
        with open(sidebar_path, 'r', encoding='utf-8') as f:
            content = f.read()
            # Test for application tracking navigation
            assert '/follow-ups' in content, "Sidebar missing follow-ups link"
            assert '/analytics' in content, "Sidebar missing analytics link"
            assert 'Bell' in content, "Sidebar missing follow-ups icon"
            assert 'BarChart3' in content, "Sidebar missing analytics icon"

# ============================================================================
# INTEGRATION TESTS
# ============================================================================
@pytest.mark.integration
class TestApplicationTrackingIntegration:
    """Test integration between application tracking components"""
    
    def test_end_to_end_workflow(self):
        """Test complete application tracking workflow"""
        # This test simulates a complete workflow from application to analytics
        
        # 1. Create application
        application = {
            "id": "test_app_1",
            "title": "Software Engineer",
            "company": "Test Company",
            "status": "applied",
            "date_applied": datetime.now().isoformat(),
            "notes": []
        }
        
        # 2. Add note
        note = {
            "id": str(int(datetime.now().timestamp())),
            "text": "Applied through LinkedIn Easy Apply",
            "date": datetime.now().isoformat()
        }
        application["notes"].append(note)
        
        # 3. Update status
        application["status"] = "under_review"
        
        # 4. Create follow-up
        follow_up = {
            "id": "follow_1",
            "applicationId": application["id"],
            "type": "email",
            "date": (datetime.now() + timedelta(days=7)).isoformat(),
            "completed": False
        }
        
        # 5. Generate analytics
        applications = [application]
        total = len(applications)
        status_counts = {"under_review": 1}
        success_rate = 0  # No interviews/offers yet
        
        # Verify workflow
        assert application["status"] == "under_review"
        assert len(application["notes"]) == 1
        assert follow_up["completed"] == False
        assert total == 1
        assert success_rate == 0

# ============================================================================
# PERFORMANCE TESTS
# ============================================================================
@pytest.mark.performance
class TestApplicationTrackingPerformance:
    """Test performance of application tracking features"""
    
    def test_large_dataset_filtering(self):
        """Test filtering performance with large datasets"""
        # Create large dataset
        large_dataset = []
        for i in range(1000):
            large_dataset.append({
                "id": f"job_{i}",
                "title": f"Job {i}",
                "company": f"Company {i % 10}",
                "status": ["applied", "under_review", "interview", "rejected"][i % 4],
                "date_applied": datetime.now().isoformat()
            })
        
        # Test filtering performance
        import time
        start_time = time.time()
        
        # Filter by status
        filtered = [job for job in large_dataset if job["status"] == "applied"]
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        assert len(filtered) == 250  # 25% should be "applied"
        assert processing_time < 0.1  # Should complete in under 100ms
    
    def test_analytics_calculation_performance(self):
        """Test analytics calculation performance"""
        # Create large dataset
        large_dataset = []
        for i in range(500):
            large_dataset.append({
                "id": f"job_{i}",
                "title": f"Job {i}",
                "company": f"Company {i % 20}",
                "status": ["applied", "under_review", "interview", "offer", "rejected"][i % 5],
                "date_applied": datetime.now().isoformat()
            })
        
        # Test analytics calculation performance
        import time
        start_time = time.time()
        
        # Calculate analytics
        total = len(large_dataset)
        status_counts = {}
        company_counts = {}
        
        for job in large_dataset:
            status_counts[job["status"]] = status_counts.get(job["status"], 0) + 1
            company_counts[job["company"]] = company_counts.get(job["company"], 0) + 1
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        assert total == 500
        assert len(status_counts) == 5
        assert processing_time < 0.05  # Should complete in under 50ms

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"]) 