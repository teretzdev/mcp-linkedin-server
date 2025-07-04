#!/usr/bin/env python3
"""
Enhanced API Bridge with Database Integration
Replaces file-based storage with SQLite database
"""

import os
import sys
import json
import time
import logging
import asyncio
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path

# Add current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# Import database components
from database.database import DatabaseManager
from database.models import User, SavedJob, AppliedJob, SessionData, AutomationLog

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="LinkedIn Job Hunter API", version="2.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global database manager
db_manager: Optional[DatabaseManager] = None

# Cache for API responses
api_cache = {}
CACHE_DURATION = 300  # 5 minutes

# Pydantic models for API requests/responses
class JobSearchRequest(BaseModel):
    query: str
    location: Optional[str] = None
    count: int = 10

class JobApplyRequest(BaseModel):
    job_id: str
    job_url: str
    title: str
    company: str
    location: Optional[str] = None
    cover_letter: Optional[str] = None
    resume_used: Optional[str] = None
    notes: Optional[str] = None

class SaveJobRequest(BaseModel):
    job_id: str
    job_url: str
    title: str
    company: str
    location: Optional[str] = None
    description: Optional[str] = None
    salary_range: Optional[str] = None
    job_type: Optional[str] = None
    experience_level: Optional[str] = None
    easy_apply: bool = False
    remote_work: bool = False
    notes: Optional[str] = None
    tags: Optional[List[str]] = None

class CredentialsRequest(BaseModel):
    username: str
    password: str

class UserProfileRequest(BaseModel):
    username: str
    email: Optional[str] = None
    current_position: Optional[str] = None
    skills: Optional[List[str]] = None
    target_roles: Optional[List[str]] = None
    target_locations: Optional[List[str]] = None
    experience_years: Optional[int] = None
    resume_url: Optional[str] = None

class SessionRequest(BaseModel):
    session_id: str
    automation_mode: str = "manual"

# Dependency to get database manager
def get_db_manager() -> DatabaseManager:
    if db_manager is None:
        raise HTTPException(status_code=500, detail="Database not initialized")
    return db_manager

