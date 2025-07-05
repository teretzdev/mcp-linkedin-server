import pytest
from unittest.mock import AsyncMock, patch

from mcp_server.tools.authentication import login_linkedin_secure
from mcp_server.core.server import LinkedInMCPServer


@pytest.mark.asyncio
async def test_login_linkedin_secure(mocker):
    """
    Test the secure LinkedIn login tool.
    """
    # Create a mock server instance
    mock_server = AsyncMock(spec=LinkedInMCPServer)
    
    # Mock the get_server call to return our mock server
    mocker.patch('mcp_server.tools.authentication.get_server', return_value=mock_server)
    
    # Mock environment variables
    mocker.patch('os.getenv', side_effect=lambda key: "test_user" if key == "LINKEDIN_USERNAME" else "test_password")

    # Mock the browser manager and its methods
    mock_browser_manager = AsyncMock()
    mock_context = AsyncMock()
    mock_page = AsyncMock()
    
    mock_browser_manager.get_session.return_value = mock_context
    mock_context.new_page.return_value = mock_page
    mock_page.url = "https://www.linkedin.com/feed/"

    # Assign the mock browser manager to the mock server instance
    mock_server.browser_manager = mock_browser_manager
    
    # Create a mock context
    mock_ctx = AsyncMock()
    mock_ctx.session_id = "test_session"
    
    result = await login_linkedin_secure(mock_ctx)

    assert result["status"] == "success"
    assert result["message"] == "Login successful."
    
    mock_browser_manager.get_session.assert_called_with("test_session")
    mock_page.goto.assert_called_with("https://www.linkedin.com/login")
    mock_page.fill.assert_any_call("#username", "test_user")
    mock_page.fill.assert_any_call("#password", "test_password")
    mock_page.click.assert_called_with('button[type="submit"]')
    mock_page.wait_for_url.assert_called_with("**/feed/**", timeout=15000)