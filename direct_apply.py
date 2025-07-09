import asyncio
import json
from fastmcp import Client
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def find_and_apply():
    """
    Logs into LinkedIn, searches for jobs, and applies to the first 3 easy apply jobs.
    """
    client = Client(str(Path(__file__).parent / "linkedin_browser_mcp.py"))
    applied_count = 0
    max_applications = 3

    async with client:
        # 1. Login
        logger.info("Attempting to log in...")
        # NOTE: Replace with your actual LinkedIn credentials
        login_result = await client.call_tool("login_linkedin", {"username": "YOUR_USERNAME", "password": "YOUR_PASSWORD"})
        login_content = login_result[0].text if isinstance(login_result, list) and login_result else "{}"
        login_data = json.loads(login_content)
        
        if login_data.get("status") != "success":
            logger.error(f"Login failed: {login_data.get('message')}")
            return
        logger.info("Login successful.")

        # 2. Search for jobs
        logger.info("Searching for 'Software Engineer' jobs...")
        search_result = await client.call_tool("search_linkedin_jobs", {"query": "Software Engineer", "count": 25})
        search_content = search_result[0].text if isinstance(search_result, list) and search_result else "{}"
        search_data = json.loads(search_content)

        if search_data.get("status") != "success":
            logger.error(f"Job search failed: {search_data.get('message')}")
            return
        
        jobs = search_data.get("jobs", [])
        logger.info(f"Found {len(jobs)} jobs.")

        # 3. Apply to jobs
        for job in jobs:
            if applied_count >= max_applications:
                break

            job_url = job.get("jobUrl")
            if not job_url:
                continue

            logger.info(f"Attempting to apply to: {job.get('title')} at {job.get('company')}")
            
            apply_result = await client.call_tool("apply_to_linkedin_job", {"job_url": job_url})
            apply_content = apply_result[0].text if isinstance(apply_result, list) and apply_result else "{}"
            apply_data = json.loads(apply_content)

            if apply_data.get("status") == "success":
                logger.info(f"Successfully applied to {job_url}")
                applied_count += 1
            elif apply_data.get("status") == "partial":
                logger.warning(f"Partially applied to {job_url}: {apply_data.get('message')}")
                applied_count += 1
            else:
                logger.error(f"Failed to apply to {job_url}: {apply_data.get('message')}")
    
    logger.info(f"Finished. Applied to {applied_count} jobs.")

if __name__ == "__main__":
    asyncio.run(find_and_apply()) 