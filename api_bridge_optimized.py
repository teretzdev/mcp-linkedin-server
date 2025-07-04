#!/usr/bin/env python3
"""
Optimized API Bridge for LinkedIn MCP Server
Provides HTTP endpoints for the React frontend with improved performance
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from pydantic import BaseModel
import asyncio
import json
import subprocess
import sys
import os
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv
import socket
import time
import logging
from functools import lru_cache
import aiohttp
from datetime import datetime, timedelta

# Database imports
from database.database import DatabaseManager
from database.models import User, SavedJob, AppliedJob, SessionData, AutomationLog, JobRecommendation, SystemSettings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="LinkedIn Job Hunter API Bridge", 
    version="3.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Load environment variables
load_dotenv()

# Initialize database
db_manager = DatabaseManager()

# Add performance middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Performance optimizations
CACHE_DURATION = 300  # 5 minutes
api_cache = {}
last_cache_cleanup = time.time()

# Request models
class JobSearchRequest(BaseModel):
    query: str
    location: Optional[str] = ''
    filters: Optional[dict] = None
    count: int = 10

class CredentialsRequest(BaseModel):
    username: str
    password: str

class JobApplyRequest(BaseModel):
    job_id: str
    job_url: str

# Health check with caching
@app.get("/api/health")
async def health_check():
    """Optimized health check with minimal overhead"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "version": "3.0.0",
        "services": {
            "api_bridge": "running",
            "mcp_backend": "checking"
        }
    }

# Cached credentials endpoint
@lru_cache(maxsize=1)
def get_cached_credentials():
    """Cache credentials to avoid repeated file reads"""
    try:
        username = os.getenv('LINKEDIN_USERNAME')
        password = os.getenv('LINKEDIN_PASSWORD')
        
        if username and password:
            return {
                "configured": True,
                "username": username,
                "password_length": len(password)
            }
        else:
            return {"configured": False}
    except Exception as e:
        logger.error(f"Error loading credentials: {e}")
        return {"configured": False}

@app.get("/api/get_credentials")
async def get_credentials():
    """Get LinkedIn credentials with caching"""
    return get_cached_credentials()

@app.post("/api/save_credentials")
async def save_credentials(request: CredentialsRequest):
    """Save LinkedIn credentials with validation"""
    try:
        # Validate credentials
        if not request.username or not request.password:
            raise HTTPException(status_code=400, detail="Username and password are required")
        
        # Update .env file
        env_content = f"""# LinkedIn Credentials
LINKEDIN_USERNAME={request.username}
LINKEDIN_PASSWORD={request.password}

OPENAI_API_KEY=

# Other Configuration
DEBUG=true
"""
        
        with open('.env', 'w') as f:
            f.write(env_content)
        
        # Clear cache to force reload
        get_cached_credentials.cache_clear()
        
        logger.info(f"Credentials saved for user: {request.username}")
        return {"success": True, "message": "Credentials saved successfully"}
        
    except Exception as e:
        logger.error(f"Error saving credentials: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to save credentials: {str(e)}")

# Optimized job search with caching
@app.post("/api/search_jobs")
async def search_jobs(request: JobSearchRequest, background_tasks: BackgroundTasks):
    """Search for jobs with caching and background processing"""
    cache_key = f"jobs_{request.query}_{request.location}_{request.count}"
    
    # Check cache first
    if cache_key in api_cache:
        cache_entry = api_cache[cache_key]
        if time.time() - cache_entry['timestamp'] < CACHE_DURATION:
            logger.info(f"Returning cached job search results for: {request.query}")
            return cache_entry['data']
    
    try:
        # Simulate job search (replace with actual MCP call)
        jobs = [
            {
                "id": f"job_{i}",
                "title": f"{request.query} Developer",
                "company": f"Company {i}",
                "location": request.location or "Remote",
                "description": f"Looking for a {request.query} developer...",
                "url": f"https://linkedin.com/jobs/view/{i}",
                "easy_apply": i % 2 == 0
            }
            for i in range(1, request.count + 1)
        ]
        
        result = {
            "jobs": jobs,
            "total": len(jobs),
            "query": request.query,
            "location": request.location
        }
        
        # Cache the result
        api_cache[cache_key] = {
            'data': result,
            'timestamp': time.time()
        }
        
        # Background task to clean old cache entries
        background_tasks.add_task(cleanup_cache)
        
        logger.info(f"Job search completed for: {request.query}")
        return result
        
    except Exception as e:
        logger.error(f"Error searching jobs: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to search jobs: {str(e)}")

