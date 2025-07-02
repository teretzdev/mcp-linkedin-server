#!/usr/bin/env python3
"""
Test script for credential saving functionality
"""

import os
import requests
import json
from dotenv import load_dotenv

def test_credential_saving():
    """Test the credential saving functionality"""
    
    # Test data
    test_username = "test@example.com"
    test_password = "testpassword123"
    
    print("🧪 Testing Credential Saving Functionality")
    print("=" * 50)
    
    # Check if API bridge is running
    try:
        response = requests.get("http://localhost:8001/api/health", timeout=5)
        if response.status_code == 200:
            print("✅ API Bridge is running")
        else:
            print("❌ API Bridge returned error status")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ API Bridge is not running: {e}")
        return False
    
    # Test 1: Save credentials
    print("\n📝 Test 1: Saving credentials...")
    try:
        response = requests.post(
            "http://localhost:8001/api/update_credentials",
            json={
                "username": test_username,
                "password": test_password
            },
            timeout=10
        )
        
        print(f"Response status: {response.status_code}")
        print(f"Response body: {response.text}")
        
        if response.status_code == 200:
            print("✅ Credentials saved successfully")
        else:
            print(f"❌ Failed to save credentials: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error saving credentials: {e}")
        return False
    
    # Test 2: Retrieve credentials
    print("\n📖 Test 2: Retrieving credentials...")
    try:
        response = requests.get("http://localhost:8001/api/get_credentials", timeout=5)
        
        print(f"Response status: {response.status_code}")
        print(f"Response body: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get("username") == test_username:
                print("✅ Credentials retrieved successfully")
            else:
                print(f"❌ Retrieved username doesn't match: {data.get('username')}")
                return False
        else:
            print(f"❌ Failed to retrieve credentials: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error retrieving credentials: {e}")
        return False
    
    # Test 3: Check .env file
    print("\n📁 Test 3: Checking .env file...")
    try:
        load_dotenv(override=True)
        env_username = os.getenv('LINKEDIN_USERNAME', '')
        env_password = os.getenv('LINKEDIN_PASSWORD', '')
        
        print(f"Environment username: {env_username}")
        print(f"Environment password: {'*' * len(env_password) if env_password else 'Not set'}")
        
        if env_username == test_username and env_password == test_password:
            print("✅ .env file updated correctly")
        else:
            print("❌ .env file not updated correctly")
            return False
            
    except Exception as e:
        print(f"❌ Error checking .env file: {e}")
        return False
    
    # Test 4: Test login (this will fail but should not crash)
    print("\n🔐 Test 4: Testing login (expected to fail with test credentials)...")
    try:
        response = requests.post("http://localhost:8001/api/test_login", timeout=30)
        
        print(f"Response status: {response.status_code}")
        print(f"Response body: {response.text}")
        
        # Login should fail with test credentials, but API should respond
        if response.status_code in [200, 400, 500]:
            print("✅ Login test completed (as expected)")
        else:
            print(f"❌ Unexpected response: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error testing login: {e}")
    
    print("\n🎉 All tests completed!")
    return True

def check_env_file():
    """Check the current .env file contents"""
    print("\n📋 Current .env file contents:")
    print("=" * 30)
    
    if os.path.exists('.env'):
        with open('.env', 'r') as f:
            content = f.read()
            lines = content.split('\n')
            for line in lines:
                if line.strip() and not line.startswith('#'):
                    if 'PASSWORD' in line:
                        # Mask password
                        parts = line.split('=', 1)
                        if len(parts) == 2:
                            print(f"{parts[0]}=***MASKED***")
                        else:
                            print(line)
                    else:
                        print(line)
    else:
        print("❌ .env file does not exist")

if __name__ == "__main__":
    check_env_file()
    test_credential_saving() 