from playwright.async_api import async_playwright
from playwright_stealth import stealth_async
import asyncio
import os
import json
import logging
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from cryptography.fernet import Fernet
import time
import sys
from pathlib import Path
from datetime import datetime, timedelta
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from legacy.database.models import Base, ScrapedJob, User
import argparse
from urllib.parse import urlencode

# --- Setup ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stderr)]
)
logger = logging.getLogger(__name__)

env_path = Path(__file__).parent / '.env'
if env_path.exists():
    load_dotenv(env_path)

# --- Database Setup ---
DATABASE_URL = "sqlite:///linkedin_jobs.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)

# --- Constants ---
BASE_URL = "https://www.linkedin.com"
JOB_SEARCH_URL_TEMPLATE = "https://www.linkedin.com/jobs/search/?keywords={keywords}&location={location}"
SELECTORS = {
    "job_list": 'div.job-card-container',
    "title": 'a.job-card-list__title--link',
    "company": 'div.artdeco-entity-lockup__subtitle span',
    "location": 'ul.job-card-container__metadata-wrapper > li:first-child',
    "url": 'a.job-card-list__title--link',
    "easy_apply": 'li.job-card-container__footer-item:has-text("Easy Apply")'
}

# --- Helper Classes & Functions ---

class DummyContext:
    """A dummy context for logging to replace the MCP context."""
    def info(self, msg):
        logger.info(msg)
    def error(self, msg):
        logger.error(msg)
    def warning(self, msg):
        logger.warning(msg)

def report_progress(ctx, current, total, message):
    """A dummy progress reporting function."""
    progress = (current / total) * 100
    ctx.info(f"[PROGRESS] {progress:.0f}%: {message}")

def save_jobs_to_db(jobs: list, db_session):
    """Saves a list of jobs to the database."""
    for job_data in jobs:
        save_job_to_db(job_data, db_session)

def save_job_to_db(job_data: dict, db_session):
    """Saves a single job to the database, avoiding duplicates."""
    logger.debug(f"Attempting to save job: {job_data.get('title')}")
    try:
        # Check if job already exists
        existing_job = db_session.query(ScrapedJob).filter_by(job_id=job_data.get("job_id")).first()
        if existing_job:
            logger.debug(f"Job '{job_data.get('title')}' already exists in DB. Skipping.")
            return None

        # Create new job entry
        new_job = ScrapedJob(
            job_id=job_data.get("job_id"),
            title=job_data.get("title"),
            company=job_data.get("company"),
            location=job_data.get("location"),
            job_url=job_data.get("url"),
            description=job_data.get("description", ""), # Add default empty description
            easy_apply=job_data.get("easy_apply"),
            scraped_at=datetime.utcnow(),
            user_id=1 # Default to user 1 for now
        )
        db_session.add(new_job)
        db_session.commit()
        logger.info(f"Successfully saved new job to DB: {new_job.title} (ID: {new_job.job_id})")
        return new_job
    except Exception as e:
        db_session.rollback()
        logger.error(f"Failed to save job '{job_data.get('title')}' to DB. Error: {e}", exc_info=True)
        return None

async def login_to_linkedin(page):
    email = os.getenv("LINKEDIN_EMAIL") or os.getenv("LINKEDIN_USERNAME")
    password = os.getenv("LINKEDIN_PASSWORD")
    if not email or not password:
        logger.error("[LOGIN_FATAL] LinkedIn credentials not found in environment variables. Please set LINKEDIN_EMAIL/USERNAME and LINKEDIN_PASSWORD in your .env file.")
        return False
    logger.info("Attempting automated login...")
    await page.goto("https://www.linkedin.com/login")
    await page.fill('input[name="session_key"]', email)
    await page.fill('input[name="session_password"]', password)
    await page.click('button[type="submit"]')
    await page.wait_for_timeout(5000)
    if "feed" in page.url:
        logger.info("Automated login successful!")
        return True
    else:
        logger.error("[LOGIN_FATAL] Automated login failed. Check credentials or for LinkedIn blocks.")
        return False

