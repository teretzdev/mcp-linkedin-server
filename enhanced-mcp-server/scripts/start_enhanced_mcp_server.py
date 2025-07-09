#!/usr/bin/env python3
"""
Enhanced MCP Server Startup Script
Starts the enhanced LinkedIn Job Hunter MCP server with new directory structure
"""

import asyncio
import sys
import os
from pathlib import Path
import uvicorn
import logging

# Add the project root to the Python path to ensure correct module resolution.
# This makes `from mcp_server...` imports work correctly from anywhere.
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from mcp_server.core.server import LinkedInMCPServer, initialize_server, cleanup_server
from mcp_server.tools.job_automation import JobAutomation
from mcp_server.core.config import load_config
from starlette.responses import JSONResponse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def main():
    """
    Initializes and runs the Enhanced MCP FastAPI server.

    This function sets up the server, creates the necessary components like the
    BrowserManager and JobAutomation tools, and defines an API endpoint
    to trigger the job automation process.
    """
    server: LinkedInMCPServer = None
    try:
        # Load server configuration from file
        config = load_config()
        
        # Initialize the main server components
        server = await initialize_server(config)
        logger.info("Enhanced MCP Server initialized successfully.")
        
        # Create an instance of the JobAutomation tool, providing it with the
        # server's browser manager.
        job_automation = JobAutomation(
            browser_manager=server.browser_manager,
            auth_manager=server.auth_manager,
            error_handler=server.error_handler
        )
        logger.info("JobAutomation tool initialized.")

        # Define an API endpoint for health checks
        @server.app.get("/health")
        async def health_check_endpoint():
            """A simple endpoint to confirm the server is running."""
            return {"status": "ok"}

        # Define an API endpoint to trigger the job automation
        @server.app.post("/run-automation")
        async def run_automation_endpoint():
            """API endpoint to start the job automation process."""
            logger.info("Received request to run job automation via /run-automation endpoint.")
            try:
                # IMPORTANT: We are NOT awaiting this. This starts the task in the background.
                # The endpoint returns immediately, allowing the UI to not be blocked.
                # In a real app, we'd return a task ID to check status.
                asyncio.create_task(job_automation.run_job_automation())
                
                return JSONResponse(
                    status_code=202, # 202 Accepted: The request has been accepted for processing
                    content={"status": "processing", "message": "Job automation process started in the background."}
                )
            except Exception as e:
                logger.error(f"An error occurred when trying to start job automation: {e}", exc_info=True)
                return JSONResponse(
                    status_code=500,
                    content={"status": "error", "message": f"An error occurred: {e}"}
                )

        # Get server host and port from config, with defaults
        server_config = config.get('server', {})
        host = server_config.get('host', '127.0.0.1')
        port = server_config.get('port', 8101)

        logger.info(f"Starting FastAPI server at http://{host}:{port}")
        logger.info(f"Health check is available at http://{host}:{port}/health (GET)")
        logger.info(f"To trigger job automation, send a POST request to http://{host}:{port}/run-automation")

        # Start the Uvicorn server to serve the FastAPI application
        uvicorn_config = uvicorn.Config(server.app, host=host, port=port, log_level="info")
        uvicorn_server = uvicorn.Server(uvicorn_config)
        await uvicorn_server.serve()

    except Exception as e:
        logger.error(f"A critical error occurred in the main server loop: {e}", exc_info=True)
    finally:
        # Ensure cleanup runs even if the server crashes
        if server:
            await cleanup_server(server)
            logger.info("Server cleanup has been completed.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Server stopped by user (Ctrl+C).")
    except Exception as e:
        logger.critical(f"Unhandled exception at the top level: {e}", exc_info=True)
        sys.exit(1)