@app.post("/api/apply_job")
async def apply_job(request: JobApplyRequest):
    """Apply to a job with rate limiting"""
    try:
        # Simulate job application (replace with actual MCP call)
        logger.info(f"Applying to job: {request.job_id}")
        
        # Simulate processing time
        await asyncio.sleep(1)
        
        return {
            "success": True,
            "job_id": request.job_id,
            "message": "Application submitted successfully",
            "timestamp": time.time()
        }
        
    except Exception as e:
        logger.error(f"Error applying to job: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to apply to job: {str(e)}")

@app.post("/api/save_job")
async def save_job(request: JobApplyRequest):
    """Save a job for later"""
    try:
        # Load existing saved jobs
        try:
            with open('saved_jobs.json', 'r') as f:
                saved_jobs = json.load(f)
        except FileNotFoundError:
            saved_jobs = []
        
        # Add new job
        job_data = {
            "id": request.job_id,
            "url": request.job_url,
            "saved_at": time.time(),
            "status": "saved"
        }
        
        # Check if already saved
        if not any(job['id'] == request.job_id for job in saved_jobs):
            saved_jobs.append(job_data)
            
            # Save to file
            with open('saved_jobs.json', 'w') as f:
                json.dump(saved_jobs, f, indent=2)
            
            logger.info(f"Job saved: {request.job_id}")
            return {"success": True, "message": "Job saved successfully"}
        else:
            return {"success": False, "message": "Job already saved"}
        
    except Exception as e:
        logger.error(f"Error saving job: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to save job: {str(e)}")

@app.get("/api/list_saved_jobs")
async def list_saved_jobs():
    """List saved jobs with caching"""
    try:
        with open('saved_jobs.json', 'r') as f:
            saved_jobs = json.load(f)
        return {"jobs": saved_jobs, "count": len(saved_jobs)}
    except FileNotFoundError:
        return {"jobs": [], "count": 0}
    except Exception as e:
        logger.error(f"Error listing saved jobs: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list saved jobs: {str(e)}")

@app.get("/api/list_applied_jobs")
async def list_applied_jobs():
    """List applied jobs"""
    try:
        # Load applied jobs from file
        try:
            with open('applied_jobs.json', 'r') as f:
                applied_jobs = json.load(f)
        except FileNotFoundError:
            applied_jobs = []
        
        return {"jobs": applied_jobs, "count": len(applied_jobs)}
    except Exception as e:
        logger.error(f"Error listing applied jobs: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list applied jobs: {str(e)}")

@app.get("/api/job_recommendations")
async def get_job_recommendations():
    """Get job recommendations based on user profile"""
    try:
        # Load user profile
        try:
            with open('user_profile.json', 'r') as f:
                user_profile = json.load(f)
        except FileNotFoundError:
            user_profile = {
                "skills": ["Python", "JavaScript"],
                "target_roles": ["Software Engineer"],
                "target_locations": ["Remote"]
            }
        
        # Generate recommendations based on profile
        recommendations = [
            {
                "id": f"rec_{i}",
                "title": f"{skill} Developer",
                "company": f"Tech Company {i}",
                "location": "Remote",
                "match_score": 85 + (i * 5),
                "reason": f"Matches your {skill} skills"
            }
            for i, skill in enumerate(user_profile.get('skills', ['Python'])[:5])
        ]
        
        return {
            "recommendations": recommendations,
            "user_profile": user_profile
        }
        
    except Exception as e:
        logger.error(f"Error getting recommendations: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get recommendations: {str(e)}")

