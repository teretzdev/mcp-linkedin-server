#!/usr/bin/env python3
"""
Autonomous Job Applier
This script uses the enhanced MCP server to autonomously search for jobs
and apply to them using a provided resume.
"""

import asyncio
import os
import json
from pathlib import Path
import structlog
import sys

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from mcp_server.core.server import get_server
from fastmcp import FastMCP
from dotenv import load_dotenv

logger = structlog.get_logger(__name__)

async def run_autonomous_job_application(job_query: str, location: str, resume_path: str):
    """
    Runs the autonomous job application process.
    """
    server = get_server()
    await server.initialize()

    try:
        logger.info("Starting autonomous job application process...")
        
        # 1. Login to LinkedIn
        login_result = await server.mcp.tools["login_linkedin_secure"](ctx=None)
        if login_result.get("status") != "success":
            logger.error("Login failed", reason=login_result.get("message"))
            return
            
        logger.info("Login successful. Starting job search...")

        # 2. Search for jobs
        search_result = await server.mcp.tools["search_linkedin_jobs"](ctx=None, query=job_query, location=location, count=10)

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
            apply_result = await server.mcp.tools["apply_to_linkedin_job"](ctx=None, job_url=job_url, resume_path=resume_path)
            
            if apply_result.get("status") == "success":
                logger.info("Successfully applied to job", job_url=job_url)
            else:
                logger.error("Failed to apply to job", job_url=job_url, reason=apply_result.get("message"))

    finally:
        await server.cleanup()
        logger.info("Autonomous job application process finished.")


if __name__ == "__main__":
    # Load environment variables from .env file
    load_dotenv()

    # Configuration
    JOB_QUERY = "Software Engineer"
    LOCATION = "Remote"
    RESUME_PATH = "resumes/test_resume.pdf" # Make sure this path is correct

    # Run the main async function
    asyncio.run(run_autonomous_job_application(JOB_QUERY, LOCATION, RESUME_PATH))