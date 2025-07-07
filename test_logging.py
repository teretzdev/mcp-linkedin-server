#!/usr/bin/env python3
"""
Test script for centralized logging system
"""

import time
from centralized_logging import get_logger, log_manager

def test_logging():
    """Test the logging system"""
    print("Testing centralized logging system...")
    
    # Get logger for test service
    logger = get_logger("test_service")
    
    # Test different log levels
    logger.log_info("Test info message", test_data="info_test")
    logger.log_warning("Test warning message", test_data="warning_test")
    
    # Test error logging
    try:
        raise ValueError("Test error for logging")
    except Exception as e:
        logger.log_error("Test error occurred", e, error_type="test_error")
    
    # Test performance logging
    logger.log_performance("test_operation", 0.5, operation_type="test")
    
    # Test audit logging
    logger.log_audit("test_action", "test_user", action_type="test")
    
    # Test critical error
    logger.log_critical("Test critical error", None, critical_type="test")
    
    print("✅ Basic logging tests completed")
    
    # Get summaries
    print("\nGetting log summaries...")
    summaries = log_manager.get_all_summaries()
    
    print(f"Total services: {summaries['system']['total_services']}")
    for service_name, service_data in summaries['system']['services'].items():
        print(f"\nService: {service_name}")
        print(f"  Error count: {service_data['error_summary']['error_count']}")
        print(f"  Operations: {service_data['performance_summary']['operations']}")
        if service_data['performance_summary']['operations'] > 0:
            print(f"  Avg duration: {service_data['performance_summary']['avg_duration']:.3f}s")
    
    print("\n✅ Logging system test completed!")

if __name__ == "__main__":
    test_logging() 