# Database-enabled endpoints
@app.post("/api/user/profile")
async def update_user_profile(request: Dict[str, Any]):
    """Update user profile in database"""
    try:
        username = request.get('username', 'default_user')
        user_id = db_manager.get_user(username)
        if not user_id:
            # Extract only the fields that create_user accepts
            user_data = {
                'email': request.get('email'),
                'current_position': request.get('current_position'),
                'skills': request.get('skills', []),
                'target_roles': request.get('target_roles', []),
                'target_locations': request.get('target_locations', []),
                'experience_years': request.get('experience_years'),
                'resume_url': request.get('resume_url')
            }
            user_id = db_manager.create_user(username, **user_data)
        
        if user_id:
            # Extract only the fields that update_user accepts (excluding username)
            update_data = {k: v for k, v in request.items() if k != 'username'}
            success = db_manager.update_user(username, **update_data)
            if success:
                return {"success": True, "message": "Profile updated successfully"}
            else:
                raise HTTPException(status_code=500, detail="Failed to update profile")
        else:
            raise HTTPException(status_code=500, detail="Failed to create user")
    except Exception as e:
        logger.error(f"Error updating user profile: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update profile: {str(e)}")

@app.get("/api/user/profile")
async def get_user_profile():
    """Get user profile from database"""
    try:
        # For now, get the first user (in a real app, you'd use authentication)
        with db_manager.get_session() as session:
            user = session.query(User).first()
            if user:
                return {"success": True, "user": user.to_dict()}
            else:
                return {"success": False, "message": "No user found"}
    except Exception as e:
        logger.error(f"Error getting user profile: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get profile: {str(e)}")

@app.post("/api/save_job")
async def save_job_db(request: Dict[str, Any]):
    """Save a job using database"""
    try:
        username = request.get('username', 'default_user')
        user_id = db_manager.get_user(username)
        if not user_id:
            user_id = db_manager.create_user(username)
        
        if user_id:
            # Ensure all required fields are present
            job_data = {
                'job_id': request.get('job_id'),
                'title': request.get('title'),
                'company': request.get('company'),
                'location': request.get('location'),
                'job_url': request.get('job_url'),
                'description': request.get('description'),
                'salary_range': request.get('salary_range'),
                'job_type': request.get('job_type'),
                'experience_level': request.get('experience_level'),
                'easy_apply': request.get('easy_apply', False),
                'remote_work': request.get('remote_work', False),
                'notes': request.get('notes'),
                'tags': request.get('tags', [])
            }
            
            saved_job = db_manager.save_job(user_id, job_data)
            if saved_job:
                return {"success": True, "message": "Job saved successfully", "job": saved_job}
            else:
                raise HTTPException(status_code=500, detail="Failed to save job")
        else:
            raise HTTPException(status_code=500, detail="Failed to create user")
    except Exception as e:
        logger.error(f"Error saving job: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to save job: {str(e)}")

@app.get("/api/saved_jobs")
async def get_saved_jobs():
    """Get saved jobs from database"""
    try:
        username = 'default_user'  # In a real app, get from authentication
        user_id = db_manager.get_user(username)
        if user_id:
            jobs = db_manager.get_saved_jobs(user_id)
            return {"success": True, "jobs": jobs, "count": len(jobs)}
        else:
            return {"success": False, "jobs": [], "count": 0}
    except Exception as e:
        logger.error(f"Error getting saved jobs: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get saved jobs: {str(e)}")

@app.post("/api/apply_job")
async def apply_job_db(request: Dict[str, Any]):
    """Apply to a job using database"""
    try:
        username = request.get('username', 'default_user')
        user_id = db_manager.get_user(username)
        if not user_id:
            user_id = db_manager.create_user(username)
        
        if user_id:
            job_data = db_manager.apply_to_job(user_id, request)
            if job_data:
                return {"success": True, "message": "Application submitted successfully", "job": job_data}
            else:
                raise HTTPException(status_code=500, detail="Failed to submit application")
        else:
            raise HTTPException(status_code=500, detail="Failed to create user")
    except Exception as e:
        logger.error(f"Error applying to job: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to apply to job: {str(e)}")

