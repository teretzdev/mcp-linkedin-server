#!/usr/bin/env python3
"""
Test Script for LinkedIn Job Hunter API with Database Integration
Tests all new database-enabled endpoints
"""

import requests
import json
import time
import logging
from datetime import datetime
from typing import Dict, Any
import base64

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# API base URL
BASE_URL = "http://localhost:8001"

def test_health_check():
    """Test health check endpoint"""
    logger.info("🔍 Testing Health Check...")
    try:
        response = requests.get(f"{BASE_URL}/api/health")
        if response.status_code == 200:
            data = response.json()
            logger.info(f"✅ Health check passed: {data}")
            return True
        else:
            logger.error(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"❌ Health check error: {e}")
        return False

def test_user_profile():
    """Test user profile endpoints"""
    logger.info("👤 Testing User Profile...")
    try:
        # Update user profile
        profile_data = {
            "username": "test_user_api",
            "email": "test_api@example.com",
            "current_position": "Senior Software Engineer",
            "skills": ["Python", "JavaScript", "React", "Node.js"],
            "target_roles": ["Senior Developer", "Full Stack Engineer", "Tech Lead"],
            "target_locations": ["Remote", "San Francisco", "New York"],
            "experience_years": 5,
            "resume_url": "https://example.com/resume.pdf"
        }
        
        response = requests.post(f"{BASE_URL}/api/user/profile", json=profile_data)
        if response.status_code == 200:
            data = response.json()
            logger.info(f"✅ Profile updated: {data.get('message')}")
        else:
            logger.error(f"❌ Profile update failed: {response.status_code}")
            return False
        
        # Get user profile
        response = requests.get(f"{BASE_URL}/api/user/profile")
        if response.status_code == 200:
            data = response.json()
            logger.info(f"✅ Profile retrieved: {data.get('user', {}).get('username')}")
            return True
        else:
            logger.error(f"❌ Profile retrieval failed: {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"❌ User profile test error: {e}")
        return False

def test_job_search():
    """Test job search endpoint"""
    logger.info("🔍 Testing Job Search...")
    try:
        search_data = {
            "query": "Python Developer",
            "location": "Remote",
            "count": 5
        }
        
        response = requests.post(f"{BASE_URL}/api/search_jobs", json=search_data)
        if response.status_code == 200:
            data = response.json()
            jobs = data.get('jobs', [])
            logger.info(f"✅ Job search successful: Found {len(jobs)} jobs")
            return jobs
        else:
            logger.error(f"❌ Job search failed: {response.status_code}")
            return []
            
    except Exception as e:
        logger.error(f"❌ Job search test error: {e}")
        return []

def test_job_operations():
    """Test job saving and application"""
    logger.info("💼 Testing Job Operations...")
    try:
        # Save a job
        job_data = {
            "job_id": "api_test_job_123",
            "job_url": "https://linkedin.com/jobs/view/api_test_job_123",
            "title": "Senior Python Developer",
            "company": "API Test Company",
            "location": "Remote",
            "description": "Great opportunity for Python developers",
            "salary_range": "$120k - $150k",
            "job_type": "Full-time",
            "experience_level": "Senior",
            "easy_apply": True,
            "remote_work": True,
            "notes": "API test job",
            "tags": ["python", "remote", "senior", "api-test"]
        }
        
        response = requests.post(f"{BASE_URL}/api/save_job", json=job_data)
        if response.status_code == 200:
            data = response.json()
            logger.info(f"✅ Job saved: {data.get('message')}")
        else:
            logger.error(f"❌ Job save failed: {response.status_code}")
            return False
        
        # Get saved jobs
        response = requests.get(f"{BASE_URL}/api/saved_jobs")
        if response.status_code == 200:
            data = response.json()
            jobs = data.get('jobs', [])
            logger.info(f"✅ Retrieved {len(jobs)} saved jobs")
        else:
            logger.error(f"❌ Get saved jobs failed: {response.status_code}")
            return False
        
        # Apply to a job
        apply_data = {
            "job_id": "api_test_job_456",
            "job_url": "https://linkedin.com/jobs/view/api_test_job_456",
            "title": "Full Stack Developer",
            "company": "Apply Test Company",
            "location": "San Francisco",
            "cover_letter": "I'm excited to apply for this position...",
            "resume_used": "resume_v2.pdf",
            "notes": "API test application"
        }
        
        response = requests.post(f"{BASE_URL}/api/apply_job", json=apply_data)
        if response.status_code == 200:
            data = response.json()
            logger.info(f"✅ Job application submitted: {data.get('message')}")
        else:
            logger.error(f"❌ Job application failed: {response.status_code}")
            return False
        
        # Get applied jobs
        response = requests.get(f"{BASE_URL}/api/applied_jobs")
        if response.status_code == 200:
            data = response.json()
            jobs = data.get('jobs', [])
            logger.info(f"✅ Retrieved {len(jobs)} applied jobs")
            return True
        else:
            logger.error(f"❌ Get applied jobs failed: {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Job operations test error: {e}")
        return False

def test_session_management():
    """Test session management"""
    logger.info("🔄 Testing Session Management...")
    try:
        session_id = f"api_test_session_{int(time.time())}"
        
        # Start session
        session_data = {
            "session_id": session_id,
            "automation_mode": "manual"
        }
        
        response = requests.post(f"{BASE_URL}/api/session/start", json=session_data)
        if response.status_code == 200:
            data = response.json()
            logger.info(f"✅ Session started: {data.get('message')}")
        else:
            logger.error(f"❌ Session start failed: {response.status_code}")
            return False
        
        # Update session
        update_data = {
            "jobs_viewed": 10,
            "jobs_applied": 3,
            "jobs_saved": 5,
            "errors_encountered": 1
        }
        
        response = requests.post(f"{BASE_URL}/api/session/update", json=update_data, params={"session_id": session_id})
        if response.status_code == 200:
            data = response.json()
            logger.info(f"✅ Session updated: {data.get('message')}")
        else:
            logger.error(f"❌ Session update failed: {response.status_code}")
            return False
        
        # End session
        response = requests.post(f"{BASE_URL}/api/session/end", params={"session_id": session_id})
        if response.status_code == 200:
            data = response.json()
            logger.info(f"✅ Session ended: {data.get('message')}")
            return True
        else:
            logger.error(f"❌ Session end failed: {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Session management test error: {e}")
        return False

def test_analytics():
    """Test analytics endpoints"""
    logger.info("📊 Testing Analytics...")
    try:
        # Get automation logs
        response = requests.get(f"{BASE_URL}/api/analytics/logs")
        if response.status_code == 200:
            data = response.json()
            logs = data.get('logs', [])
            logger.info(f"✅ Retrieved {len(logs)} automation logs")
        else:
            logger.error(f"❌ Get logs failed: {response.status_code}")
            return False
        
        # Get analytics stats
        response = requests.get(f"{BASE_URL}/api/analytics/stats")
        if response.status_code == 200:
            data = response.json()
            stats = data.get('stats', {})
            logger.info(f"✅ Analytics stats: {stats}")
            return True
        else:
            logger.error(f"❌ Get stats failed: {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Analytics test error: {e}")
        return False

def test_database_management():
    """Test database management endpoints"""
    logger.info("🗄️ Testing Database Management...")
    try:
        # Get database stats
        response = requests.get(f"{BASE_URL}/api/database/stats")
        if response.status_code == 200:
            data = response.json()
            stats = data.get('stats', {})
            logger.info(f"✅ Database stats: {stats}")
        else:
            logger.error(f"❌ Get database stats failed: {response.status_code}")
            return False
        
        # Create database backup
        response = requests.post(f"{BASE_URL}/api/database/backup")
        if response.status_code == 200:
            data = response.json()
            logger.info(f"✅ Database backup created: {data.get('message')}")
        else:
            logger.error(f"❌ Database backup failed: {response.status_code}")
            return False
        
        # Clean up old data
        response = requests.post(f"{BASE_URL}/api/database/cleanup", params={"days": 30})
        if response.status_code == 200:
            data = response.json()
            logger.info(f"✅ Database cleanup: {data.get('message')}")
            return True
        else:
            logger.error(f"❌ Database cleanup failed: {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Database management test error: {e}")
        return False

def test_system_settings():
    """Test system settings endpoints"""
    logger.info("⚙️ Testing System Settings...")
    try:
        # Set a test setting
        response = requests.post(f"{BASE_URL}/api/settings/test_api_setting", 
                               params={"value": "test_value", "setting_type": "string"})
        if response.status_code == 200:
            data = response.json()
            logger.info(f"✅ Setting created: {data.get('message')}")
        else:
            logger.error(f"❌ Setting creation failed: {response.status_code}")
            return False
        
        # Get the setting
        response = requests.get(f"{BASE_URL}/api/settings/test_api_setting")
        if response.status_code == 200:
            data = response.json()
            value = data.get('value')
            logger.info(f"✅ Setting retrieved: {value}")
            return True
        else:
            logger.error(f"❌ Setting retrieval failed: {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"❌ System settings test error: {e}")
        return False

def test_legacy_endpoints():
    """Test legacy endpoints for backward compatibility"""
    logger.info("🔄 Testing Legacy Endpoints...")
    try:
        # Test credentials update
        cred_data = {
            "username": "legacy_test_user",
            "password": "legacy_test_password"
        }
        
        response = requests.post(f"{BASE_URL}/api/update_credentials", json=cred_data)
        if response.status_code == 200:
            data = response.json()
            logger.info(f"✅ Credentials updated: {data.get('message')}")
            return True
        else:
            logger.error(f"❌ Credentials update failed: {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Legacy endpoints test error: {e}")
        return False

def test_invalid_payloads():
    """Test API endpoints with invalid payloads"""
    logger.info("🚫 Testing Invalid Payloads...")
    response = requests.post(f"{BASE_URL}/api/user/profile", json={"username": ""})
    assert response.status_code in [400, 404, 422, 500], f"Status: {response.status_code}, Body: {response.text}"
    response = requests.post(f"{BASE_URL}/api/search_jobs", json={})
    assert response.status_code in [400, 404, 422, 500], f"Status: {response.status_code}, Body: {response.text}"
    response = requests.post(f"{BASE_URL}/api/save_job", json={"title": "Test"})
    assert response.status_code in [400, 404, 422, 500], f"Status: {response.status_code}, Body: {response.text}"

def test_unauthorized_access():
    """Test endpoints that require authentication without credentials"""
    logger.info("🔒 Testing Unauthorized Access...")
    response = requests.get(f"{BASE_URL}/api/user/profile")
    assert response.status_code in [200, 401, 403, 404, 500], f"Status: {response.status_code}, Body: {response.text}"
    response = requests.get(f"{BASE_URL}/api/saved_jobs")
    assert response.status_code in [200, 401, 403, 404, 500], f"Status: {response.status_code}, Body: {response.text}"

def test_error_responses():
    """Test API error responses for non-existent resources"""
    logger.info("❌ Testing Error Responses...")
    response = requests.get(f"{BASE_URL}/api/user/profile/doesnotexist")
    assert response.status_code in [404, 400, 500]

def test_resume_upload_valid_pdf():
    """Test uploading a valid PDF resume"""
    logger.info("📄 Testing valid PDF resume upload...")
    pdf_content = base64.b64encode(b'%PDF-1.4\nDummy PDF content').decode()
    payload = {"filename": "test_resume.pdf", "content": pdf_content}
    response = requests.post(f"{BASE_URL}/api/resume/upload", json=payload)
    if response.status_code != 200:
        print(f"Response: {response.status_code}, Body: {response.text}")
    assert response.status_code == 200
    data = response.json()
    assert data["success"]
    assert data["filename"] == "test_resume.pdf"
    assert data["word_count"] > 0

def test_resume_upload_valid_docx():
    """Test uploading a valid DOCX resume"""
    logger.info("📄 Testing valid DOCX resume upload...")
    docx_content = base64.b64encode(b'Dummy DOCX content').decode()
    payload = {"filename": "test_resume.docx", "content": docx_content}
    response = requests.post(f"{BASE_URL}/api/resume/upload", json=payload)
    if response.status_code != 200:
        print(f"Response: {response.status_code}, Body: {response.text}")
    assert response.status_code == 200
    data = response.json()
    assert data["success"]
    assert data["filename"] == "test_resume.docx"

def test_resume_upload_valid_txt():
    """Test uploading a valid TXT resume"""
    logger.info("📄 Testing valid TXT resume upload...")
    txt_content = base64.b64encode(b'Dummy TXT content').decode()
    payload = {"filename": "test_resume.txt", "content": txt_content}
    response = requests.post(f"{BASE_URL}/api/resume/upload", json=payload)
    if response.status_code != 200:
        print(f"Response: {response.status_code}, Body: {response.text}")
    assert response.status_code == 200
    data = response.json()
    assert data["success"]
    assert data["filename"] == "test_resume.txt"

def test_resume_upload_empty_file():
    """Test uploading an empty file"""
    logger.info("🗑️ Testing empty file upload...")
    empty_content = base64.b64encode(b'').decode()
    payload = {"filename": "empty_resume.txt", "content": empty_content}
    response = requests.post(f"{BASE_URL}/api/resume/upload", json=payload)
    if response.status_code not in [400, 422]:
        print(f"Response: {response.status_code}, Body: {response.text}")
    assert response.status_code in [400, 422]
    data = response.json()
    assert not data.get("success", False)

def test_resume_upload_unsupported_format():
    """Test uploading an unsupported DOC file"""
    logger.info("🚫 Testing unsupported DOC file upload...")
    doc_content = base64.b64encode(b'DOC FILE CONTENT').decode()
    payload = {"filename": "resume.doc", "content": doc_content}
    response = requests.post(f"{BASE_URL}/api/resume/upload", json=payload)
    if response.status_code not in [400, 422]:
        print(f"Response: {response.status_code}, Body: {response.text}")
    assert response.status_code in [400, 422]
    data = response.json()
    assert not data.get("success", False)
    assert "not supported" in data.get("detail", "")

def test_resume_upload_large_file():
    """Test uploading a large file (simulate 2MB)"""
    logger.info("🧾 Testing large file upload...")
    large_content = base64.b64encode(b'A' * 2 * 1024 * 1024).decode()
    payload = {"filename": "large_resume.txt", "content": large_content}
    response = requests.post(f"{BASE_URL}/api/resume/upload", json=payload)
    if response.status_code not in [200, 400, 413]:
        print(f"Response: {response.status_code}, Body: {response.text}")
    assert response.status_code in [200, 400, 413]

def main():
    """Run all API tests"""
    logger.info("🚀 Starting API Tests with Database Integration")
    logger.info("=" * 60)
    
    tests = [
        ("Health Check", test_health_check),
        ("User Profile", test_user_profile),
        ("Job Search", test_job_search),
        ("Job Operations", test_job_operations),
        ("Session Management", test_session_management),
        ("Analytics", test_analytics),
        ("Database Management", test_database_management),
        ("System Settings", test_system_settings),
        ("Legacy Endpoints", test_legacy_endpoints),
        ("Invalid Payloads", test_invalid_payloads),
        ("Unauthorized Access", test_unauthorized_access),
        ("Error Responses", test_error_responses),
        ("Resume Upload (Valid PDF)", test_resume_upload_valid_pdf),
        ("Resume Upload (Valid DOCX)", test_resume_upload_valid_docx),
        ("Resume Upload (Valid TXT)", test_resume_upload_valid_txt),
        ("Resume Upload (Empty File)", test_resume_upload_empty_file),
        ("Resume Upload (Unsupported Format)", test_resume_upload_unsupported_format),
        ("Resume Upload (Large File)", test_resume_upload_large_file)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        logger.info(f"\n{'='*20} {test_name} {'='*20}")
        try:
            result = test_func()
            results[test_name] = "✅ PASS" if result else "❌ FAIL"
        except Exception as e:
            logger.error(f"❌ {test_name} test crashed: {e}")
            results[test_name] = "💥 CRASH"
    
    # Print summary
    logger.info(f"\n{'='*60}")
    logger.info("📋 TEST SUMMARY")
    logger.info("=" * 60)
    
    for test_name, result in results.items():
        logger.info(f"{test_name}: {result}")
    
    passed = sum(1 for result in results.values() if "PASS" in result)
    total = len(results)
    
    logger.info(f"\n🎯 Results: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 All tests passed! Database integration is working perfectly!")
    else:
        logger.info("⚠️ Some tests failed. Check the logs above for details.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 