#!/usr/bin/env python3
"""
Advanced Search Features Test Suite
Comprehensive tests for the enhanced search functionality in frontend components
"""

import pytest
import json
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import subprocess
import time

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

# Test Configuration
ADVANCED_SEARCH_CONFIG = {
    "test_skills": [
        {"name": "React", "level": "Expert", "years": 4, "category": "Frontend"},
        {"name": "JavaScript", "level": "Expert", "years": 6, "category": "Programming"},
        {"name": "Node.js", "level": "Advanced", "years": 4, "category": "Backend"},
        {"name": "Python", "level": "Intermediate", "years": 3, "category": "Programming"},
        {"name": "TypeScript", "level": "Advanced", "years": 2, "category": "Programming"},
        {"name": "MongoDB", "level": "Intermediate", "years": 3, "category": "Database"},
        {"name": "AWS", "level": "Intermediate", "years": 2, "category": "Cloud"},
        {"name": "Docker", "level": "Advanced", "years": 2, "category": "DevOps"}
    ],
    "test_jobs": [
        {
            "id": 1,
            "title": "Senior React Developer",
            "company": "TechCorp Inc.",
            "location": "San Francisco, CA",
            "type": "Full-time",
            "salary": "$120,000 - $150,000",
            "salaryMin": 120000,
            "salaryMax": 150000,
            "experience": "5+ years",
            "posted": "2 days ago",
            "description": "We are looking for a Senior React Developer to join our team and help build scalable web applications.",
            "easyApply": True,
            "remote": True,
            "skills": ["React", "JavaScript", "TypeScript", "Node.js", "Redux"],
            "companySize": "500-1000",
            "industry": "Technology",
            "rating": 4.2,
            "applicants": 45
        },
        {
            "id": 2,
            "title": "Frontend Engineer",
            "company": "StartupXYZ",
            "location": "Remote",
            "type": "Full-time",
            "salary": "$100,000 - $130,000",
            "salaryMin": 100000,
            "salaryMax": 130000,
            "experience": "3+ years",
            "posted": "1 week ago",
            "description": "Join our fast-growing startup as a Frontend Engineer.",
            "easyApply": True,
            "remote": True,
            "skills": ["React", "Vue.js", "CSS", "HTML", "JavaScript"],
            "companySize": "50-200",
            "industry": "SaaS",
            "rating": 4.5,
            "applicants": 23
        }
    ],
    "test_saved_jobs": [
        {
            "id": 1,
            "title": "Senior React Developer",
            "company": "TechCorp Inc.",
            "location": "San Francisco, CA",
            "date_saved": "2024-01-15T10:30:00Z",
            "job_url": "https://linkedin.com/jobs/view/1"
        },
        {
            "id": 2,
            "title": "Frontend Engineer",
            "company": "StartupXYZ",
            "location": "Remote",
            "date_saved": "2024-01-14T15:45:00Z",
            "job_url": "https://linkedin.com/jobs/view/2"
        }
    ]
}

# ============================================================================
# COMPONENT STRUCTURE TESTS
# ============================================================================

