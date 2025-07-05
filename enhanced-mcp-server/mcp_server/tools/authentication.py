# Authentication tools for the Enhanced MCP Server

from fastmcp import FastMCP, Context
import os
import structlog
from typing import Dict, Any

from ..core.server import get_server

logger = structlog.get_logger(__name__)

async def login_linkedin_secure(ctx: Context) -> Dict[str, Any]:
    """
    Logs into LinkedIn using credentials from environment variables.
    """
    server = get_server()
    browser_manager = server.browser_manager
    session_id = ctx.session_id if ctx else "default"

    try:
        username = os.getenv("LINKEDIN_USERNAME")
        password = os.getenv("LINKEDIN_PASSWORD")

        if not username or not password:
            return {"status": "error", "message": "LinkedIn credentials not found in environment variables."}

        browser_context = await browser_manager.get_session(session_id)
        if not browser_context:
            return {"status": "error", "message": f"Failed to get browser session for {session_id}"}
        page = await browser_context.new_page()
        
        await page.goto("https://www.linkedin.com/login")

        await page.fill("#username", username)
        await page.fill("#password", password)
        await page.click('button[type="submit"]')

        await page.wait_for_url("**/feed/**", timeout=15000)

        if "feed" in page.url:
            logger.info("Login successful", session_id=session_id)
            await browser_manager.cleanup_session(session_id) # saves cookies
            return {"status": "success", "message": "Login successful."}
        else:
            logger.warning("Login failed", session_id=session_id)
            return {"status": "error", "message": "Login failed. Please check your credentials."}

    except Exception as e:
        logger.error("An error occurred during login", error=str(e), session_id=session_id)
        return {"status": "error", "message": f"An error occurred: {e}"}


def register_tools(mcp: FastMCP):
    mcp.tool()(login_linkedin_secure)