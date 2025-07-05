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
        
        # Ensure a clean state for testing
        test_resume_name = "test_resume"
        test_resume_filename = f"{test_resume_name}.pdf"
        test_resume_src_path = "test_resume.pdf"
        
        # Create a dummy test resume if it doesn't exist
        if not os.path.exists(test_resume_src_path):
            print(f"ℹ️  Creating dummy resume file: {test_resume_src_path}")
            with open(test_resume_src_path, "w") as f:
                f.write("This is a test resume.")
        
        # Clean up any previous test resume from the resumes directory
        if resume_manager.get_resume_path(test_resume_name):
            print(f"ℹ️  Cleaning up previous test resume: {test_resume_filename}")
            resume_manager.delete_resume(test_resume_name)

        resumes = resume_manager.list_resumes()
        print(f"✅ Resume manager working - {len(resumes)} resumes found initially")
        
        # Test resume upload
        success = resume_manager.upload_resume(test_resume_src_path, test_resume_name)
        if success:
            print("✅ Test resume uploaded successfully")
            
            # Verify it's in the list
            resumes = resume_manager.list_resumes()
            if any(r['name'] == test_resume_name for r in resumes):
                print("✅ Uploaded resume found in list")
            else:
                print("❌ Uploaded resume NOT found in list")
            
            # Test resume deletion
            success_delete = resume_manager.delete_resume(test_resume_name)
            if success_delete:
                print("✅ Test resume deleted successfully")
                resumes = resume_manager.list_resumes()
                if not any(r['name'] == test_resume_name for r in resumes):
                    print("✅ Deleted resume is no longer in the list")
                else:
                    print("❌ Deleted resume still found in list")
            else:
                print("❌ Test resume deletion failed")
        else:
            print("❌ Test resume upload failed")

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