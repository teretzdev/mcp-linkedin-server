import asyncio
from ai_job_automation import AIJobAutomation

async def find_and_apply_to_jobs():
    """
    Finds jobs and then applies to a specific number of them.
    """
    automation = AIJobAutomation()
    # First, run the recon phase to find jobs
    await automation.run_recon_phase(query="Software Engineer", count=10)
    # Then, run the application phase
    await automation.run_application_phase(max_applications=3)

if __name__ == "__main__":
    asyncio.run(find_and_apply_to_jobs()) 