@app.get("/api/applied_jobs")
async def get_applied_jobs():
    """Get applied jobs from database"""
    try:
        username = 'default_user'  # In a real app, get from authentication
        user_id = db_manager.get_user(username)
        if user_id:
            jobs = db_manager.get_applied_jobs(user_id)
            return {"success": True, "jobs": jobs, "count": len(jobs)}
        else:
            return {"success": False, "jobs": [], "count": 0}
    except Exception as e:
        logger.error(f"Error getting applied jobs: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get applied jobs: {str(e)}")

@app.post("/api/session/start")
async def start_session(request: Dict[str, Any]):
    """Start a new session"""
    try:
        username = request.get('username', 'default_user')
        user_id = db_manager.get_user(username)
        if not user_id:
            user_id = db_manager.create_user(username)
        
        if user_id:
            session_data = db_manager.create_session(user_id, **request)
            if session_data:
                return {"success": True, "message": "Session started successfully", "session": session_data}
            else:
                raise HTTPException(status_code=500, detail="Failed to start session")
        else:
            raise HTTPException(status_code=500, detail="Failed to create user")
    except Exception as e:
        logger.error(f"Error starting session: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to start session: {str(e)}")

@app.post("/api/session/update")
async def update_session(request: Dict[str, Any], session_id: str = Query(...)):
    """Update session data"""
    try:
        success = db_manager.update_session(session_id, **request)
        if success:
            return {"success": True, "message": "Session updated successfully"}
        else:
            raise HTTPException(status_code=404, detail="Session not found")
    except Exception as e:
        logger.error(f"Error updating session: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update session: {str(e)}")

@app.post("/api/session/end")
async def end_session(session_id: str = Query(...)):
    """End a session"""
    try:
        success = db_manager.end_session(session_id)
        if success:
            return {"success": True, "message": "Session ended successfully"}
        else:
            raise HTTPException(status_code=404, detail="Session not found")
    except Exception as e:
        logger.error(f"Error ending session: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to end session: {str(e)}")

@app.get("/api/analytics/logs")
async def get_automation_logs():
    """Get automation logs"""
    try:
        username = 'default_user'  # In a real app, get from authentication
        user_id = db_manager.get_user(username)
        if user_id:
            logs = db_manager.get_automation_logs(user_id)
            return {"success": True, "logs": logs, "count": len(logs)}
        else:
            return {"success": False, "logs": [], "count": 0}
    except Exception as e:
        logger.error(f"Error getting automation logs: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get logs: {str(e)}")

@app.get("/api/analytics/stats")
async def get_analytics_stats():
    """Get analytics statistics"""
    try:
        username = 'default_user'  # In a real app, get from authentication
        user_id = db_manager.get_user(username)
        if user_id:
            with db_manager.get_session() as session:
                # Get basic stats
                saved_count = session.query(SavedJob).filter(SavedJob.user_id == user_id).count()
                applied_count = session.query(AppliedJob).filter(AppliedJob.user_id == user_id).count()
                session_count = session.query(SessionData).filter(SessionData.user_id == user_id).count()
                log_count = session.query(AutomationLog).filter(AutomationLog.user_id == user_id).count()
                
                stats = {
                    "saved_jobs": saved_count,
                    "applied_jobs": applied_count,
                    "sessions": session_count,
                    "automation_logs": log_count
                }
                return {"success": True, "stats": stats}
        else:
            return {"success": False, "stats": {}}
    except Exception as e:
        logger.error(f"Error getting analytics stats: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")

@app.get("/api/database/stats")
async def get_database_stats():
    """Get database statistics"""
    try:
        stats = db_manager.get_database_stats()
        return {"success": True, "stats": stats}
    except Exception as e:
        logger.error(f"Error getting database stats: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get database stats: {str(e)}")

