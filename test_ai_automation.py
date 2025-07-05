#!/usr/bin/env python3
"""
Test script for AI Job Automation System
"""

import asyncio
import json
import os
from ai_job_automation import AIJobAutomation, ResumeManager

async def test_ai_automation():
    """Test the AI automation system"""
    print("🤖 Testing AI Job Automation System...")
    print("=" * 50)
    
    # Test 1: Create automation instance
    print("\n1. Testing automation instance creation...")
    try:
        automation = AIJobAutomation()
        print("✅ Automation instance created successfully")
        print(f"   - API Base URL: {automation.api_base_url}")
        print(f"   - Gemini Available: {automation.gemini_model is not None}")
    except Exception as e:
        print(f"❌ Failed to create automation instance: {e}")
        return
    
    # Test 2: Test preferences
    print("\n2. Testing preferences management...")
    try:
        # Update preferences
        automation.update_preferences(
            keywords=["python developer", "software engineer"],
            location="Remote",
            experience_level="mid-level",
            job_type="full-time",
            remote_preference=True,
            skills_required=["Python", "Django"],
            skills_preferred=["React", "AWS"]
        )
        print("✅ Preferences updated successfully")
        
        # Check preferences
        prefs = automation.preferences
        print(f"   - Keywords: {prefs.keywords}")
        print(f"   - Location: {prefs.location}")
        print(f"   - Experience: {prefs.experience_level}")
        print(f"   - Job Type: {prefs.job_type}")
    except Exception as e:
        print(f"❌ Failed to update preferences: {e}")
    
    # Test 3: Test resume management
    print("\n3. Testing resume management...")
    try:
        resume_manager = automation.resume_manager
        resumes = resume_manager.list_resumes()
        print(f"✅ Resume manager working - {len(resumes)} resumes found")
        
        # Test resume upload (if we have a test file)
        test_resume_path = "test_resume.pdf"
        if os.path.exists(test_resume_path):
            success = resume_manager.upload_resume(test_resume_path, "test_resume")
            if success:
                print("✅ Test resume uploaded successfully")
            else:
                print("⚠️  Test resume upload failed")
        else:
            print("ℹ️  No test resume file found, skipping upload test")
    except Exception as e:
        print(f"❌ Resume management test failed: {e}")
    
    # Test 4: Test job scoring
    print("\n4. Testing job scoring...")
    try:
        # Create a sample job
        sample_job = {
            "title": "Senior Python Developer",
            "company": "TechCorp Inc.",
            "location": "Remote",
            "descriptionSnippet": "We are looking for a Python developer with Django experience...",
            "jobUrl": "https://linkedin.com/jobs/view/123"
        }
        
        # Score the job
        match = automation.score_job(sample_job)
        print(f"✅ Job scoring working")
        print(f"   - Match Score: {match.match_score:.2f}")
        print(f"   - Should Apply: {match.should_apply}")
        print(f"   - Reasons: {', '.join(match.match_reasons)}")
    except Exception as e:
        print(f"❌ Job scoring test failed: {e}")
    
    # Test 5: Test stats
    print("\n5. Testing statistics...")
    try:
        stats = automation.get_stats()
        print("✅ Statistics working")
        print(f"   - Jobs Searched: {stats['jobs_searched']}")
        print(f"   - Jobs Applied: {stats['jobs_applied']}")
        print(f"   - Jobs Saved: {stats['jobs_saved']}")
        print(f"   - Cycles Completed: {stats['cycles_completed']}")
        print(f"   - Errors: {stats['errors']}")
    except Exception as e:
        print(f"❌ Statistics test failed: {e}")
    
    # Test 6: Test Gemini integration (if available)
    if automation.gemini_model:
        print("\n6. Testing Gemini AI integration...")
        try:
            # Test Gemini analysis
            sample_job = {
                "title": "Python Backend Developer",
                "company": "StartupXYZ",
                "location": "Remote",
                "descriptionSnippet": "Looking for a Python developer with Django and PostgreSQL experience..."
            }
            
            analysis = await automation.analyze_job_with_gemini(sample_job, automation.preferences)
            if analysis:
                print("✅ Gemini analysis working")
                print(f"   - Analysis: {analysis[:100]}...")
            else:
                print("⚠️  Gemini analysis returned None")
        except Exception as e:
            print(f"❌ Gemini integration test failed: {e}")
    else:
        print("\n6. Gemini not available - skipping AI analysis test")
    
    # Test 7: Edge case - job scoring with missing fields
    print("\n7. Testing job scoring with missing fields...")
    try:
        incomplete_job = {"title": "", "company": "", "location": "", "descriptionSnippet": ""}
        match = automation.score_job(incomplete_job)
        print(f"✅ Edge case handled - Match Score: {match.match_score:.2f}, Should Apply: {match.should_apply}")
    except Exception as e:
        print(f"❌ Edge case job scoring failed: {e}")

    # Test 8: LLM integration failure (simulate missing API key)
    print("\n8. Testing LLM integration failure...")
    try:
        automation.gemini_model = None  # Simulate missing Gemini
        analysis = await automation.analyze_job_with_gemini({"title": "Test"}, automation.preferences)
        if analysis is None:
            print("✅ LLM integration failure handled gracefully")
        else:
            print("⚠️  LLM integration did not fail as expected")
    except Exception as e:
        print(f"✅ LLM integration failure raised exception as expected: {e}")

    # Test 9: Negative resume upload (nonexistent file)
    print("\n9. Testing negative resume upload...")
    try:
        resume_manager = automation.resume_manager
        success = resume_manager.upload_resume("nonexistent_file.pdf", "bad_resume")
        if not success:
            print("✅ Negative resume upload handled correctly")
        else:
            print("❌ Negative resume upload should have failed")
    except Exception as e:
        print(f"✅ Negative resume upload raised exception as expected: {e}")
    
    # Test 10: Upload, list, and delete resumes
    print("\n10. Testing upload, list, and delete resumes...")
    try:
        resume_manager = automation.resume_manager
        # Clean up any existing test resumes
        for r in resume_manager.list_resumes():
            resume_manager.delete_resume(r['name'])
        # Create a dummy resume file
        test_resume_path = "test_resume_upload.pdf"
        with open(test_resume_path, "wb") as f:
            f.write(b"Dummy PDF content")
        # Upload resumes up to max
        for i in range(resume_manager.max_resumes):
            success = resume_manager.upload_resume(test_resume_path, f"test_resume_{i}")
            assert success, f"Failed to upload resume {i}"
        # Try to upload one more (should fail)
        success = resume_manager.upload_resume(test_resume_path, "overflow_resume")
        assert not success, "Should not allow more than max resumes"
        # List resumes
        resumes = resume_manager.list_resumes()
        assert len(resumes) == resume_manager.max_resumes, "Resume count mismatch"
        # Delete a resume
        del_success = resume_manager.delete_resume(resumes[0]['name'])
        assert del_success, "Failed to delete resume"
        # Try to delete again (should fail)
        del_again = resume_manager.delete_resume(resumes[0]['name'])
        assert not del_again, "Should not delete nonexistent resume"
        # Clean up
        for r in resume_manager.list_resumes():
            resume_manager.delete_resume(r['name'])
        os.remove(test_resume_path)
        print("✅ Upload, list, and delete resumes tested successfully")
    except Exception as e:
        print(f"❌ Resume upload/list/delete test failed: {e}")

    # Test 11: Duplicate resume name
    print("\n11. Testing duplicate resume name...")
    try:
        resume_manager = automation.resume_manager
        test_resume_path = "test_resume_upload.pdf"
        with open(test_resume_path, "wb") as f:
            f.write(b"Dummy PDF content")
        resume_manager.upload_resume(test_resume_path, "dup_resume")
        # Try to upload again with same name (should overwrite or fail gracefully)
        result = resume_manager.upload_resume(test_resume_path, "dup_resume")
        assert result, "Duplicate upload should succeed (overwrite allowed)"
        resume_manager.delete_resume("dup_resume")
        os.remove(test_resume_path)
        print("✅ Duplicate resume name handled correctly")
    except Exception as e:
        print(f"❌ Duplicate resume name test failed: {e}")

    # Test 12: Invalid file format
    print("\n12. Testing invalid file format...")
    try:
        resume_manager = automation.resume_manager
        test_resume_path = "test_resume_upload.txt"
        with open(test_resume_path, "w") as f:
            f.write("")  # Empty file
        success = resume_manager.upload_resume(test_resume_path, "empty_resume")
        assert not success, "Should not upload empty/invalid resume"
        os.remove(test_resume_path)
        print("✅ Invalid file format handled correctly")
    except Exception as e:
        print(f"❌ Invalid file format test failed: {e}")
    
    # Frontend (React) upload tests are recommended for ResumeManager.js:
    # - Simulate file selection and upload (mock axios)
    # - Test UI state changes (isUploading, error display)
    # - Test resume list updates after upload
    # - Test error handling for invalid/large/unsupported files
    # - Test delete and select resume actions
    # These can be implemented using Jest + React Testing Library.
    
    print("\n" + "=" * 50)
    print("🎉 AI Automation System Test Complete!")
    print("\nNext steps:")
    print("1. Set your GEMINI_API_KEY environment variable")
    print("2. Start the API bridge: start_all_optimized.bat")
    print("3. Start the React frontend: cd src && npm start")
    print("4. Access the dashboard at http://localhost:3000")
    print("5. Navigate to 'AI Automation' in the sidebar")

if __name__ == "__main__":
    asyncio.run(test_ai_automation()) 