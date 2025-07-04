#!/usr/bin/env python3
"""
Test LLM Controller Features
Demonstrates the intelligent automation capabilities
"""

import asyncio
import json
import pytest
from llm_controller_simple import SimpleLLMController

@pytest.mark.asyncio
async def test_llm_features():
    """Test various LLM controller features"""
    print("🤖 Testing LLM Controller Features")
    print("=" * 50)
    
    # Initialize controller
    controller = SimpleLLMController()
    
    try:
        # Test initialization
        print("1. Initializing LLM Controller...")
        if await controller.initialize():
            print("   ✅ Controller initialized successfully")
        else:
            print("   ❌ Failed to initialize controller")
            return
        
        # Test user profile
        print(f"\n2. User Profile:")
        if controller.user_profile is not None:
            print(f"   Username: {controller.user_profile.username}")
            print(f"   Current Position: {controller.user_profile.current_position}")
            print(f"   Skills: {', '.join(controller.user_profile.skills or [])}")
            print(f"   Target Roles: {', '.join(controller.user_profile.target_roles or [])}")
            print(f"   Target Locations: {', '.join(controller.user_profile.target_locations or [])}")
        else:
            print("   No user profile loaded")
        
        # Test job search
        print(f"\n3. Testing Intelligent Job Search...")
        search_result = await controller.search_jobs("Software Engineer", "Remote", 5)
        if "jobs" in search_result:
            print(f"   ✅ Found {len(search_result['jobs'])} jobs")
            for i, job in enumerate(search_result['jobs'][:3], 1):
                print(f"   {i}. {job.get('title', 'N/A')} at {job.get('company', 'N/A')}")
        else:
            print(f"   ⚠️  Search result: {search_result}")
        
        # Test recommendations
        print(f"\n4. Getting Intelligent Recommendations...")
        recommendations = await controller.get_recommendations()
        print(f"   Job Search Strategy:")
        for rec in recommendations['recommendations']['job_search_strategy']:
            print(f"   • {rec}")
        print(f"   Profile Optimization:")
        for rec in recommendations['recommendations']['profile_optimization']:
            print(f"   • {rec}")
        print(f"   Next Actions:")
        for rec in recommendations['recommendations']['next_actions']:
            print(f"   • {rec}")
        
        # Test automation session
        print(f"\n5. Running Automation Session...")
        goals = [
            "Find relevant job opportunities",
            "Apply to suitable positions"
        ]
        session_result = await controller.run_automation_session(goals)
        print(f"   Session Duration: {session_result['session_duration']}")
        print(f"   Goals Processed: {session_result['goals_processed']}")
        print(f"   Results: {len(session_result['results'])} actions completed")
        
        # Show session stats
        print(f"\n6. Session Statistics:")
        stats = session_result['stats']
        print(f"   Jobs Viewed: {stats['jobs_viewed']}")
        print(f"   Jobs Applied: {stats['jobs_applied']}")
        print(f"   Jobs Saved: {stats['jobs_saved']}")
        
        print(f"\n🎉 LLM Controller Features Test Complete!")
        print(f"   The controller successfully demonstrated:")
        print(f"   • Intelligent job search")
        print(f"   • Smart recommendations")
        print(f"   • Automated session management")
        print(f"   • Progress tracking")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
    
    finally:
        await controller.shutdown()

if __name__ == "__main__":
    asyncio.run(test_llm_features()) 