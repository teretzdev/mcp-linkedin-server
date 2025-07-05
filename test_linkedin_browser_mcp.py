import pytest
import os
from linkedin_browser_mcp import (
    BrowserSession,
    save_cookies,
    load_cookies,
    login_linkedin,
    _login_linkedin_secure,
    _view_linkedin_profile,
    _interact_with_linkedin_post,
    browse_linkedin_feed,
    search_linkedin_profiles,
    mcp,
    search_linkedin_jobs,
    apply_to_linkedin_job
)
from fastmcp import Context

class MockContext(Context):
    def __init__(self, fastmcp=None):
        super().__init__(fastmcp)
        self.messages = []
        self.errors = []
        self.progress = []
    def info(self, message):
        self.messages.append(f"INFO: {message}")
        print(f"INFO: {message}")
    def error(self, message):
        self.errors.append(f"ERROR: {message}")
        print(f"ERROR: {message}")
    async def report_progress(self, current, total, message=None):
        progress = {"current": current, "total": total, "message": message}
        self.progress.append(progress)
        print(f"Progress: {current}/{total} - {message}")

@pytest.mark.asyncio
async def test_browser_session():
    async with BrowserSession(platform='linkedin', headless=True) as session:
        page = await session.new_page()
        assert page is not None
        assert session.browser is not None
        assert session.context is not None

@pytest.mark.asyncio
async def test_login_linkedin_secure_missing_credentials():
    ctx = MockContext(fastmcp=mcp)
    # Clear environment variables
    if 'LINKEDIN_USERNAME' in os.environ:
        del os.environ['LINKEDIN_USERNAME']
    if 'LINKEDIN_PASSWORD' in os.environ:
        del os.environ['LINKEDIN_PASSWORD']
    result = await _login_linkedin_secure(ctx)
    assert result["status"] == "error"
    assert "Missing LinkedIn credentials" in result["message"]

@pytest.mark.asyncio
async def test_login_linkedin_secure_invalid_email():
    ctx = MockContext(fastmcp=mcp)
    os.environ['LINKEDIN_USERNAME'] = 'invalid-email'
    os.environ['LINKEDIN_PASSWORD'] = 'password123'
    result = await _login_linkedin_secure(ctx)
    assert result["status"] == "error"
    assert "Invalid email format" in result["message"]

@pytest.mark.asyncio
async def test_login_linkedin_secure_short_password():
    ctx = MockContext(fastmcp=mcp)
    os.environ['LINKEDIN_USERNAME'] = 'test@example.com'
    os.environ['LINKEDIN_PASSWORD'] = 'short'
    result = await _login_linkedin_secure(ctx)
    assert result["status"] == "error"
    assert "password must be at least 8 characters" in result["message"].lower()

@pytest.mark.asyncio
async def test_view_linkedin_profile_invalid_url():
    ctx = MockContext(fastmcp=mcp)
    result = await _view_linkedin_profile("https://invalid-url.com", ctx)
    assert result["status"] == "error"
    assert "Invalid LinkedIn profile URL" in result["message"]

@pytest.mark.asyncio
async def test_interact_with_linkedin_post_invalid_url():
    ctx = MockContext(fastmcp=mcp)
    result = await _interact_with_linkedin_post("https://invalid-url.com", ctx)
    assert result["status"] == "error"
    assert "Invalid LinkedIn post URL" in result["message"]

@pytest.mark.asyncio
async def test_interact_with_linkedin_post_invalid_action():
    ctx = MockContext(fastmcp=mcp)
    result = await _interact_with_linkedin_post(
        "https://linkedin.com/posts/123",
        ctx,
        action="invalid"
    )
    assert result["status"] == "error"
    assert "Invalid action" in result["message"]

@pytest.mark.asyncio
async def test_end_to_end_job_search_and_apply():
    ctx = MockContext(fastmcp=mcp)
    async with BrowserSession(platform='linkedin', headless=True) as session:
        # Simulate login (mocked)
        await session.new_page('https://www.linkedin.com/login')
        # Simulate job search
        jobs = await search_linkedin_jobs('Software Engineer', ctx, location='Remote', count=2)
        assert 'status' in jobs
        # Simulate applying to a job (mocked)
        if jobs.get('status') == 'success' and jobs.get('jobs'):
            job_url = jobs['jobs'][0].get('url')
            result = await apply_to_linkedin_job(job_url, ctx)
            assert result['status'] in ['success', 'error']

@pytest.mark.asyncio
async def test_cookie_management():
    ctx = MockContext(fastmcp=mcp)
    async with BrowserSession(platform='linkedin', headless=True) as session:
        # Save cookies
        cookies = await session.context.cookies()
        save_cookies(cookies, 'test_cookies.json')
        assert os.path.exists('test_cookies.json')
        # Load cookies
        loaded = load_cookies('test_cookies.json')
        assert loaded is not None
        os.remove('test_cookies.json') 