import pytest
import asyncio
from pathlib import Path
import sys

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from mcp_server.core.server import LinkedInMCPServer

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def mcp_server_instance():
    """Fixture to create and clean up a LinkedInMCPServer instance."""
    server = LinkedInMCPServer()
    await server.initialize()
    yield server
    await server.cleanup()