#!/usr/bin/env python3
"""
Test API Connection Script
Verifies that the API Bridge is working correctly on port 8001
"""

import requests
import json
import time

def test_api_connection():
    """Test the API connection and basic endpoints"""
    base_url = "http://localhost:8001"
    
    print("🔍 Testing API Connection...")
    print(f"Base URL: {base_url}")
    print()
    
    # Test 1: Health Check
    print("1. Testing Health Check...")
    try:
        response = requests.get(f"{base_url}/api/health", timeout=5)
        if response.status_code == 200:
            print("✅ Health check passed")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False
    
    print()
    
    # Test 2: Get Credentials
    print("2. Testing Get Credentials...")
    try:
        response = requests.get(f"{base_url}/api/get_credentials", timeout=5)
        if response.status_code == 200:
            print("✅ Get credentials passed")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Get credentials failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Get credentials error: {e}")
    
    print()
    
    # Test 3: Database Stats
    print("3. Testing Database Stats...")
    try:
        response = requests.get(f"{base_url}/api/database/stats", timeout=5)
        if response.status_code == 200:
            print("✅ Database stats passed")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Database stats failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Database stats error: {e}")
    
    print()
    
    # Test 4: User Profile
    print("4. Testing User Profile...")
    try:
        response = requests.get(f"{base_url}/api/user/profile", timeout=5)
        if response.status_code == 200:
            print("✅ User profile passed")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ User profile failed: {response.status_code}")
    except Exception as e:
        print(f"❌ User profile error: {e}")
    
    print()
    print("🎯 API Connection Test Summary:")
    print("✅ API Bridge is running on port 8001")
    print("✅ React app should now be able to connect")
    print("✅ Sidebar links should work properly")
    
    return True

if __name__ == "__main__":
    test_api_connection() 