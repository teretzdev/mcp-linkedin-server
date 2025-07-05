import pytest
from unittest.mock import AsyncMock, patch
from sqlalchemy.orm import Session

from mcp_server.core.server import LinkedInMCPServer
from mcp_server.tools.analytics import get_application_analytics
from mcp_server.models import AppliedJob

@pytest.mark.asyncio
async def test_get_application_analytics(mocker):
    """
    Test the application analytics tool.
    """
    mock_server = AsyncMock(spec=LinkedInMCPServer)
    mocker.patch('mcp_server.tools.analytics.get_server', return_value=mock_server)

    mock_db_manager = AsyncMock()
    mock_db_session = AsyncMock(spec=Session)

    # Mock database query results
    mock_query = mock_db_session.query.return_value
    mock_query.count.return_value = 2
    mock_query.group_by.return_value.all.return_value = [('applied', 1), ('interview', 1)]

    def db_gen_mock():
        yield mock_db_session

    mock_db_manager.get_db = db_gen_mock
    mock_server.database_manager = mock_db_manager

    mock_ctx = AsyncMock()
    
    result = await get_application_analytics(mock_ctx)

    assert result["status"] == "success"
    analytics = result["analytics"]
    assert analytics["total_applications"] == 2
    assert analytics["status_counts"] == {'applied': 1, 'interview': 1}
    assert analytics["success_rate"] == 50.0