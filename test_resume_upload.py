#!/usr/bin/env python3
"""
Test Script for LinkedIn Job Hunter API Resume Upload
Covers all supported and unsupported formats, empty file, and large file cases.
"""

import requests
import logging
import base64

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_URL = "http://localhost:8001"

def test_resume_upload_valid_pdf():
    logger.info("📄 Testing valid PDF resume upload...")
    pdf_content = base64.b64encode(b'%PDF-1.4\nDummy PDF content').decode()
    payload = {"filename": "test_resume.pdf", "content": pdf_content}
    response = requests.post(f"{BASE_URL}/api/resume/upload", json=payload)
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["success"]
    assert data["filename"] == "test_resume.pdf"
    assert data["word_count"] > 0

def test_resume_upload_valid_doc():
    logger.info("📄 Testing valid DOC resume upload...")
    doc_content = base64.b64encode(b'Dummy DOC content').decode()
    payload = {"filename": "test_resume.doc", "content": doc_content}
    response = requests.post(f"{BASE_URL}/api/resume/upload", json=payload)
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["success"]
    assert data["filename"] == "test_resume.doc"

def test_resume_upload_valid_docx():
    logger.info("📄 Testing valid DOCX resume upload...")
    docx_content = base64.b64encode(b'Dummy DOCX content').decode()
    payload = {"filename": "test_resume.docx", "content": docx_content}
    response = requests.post(f"{BASE_URL}/api/resume/upload", json=payload)
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["success"]
    assert data["filename"] == "test_resume.docx"

def test_resume_upload_valid_txt():
    logger.info("📄 Testing valid TXT resume upload...")
    txt_content = base64.b64encode(b'Dummy TXT content').decode()
    payload = {"filename": "test_resume.txt", "content": txt_content}
    response = requests.post(f"{BASE_URL}/api/resume/upload", json=payload)
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["success"]
    assert data["filename"] == "test_resume.txt"

def test_resume_upload_empty_file():
    logger.info("🗑️ Testing empty file upload...")
    empty_content = base64.b64encode(b'').decode()
    payload = {"filename": "empty_resume.txt", "content": empty_content}
    response = requests.post(f"{BASE_URL}/api/resume/upload", json=payload)
    assert response.status_code in [400, 422], response.text
    data = response.json()
    assert not data.get("success", False)

def test_resume_upload_unsupported_format():
    logger.info("🚫 Testing unsupported ZIP file upload...")
    zip_content = base64.b64encode(b'ZIP FILE CONTENT').decode()
    payload = {"filename": "resume.zip", "content": zip_content}
    response = requests.post(f"{BASE_URL}/api/resume/upload", json=payload)
    assert response.status_code in [400, 422], response.text
    data = response.json()
    assert not data.get("success", False)
    assert "not supported" in data.get("detail", data.get("message", ""))

def test_resume_upload_large_file():
    logger.info("🧾 Testing large file upload...")
    large_content = base64.b64encode(b'A' * 2 * 1024 * 1024).decode()
    payload = {"filename": "large_resume.txt", "content": large_content}
    response = requests.post(f"{BASE_URL}/api/resume/upload", json=payload)
    assert response.status_code in [200, 400, 413], response.text

def main():
    logger.info("🚀 Starting Resume Upload Tests")
    tests = [
        ("Valid PDF", test_resume_upload_valid_pdf),
        ("Valid DOC", test_resume_upload_valid_doc),
        ("Valid DOCX", test_resume_upload_valid_docx),
        ("Valid TXT", test_resume_upload_valid_txt),
        ("Empty File", test_resume_upload_empty_file),
        ("Unsupported Format", test_resume_upload_unsupported_format),
        ("Large File", test_resume_upload_large_file)
    ]
    results = {}
    for name, func in tests:
        try:
            func()
            results[name] = "✅ PASS"
        except Exception as e:
            logger.error(f"❌ {name} failed: {e}")
            results[name] = f"❌ FAIL: {e}"
    logger.info("\nTest Results:")
    for name, result in results.items():
        logger.info(f"{name}: {result}")
    passed = sum(1 for r in results.values() if r.startswith("✅"))
    logger.info(f"\n{passed}/{len(tests)} tests passed.")

if __name__ == "__main__":
    main()