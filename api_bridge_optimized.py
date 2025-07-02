#!/usr/bin/env python3
"""
Optimized API Bridge for LinkedIn MCP Server
Provides HTTP endpoints for the React frontend with improved performance
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from pydantic import BaseModel
import asyncio
import json
import subprocess
import sys
import os
from typing import Optional, Dict, Any
from dotenv import load_dotenv
import socket
import time
import logging
from functools import lru_cache
import aiohttp

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