# Job application tools for the Enhanced MCP Server

from fastmcp import FastMCP, Context
import structlog
from typing import Dict, Any
from sqlalchemy.orm import Session

from ..core.server import get_server
from ..models import AppliedJob, SavedJob, User

logger = structlog.get_logger(__name__)

async def apply_to_linkedin_job(ctx: Context, job_url: str, resume_path: str = '', cover_letter_path: str = '') -> Dict[str, Any]:
    """
    Applies to a LinkedIn job (Easy Apply only).
    """
    server = get_server()
    browser_manager = server.browser_manager
    db_manager = server.database_manager
    session_id = ctx.session_id if ctx else "default"

    if 'linkedin.com/jobs/view/' not in job_url:
        return {"status": "error", "message": "Invalid LinkedIn job URL."}

    try:
        browser_context = await browser_manager.get_session(session_id)
        if not browser_context:
            return {"status": "error", "message": f"Failed to get browser session for {session_id}"}
        
        page = await browser_context.new_page()
        await page.goto(job_url)

        easy_apply_button = await page.query_selector('button[aria-label*="Easy Apply"]')
        if not easy_apply_button:
            return {"status": "error", "message": "Easy Apply not available for this job."}

        await easy_apply_button.click()
        await page.wait_for_selector('.jobs-easy-apply-modal', timeout=5000)

        submit_button = await page.query_selector('button[aria-label="Submit application"]')
        if submit_button:
            await submit_button.click()
            
            # Save to database
            db_gen = db_manager.get_db()
            db: Session = next(db_gen)
            try:
                # Assuming a default user for now
                user = db.query(User).filter(User.username == "default_user").first()
                if not user:
                    user = User(username="default_user")
                    db.add(user)
                    db.commit()
                    db.refresh(user)

                new_application = AppliedJob(
                    user_id=user.id,
                    job_id=job_url.split('/')[-1].split('?')[0],
                    title=await page.title(),
                    company="Unknown", # Placeholder
                    job_url=job_url,
                    application_status='applied'
                )
                db.add(new_application)
                db.commit()
            finally:
                db.close()

            return {"status": "success", "message": "Application submitted successfully."}
        else:
            return {"status": "partial", "message": "Application requires manual completion."}

    except Exception as e:
        logger.error("An error occurred during job application", error=str(e), session_id=session_id)
        return {"status": "error", "message": f"An error occurred: {e}"}
    finally:
        if 'page' in locals() and not page.is_closed():
            await page.close()


async def save_linkedin_job(ctx: Context, job_url: str) -> Dict[str, Any]:
    """Saves a LinkedIn job."""
    server = get_server()
    browser_manager = server.browser_manager
    db_manager = server.database_manager
    session_id = ctx.session_id if ctx else "default"

    if 'linkedin.com/jobs/view/' not in job_url:
        return {"status": "error", "message": "Invalid LinkedIn job URL."}

    try:
        browser_context = await browser_manager.get_session(session_id)
        if not browser_context:
            return {"status": "error", "message": f"Failed to get browser session for {session_id}"}
        
        page = await browser_context.new_page()
        await page.goto(job_url)

        save_button = await page.query_selector('button[aria-label*="Save job"]')
        if not save_button:
            save_button = await page.query_selector('.jobs-save-button')

        if save_button:
            await save_button.click()
            
            # Save to database
            db_gen = db_manager.get_db()
            db: Session = next(db_gen)
            try:
                # Assuming a default user for now
                user = db.query(User).filter(User.username == "default_user").first()
                if not user:
                    user = User(username="default_user")
                    db.add(user)
                    db.commit()
                    db.refresh(user)

                new_saved_job = SavedJob(
                    user_id=user.id,
                    job_id=job_url.split('/')[-1].split('?')[0],
                    title=await page.title(),
                    company="Unknown", # Placeholder
                    job_url=job_url,
                )
                db.add(new_saved_job)
                db.commit()
            finally:
                db.close()

            return {"status": "success", "message": "Job saved successfully."}
        else:
            return {"status": "error", "message": "Could not find save button."}

    except Exception as e:
        logger.error("An error occurred during job saving", error=str(e), session_id=session_id)
        return {"status": "error", "message": f"An error occurred: {e}"}
    finally:
        if 'page' in locals() and not page.is_closed():
            await page.close()


def register_tools(mcp: FastMCP):
    mcp.tool()(apply_to_linkedin_job)
    mcp.tool()(save_linkedin_job)