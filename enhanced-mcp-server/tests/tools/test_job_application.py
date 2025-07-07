import pytest
from unittest.mock import AsyncMock, patch
from sqlalchemy.orm import Session

from mcp_server.core.server import LinkedInMCPServer
from mcp_server.tools.job_application import apply_to_linkedin_job, save_linkedin_job

@pytest.mark.asyncio
async def test_apply_to_linkedin_job(mocker):
    mock_server = AsyncMock(spec=LinkedInMCPServer)
    mocker.patch('mcp_server.tools.job_application.get_server', return_value=mock_server)

    mock_browser_manager = AsyncMock()
    mock_context = AsyncMock()
    mock_page = AsyncMock()
    mock_browser_manager.get_session.return_value = mock_context
    mock_context.new_page.return_value = mock_page
    mock_page.query_selector.return_value = AsyncMock() # For Easy Apply button
    mock_page.title.return_value = "Test Job"
    mock_server.browser_manager = mock_browser_manager

    mock_db_manager = AsyncMock()
    mock_db_session = AsyncMock(spec=Session)

    def db_gen_mock():
        yield mock_db_session

    mock_db_manager.get_db = db_gen_mock
    mock_server.database_manager = mock_db_manager

    mock_ctx = AsyncMock()
    mock_ctx.session_id = "test_session"

    result = await apply_to_linkedin_job(mock_ctx, job_url="https://www.linkedin.com/jobs/view/123")

    assert result["status"] == "success"
    mock_db_session.add.assert_called_once()
    mock_db_session.commit.assert_called_once()

@pytest.mark.asyncio
async def test_save_linkedin_job(mocker):
    mock_server = AsyncMock(spec=LinkedInMCPServer)
    mocker.patch('mcp_server.tools.job_application.get_server', return_value=mock_server)

    mock_browser_manager = AsyncMock()
    mock_context = AsyncMock()
    mock_page = AsyncMock()
    mock_browser_manager.get_session.return_value = mock_context
    mock_context.new_page.return_value = mock_page
    mock_page.query_selector.return_value = AsyncMock() # For Save button
    mock_page.title.return_value = "Test Job"
    mock_server.browser_manager = mock_browser_manager

    mock_db_manager = AsyncMock()
    mock_db_session = AsyncMock(spec=Session)
    
    def db_gen_mock():
        yield mock_db_session

    mock_db_manager.get_db = db_gen_mock
    mock_server.database_manager = mock_db_manager

    mock_ctx = AsyncMock()
    mock_ctx.session_id = "test_session"

    result = await save_linkedin_job(mock_ctx, job_url="https://www.linkedin.com/jobs/view/123")

    assert result["status"] == "success"
    mock_db_session.add.assert_called_once()
    mock_db_session.commit.assert_called_once()

def register_tools(mcp):
    pass