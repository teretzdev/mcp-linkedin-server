#!/usr/bin/env python3
"""
LLM Controller for LinkedIn Automation
An intelligent agent that manages LinkedIn automation tasks
"""

import asyncio
import json
import logging
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from dotenv import load_dotenv
import aiohttp
from aiohttp import web

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class UserProfile:
    username: str
    current_position: str = ""
    skills: Optional[List[str]] = None
    target_roles: Optional[List[str]] = None
    target_locations: Optional[List[str]] = None
    
    def __post_init__(self):
        if self.skills is None:
            self.skills = []
        if self.target_roles is None:
            self.target_roles = []
        if self.target_locations is None:
            self.target_locations = []

class LLMController:
    """Intelligent controller for LinkedIn automation"""
    
    def __init__(self):
        self.api_base_url = "http://localhost:8001/api"
        self.user_profile: Optional[UserProfile] = None
        self.session_stats = {
            'jobs_viewed': 0,
            'jobs_applied': 0,
            'jobs_saved': 0,
            'start_time': datetime.now()
        }
        
        logger.info("LLM Controller initialized")
    
    async def initialize(self):
        """Initialize the controller"""
        try:
            await self.load_user_profile()
            
            # Check if API is available
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.api_base_url}/health") as response:
                    if response.status == 200:
                        logger.info("API bridge is available")
                        return True
                    else:
                        logger.error("API bridge is not responding")
                        return False
                        
        except Exception as e:
            logger.error(f"Failed to initialize: {e}")
            return False
    
    async def load_user_profile(self):
        """Load or create user profile"""
        profile_file = "user_profile.json"
        try:
            if os.path.exists(profile_file):
                with open(profile_file, 'r') as f:
                    data = json.load(f)
                    self.user_profile = UserProfile(**data)
                    logger.info("User profile loaded")
            else:
                # Create default profile
                self.user_profile = UserProfile(
                    username=os.getenv('LINKEDIN_USERNAME', ''),
                    current_position="Software Engineer",
                    skills=["Python", "JavaScript", "React", "Node.js"],
                    target_roles=["Senior Software Engineer", "Full Stack Developer"],
                    target_locations=["Remote", "San Francisco", "New York"]
                )
                await self.save_user_profile()
                logger.info("Default user profile created")
        except Exception as e:
            logger.error(f"Failed to load user profile: {e}")
            self.user_profile = UserProfile(username="")
    
    async def save_user_profile(self):
        """Save user profile to file"""
        if self.user_profile:
            # Ensure all fields are not None
            profile_dict = asdict(self.user_profile)
            profile_dict['skills'] = profile_dict.get('skills') or []
            profile_dict['target_roles'] = profile_dict.get('target_roles') or []
            profile_dict['target_locations'] = profile_dict.get('target_locations') or []
            profile_dict['username'] = profile_dict.get('username') or ""
            profile_dict['current_position'] = profile_dict.get('current_position') or ""
            with open("user_profile.json", 'w') as f:
                json.dump(profile_dict, f, indent=2, default=str)
    
    async def search_jobs(self, query: str = None, location: str = "", count: int = 10) -> Dict[str, Any]:
        """Search for jobs using intelligent parameters"""
        if not query:
            # Use LLM-like logic to generate search query
            if self.user_profile and self.user_profile.target_roles:
                query = self.user_profile.target_roles[0]
            else:
                query = "software engineer"
        
        logger.info(f"Searching for jobs: {query} in {location}")
        
        async with aiohttp.ClientSession() as session:
            payload = {
                "query": query,
                "location": location,
                "count": count
            }
            
            async with session.post(f"{self.api_base_url}/search_jobs", json=payload) as response:
                result = await response.json()
                
                if "jobs" in result:
                    self.session_stats['jobs_viewed'] += len(result["jobs"])
                    logger.info(f"Found {len(result['jobs'])} jobs")
                
                return result
    
    async def apply_to_job(self, job_url: str) -> Dict[str, Any]:
        """Apply to a job with intelligent decision making"""
        logger.info(f"Applying to job: {job_url}")
        
        # Simple decision logic (in a real implementation, this would use an LLM)
        should_apply = True  # For now, always apply
        
        if should_apply:
            async with aiohttp.ClientSession() as session:
                payload = {"job_url": job_url}
                async with session.post(f"{self.api_base_url}/apply_job", json=payload) as response:
                    result = await response.json()
                    
                    if result.get("success"):
                        self.session_stats['jobs_applied'] += 1
                        logger.info("Job application successful")
                    
                    return result
        else:
            return {"status": "skipped", "reason": "Decision logic recommended skipping"}
    
    async def save_job(self, job_url: str) -> Dict[str, Any]:
        """Save a job for later review"""
        logger.info(f"Saving job: {job_url}")
        
        async with aiohttp.ClientSession() as session:
            payload = {"job_url": job_url}
            async with session.post(f"{self.api_base_url}/save_job", json=payload) as response:
                result = await response.json()
                
                if result.get("success"):
                    self.session_stats['jobs_saved'] += 1
                    logger.info("Job saved successfully")
                
                return result
    
    async def get_recommendations(self) -> Dict[str, Any]:
        """Get intelligent recommendations based on current state"""
        recommendations = {
            "job_search_strategy": [],
            "profile_optimization": [],
            "next_actions": []
        }
        
        # Simple recommendation logic
        if self.session_stats['jobs_viewed'] < 10:
            recommendations["job_search_strategy"].append("Search for more job opportunities")
        
        if self.session_stats['jobs_saved'] > 0 and self.session_stats['jobs_applied'] < 3:
            recommendations["next_actions"].append("Review saved jobs and apply to best matches")
        
        if self.user_profile is not None and not self.user_profile.skills:
            recommendations["profile_optimization"].append("Update skills in profile")
        
        return {
            "recommendations": recommendations,
            "current_stats": self.session_stats,
            "user_profile": asdict(self.user_profile) if self.user_profile else None
        }
    
    async def run_automation_session(self, goals: List[str]) -> Dict[str, Any]:
        """Run an automated LinkedIn session based on goals"""
        logger.info(f"Starting automation session with goals: {goals}")
        
        session_start = datetime.now()
        results = []
        
        for goal in goals:
            if "job search" in goal.lower() or "find jobs" in goal.lower():
                # Search for jobs
                search_result = await self.search_jobs()
                results.append({
                    "goal": goal,
                    "action": "job_search",
                    "result": search_result
                })
                
                # If jobs found, save some for later
                if "jobs" in search_result and search_result["jobs"]:
                    for job in search_result["jobs"][:3]:  # Save first 3 jobs
                        url = job.get("url") or ""
                        await self.save_job(url)
            
            elif "apply" in goal.lower():
                # Get saved jobs and apply to some
                async with aiohttp.ClientSession() as session:
                    async with session.get(f"{self.api_base_url}/list_saved_jobs") as response:
                        saved_jobs = await response.json()
                        
                        if "jobs" in saved_jobs and saved_jobs["jobs"]:
                            # Apply to first job
                            job_url = saved_jobs["jobs"][0].get("url", "")
                            if job_url:
                                apply_result = await self.apply_to_job(job_url)
                                results.append({
                                    "goal": goal,
                                    "action": "job_application",
                                    "result": apply_result
                                })
        
        session_duration = datetime.now() - session_start
        
        return {
            "session_duration": str(session_duration),
            "goals_processed": len(goals),
            "results": results,
            "stats": self.session_stats
        }
    
    async def shutdown(self):
        """Clean shutdown of the controller"""
        logger.info("Shutting down LLM Controller")
        await self.save_user_profile()
        
        # Save session data
        session_data = {
            "session_stats": {k: (str(v) if isinstance(v, datetime) else v) for k, v in self.session_stats.items()},
            "timestamp": datetime.now().isoformat()
        }
        
        with open("session_data.json", 'w') as f:
            json.dump(session_data, f, indent=2, default=str)
        
        logger.info("LLM Controller shutdown complete")

async def health_check(request):
    """Health check endpoint for the LLM Controller"""
    return web.json_response({
        "status": "healthy",
        "server": "LLM Controller",
        "timestamp": datetime.now().isoformat()
    })

# Example usage
async def main():
    """Main entry point for the LLM Controller service"""
    controller = LLMController()
    
    try:
        # Initialize
        if not await controller.initialize():
            logger.error("Failed to initialize controller, but starting server anyway.")

        app = web.Application()
        app.router.add_get("/health", health_check)

        # You can add more routes here to trigger controller actions, for example:
        # async def run_automation_handler(request):
        #     goals = ["Find relevant job opportunities"]
        #     result = await controller.run_automation_session(goals)
        #     return web.json_response(result)
        # app.router.add_post("/api/run_automation", run_automation_handler)

        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, '0.0.0.0', 8003)
        await site.start()
        
        logger.info("LLM Controller server started on http://0.0.0.0:8003")
        
        # Keep the server running
        await asyncio.Event().wait()
        
    except Exception as e:
        logger.error(f"Error in main: {e}")
    
    finally:
        await controller.shutdown()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("LLM Controller stopped by user.") 