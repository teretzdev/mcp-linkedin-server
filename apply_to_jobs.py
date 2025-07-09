# apply_to_jobs.py
import asyncio
import json
import logging
import time
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import aiohttp
from dataclasses import dataclass, asdict, field
from pathlib import Path
import centralized_logging

central_logger = centralized_logging.get_logger("apply_to_jobs")

class JobApplicationManager:
    """Handles the job application phase."""
    
    def __init__(self, api_base_url: str | None = None):
        try:
            with open('service_ports.json', 'r') as f:
                ports = json.load(f)
            job_mgmt_port = ports.get('job_management_api', 8006)
        except:
            job_mgmt_port = 8006
            
        self.job_management_api_base_url = f"http://localhost:{job_mgmt_port}"
        
        self.application_stats = {
            "jobs_applied": 0,
            "last_run": None,
            "total_runtime": 0,
            "errors": 0
        }

    async def run_application_phase(self, max_applications: int = 20):
        """Phase 2: Fetch jobs from the database and apply to them."""
        central_logger.log_info("--- Starting Phase 2: Application ---")
        jobs_to_apply = await self._get_jobs_by_status('scraped', max_applications)
        
        if not jobs_to_apply:
            central_logger.log_info("No new jobs to apply for in this cycle.")
            return

        applied_count = 0
        for job in jobs_to_apply:
            if applied_count >= max_applications:
                central_logger.log_info("Reached max application limit for this cycle.")
                break
            
            job_id = job.get('job_id')
            if not job_id:
                central_logger.log_warning("Skipping job with no job_id.")
                continue

            central_logger.log_info(f"Applying to: {job.get('title')} ({job_id})")
            
            await self._update_job_status(job_id, 'applying')
            
            # This is where the real application automation would happen.
            # For now, we'll simulate it.
            await asyncio.sleep(5) 
            application_successful = True 
            error_message = None
            
            if application_successful:
                await self._update_job_status(job_id, 'applied')
                self.application_stats['jobs_applied'] += 1
                applied_count += 1
            else:
                await self._update_job_status(job_id, 'error', error_message)
                self.application_stats['errors'] += 1
        
        central_logger.log_info(f"--- Application Phase Completed Successfully ---")

    async def _get_jobs_by_status(self, status: str, limit: int) -> List[Dict]:
        """Helper to get jobs from the job management API."""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.job_management_api_base_url}/api/jobs/status/{status}?limit={limit}"
                async with session.get(url) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        central_logger.log_error(f"Failed to get jobs with status {status}. API returned {response.status}")
                        return []
        except Exception as e:
            central_logger.log_error(f"Exception while getting jobs by status: {e}")
            return []

    async def _update_job_status(self, job_id: str, status: str, error_message: Optional[str] = None):
        """Helper to update a job's status via the API."""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.job_management_api_base_url}/api/jobs/{job_id}/status/{status}"
                params = {}
                if error_message:
                    params['error_message'] = error_message
                async with session.put(url, params=params) as response:
                    if response.status != 200:
                        central_logger.log_error(f"Failed to update job {job_id} status to {status}. API responded with {response.status}")
        except Exception as e:
            central_logger.log_error(f"Exception while updating job status for {job_id}: {e}")

async def main():
    manager = JobApplicationManager()
    await manager.run_application_phase()
    
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        central_logger.log_info("Application process stopped by user.")
    except Exception as e:
        central_logger.log_error(f"A fatal error occurred in the application process: {e}", exc_info=True) 