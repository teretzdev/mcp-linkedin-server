#!/usr/bin/env python3
"""
Test script to verify automation features work correctly
"""

import os
import sys
import time
import subprocess
import requests
import socket
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AutomationTester:
    def __init__(self):
        self.test_results = []
        
    def test_port_detection(self):
        """Test automatic port detection"""
        logger.info("Testing port detection...")
        
        try:
            # Test if we can find available ports
            from auto_startup import AutoStartup
            startup = AutoStartup()
            
            # Test port availability check
            port_3000_available = startup.check_port_available(3000)
            logger.info(f"Port 3000 available: {port_3000_available}")
            
            # Test finding available port
            available_port = startup.find_available_port(3000)
            logger.info(f"Found available port: {available_port}")
            
            self.test_results.append(("Port Detection", "PASS"))
            return True
            
        except Exception as e:
            logger.error(f"Port detection test failed: {e}")
            self.test_results.append(("Port Detection", "FAIL"))
            return False
    
    def test_env_creation(self):
        """Test automatic .env file creation"""
        logger.info("Testing .env file creation...")
        
        try:
            # Backup existing .env if it exists
            env_backup = None
            if Path('.env').exists():
                env_backup = Path('.env').read_text()
                Path('.env').unlink()
            
            # Test env creation
            from auto_startup import AutoStartup
            startup = AutoStartup()
            result = startup.create_env_if_missing()
            
            # Restore backup if it existed
            if env_backup:
                Path('.env').write_text(env_backup)
            
            if result:
                logger.info("Env creation test passed")
                self.test_results.append(("Env Creation", "PASS"))
                return True
            else:
                logger.error("Env creation test failed")
                self.test_results.append(("Env Creation", "FAIL"))
                return False
                
        except Exception as e:
            logger.error(f"Env creation test failed: {e}")
            self.test_results.append(("Env Creation", "FAIL"))
            return False
    
    def test_service_health_check(self):
        """Test service health monitoring"""
        logger.info("Testing service health check...")
        
        try:
            from auto_startup import AutoStartup
            startup = AutoStartup()
            
            # Test with a non-existent service (should timeout)
            result = startup.wait_for_service("http://localhost:9999/health", timeout=2)
            if not result:
                logger.info("Health check correctly detected unavailable service")
                self.test_results.append(("Health Check", "PASS"))
                return True
            else:
                logger.error("Health check incorrectly reported unavailable service as available")
                self.test_results.append(("Health Check", "FAIL"))
                return False
                
        except Exception as e:
            logger.error(f"Health check test failed: {e}")
            self.test_results.append(("Health Check", "FAIL"))
            return False
    
    def test_dependencies(self):
        """Test required dependencies are available"""
        logger.info("Testing dependencies...")
        
        try:
            import psutil
            import requests
            logger.info("All required dependencies are available")
            self.test_results.append(("Dependencies", "PASS"))
            return True
            
        except ImportError as e:
            logger.error(f"Missing dependency: {e}")
            self.test_results.append(("Dependencies", "FAIL"))
            return False
    
    def test_automation_script(self):
        """Test that automation script can be imported and initialized"""
        logger.info("Testing automation script...")
        
        try:
            from auto_startup import AutoStartup
            startup = AutoStartup()
            
            # Test basic initialization
            assert startup.services is not None
            assert len(startup.services) == 4  # api_bridge, mcp_backend, llm_controller, react_frontend
            
            logger.info("Automation script initialization successful")
            self.test_results.append(("Automation Script", "PASS"))
            return True
            
        except Exception as e:
            logger.error(f"Automation script test failed: {e}")
            self.test_results.append(("Automation Script", "FAIL"))
            return False
    
    def test_batch_files_exist(self):
        """Test that all automation batch files exist"""
        logger.info("Testing batch files...")
        
        batch_files = [
            'start_auto.bat',
            'start_all_auto.bat', 
            'start_frontend_auto.bat'
        ]
        
        missing_files = []
        for file in batch_files:
            if not Path(file).exists():
                missing_files.append(file)
        
        if not missing_files:
            logger.info("All automation batch files exist")
            self.test_results.append(("Batch Files", "PASS"))
            return True
        else:
            logger.error(f"Missing batch files: {missing_files}")
            self.test_results.append(("Batch Files", "FAIL"))
            return False
    
    def run_all_tests(self):
        """Run all automation tests"""
        logger.info("Starting automation tests...")
        
        tests = [
            self.test_dependencies,
            self.test_batch_files_exist,
            self.test_automation_script,
            self.test_port_detection,
            self.test_env_creation,
            self.test_service_health_check
        ]
        
        passed = 0
        total = len(tests)
        
        for test in tests:
            try:
                if test():
                    passed += 1
            except Exception as e:
                logger.error(f"Test {test.__name__} failed with exception: {e}")
        
        # Print results
        logger.info("\n" + "="*50)
        logger.info("AUTOMATION TEST RESULTS")
        logger.info("="*50)
        
        for test_name, result in self.test_results:
            logger.info(f"{test_name:<20} : {result}")
        
        logger.info("="*50)
        logger.info(f"Passed: {passed}/{total}")
        logger.info(f"Success Rate: {(passed/total)*100:.1f}%")
        
        if passed == total:
            logger.info("🎉 ALL AUTOMATION TESTS PASSED!")
            logger.info("The automation system is ready to use without manual intervention.")
        else:
            logger.warning("⚠️  Some tests failed. Check the logs above for details.")
        
        return passed == total

def main():
    """Main test function"""
    tester = AutomationTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 