async def search_and_scrape_jobs(page, search_criteria):
    """
    Searches for jobs on LinkedIn based on search_criteria and scrapes the results.
    """
    keywords = "+".join(search_criteria["keywords"])
    location = search_criteria["job_location"]
    url = JOB_SEARCH_URL_TEMPLATE.format(keywords=keywords, location=location)
    
    logger.info(f"Navigating to job search URL: {url}")
    await page.goto(url, wait_until="domcontentloaded")
    await page.wait_for_timeout(5000)  # Wait for dynamic content to load

    logger.info("Waiting for job listings to appear...")
    try:
        await page.wait_for_selector(SELECTORS["job_list"], timeout=30000)
        logger.info("Job listings found.")
    except Exception as e:
        logger.error(f"Timed out waiting for job listings: {e}")
        await page.screenshot(path='job_search_debug_timeout.png')
        content = await page.content()
        with open('job_search_debug_timeout.html', 'w', encoding='utf-8') as f:
            f.write(content)
        return []

    jobs = []
    job_cards = await page.query_selector_all(SELECTORS["job_list"])
    logger.info(f"Found {len(job_cards)} job cards on the page.")

    for job_card in job_cards[:search_criteria["num_jobs"]]:
        try:
            job_id = await job_card.get_attribute("data-job-id")
            title_element = await job_card.query_selector(SELECTORS["title"])
            company_element = await job_card.query_selector(SELECTORS["company"])
            location_element = await job_card.query_selector(SELECTORS["location"])
            easy_apply_element = await job_card.query_selector(SELECTORS["easy_apply"])

            title = await title_element.inner_text() if title_element else "N/A"
            company = await company_element.inner_text() if company_element else "N/A"
            location = await location_element.inner_text() if location_element else "N/A"
            url = await title_element.get_attribute("href") if title_element else "N/A"
            easy_apply = True if easy_apply_element else False
            
            if not url.startswith("http"):
                url = BASE_URL + url

            job_data = {
                "job_id": job_id,
                "title": title.strip(),
                "company": company.strip(),
                "location": location.strip(),
                "url": url,
                "easy_apply": easy_apply,
            }
            jobs.append(job_data)
            logger.info(f"Scraped job: {title} at {company}")

        except Exception as e:
            logger.error(f"Error scraping a job card: {e}")
            # Optionally, save the HTML of the problematic card for debugging
            # card_html = await job_card.inner_html()
            # with open(f"error_card_{time.time()}.html", "w", encoding='utf-8') as f:
            #     f.write(card_html)
    
    logger.info(f"Scraped {len(jobs)} jobs.")
    
    if jobs:
        logger.info(f"Sample job scraped: {json.dumps(jobs[0], indent=2)}")

    return jobs

async def main(args):
    """
    Main function to run the LinkedIn job scraper.
    """
    db_session = SessionLocal()
    try:
        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch(headless=args.headless)
            context = await browser.new_context()
            page = await context.new_page()
            await stealth_async(page)

            logged_in = await login_to_linkedin(page)
            if not logged_in:
                logger.error("LinkedIn login failed. Exiting.")
                return

            search_criteria = {
                "keywords": args.query.split(','),
                "job_location": args.location,
                "num_jobs": args.count
            }
            scraped_jobs = await search_and_scrape_jobs(page, search_criteria)

            if scraped_jobs:
                logger.info(f"Successfully scraped {len(scraped_jobs)} jobs.")
                save_jobs_to_db(scraped_jobs, db_session)
                logger.info("Jobs saved to database.")
            else:
                logger.warning("No jobs were scraped.")

    except Exception as e:
        logger.exception(f"An unexpected error occurred: {e}")
    finally:
        db_session.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="LinkedIn Job Scraper")
    parser.add_argument("--query", type=str, required=True, help="Job search query.")
    parser.add_argument("--location", type=str, default="", help="Job location.")
    parser.add_argument("--count", type=int, default=10, help="Number of jobs to scrape.")
    parser.add_argument('--headless', action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument('--source', type=str, default='manual', help='Source of the scraping request (for compatibility, ignored).')
    args = parser.parse_args()
    
    logger.info(f"Scraper started with args: {sys.argv}")
    try:
        logger.info(f"Navigating to LinkedIn login page...")
        asyncio.run(main(args))
    except Exception as e:
        logger.exception(f"Scraper failed: {e}")
        sys.exit(1)
    logger.info("Scraper completed successfully.")
    sys.exit(0)