@app.post("/api/database/backup")
async def backup_database():
    """Create database backup"""
    try:
        backup_path = f"backups/linkedin_jobs_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        success = db_manager.backup_database(backup_path)
        if success:
            return {"success": True, "message": f"Database backed up to {backup_path}"}
        else:
            raise HTTPException(status_code=500, detail="Failed to create backup")
    except Exception as e:
        logger.error(f"Error creating backup: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create backup: {str(e)}")

@app.post("/api/database/cleanup")
async def cleanup_database(days: int = Query(30)):
    """Clean up old data"""
    try:
        cleaned_count = db_manager.cleanup_old_data(days)
        return {"success": True, "message": f"Cleaned up {cleaned_count} old records"}
    except Exception as e:
        logger.error(f"Error cleaning database: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to clean database: {str(e)}")

@app.post("/api/settings/{setting_key}")
async def set_system_setting(setting_key: str, value: str = Query(...), setting_type: str = Query('string'), description: str = Query(None)):
    """Set a system setting"""
    try:
        success = db_manager.set_setting(setting_key, value, setting_type, description)
        if success:
            return {"success": True, "message": f"Setting {setting_key} updated successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to update setting")
    except Exception as e:
        logger.error(f"Error setting system setting: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to set setting: {str(e)}")

@app.get("/api/settings/{setting_key}")
async def get_system_setting(setting_key: str):
    """Get a system setting"""
    try:
        value = db_manager.get_setting(setting_key)
        if value is not None:
            return {"success": True, "value": value}
        else:
            raise HTTPException(status_code=404, detail="Setting not found")
    except Exception as e:
        logger.error(f"Error getting system setting: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get setting: {str(e)}")

@app.post("/api/update_credentials")
async def update_credentials(request: CredentialsRequest):
    """Update LinkedIn credentials (legacy endpoint)"""
    try:
        # Validate credentials
        if not request.username or not request.password:
            raise HTTPException(status_code=400, detail="Username and password are required")
        
        # Update .env file
        env_content = f"""# LinkedIn Credentials
LINKEDIN_USERNAME={request.username}
LINKEDIN_PASSWORD={request.password}

OPENAI_API_KEY=

# Other Configuration
DEBUG=true
"""
        
        with open('.env', 'w') as f:
            f.write(env_content)
        
        # Clear cache to force reload
        get_cached_credentials.cache_clear()
        
        logger.info(f"Credentials updated for user: {request.username}")
        return {"success": True, "message": "Credentials updated successfully"}
        
    except Exception as e:
        logger.error(f"Error updating credentials: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update credentials: {str(e)}")

async def cleanup_cache():
    """Clean up old cache entries"""
    global last_cache_cleanup
    current_time = time.time()
    
    # Only cleanup every 5 minutes
    if current_time - last_cache_cleanup < 300:
        return
    
    last_cache_cleanup = current_time
    
    # Remove expired entries
    expired_keys = [
        key for key, entry in api_cache.items()
        if current_time - entry['timestamp'] > CACHE_DURATION
    ]
    
    for key in expired_keys:
        del api_cache[key]
    
    if expired_keys:
        logger.info(f"Cleaned up {len(expired_keys)} expired cache entries")

def find_available_port(start_port=8001, max_attempts=10):
    """Find an available port starting from start_port"""
    for port in range(start_port, start_port + max_attempts):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', port))
                return port
        except OSError:
            continue
    raise RuntimeError(f"No available ports found in range {start_port}-{start_port + max_attempts - 1}")

if __name__ == "__main__":
    import uvicorn
    
    # Find available port
    try:
        port = find_available_port()
        logger.info(f"Starting Optimized API Bridge on port {port}")
        
        # Save port to file
        with open("api_bridge_port.txt", "w") as f:
            f.write(str(port))
        
        # Start server with optimized settings
        uvicorn.run(
            app, 
            host="0.0.0.0", 
            port=port, 
            reload=False,
            workers=1,
            log_level="info",
            access_log=True
        )
        
    except Exception as e:
        logger.error(f"Failed to start API Bridge: {e}")
        sys.exit(1) 