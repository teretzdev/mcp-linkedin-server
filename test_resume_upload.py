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
    """Test uploading an unsupported file format like .zip"""
    logger.info("🚫 Testing unsupported ZIP file upload...")
    zip_content = base64.b64encode(b'ZIP FILE CONTENT').decode()
    payload = {"filename": "resume.zip", "content": zip_content}
    response = requests.post(f"{BASE_URL}/api/resume/upload", json=payload)
    if response.status_code not in [400, 422]:
        print(f"Response: {response.status_code}, Body: {response.text}")
    assert response.status_code in [400, 422]
    data = response.json()
    assert not data.get("success", False)
    assert "not supported" in data.get("message", "")

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