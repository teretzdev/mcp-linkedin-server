#!/usr/bin/env python3
"""
Debug script to test API connection and identify issues
"""
import asyncio
import aiohttp
import json
import sys

async def test_health_endpoint():
    """Test the health endpoint"""
    url = "http://localhost:8002/api/health"
    print(f"Testing health endpoint: {url}")
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=5) as response:
                print(f"Status: {response.status}")
                
                if response.status == 200:
                    result = await response.json()
                    print(f"Response: {json.dumps(result, indent=2)}")
                    
                    if result.get("status") == "ok":
                        print("✅ Health check PASSED")
                        return True
                    else:
                        print("❌ Health check FAILED - wrong status")
                        return False
                else:
                    text = await response.text()
                    print(f"❌ Health check FAILED - status {response.status}: {text}")
                    return False
                    
    except Exception as e:
        print(f"❌ Health check FAILED - exception: {e}")
        return False

async def test_search_endpoint():
    """Test the search endpoint with minimal payload"""
    url = "http://localhost:8002/api/search_jobs_internal"
    print(f"\nTesting search endpoint: {url}")
    
    payload = {
        "query": "test",
        "location": "Remote",
        "count": 1
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, timeout=10) as response:
                print(f"Status: {response.status}")
                
                if response.status == 200:
                    result = await response.json()
                    print("✅ Search endpoint ACCESSIBLE")
                    print(f"Response keys: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}")
                    return True
                else:
                    text = await response.text()
                    print(f"❌ Search endpoint FAILED - status {response.status}: {text}")
                    return False
                    
    except Exception as e:
        print(f"❌ Search endpoint FAILED - exception: {e}")
        return False

async def test_refactored_system():
    """Test the refactored system connection"""
    print("\n" + "="*50)
    print("Testing refactored system connection...")
    
    # Import and test the job search service
    try:
        from services.job_search_service import JobSearchService
        
        service = JobSearchService()
        success = await service.test_connection()
        
        if success:
            print("✅ Refactored system connection PASSED")
            return True
        else:
            print("❌ Refactored system connection FAILED")
            return False
            
    except Exception as e:
        print(f"❌ Refactored system test FAILED - exception: {e}")
        return False

async def main():
    print("🔧 API Debug Session")
    print("=" * 50)
    
    # Test 1: Health endpoint
    health_ok = await test_health_endpoint()
    
    # Test 2: Search endpoint
    search_ok = await test_search_endpoint()
    
    # Test 3: Refactored system
    refactored_ok = await test_refactored_system()
    
    print("\n" + "=" * 50)
    print("DEBUG RESULTS:")
    print(f"Health endpoint: {'✅ PASS' if health_ok else '❌ FAIL'}")
    print(f"Search endpoint: {'✅ PASS' if search_ok else '❌ FAIL'}")
    print(f"Refactored system: {'✅ PASS' if refactored_ok else '❌ FAIL'}")
    
    if health_ok and search_ok and refactored_ok:
        print("\n🎉 ALL TESTS PASSED - System should work!")
        return True
    else:
        print("\n❌ Some tests failed - need to debug further")
        return False

if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(0 if result else 1) 