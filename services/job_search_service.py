"""
Job search service with proper error handling and timeout management.
"""
import asyncio
import logging
from typing import List, Optional
from datetime import datetime
from pathlib import Path

from core.models.job_data import JobData, SearchCriteria, JobStatus
from core.config.settings import get_config

# Import HTTP client for MCP communication
import aiohttp
import subprocess
import json
from pathlib import Path

MCP_AVAILABLE = True  # We'll use HTTP to communicate with MCP server


class JobSearchService:
    """Service for searching jobs with proper error handling and timeouts"""
    
    def __init__(self):
        self.config = get_config()
        self.logger = logging.getLogger(__name__)
        
    async def search_jobs(self, criteria: SearchCriteria) -> List[JobData]:
        """
        Search for jobs using the specified criteria.
        
        Args:
            criteria: Search criteria including query, location, count
            
        Returns:
            List of JobData objects found
            
        Raises:
            JobSearchError: If search fails
        """
        self.logger.info(f"Starting job search: {criteria.query} in {criteria.location}")
        
        if not MCP_AVAILABLE:
            raise JobSearchError("MCP client not available - cannot search jobs")
        
        try:
            # Use asyncio.wait_for to implement timeout
            search_timeout = self.config.automation.job_search_timeout_seconds
            jobs = await asyncio.wait_for(
                self._perform_search(criteria),
                timeout=search_timeout
            )
            
            self.logger.info(f"Job search completed: found {len(jobs)} jobs")
            return jobs
            
        except asyncio.TimeoutError:
            error_msg = f"Job search timed out after {search_timeout} seconds"
            self.logger.error(error_msg)
            raise JobSearchTimeoutError(error_msg)
            
        except Exception as e:
            error_msg = f"Job search failed: {type(e).__name__}: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            raise JobSearchError(error_msg) from e
    
    async def _perform_search(self, criteria: SearchCriteria) -> List[JobData]:
        """Perform the actual job search using the existing API"""
        jobs = []
        
        try:
            # For now, we'll use the existing API bridge instead of MCP directly
            # This is a temporary solution until we properly integrate MCP
            
            # Get API port from config
            api_port = self.config.service_ports.api_bridge
            api_url = f"http://localhost:{api_port}/api/search_jobs_internal"
            
            self.logger.info(f"Calling job search API: {api_url}")
            
            async with aiohttp.ClientSession() as session:
                payload = criteria.to_dict()
                
                async with session.post(api_url, json=payload, timeout=300) as response:
                    if response.status == 200:
                        result = await response.json()
                        
                        if result.get("status") == "success":
                            raw_jobs = result.get("jobs", [])
                            self.logger.info(f"API returned {len(raw_jobs)} jobs")
                            
                            # Convert raw job data to JobData objects
                            for raw_job in raw_jobs:
                                try:
                                    job_data = self._convert_raw_job(raw_job)
                                    jobs.append(job_data)
                                except Exception as e:
                                    self.logger.warning(f"Failed to convert job data: {e}")
                                    continue
                        else:
                            error_msg = result.get("message", "Unknown API error")
                            raise JobSearchError(f"API job search failed: {error_msg}")
                    else:
                        error_text = await response.text()
                        raise JobSearchError(f"API returned status {response.status}: {error_text}")
                        
        except aiohttp.ClientError as e:
            raise JobSearchError(f"API connection error: {str(e)}") from e
        except asyncio.TimeoutError:
            raise  # Re-raise timeout errors
        except Exception as e:
            if isinstance(e, JobSearchError):
                raise  # Re-raise our custom errors
            raise JobSearchError(f"Job search error: {str(e)}") from e
            
        return jobs
    
    def _convert_raw_job(self, raw_job: dict) -> JobData:
        """Convert raw job data from MCP to JobData object"""
        try:
            return JobData(
                job_id=raw_job.get('job_id', ''),
                title=raw_job.get('title', ''),
                company=raw_job.get('company', ''),
                location=raw_job.get('location', ''),
                job_url=raw_job.get('job_url', ''),
                description=raw_job.get('description', ''),
                salary_range=raw_job.get('salary_range'),
                job_type=raw_job.get('job_type'),
                experience_level=raw_job.get('experience_level'),
                easy_apply=raw_job.get('easy_apply', False),
                remote_work=raw_job.get('remote_work', False),
                source='linkedin',
                status=JobStatus.SCRAPED,
                scraped_at=datetime.now()
            )
        except Exception as e:
            raise JobSearchError(f"Failed to convert job data: {e}") from e
    
    async def test_connection(self) -> bool:
        """Test if the job search service can connect to the API"""
        try:
            self.logger.info("Testing API connection...")
            
            # Get API port from config
            api_port = self.config.service_ports.api_bridge
            api_url = f"http://localhost:{api_port}/api/health"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(api_url, timeout=10) as response:
                    if response.status == 200:
                        result = await response.json()
                        success = result.get("status") == "ok"
                        self.logger.info(f"API connection test: {'SUCCESS' if success else 'FAILED'}")
                        return success
                    else:
                        self.logger.error(f"API health check failed: status {response.status}")
                        return False
                
        except Exception as e:
            self.logger.error(f"API connection test failed: {e}")
            return False


class JobSearchError(Exception):
    """Base exception for job search errors"""
    pass


class JobSearchTimeoutError(JobSearchError):
    """Exception raised when job search times out"""
    pass


class JobSearchConnectionError(JobSearchError):
    """Exception raised when cannot connect to LinkedIn"""
    pass 