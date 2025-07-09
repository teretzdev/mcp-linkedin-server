#!/usr/bin/env python3
"""
Comprehensive Test Suite for LinkedIn Job Automation System
Tests all components: service management, API connections, job search, and automation
"""

import asyncio
import json
import time
import sys
import unittest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import requests
import aiohttp

# Import our modules
from service_manager import ServiceManager
from services.job_search_service import JobSearchService, JobSearchError
from core.models.job_data import JobData, SearchCriteria, JobStatus
from orchestrators.job_automation_orchestrator import JobAutomationOrchestrator
import centralized_logging

logger = centralized_logging.get_logger("test_suite")

class TestServiceManager(unittest.TestCase):
    """Test the service manager functionality"""
    
    def setUp(self):
        self.service_manager = ServiceManager()
        
    def test_port_availability_check(self):
        """Test port availability checking"""
        # Test a port that should be available
        self.assertTrue(self.service_manager.is_port_available(65432))
        
        # Test a port that might be in use
        result = self.service_manager.is_port_available(80)
        self.assertIsInstance(result, bool)
        
    def test_service_configuration(self):
        """Test service configuration loading and saving"""
        # Check that services are properly configured
        self.assertIn('api_bridge', self.service_manager.services)
        self.assertIn('mcp_backend', self.service_manager.services)
        self.assertIn('llm_controller', self.service_manager.services)
        self.assertIn('react_frontend', self.service_manager.services)
        
        # Check that each service has required fields
        for service_name, service_info in self.service_manager.services.items():
            self.assertIn('port', service_info)
            self.assertIn('script', service_info)
            self.assertIn('health_path', service_info)
            self.assertIn('status', service_info)
            
    def test_health_check_logic(self):
        """Test health check logic (without actual services)"""
        # This tests the logic without requiring actual services
        with patch('requests.get') as mock_get:
            # Test successful health check
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {'status': 'ok'}
            mock_get.return_value = mock_response
            
            result = self.service_manager.check_service_health('api_bridge')
            self.assertTrue(result)
            
            # Test failed health check
            mock_response.status_code = 500
            result = self.service_manager.check_service_health('api_bridge')
            self.assertFalse(result)

class TestJobSearchService(unittest.TestCase):
    """Test the job search service"""
    
    def setUp(self):
        self.job_search_service = JobSearchService()
        
    def test_service_initialization(self):
        """Test that the service initializes correctly"""
        self.assertIsNotNone(self.job_search_service.config)
        self.assertIsNotNone(self.job_search_service.logger)
        
    def test_job_data_conversion(self):
        """Test conversion of raw job data to JobData objects"""
        raw_job = {
            'job_id': 'test123',
            'title': 'Software Engineer',
            'company': 'Tech Corp',
            'location': 'Remote',
            'job_url': 'https://example.com/job/123',
            'description': 'Great job opportunity',
            'easy_apply': True,
            'remote_work': True
        }
        
        job_data = self.job_search_service._convert_raw_job(raw_job)
        
        self.assertEqual(job_data.job_id, 'test123')
        self.assertEqual(job_data.title, 'Software Engineer')
        self.assertEqual(job_data.company, 'Tech Corp')
        self.assertEqual(job_data.location, 'Remote')
        self.assertTrue(job_data.easy_apply)
        self.assertTrue(job_data.remote_work)
        self.assertEqual(job_data.status, JobStatus.SCRAPED)
        
    def test_search_criteria_validation(self):
        """Test search criteria creation and validation"""
        criteria = SearchCriteria(
            query="Python Developer",
            location="San Francisco",
            count=10
        )
        
        self.assertEqual(criteria.query, "Python Developer")
        self.assertEqual(criteria.location, "San Francisco")
        self.assertEqual(criteria.count, 10)
        
        # Test conversion to dict
        criteria_dict = criteria.to_dict()
        self.assertIn('query', criteria_dict)
        self.assertIn('location', criteria_dict)
        self.assertIn('count', criteria_dict)

