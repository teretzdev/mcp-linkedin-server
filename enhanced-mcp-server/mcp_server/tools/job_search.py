# Job search tools for the Enhanced MCP Server

from fastmcp import FastMCP, Context
import structlog
from typing import Dict, Any, List

from ..core.server import get_server

logger = structlog.get_logger(__name__)

async def search_linkedin_jobs(ctx: Context, query: str, location: str = '', count: int = 10) -> Dict[str, Any]:
    """
    Searches for LinkedIn jobs.
    """
    server = get_server()
    browser_manager = server.browser_manager
    session_id = ctx.session_id if ctx else "default"

    try:
        browser_context = await browser_manager.get_session(session_id)
        if not browser_context:
            return {"status": "error", "message": f"Failed to get browser session for {session_id}"}
        
        page = await browser_context.new_page()

        search_url = f'https://www.linkedin.com/jobs/search/?keywords={query.replace(" ", "%20")}'
        if location:
            search_url += f'&location={location.replace(" ", "%20")}'
        
        await page.goto(search_url)

        await page.wait_for_selector('.jobs-search-results__list-item', timeout=10000)

        jobs = await page.evaluate('''(count) => {
            const results = [];
            const jobCards = document.querySelectorAll('.jobs-search-results__list-item');
            for (let i = 0; i < Math.min(jobCards.length, count); i++) {
                const card = jobCards[i];
                try {
                    const job = {
                        title: card.querySelector('.base-search-card__title')?.innerText?.trim() || '',
                        company: card.querySelector('.base-search-card__subtitle')?.innerText?.trim() || '',
                        location: card.querySelector('.job-search-card__location')?.innerText?.trim() || '',
                        posted: card.querySelector('time')?.getAttribute('datetime') || '',
                        jobUrl: card.querySelector('a.base-card__full-link')?.href || '',
                        descriptionSnippet: card.querySelector('.job-search-card__snippet')?.innerText?.trim() || ''
                    };
                    results.push(job);
                } catch (e) {
                    // skip
                }
            }
            return results;
        }''', count)
        
        await page.close()

        return {
            "status": "success",
            "jobs": jobs,
            "count": len(jobs)
        }

    except Exception as e:
        logger.error("An error occurred during job search", error=str(e), session_id=session_id)
        return {"status": "error", "message": f"An error occurred: {e}"}

def register_tools(mcp: FastMCP):
    mcp.tool()(search_linkedin_jobs)