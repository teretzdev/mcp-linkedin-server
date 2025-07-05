#!/usr/bin/env python3
"""
Autonomous Job Applier - Legacy Version
This script uses the legacy MCP server to autonomously search for jobs
and apply to them using a provided resume.
"""

import asyncio
import os
import json
from pathlib import Path
import structlog

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
import sys
sys.path.insert(0, str(project_root))

# Use the legacy MCP client
from legacy.mcp_client import MCPClient, call_mcp_tool, shutdown_mcp_client
from dotenv import load_dotenv

logger = structlog.get_logger(__name__)

async def run_autonomous_job_application(job_query: str, location: str, resume_path: str):
    """
    Runs the autonomous job application process using the legacy system.
    """
    # Use a path relative to the project root
    legacy_server_path = str(Path(__file__).parent / 'legacy' / 'linkedin_browser_mcp.py')
    client = MCPClient(command=f"python3 {legacy_server_path}")
    
    try:
        logger.info("Starting autonomous job application process with legacy system...")
        
        # 1. Login to LinkedIn
        await client.connect()
        login_result = await call_mcp_tool("login_linkedin_secure")
        if login_result.get("status") != "success":
            logger.error("Login failed", reason=login_result.get("message"))
            return
            
        logger.info("Login successful. Starting job search...")

        # 2. Search for jobs
        search_result = await call_mcp_tool(
            "search_linkedin_jobs",
            {"query": job_query, "location": location, "count": 10}
        )
        if search_result.get("status") != "success":
            logger.error("Job search failed", reason=search_result.get("message"))
            return

        jobs = search_result.get("jobs", [])
        logger.info(f"Found {len(jobs)} jobs to process.")

        # 3. Apply to jobs
        for job in jobs:
            job_url = job.get("jobUrl")
            if not job_url:
                continue

            logger.info(f"Applying to job: {job.get('title')} at {job.get('company')}")
            apply_result = await call_mcp_tool(
                "apply_to_linkedin_job",
                {"job_url": job_url, "resume_path": resume_path}
            )
            
            if apply_result.get("status") == "success":
                logger.info("Successfully applied to job", job_url=job_url)
            else:
                logger.error("Failed to apply to job", job_url=job_url, reason=apply_result.get("message"))

    finally:
        await client.close()
        logger.info("Autonomous job application process finished.")


if __name__ == "__main__":
    # Load environment variables from .env file in the legacy directory
    load_dotenv(dotenv_path=project_root / 'legacy' / '.env')

    # Configuration
    JOB_QUERY = "Software Engineer"
    LOCATION = "Remote"
    RESUME_PATH = "resumes/test_resume.pdf" # Make sure this path is correct

    # Run the main async function
    asyncio.run(run_autonomous_job_application(JOB_QUERY, LOCATION, RESUME_PATH))