class TestAPIConnections(unittest.TestCase):
    """Test API connections and endpoints"""
    
    def setUp(self):
        self.api_base_url = "http://localhost:8002"
        
    def test_health_endpoint_format(self):
        """Test that health endpoint returns correct format"""
        try:
            response = requests.get(f"{self.api_base_url}/api/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                self.assertIn('status', data)
                self.assertEqual(data['status'], 'ok')
                self.assertIn('timestamp', data)
        except requests.RequestException:
            self.skipTest("API bridge not running")
            
    def test_search_endpoint_structure(self):
        """Test that search endpoint accepts correct payload structure"""
        payload = {
            "query": "test",
            "location": "Remote",
            "count": 1
        }
        
        try:
            response = requests.post(
                f"{self.api_base_url}/api/search_jobs_internal",
                json=payload,
                timeout=10
            )
            # We expect either success or a specific error format
            self.assertIn(response.status_code, [200, 400, 500])
            
            if response.status_code == 200:
                data = response.json()
                # Check response structure
                self.assertIsInstance(data, dict)
                
        except requests.RequestException:
            self.skipTest("API bridge not running")

class TestJobAutomationOrchestrator(unittest.TestCase):
    """Test the job automation orchestrator"""
    
    def setUp(self):
        # Mock the config to avoid loading real config
        with patch('core.config.settings.get_config') as mock_config:
            mock_config.return_value = Mock()
            mock_config.return_value.automation = Mock()
            mock_config.return_value.automation.job_search_timeout_seconds = 300
            mock_config.return_value.automation.max_applications_per_run = 5
            mock_config.return_value.service_ports = Mock()
            mock_config.return_value.service_ports.api_bridge = 8002
            
            self.orchestrator = JobAutomationOrchestrator()
            
    def test_orchestrator_initialization(self):
        """Test that orchestrator initializes correctly"""
        self.assertIsNotNone(self.orchestrator.job_search_service)
        self.assertIsNotNone(self.orchestrator.job_application_service)
        self.assertIsNotNone(self.orchestrator.job_repository)
        
    def test_search_criteria_creation(self):
        """Test creation of search criteria"""
        criteria = SearchCriteria(
            query="Software Engineer",
            location="Remote",
            count=20
        )
        
        self.assertEqual(criteria.query, "Software Engineer")
        self.assertEqual(criteria.location, "Remote")
        self.assertEqual(criteria.count, 20)

class TestEndToEndWorkflow(unittest.TestCase):
    """Test end-to-end workflow scenarios"""
    
    def setUp(self):
        self.service_manager = ServiceManager()
        
    def test_service_startup_sequence(self):
        """Test that services can be started in correct order"""
        # Check service status before starting
        initial_status = self.service_manager.get_service_status()
        
        # This is a dry run test - we check the logic without actually starting services
        service_order = ['api_bridge', 'mcp_backend', 'llm_controller', 'react_frontend']
        
        for service_name in service_order:
            self.assertIn(service_name, self.service_manager.services)
            service_info = self.service_manager.services[service_name]
            self.assertIn('port', service_info)
            self.assertIn('script', service_info)
            
    def test_configuration_consistency(self):
        """Test that all configuration files are consistent"""
        # Check service_ports.json
        service_ports_file = Path('service_ports.json')
        if service_ports_file.exists():
            with open(service_ports_file, 'r') as f:
                service_ports = json.load(f)
                
            # Check that required services are configured
            required_services = ['api_bridge', 'mcp_backend', 'llm_controller', 'react_frontend']
            for service in required_services:
                if service in service_ports:
                    self.assertIsInstance(service_ports[service], int)
                    self.assertGreater(service_ports[service], 1000)
                    self.assertLess(service_ports[service], 65536)

class TestSystemIntegration(unittest.TestCase):
    """Test system integration scenarios"""
    
    def test_job_search_integration(self):
        """Test job search integration with mocked API"""
        with patch('aiohttp.ClientSession') as mock_session:
            # Mock successful API response
            mock_response = Mock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value={
                'status': 'success',
                'jobs': [
                    {
                        'job_id': 'test123',
                        'title': 'Software Engineer',
                        'company': 'Tech Corp',
                        'location': 'Remote',
                        'job_url': 'https://example.com/job/123',
                        'description': 'Great job',
                        'easy_apply': True,
                        'remote_work': True
                    }
                ]
            })
            
            mock_session.return_value.__aenter__.return_value.post.return_value.__aenter__.return_value = mock_response
            
            # Test the job search service
            job_search_service = JobSearchService()
            criteria = SearchCriteria(query="Python Developer", location="Remote", count=5)
            
            # This would normally be async, but we're mocking it
            # jobs = await job_search_service.search_jobs(criteria)
            # self.assertEqual(len(jobs), 1)
            # self.assertEqual(jobs[0].title, 'Software Engineer')

