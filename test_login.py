#!/usr/bin/env python3
"""
Test script to verify the login endpoint is working
"""

import requests
import json

def test_login_endpoint():
    """Test the login endpoint"""
    try:
        # Test the login endpoint
        response = requests.post('http://localhost:8001/api/login_linkedin_secure')
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Login endpoint is working!")
            return True
        else:
            print("❌ Login endpoint failed!")
            return False
            
    except Exception as e:
        print(f"❌ Error testing login endpoint: {e}")
        return False

def test_health_endpoint():
    """Test the health endpoint"""
    try:
        response = requests.get('http://localhost:8001/api/health')
        print(f"Health Status: {response.status_code}")
        return response.status_code == 200
    except Exception as e:
        print(f"Health check failed: {e}")
        return False

if __name__ == "__main__":
    print("Testing API endpoints...")
    print("=" * 40)
    
    # Test health first
    if test_health_endpoint():
        print("✅ Health endpoint working")
    else:
        print("❌ Health endpoint failed")
        exit(1)
    
    print()
    
    # Test login endpoint
    if test_login_endpoint():
        print("✅ All tests passed!")
    else:
        print("❌ Login test failed!") 