# Dependency to get current user
def get_current_user(db: DatabaseManager = Depends(get_db_manager)) -> User:
    # For now, return the first user or create a default one
    # In a real application, you'd implement proper authentication
    user = db.get_user("default_user")
    if not user:
        user = db.create_user(
            username="default_user",
            email="default@example.com",
            current_position="Software Engineer"
        )
    return user

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    global db_manager
    try:
        logger.info("🚀 Starting LinkedIn Job Hunter API with Database Integration")
        
        # Initialize database
        db_manager = DatabaseManager("linkedin_jobs.db")
        
        # Test database connection
        if not db_manager.test_connection():
            logger.error("❌ Database connection failed")
            raise Exception("Database connection failed")
        
        logger.info("✅ Database initialized successfully")
        
        # Log startup action
        user = get_current_user(db_manager)
        db_manager.log_automation_action(
            user_id=user.id,
            action="api_startup",
            success=True,
            details={"version": "2.0.0", "database": "sqlite"}
        )
        
    except Exception as e:
        logger.error(f"❌ Startup failed: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    global db_manager
    try:
        if db_manager:
            # Log shutdown action
            user = get_current_user(db_manager)
            db_manager.log_automation_action(
                user_id=user.id,
                action="api_shutdown",
                success=True,
                details={"duration": "session_duration"}
            )
            
            logger.info("✅ API shutdown completed")
    except Exception as e:
        logger.error(f"❌ Shutdown error: {e}")

# Health check endpoint
@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    try:
        db = get_db_manager()
        if db.test_connection():
            return {
                "status": "healthy",
                "database": "connected",
                "timestamp": datetime.now().isoformat(),
                "version": "2.0.0"
            }
        else:
            raise HTTPException(status_code=500, detail="Database connection failed")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")

# User management endpoints
@app.post("/api/user/profile")
async def update_user_profile(request: UserProfileRequest, db: DatabaseManager = Depends(get_db_manager)):
    """Update user profile"""
    try:
        user = db.get_user(request.username)
        if not user:
            # Create new user
            user = db.create_user(
                username=request.username,
                email=request.email,
                current_position=request.current_position,
                skills=request.skills or [],
                target_roles=request.target_roles or [],
                target_locations=request.target_locations or [],
                experience_years=request.experience_years,
                resume_url=request.resume_url
            )
        else:
            # Update existing user
            db.update_user(
                username=request.username,
                email=request.email,
                current_position=request.current_position,
                skills=request.skills or [],
                target_roles=request.target_roles or [],
                target_locations=request.target_locations or [],
                experience_years=request.experience_years,
                resume_url=request.resume_url
            )
        
        # Log action
        db.log_automation_action(
            user_id=user.id,
            action="update_profile",
            success=True,
            details={"profile_updated": True}
        )
        
        return {"success": True, "message": "Profile updated successfully", "user": user.to_dict()}
        
    except Exception as e:
        logger.error(f"Error updating user profile: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update profile: {str(e)}")

@app.get("/api/user/profile")
async def get_user_profile(user: User = Depends(get_current_user)):
    """Get user profile"""
    try:
        return {"success": True, "user": user.to_dict()}
    except Exception as e:
        logger.error(f"Error getting user profile: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get profile: {str(e)}")

# Job search endpoint
@app.post("/api/search_jobs")
async def search_jobs(request: JobSearchRequest, background_tasks: BackgroundTasks, user: User = Depends(get_current_user)):
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
        
        # Log search action
        db_manager.log_automation_action(
            user_id=user.id,
            action="job_search",
            success=True,
            details={"query": request.query, "location": request.location, "count": request.count}
        )
        
        # Background task to clean old cache entries
        background_tasks.add_task(cleanup_cache)
        
        logger.info(f"Job search completed for: {request.query}")
        return result
        
    except Exception as e:
        logger.error(f"Error searching jobs: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to search jobs: {str(e)}")

# Job management endpoints
@app.post("/api/save_job")
async def save_job(request: SaveJobRequest, user: User = Depends(get_current_user)):
    """Save a job for later"""
    try:
        job_data = {
            "job_id": request.job_id,
            "title": request.title,
            "company": request.company,
            "location": request.location,
            "job_url": request.job_url,
            "description": request.description,
            "salary_range": request.salary_range,
            "job_type": request.job_type,
            "experience_level": request.experience_level,
            "easy_apply": request.easy_apply,
            "remote_work": request.remote_work,
            "notes": request.notes,
            "tags": request.tags or []
        }
        
        saved_job = db_manager.save_job(user.id, job_data)
        
        if saved_job:
            # Log action
            db_manager.log_automation_action(
                user_id=user.id,
                action="save_job",
                success=True,
                details={"job_id": request.job_id, "title": request.title},
                job_id=request.job_id
            )
            
            logger.info(f"Job saved: {request.job_id}")
            return {"success": True, "message": "Job saved successfully", "job": saved_job.to_dict()}
        else:
            return {"success": False, "message": "Job already saved"}
        
    except Exception as e:
        logger.error(f"Error saving job: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to save job: {str(e)}")

@app.post("/api/apply_job")
async def apply_job(request: JobApplyRequest, user: User = Depends(get_current_user)):
    """Apply to a job"""
    try:
        job_data = {
            "job_id": request.job_id,
            "title": request.title,
            "company": request.company,
            "location": request.location,
            "job_url": request.job_url,
            "cover_letter": request.cover_letter,
            "resume_used": request.resume_used,
            "notes": request.notes
        }
        
        applied_job = db_manager.apply_to_job(user.id, job_data)
        
        if applied_job:
            # Log action
            db_manager.log_automation_action(
                user_id=user.id,
                action="apply_job",
                success=True,
                details={"job_id": request.job_id, "title": request.title},
                job_id=request.job_id
            )
            
            logger.info(f"Applied to job: {request.job_id}")
            return {"success": True, "message": "Application submitted successfully", "job": applied_job.to_dict()}
        else:
            return {"success": False, "message": "Already applied to this job"}
        
    except Exception as e:
        logger.error(f"Error applying to job: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to apply to job: {str(e)}")

@app.get("/api/saved_jobs")
async def get_saved_jobs(user: User = Depends(get_current_user), limit: int = 50):
    """Get saved jobs"""
    try:
        saved_jobs = db_manager.get_saved_jobs(user.id, limit)
        return {
            "success": True,
            "jobs": [job.to_dict() for job in saved_jobs],
            "total": len(saved_jobs)
        }
    except Exception as e:
        logger.error(f"Error getting saved jobs: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get saved jobs: {str(e)}")

@app.get("/api/applied_jobs")
async def get_applied_jobs(user: User = Depends(get_current_user), limit: int = 50):
    """Get applied jobs"""
    try:
        applied_jobs = db_manager.get_applied_jobs(user.id, limit)
        return {
            "success": True,
            "jobs": [job.to_dict() for job in applied_jobs],
            "total": len(applied_jobs)
        }
    except Exception as e:
        logger.error(f"Error getting applied jobs: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get applied jobs: {str(e)}")

# Session management endpoints
@app.post("/api/session/start")
async def start_session(request: SessionRequest, user: User = Depends(get_current_user)):
    """Start a new session"""
    try:
        session = db_manager.create_session(
            user_id=user.id,
            session_id=request.session_id,
            automation_mode=request.automation_mode
        )
        
        if session:
            # Log action
            db_manager.log_automation_action(
                user_id=user.id,
                action="start_session",
                success=True,
                details={"session_id": request.session_id, "mode": request.automation_mode}
            )
            
            return {"success": True, "message": "Session started", "session": session.to_dict()}
        else:
            raise HTTPException(status_code=500, detail="Failed to start session")
        
    except Exception as e:
        logger.error(f"Error starting session: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to start session: {str(e)}")

@app.post("/api/session/end")
async def end_session(session_id: str, user: User = Depends(get_current_user)):
    """End a session"""
    try:
        success = db_manager.end_session(session_id)
        
        if success:
            # Log action
            db_manager.log_automation_action(
                user_id=user.id,
                action="end_session",
                success=True,
                details={"session_id": session_id}
            )
            
            return {"success": True, "message": "Session ended"}
        else:
            raise HTTPException(status_code=404, detail="Session not found")
        
    except Exception as e:
        logger.error(f"Error ending session: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to end session: {str(e)}")

@app.post("/api/session/update")
async def update_session(session_id: str, updates: Dict[str, Any], user: User = Depends(get_current_user)):
    """Update session data"""
    try:
        success = db_manager.update_session(session_id, **updates)
        
        if success:
            return {"success": True, "message": "Session updated"}
        else:
            raise HTTPException(status_code=404, detail="Session not found")
        
    except Exception as e:
        logger.error(f"Error updating session: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update session: {str(e)}")

# Analytics and logging endpoints
@app.get("/api/analytics/logs")
async def get_automation_logs(user: User = Depends(get_current_user), limit: int = 100):
    """Get automation logs"""
    try:
        logs = db_manager.get_automation_logs(user.id, limit)
        return {
            "success": True,
            "logs": [log.to_dict() for log in logs],
            "total": len(logs)
        }
    except Exception as e:
        logger.error(f"Error getting automation logs: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get logs: {str(e)}")

@app.get("/api/analytics/stats")
async def get_analytics_stats(user: User = Depends(get_current_user)):
    """Get analytics statistics"""
    try:
        # Get user's saved and applied jobs
        saved_jobs = db_manager.get_saved_jobs(user.id, 1000)
        applied_jobs = db_manager.get_applied_jobs(user.id, 1000)
        logs = db_manager.get_automation_logs(user.id, 1000)
        
        # Calculate statistics
        stats = {
            "total_saved_jobs": len(saved_jobs),
            "total_applied_jobs": len(applied_jobs),
            "total_automation_actions": len(logs),
            "successful_actions": len([log for log in logs if log.success]),
            "failed_actions": len([log for log in logs if not log.success]),
            "recent_activity": {
                "last_7_days": len([log for log in logs if (datetime.now() - log.timestamp).days <= 7]),
                "last_30_days": len([log for log in logs if (datetime.now() - log.timestamp).days <= 30])
            }
        }
        
        return {"success": True, "stats": stats}
        
    except Exception as e:
        logger.error(f"Error getting analytics stats: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")

# System settings endpoints
@app.get("/api/settings/{key}")
async def get_setting(key: str, db: DatabaseManager = Depends(get_db_manager)):
    """Get system setting"""
    try:
        value = db.get_setting(key)
        return {"success": True, "key": key, "value": value}
    except Exception as e:
        logger.error(f"Error getting setting: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get setting: {str(e)}")

@app.post("/api/settings/{key}")
async def set_setting(key: str, value: str, setting_type: str = "string", db: DatabaseManager = Depends(get_db_manager)):
    """Set system setting"""
    try:
        success = db.set_setting(key, value, setting_type)
        if success:
            return {"success": True, "message": "Setting updated"}
        else:
            raise HTTPException(status_code=500, detail="Failed to update setting")
    except Exception as e:
        logger.error(f"Error setting setting: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to set setting: {str(e)}")

# Database maintenance endpoints
@app.get("/api/database/stats")
async def get_database_stats(db: DatabaseManager = Depends(get_db_manager)):
    """Get database statistics"""
    try:
        stats = db.get_database_stats()
        return {"success": True, "stats": stats}
    except Exception as e:
        logger.error(f"Error getting database stats: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get database stats: {str(e)}")

@app.post("/api/database/backup")
async def backup_database(db: DatabaseManager = Depends(get_db_manager)):
    """Create database backup"""
    try:
        backup_dir = Path("backups")
        backup_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = backup_dir / f"linkedin_jobs_backup_{timestamp}.db"
        
        success = db.backup_database(str(backup_path))
        if success:
            return {"success": True, "message": "Backup created", "path": str(backup_path)}
        else:
            raise HTTPException(status_code=500, detail="Failed to create backup")
    except Exception as e:
        logger.error(f"Error creating backup: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create backup: {str(e)}")

@app.post("/api/database/cleanup")
async def cleanup_database(days: int = 30, db: DatabaseManager = Depends(get_db_manager)):
    """Clean up old data"""
    try:
        deleted_count = db.cleanup_old_data(days)
        return {"success": True, "message": f"Cleaned up {deleted_count} old records"}
    except Exception as e:
        logger.error(f"Error cleaning up database: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to cleanup database: {str(e)}")

# Utility functions
def cleanup_cache():
    """Clean up old cache entries"""
    current_time = time.time()
    expired_keys = [
        key for key, entry in api_cache.items()
        if current_time - entry['timestamp'] > CACHE_DURATION
    ]
    for key in expired_keys:
        del api_cache[key]

# Legacy endpoints for backward compatibility
@app.post("/api/update_credentials")
async def update_credentials(request: CredentialsRequest):
    """Update LinkedIn credentials (legacy endpoint)"""
    try:
        # Store credentials in database settings
        db = get_db_manager()
        db.set_setting("linkedin_username", request.username, "string", "LinkedIn username")
        db.set_setting("linkedin_password", request.password, "string", "LinkedIn password")
        
        logger.info(f"Credentials updated for user: {request.username}")
        return {"success": True, "message": "Credentials updated successfully"}
        
    except Exception as e:
        logger.error(f"Error updating credentials: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update credentials: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="info") 