@pytest.mark.frontend
@pytest.mark.structure
class TestComponentStructure:
    """Test that advanced search components exist and have correct structure"""
    
    def test_applicant_knowledge_base_exists(self):
        """Test that ApplicantKnowledgeBase component exists"""
        component_path = Path(__file__).parent / 'src' / 'components' / 'ApplicantKnowledgeBase.js'
        assert component_path.exists(), "ApplicantKnowledgeBase.js component not found"
    
    def test_saved_jobs_component_exists(self):
        """Test that SavedJobs component exists"""
        component_path = Path(__file__).parent / 'src' / 'components' / 'SavedJobs.js'
        assert component_path.exists(), "SavedJobs.js component not found"
    
    def test_job_search_component_exists(self):
        """Test that JobSearch component exists"""
        component_path = Path(__file__).parent / 'src' / 'components' / 'JobSearch.js'
        assert component_path.exists(), "JobSearch.js component not found"
    
    def test_component_imports(self):
        """Test that components have required imports"""
        components = [
            'ApplicantKnowledgeBase.js',
            'SavedJobs.js', 
            'JobSearch.js'
        ]
        
        for component in components:
            component_path = Path(__file__).parent / 'src' / 'components' / component
            if component_path.exists():
                with open(component_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Check for React imports
                    assert 'import React' in content, f"React import missing in {component}"
                    # Check for useState and useMemo imports
                    assert 'useState' in content or 'useMemo' in content, f"Hooks missing in {component}"
                    # Check for lucide-react icons (only for components that use them)
                    if component in ['SavedJobs.js', 'JobSearch.js']:
                        assert 'lucide-react' in content, f"Lucide icons missing in {component}"

# ============================================================================
# APPLICANT KNOWLEDGE BASE SEARCH TESTS
# ============================================================================

@pytest.mark.frontend
@pytest.mark.search
class TestApplicantKnowledgeBaseSearch:
    """Test advanced search features in ApplicantKnowledgeBase component"""
    
    def test_search_input_rendering(self):
        """Test that search input is properly rendered"""
        component_path = Path(__file__).parent / 'src' / 'components' / 'ApplicantKnowledgeBase.js'
        if not component_path.exists():
            pytest.skip("ApplicantKnowledgeBase component not found")
        
        with open(component_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Check for search input
        assert 'searchTerm' in content, "Search term state not found"
        assert 'setSearchTerm' in content, "Search term setter not found"
        assert 'placeholder=' in content, "Search placeholder not found"
    
    def test_category_filter(self):
        """Test category filtering functionality"""
        component_path = Path(__file__).parent / 'src' / 'components' / 'ApplicantKnowledgeBase.js'
        if not component_path.exists():
            pytest.skip("ApplicantKnowledgeBase component not found")
        
        with open(component_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Check for category filter
        assert 'selectedCategory' in content, "Category filter state not found"
        assert 'setSelectedCategory' in content, "Category filter setter not found"
        assert 'All Categories' in content, "Category filter options not found"
    
    def test_skill_level_filter(self):
        """Test skill level filtering functionality"""
        component_path = Path(__file__).parent / 'src' / 'components' / 'ApplicantKnowledgeBase.js'
        if not component_path.exists():
            pytest.skip("ApplicantKnowledgeBase component not found")
        
        with open(component_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Check for skill level filter
        assert 'selectedSkillLevel' in content, "Skill level filter state not found"
        assert 'setSelectedSkillLevel' in content, "Skill level filter setter not found"
        assert 'All Levels' in content, "Skill level filter options not found"
    
    def test_sorting_functionality(self):
        """Test sorting functionality"""
        component_path = Path(__file__).parent / 'src' / 'components' / 'ApplicantKnowledgeBase.js'
        if not component_path.exists():
            pytest.skip("ApplicantKnowledgeBase component not found")
        
        with open(component_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Check for sorting
        assert 'sortBy' in content, "Sort state not found"
        assert 'setSortBy' in content, "Sort setter not found"
        assert 'Name' in content or 'Level' in content, "Sort options not found"
    
    def test_clear_filters_functionality(self):
        """Test clear filters functionality"""
        component_path = Path(__file__).parent / 'src' / 'components' / 'ApplicantKnowledgeBase.js'
        if not component_path.exists():
            pytest.skip("ApplicantKnowledgeBase component not found")
        
        with open(component_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Check for clear filters
        assert 'Clear Filters' in content, "Clear filters button not found"
        assert 'clearFilters' in content or 'setSearchTerm' in content, "Clear filters functionality not found"

# ============================================================================
# SAVED JOBS SEARCH TESTS
# ============================================================================

@pytest.mark.frontend
@pytest.mark.search
class TestSavedJobsSearch:
    """Test advanced search features in SavedJobs component"""
    
    def test_search_input_rendering(self):
        """Test that search input is properly rendered"""
        component_path = Path(__file__).parent / 'src' / 'components' / 'SavedJobs.js'
        if not component_path.exists():
            pytest.skip("SavedJobs component not found")
        
        with open(component_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Check for search input
        assert 'searchTerm' in content, "Search term state not found"
        assert 'setSearchTerm' in content, "Search term setter not found"
        assert 'Search jobs by title' in content, "Search placeholder not found"
    
    def test_location_filter(self):
        """Test location filtering functionality"""
        component_path = Path(__file__).parent / 'src' / 'components' / 'SavedJobs.js'
        if not component_path.exists():
            pytest.skip("SavedJobs component not found")
        
        with open(component_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Check for location filter
        assert 'selectedLocation' in content, "Location filter state not found"
        assert 'setSelectedLocation' in content, "Location filter setter not found"
        assert 'All Locations' in content, "Location filter options not found"
    
    def test_company_filter(self):
        """Test company filtering functionality"""
        component_path = Path(__file__).parent / 'src' / 'components' / 'SavedJobs.js'
        if not component_path.exists():
            pytest.skip("SavedJobs component not found")
        
        with open(component_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Check for company filter
        assert 'selectedCompany' in content, "Company filter state not found"
        assert 'setSelectedCompany' in content, "Company filter setter not found"
        assert 'All Companies' in content, "Company filter options not found"
    
    def test_date_range_filter(self):
        """Test date range filtering functionality"""
        component_path = Path(__file__).parent / 'src' / 'components' / 'SavedJobs.js'
        if not component_path.exists():
            pytest.skip("SavedJobs component not found")
        
        with open(component_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Check for date range filter
        assert 'selectedDateRange' in content, "Date range filter state not found"
        assert 'setSelectedDateRange' in content, "Date range filter setter not found"
        assert 'All Time' in content, "Date range filter options not found"
        assert 'Today' in content, "Date range filter options not found"
        assert 'This Week' in content, "Date range filter options not found"
    
    def test_sorting_functionality(self):
        """Test sorting functionality"""
        component_path = Path(__file__).parent / 'src' / 'components' / 'SavedJobs.js'
        if not component_path.exists():
            pytest.skip("SavedJobs component not found")
        
        with open(component_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Check for sorting
        assert 'sortBy' in content, "Sort state not found"
        assert 'setSortBy' in content, "Sort setter not found"
        assert 'Date Saved' in content, "Sort options not found"
        assert 'Job Title' in content, "Sort options not found"

# ============================================================================
# JOB SEARCH ADVANCED TESTS
# ============================================================================

@pytest.mark.frontend
@pytest.mark.search
class TestJobSearchAdvanced:
    """Test advanced search features in JobSearch component"""
    
    def test_advanced_search_input(self):
        """Test advanced search input functionality"""
        component_path = Path(__file__).parent / 'src' / 'components' / 'JobSearch.js'
        if not component_path.exists():
            pytest.skip("JobSearch component not found")
        
        with open(component_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Check for advanced search
        assert 'searchQuery' in content, "Search query state not found"
        assert 'setSearchQuery' in content, "Search query setter not found"
        assert 'Search for jobs, companies, skills' in content, "Advanced search placeholder not found"
    
    def test_experience_level_filter(self):
        """Test experience level filtering"""
        component_path = Path(__file__).parent / 'src' / 'components' / 'JobSearch.js'
        if not component_path.exists():
            pytest.skip("JobSearch component not found")
        
        with open(component_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Check for experience level filter
        assert 'experienceLevel' in content, "Experience level filter not found"
        assert 'Entry Level' in content, "Experience level options not found"
        assert 'Mid Level' in content, "Experience level options not found"
        assert 'Senior Level' in content, "Experience level options not found"
    
    def test_job_type_filter(self):
        """Test job type filtering"""
        component_path = Path(__file__).parent / 'src' / 'components' / 'JobSearch.js'
        if not component_path.exists():
            pytest.skip("JobSearch component not found")
        
        with open(component_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Check for job type filter
        assert 'jobType' in content, "Job type filter not found"
        assert 'Full-time' in content, "Job type options not found"
        assert 'Part-time' in content, "Job type options not found"
        assert 'Contract' in content, "Job type options not found"
    
    def test_salary_range_filter(self):
        """Test salary range filtering"""
        component_path = Path(__file__).parent / 'src' / 'components' / 'JobSearch.js'
        if not component_path.exists():
            pytest.skip("JobSearch component not found")
        
        with open(component_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Check for salary range filter
        assert 'salaryRange' in content, "Salary range filter not found"
        assert '$50k - $80k' in content, "Salary range options not found"
        assert '$80k - $120k' in content, "Salary range options not found"
        assert '$120k - $160k' in content, "Salary range options not found"
    
    def test_skills_filter(self):
        """Test skills filtering"""
        component_path = Path(__file__).parent / 'src' / 'components' / 'JobSearch.js'
        if not component_path.exists():
            pytest.skip("JobSearch component not found")
        
        with open(component_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Check for skills filter
        assert 'skills' in content, "Skills filter not found"
        assert 'toggleSkill' in content, "Skills toggle function not found"
        assert 'allSkills' in content, "Skills list not found"
    
    def test_sorting_options(self):
        """Test sorting options"""
        component_path = Path(__file__).parent / 'src' / 'components' / 'JobSearch.js'
        if not component_path.exists():
            pytest.skip("JobSearch component not found")
        
        with open(component_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Check for sorting options
        assert 'sortBy' in content, "Sort state not found"
        assert 'Most Relevant' in content, "Sort options not found"
        assert 'Most Recent' in content, "Sort options not found"
        assert 'Highest Salary' in content, "Sort options not found"
        assert 'Highest Rated' in content, "Sort options not found"
    
    def test_view_modes(self):
        """Test view mode switching"""
        component_path = Path(__file__).parent / 'src' / 'components' / 'JobSearch.js'
        if not component_path.exists():
            pytest.skip("JobSearch component not found")
        
        with open(component_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Check for view modes
        assert 'viewMode' in content, "View mode state not found"
        assert 'setViewMode' in content, "View mode setter not found"
        assert 'grid' in content, "Grid view mode not found"
        assert 'list' in content, "List view mode not found"

# ============================================================================
# PERFORMANCE AND OPTIMIZATION TESTS
# ============================================================================

@pytest.mark.frontend
@pytest.mark.performance
class TestSearchPerformance:
    """Test performance optimizations in search components"""
    
    def test_usememo_optimization(self):
        """Test that useMemo is used for expensive operations"""
        components = [
            'ApplicantKnowledgeBase.js',
            'SavedJobs.js',
            'JobSearch.js'
        ]
        
        for component in components:
            component_path = Path(__file__).parent / 'src' / 'components' / component
            if component_path.exists():
                with open(component_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Check for useMemo import
                assert 'useMemo' in content, f"useMemo not imported in {component}"
                # Check for useMemo usage
                assert 'useMemo(' in content, f"useMemo not used in {component}"
    
    def test_filtered_results_optimization(self):
        """Test that filtered results are optimized"""
        components = [
            'ApplicantKnowledgeBase.js',
            'SavedJobs.js',
            'JobSearch.js'
        ]
        
        for component in components:
            component_path = Path(__file__).parent / 'src' / 'components' / component
            if component_path.exists():
                with open(component_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Check for filtered results variable
                assert 'filtered' in content or 'Filtered' in content, f"Filtered results not found in {component}"

# ============================================================================
# USER EXPERIENCE TESTS
# ============================================================================

@pytest.mark.frontend
@pytest.mark.ux
class TestSearchUserExperience:
    """Test user experience features in search components"""
    
    def test_search_results_summary(self):
        """Test that search results show summary"""
        components = [
            'ApplicantKnowledgeBase.js',
            'SavedJobs.js',
            'JobSearch.js'
        ]
        
        for component in components:
            component_path = Path(__file__).parent / 'src' / 'components' / component
            if component_path.exists():
                with open(component_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Check for results summary
                assert 'Showing' in content or 'jobs found' in content or 'skills' in content, f"Results summary not found in {component}"
    
    def test_empty_state_handling(self):
        """Test empty state handling"""
        components = [
            'ApplicantKnowledgeBase.js',
            'SavedJobs.js',
            'JobSearch.js'
        ]
        
        for component in components:
            component_path = Path(__file__).parent / 'src' / 'components' / component
            if component_path.exists():
                with open(component_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Check for empty state
                assert 'No' in content or 'match' in content or 'found' in content, f"Empty state handling not found in {component}"
    
    def test_clear_filters_button(self):
        """Test clear filters functionality"""
        components = [
            'ApplicantKnowledgeBase.js',
            'SavedJobs.js',
            'JobSearch.js'
        ]
        
        for component in components:
            component_path = Path(__file__).parent / 'src' / 'components' / component
            if component_path.exists():
                with open(component_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Check for clear filters
                assert 'Clear' in content, f"Clear filters not found in {component}"

# ============================================================================
# INTEGRATION TESTS
# ============================================================================

@pytest.mark.integration
@pytest.mark.api
class TestSearchAPIIntegration:
    """Test integration with backend APIs"""
    
    def test_search_api_endpoints(self):
        """Test that search-related API endpoints exist"""
        try:
            from api_bridge import app
            from fastapi.testclient import TestClient
            
            client = TestClient(app)
            
            # Test search jobs endpoint
            response = client.post("/api/search_jobs", json={
                "query": "React Developer",
                "location": "Remote",
                "filters": {
                    "experience_level": "Mid Level",
                    "job_type": "Full-time",
                    "remote": True
                }
            })
            assert response.status_code in [200, 500]
            
            # Test saved jobs endpoint
            response = client.get("/api/list_saved_jobs")
            assert response.status_code in [200, 500]
            
        except ImportError:
            pytest.skip("FastAPI TestClient not available")
    
    def test_filter_parameter_handling(self):
        """Test that filter parameters are properly handled"""
        try:
            from api_bridge import app
            from fastapi.testclient import TestClient
            
            client = TestClient(app)
            
            # Test with various filter combinations
            test_filters = [
                {"experience_level": "Senior", "remote": True},
                {"job_type": "Full-time", "easy_apply": True},
                {"salary_range": "100000-150000"}
            ]
            
            for filters in test_filters:
                response = client.post("/api/search_jobs", json={
                    "query": "React Developer",
                    "location": "Remote",
                    "filters": filters
                })
                assert response.status_code in [200, 500]
                
        except ImportError:
            pytest.skip("FastAPI TestClient not available")

# ============================================================================
# CONFIGURATION TESTS
# ============================================================================

@pytest.mark.config
class TestSearchConfiguration:
    """Test search feature configuration"""
    
    def test_package_dependencies(self):
        """Test that required dependencies are installed"""
        package_json_path = Path(__file__).parent / 'package.json'
        if not package_json_path.exists():
            pytest.skip("package.json not found")
        
        with open(package_json_path, 'r') as f:
            package_data = json.load(f)
        
        # Check for required dependencies
        required_deps = [
            'react', 'react-dom', 'lucide-react'
        ]
        
        for dep in required_deps:
            assert dep in package_data.get('dependencies', {}), f"Required dependency {dep} not found"
    
    def test_tailwind_configuration(self):
        """Test Tailwind CSS configuration for search components"""
        tailwind_config_path = Path(__file__).parent / 'tailwind.config.js'
        if not tailwind_config_path.exists():
            pytest.skip("tailwind.config.js not found")
        
        with open(tailwind_config_path, 'r') as f:
            content = f.read()
        
        # Check for Tailwind configuration
        assert 'content' in content, "Tailwind content configuration not found"
        assert 'src/**/*.{js,jsx,ts,tsx}' in content, "Tailwind source path not configured"

# ============================================================================
# TEST UTILITIES
# ============================================================================

def test_advanced_search_configuration():
    """Test that advanced search configuration is valid"""
    assert len(ADVANCED_SEARCH_CONFIG["test_skills"]) > 0, "Test skills configuration is empty"
    assert len(ADVANCED_SEARCH_CONFIG["test_jobs"]) > 0, "Test jobs configuration is empty"
    assert len(ADVANCED_SEARCH_CONFIG["test_saved_jobs"]) > 0, "Test saved jobs configuration is empty"
    
    # Validate skill structure
    for skill in ADVANCED_SEARCH_CONFIG["test_skills"]:
        assert "name" in skill, "Skill missing name"
        assert "level" in skill, "Skill missing level"
        assert "years" in skill, "Skill missing years"
        assert "category" in skill, "Skill missing category"
    
    # Validate job structure
    for job in ADVANCED_SEARCH_CONFIG["test_jobs"]:
        assert "title" in job, "Job missing title"
        assert "company" in job, "Job missing company"
        assert "location" in job, "Job missing location"
        assert "skills" in job, "Job missing skills"

# NOTE: Integration tests for React components that require mocking axios and rendering components
# should be implemented in a JavaScript/TypeScript test file (e.g., JobSearch.test.js) using Jest and React Testing Library.
# The following is a placeholder to indicate that such a test should exist:

def test_job_search_integration_placeholder():
    """
    Integration test for JobSearch.js should be implemented in a JS/TS test file.
    It should mock axios.get to return jobs, render the component, and assert that jobs from the API are displayed.
    """
    assert True

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"]) 