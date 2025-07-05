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

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
import sys
sys.path.insert(0, str(project_root))

from mcp_server.core.server import get_server
from fastmcp import FastMCP

logger = structlog.get_logger(__name__)

async def run_autonomous_job_application(job_query: str, location: str, resume_path: str):
    """
    Runs the autonomous job application process.
    """
    server = get_server()
    await server.initialize()

    try:
        logger.info("Starting autonomous job application process...")
        
        # 1. Search for jobs
        search_tool = get_server().mcp.tools["search_linkedin_jobs"]
        search_result = await search_tool(ctx=None, query=job_query, location=location, count=10)

        if search_result.get("status") != "success":
            logger.error("Job search failed", reason=search_result.get("message"))
            return

        jobs = search_result.get("jobs", [])
        logger.info(f"Found {len(jobs)} jobs to process.")

        # 2. Apply to jobs
        apply_tool = get_server().mcp.tools["apply_to_linkedin_job"]
        for job in jobs:
            job_url = job.get("jobUrl")
            if not job_url:
                continue

            logger.info(f"Applying to job: {job.get('title')} at {job.get('company')}")
            apply_result = await apply_tool(ctx=None, job_url=job_url, resume_path=resume_path)
            
            if apply_result.get("status") == "success":
                logger.info("Successfully applied to job", job_url=job_url)
            else:
                logger.error("Failed to apply to job", job_url=job_url, reason=apply_result.get("message"))

    finally:
        await server.cleanup()
        logger.info("Autonomous job application process finished.")


if __name__ == "__main__":
    # Configuration
    JOB_QUERY = "Software Engineer"
    LOCATION = "Remote"
    RESUME_PATH = "resumes/test_resume.pdf" # Make sure this path is correct

    # Run the main async function
    asyncio.run(run_autonomous_job_application(JOB_QUERY, LOCATION, RESUME_PATH))