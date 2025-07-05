#!/usr/bin/env python3
"""
Enhanced MCP Server Startup Script
Starts the enhanced LinkedIn Job Hunter MCP server with new directory structure
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the enhanced server to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Set shared paths as environment variables
shared_root = project_root.parent / 'shared'
os.environ['SHARED_DATABASE_PATH'] = str(shared_root / 'database')
os.environ['SHARED_SESSIONS_PATH'] = str(shared_root / 'sessions')
os.environ['SHARED_LOGS_PATH'] = str(shared_root / 'logs')
os.environ['SHARED_CONFIG_PATH'] = str(shared_root / 'config')

# Ensure shared directories exist
shared_root.mkdir(exist_ok=True)
(shared_root / 'database').mkdir(exist_ok=True)
(shared_root / 'sessions').mkdir(exist_ok=True)
(shared_root / 'logs').mkdir(exist_ok=True)
(shared_root / 'config').mkdir(exist_ok=True)

from mcp_server.core.server import LinkedInMCPServer, initialize_server, cleanup_server
import logging

# Configure basic logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

async def main():
    """Main startup function"""
    try:
        logger.info("Starting Enhanced LinkedIn MCP Server...")
        logger.info(f"Project root: {project_root}")
        logger.info(f"Shared root: {shared_root}")
        
        # Initialize the server
        success = await initialize_server()
        if not success:
            logger.error("Failed to initialize server")
            return 1
        
        # Get the server instance
        server = LinkedInMCPServer()
        
        # Get the underlying FastMCP server
        mcp_server = server.get_server()
        
        logger.info("Enhanced MCP Server started successfully")
        logger.info(f"Server version: {server.__class__.__module__}")
        logger.info(f"Active sessions: {len(server._sessions)}")
        logger.info(f"Shared database: {os.environ.get('SHARED_DATABASE_PATH')}")
        logger.info(f"Shared sessions: {os.environ.get('SHARED_SESSIONS_PATH')}")
        logger.info(f"Shared logs: {os.environ.get('SHARED_LOGS_PATH')}")
        
        # Keep the server running
        try:
            # This would normally start the MCP server
            await mcp_server.run(transport='stdio')
            
        except KeyboardInterrupt:
            logger.info("Received shutdown signal")
            
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        return 1
    
    finally:
        # Cleanup
        await cleanup_server()
        logger.info("Server shutdown complete")
    
    return 0

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1) 