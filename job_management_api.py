#!/usr/bin/env python3
"""
API endpoints for managing scraped jobs in the new two-phase system.
"""

from fastapi import FastAPI, Depends, HTTPException
from typing import List
from legacy.database.database import DatabaseManager
from legacy.database.models import ScrapedJob
from centralized_logging import get_logger
import uvicorn
from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from legacy.database.database import DatabaseManager
from legacy.database.models import ScrapedJob, Base
import port_manager

logger = get_logger("job_management_api")

app = FastAPI()

def get_db_manager():
    return DatabaseManager()

@app.get("/api/jobs/status/{status}", response_model=List[dict])
async def get_jobs_by_status(status: str, limit: int = 50, db: DatabaseManager = Depends(get_db_manager)):
    """
    Get a list of jobs with a specific status.
    """
    try:
        # Assuming a default user for now, this should be improved with proper auth
        user_id = db.get_user("default_user")
        if not user_id:
            raise HTTPException(status_code=404, detail="Default user not found")
        
        jobs = db.get_scraped_jobs_by_status(user_id, status, limit=limit)
        return jobs
    except Exception as e:
        logger.log_error(f"Error getting jobs by status '{status}': {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/jobs/{job_id}/status/{status}")
async def update_job_status_endpoint(job_id: str, status: str, error_message: str = None, db: DatabaseManager = Depends(get_db_manager)):
    """
    Update the status of a specific job.
    """
    try:
        success = db.update_job_status(job_id, status, error_message)
        if success:
            return {"status": "success", "message": f"Job {job_id} status updated to {status}"}
        else:
            raise HTTPException(status_code=404, detail=f"Job not found or failed to update: {job_id}")
    except Exception as e:
        logger.log_error(f"Error updating job status for {job_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    port = port_manager.find_available_port(start_port=8003)
    port_manager.assign_port('job_management_api', port)
    logger.log_info(f"Starting Job Management API on http://0.0.0.0:{port}")
    uvicorn.run(app, host="0.0.0.0", port=port) 