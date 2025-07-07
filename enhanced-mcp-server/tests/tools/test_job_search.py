import pytest
from unittest.mock import AsyncMock, patch

from mcp_server.core.server import LinkedInMCPServer
from mcp_server.tools.job_search import search_linkedin_jobs

@pytest.mark.asyncio
async def test_search_linkedin_jobs(mocker):
    """
    Test the LinkedIn job search tool.
    """
    # Create a mock server instance
    mock_server = AsyncMock(spec=LinkedInMCPServer)
    
    # Mock the get_server call to return our mock server
    mocker.patch('mcp_server.tools.job_search.get_server', return_value=mock_server)

    # Mock the browser manager and its methods
    mock_browser_manager = AsyncMock()
    mock_context = AsyncMock()
    mock_page = AsyncMock()
    
    mock_browser_manager.get_session.return_value = mock_context
    mock_context.new_page.return_value = mock_page
    
    # Mock the page.evaluate to return some dummy job data
    mock_page.evaluate.return_value = [
        {"title": "Software Engineer", "company": "TestCo", "location": "Testville"}
    ]

    # Assign the mock browser manager to the mock server instance
    mock_server.browser_manager = mock_browser_manager
    
    # Create a mock context
    mock_ctx = AsyncMock()
    mock_ctx.session_id = "test_session"
    
    result = await search_linkedin_jobs(mock_ctx, query="Python", location="Remote")

    assert result["status"] == "success"
    assert len(result["jobs"]) == 1
    assert result["jobs"][0]["title"] == "Software Engineer"
    
    mock_browser_manager.get_session.assert_called_with("test_session")
    mock_page.goto.assert_called_once()
    mock_page.wait_for_selector.assert_called_with('.jobs-search-results__list-item', timeout=10000)
    mock_page.evaluate.assert_called_once()
    mock_page.close.assert_called_once()