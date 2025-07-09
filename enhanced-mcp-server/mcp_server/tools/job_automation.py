import asyncio
import json
import os
from pathlib import Path
from mcp_server.core.browser_manager import BrowserManager
from mcp_server.core.auth_manager import AuthManager
from mcp_server.core.error_handler import ErrorHandler
import logging

logger = logging.getLogger("JobAutomation")

# Correct the path to be relative to this file's location
PREFERENCES_PATH = Path(__file__).resolve().parent.parent.parent.parent / "job_preferences.json"
RESUME_PATH = Path(__file__).resolve().parent.parent.parent.parent / "Resume.pdf"
APPLIED_JOBS_PATH = Path(__file__).resolve().parent.parent.parent.parent / "applied_jobs.json"

class JobAutomation:
    def __init__(self, browser_manager: BrowserManager, auth_manager: AuthManager, error_handler: ErrorHandler):
        self.browser_manager = browser_manager
        self.auth_manager = auth_manager
        self.error_handler = error_handler
        self.preferences = self.load_preferences()
        self.session_id = None

    def load_preferences(self):
        try:
            with open(PREFERENCES_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load job preferences: {e}")
            return {}

    async def run_job_automation(self):
        try:
            # The browser_manager now handles login on session creation.
            # We just need to get a session.
            logger.info("Acquiring browser session for job automation...")
            self.session_id = self.auth_manager.generate_session_id()
            context = await self.browser_manager.get_session(self.session_id)
            
            if not context:
                logger.error("Could not acquire a valid browser context. Aborting automation.")
                return

            page = await context.new_page()
            
            # Build job search URL from preferences
            keywords = self.preferences.get("keywords", ["developer"])
            location = self.preferences.get("location", "Remote")
            search_query = "%20".join(keywords)
            url = f"https://www.linkedin.com/jobs/search/?keywords={search_query}&location={location}"
            await page.goto(url)
            logger.info(f"Navigated to job search page: {url}")
            await asyncio.sleep(3)

            # --- Start of Transplanted Logic ---
            logger.info("Scanning for job cards on the page...")
            job_cards = await page.query_selector_all('div.job-card-container, li.jobs-search-results__list-item')
            
            if not job_cards:
                logger.info("No job cards found on the page.")
                return

            applied_count = 0
            # Load existing applied jobs to avoid duplicates
            if APPLIED_JOBS_PATH.exists():
                with open(APPLIED_JOBS_PATH, 'r', encoding='utf-8') as f:
                    try:
                        applied_jobs_list = json.load(f)
                    except json.JSONDecodeError:
                        applied_jobs_list = []
            else:
                applied_jobs_list = []
            
            applied_urls = {job.get('job_url') for job in applied_jobs_list}

            for idx, card in enumerate(job_cards):
                job_info = {}
                try:
                    title_elem = await card.query_selector('h3, .job-card-list__title, .job-card-container__link')
                    job_link_elem = await card.query_selector('a.job-card-container__link, a.job-card-list__title')
                    
                    if title_elem:
                        job_info['title'] = await title_elem.inner_text()
                    if job_link_elem:
                        job_info['job_url'] = await job_link_elem.get_attribute('href')
                        # Make URL absolute
                        if job_info['job_url'].startswith('/'):
                            job_info['job_url'] = f"https://www.linkedin.com{job_info['job_url']}"

                    if job_info.get('job_url') in applied_urls:
                        logger.info(f"Skipping already applied job: {job_info.get('title')}")
                        continue
                    
                    logger.info(f"Processing Job #{idx+1}: {job_info.get('title')}")

                    easy_apply_btn = await card.query_selector('button:has-text("Easy Apply")')
                    if not easy_apply_btn:
                        logger.info(f"  No Easy Apply button for this job.")
                        continue
                    
                    await easy_apply_btn.click()
                    logger.info(f"  Clicked Easy Apply for: {job_info.get('title')}")
                    await page.wait_for_timeout(2000) # Wait for modal

                    modal = await page.query_selector('[role="dialog"]:has-text("Easy Apply")')
                    if modal:
                        submit_button = await modal.query_selector('button:has-text("Submit application")')
                        if submit_button:
                            # This is the critical step: actually submitting the application.
                            await submit_button.click()
                            logger.info(f"  Clicked the final 'Submit application' button for: {job_info.get('title')}")
                            
                            # Wait for the confirmation message to appear before logging success
                            try:
                                await page.wait_for_selector('text=Your application was sent', timeout=5000)
                                logger.info(f"  Successfully applied to: {job_info.get('title')}")
                                job_info['status'] = 'applied'
                                job_info['applied_at'] = asyncio.get_event_loop().time()
                                applied_jobs_list.append(job_info)
                                applied_urls.add(job_info['job_url'])
                                applied_count += 1
                            except Exception:
                                logger.warning(f"  Application submitted, but confirmation not found for: {job_info.get('title')}")

                        # Close the modal to continue, whether submitted or not
                        close_button = await modal.query_selector('button[aria-label="Dismiss"], button[aria-label="Close"]')
                        if close_button:
                            await close_button.click()
                except Exception as e:
                    logger.error(f"Error processing job card #{idx+1}: {e}", exc_info=True)

            if applied_count > 0:
                logger.info(f"Applied to {applied_count} new jobs. Saving results...")
                with open(APPLIED_JOBS_PATH, 'w', encoding='utf-8') as f:
                    json.dump(applied_jobs_list, f, indent=2)
                logger.info("Results saved to applied_jobs.json.")
            # --- End of Transplanted Logic ---

        except Exception as e:
            logger.error(f"Error in job automation: {e}", exc_info=True)
            self.error_handler.handle_error(e) 