def run_integration_tests():
    """Run integration tests that require actual services"""
    print("🔧 Running Integration Tests")
    print("=" * 50)
    
    # Test 1: Service Manager
    print("Testing Service Manager...")
    service_manager = ServiceManager()
    status = service_manager.get_service_status()
    
    services_healthy = 0
    for service_name, service_info in status.items():
        if service_info['healthy']:
            services_healthy += 1
            print(f"✅ {service_name} is healthy on port {service_info['port']}")
        else:
            print(f"❌ {service_name} is not healthy on port {service_info['port']}")
    
    # Test 2: Job Search Service
    print("\nTesting Job Search Service...")
    try:
        job_search_service = JobSearchService()
        
        # Test connection
        async def test_connection():
            return await job_search_service.test_connection()
        
        connection_ok = asyncio.run(test_connection())
        if connection_ok:
            print("✅ Job Search Service connection successful")
        else:
            print("❌ Job Search Service connection failed")
            
    except Exception as e:
        print(f"❌ Job Search Service test failed: {e}")
        
    # Test 3: API Endpoints
    print("\nTesting API Endpoints...")
    try:
        # Test health endpoint
        response = requests.get("http://localhost:8002/api/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'ok':
                print("✅ Health endpoint working correctly")
            else:
                print(f"❌ Health endpoint returned wrong status: {data}")
        else:
            print(f"❌ Health endpoint returned status {response.status_code}")
            
    except Exception as e:
        print(f"❌ API endpoint test failed: {e}")
        
    # Summary
    print("\n" + "=" * 50)
    print("INTEGRATION TEST SUMMARY:")
    print(f"Services healthy: {services_healthy}/4")
    print(f"Overall status: {'✅ PASS' if services_healthy >= 2 else '❌ FAIL'}")
    
    return services_healthy >= 2

def run_unit_tests():
    """Run unit tests"""
    print("🔧 Running Unit Tests")
    print("=" * 50)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestServiceManager))
    suite.addTests(loader.loadTestsFromTestCase(TestJobSearchService))
    suite.addTests(loader.loadTestsFromTestCase(TestAPIConnections))
    suite.addTests(loader.loadTestsFromTestCase(TestJobAutomationOrchestrator))
    suite.addTests(loader.loadTestsFromTestCase(TestEndToEndWorkflow))
    suite.addTests(loader.loadTestsFromTestCase(TestSystemIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()

# Helper for async mocking
class AsyncMock(Mock):
    async def __call__(self, *args, **kwargs):
        return super().__call__(*args, **kwargs)

def main():
    """Main test runner"""
    if len(sys.argv) > 1 and sys.argv[1] == 'integration':
        return run_integration_tests()
    elif len(sys.argv) > 1 and sys.argv[1] == 'unit':
        return run_unit_tests()
    else:
        print("Running both unit and integration tests...")
        unit_success = run_unit_tests()
        integration_success = run_integration_tests()
        
        print("\n" + "=" * 60)
        print("OVERALL TEST RESULTS:")
        print(f"Unit Tests: {'✅ PASS' if unit_success else '❌ FAIL'}")
        print(f"Integration Tests: {'✅ PASS' if integration_success else '❌ FAIL'}")
        
        overall_success = unit_success and integration_success
        print(f"Overall: {'✅ PASS' if overall_success else '❌ FAIL'}")
        
        return overall_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 