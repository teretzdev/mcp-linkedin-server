#!/usr/bin/env python3
"""
MCP Client for LinkedIn Job Hunter
Provides reliable communication with the MCP server
"""

import asyncio
import json
import logging
import os
import subprocess
import sys
from typing import Dict, Any, Optional, List
from pathlib import Path
import aiohttp
import time
from asyncio.subprocess import Process

logger = logging.getLogger(__name__)

class MCPClient:
    """Client for communicating with the MCP server"""
    
    def __init__(self, server_script: str = "linkedin_browser_mcp.py"):
        self.server_script = server_script
        self.process: Optional[Process] = None
        self.initialized = False
        self.request_id = 1
        self.connection_timeout = 30
        self.max_retries = 3
        
    async def start_server(self) -> bool:
        """Start the MCP server process"""
        try:
            if self.process and self.process.returncode is None:
                logger.info("MCP server already running")
                return True
            
            logger.info(f"Starting MCP server: {self.server_script}")
            
            # Start the server process
            self.process = await asyncio.create_subprocess_exec(
                sys.executable, self.server_script,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # Wait a moment for the server to start
            await asyncio.sleep(2)
            
            # Initialize the connection
            if await self._initialize():
                logger.info("MCP server started and initialized successfully")
                return True
            else:
                logger.error("Failed to initialize MCP server")
                await self.stop_server()
                return False
                
        except Exception as e:
            logger.error(f"Failed to start MCP server: {e}")
            return False
    
    async def _initialize(self) -> bool:
        """Initialize the MCP connection"""
        try:
            init_request = {
                "jsonrpc": "2.0",
                "id": self.request_id,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {
                        "name": "LinkedIn Job Hunter API Bridge",
                        "version": "1.0.0"
                    }
                }
            }
            
            response = await self._send_request(init_request)
            if response and "result" in response:
                # Send initialized notification
                notify_request = {
                    "jsonrpc": "2.0",
                    "method": "notifications/initialized",
                    "params": {}
                }
                await self._send_request(notify_request)
                self.initialized = True
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Initialization failed: {e}")
            return False
    
    async def _send_request(self, request: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Send a request to the MCP server"""
        if not self.process or self.process.poll() is not None:
            raise Exception("MCP server not running")
        
        try:
            # Send the request
            request_data = json.dumps(request) + "\n"
            self.process.stdin.write(request_data.encode())
            await self.process.stdin.drain()
            
            # Read the response
            response_data = await asyncio.wait_for(
                self.process.stdout.readline(),
                timeout=self.connection_timeout
            )
            
            if response_data:
                return json.loads(response_data.decode().strip())
            
            return None
            
        except asyncio.TimeoutError:
            logger.error("Timeout waiting for MCP server response")
            return None
        except Exception as e:
            logger.error(f"Error sending request to MCP server: {e}")
            return None
    
    async def call_tool(self, tool_name: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Call an MCP tool"""
        if not self.initialized:
            if not await self.start_server():
                return {"error": "Failed to start MCP server"}
        
        try:
            self.request_id += 1
            tool_request = {
                "jsonrpc": "2.0",
                "id": self.request_id,
                "method": "tools/call",
                "params": {
                    "name": tool_name,
                    "arguments": params or {}
                }
            }
            
            response = await self._send_request(tool_request)
            if response:
                if "result" in response:
                    return response["result"]
                elif "error" in response:
                    return {"error": response["error"]["message"]}
            
            return {"error": "No valid response from MCP server"}
            
        except Exception as e:
            logger.error(f"Error calling MCP tool {tool_name}: {e}")
            return {"error": str(e)}
    
    async def stop_server(self):
        """Stop the MCP server"""
        if self.process and self.process.poll() is None:
            try:
                self.process.terminate()
                await asyncio.wait_for(self.process.wait(), timeout=5)
                logger.info("MCP server stopped")
            except asyncio.TimeoutExpired:
                self.process.kill()
                logger.info("MCP server killed")
            except Exception as e:
                logger.error(f"Error stopping MCP server: {e}")
        
        self.process = None
        self.initialized = False
    
    async def health_check(self) -> bool:
        """Check if the MCP server is healthy"""
        try:
            if not self.process or self.process.poll() is not None:
                return False
            
            # Try a simple tool call to test connectivity
            result = await self.call_tool("list_applied_jobs")
            return "error" not in result
            
        except Exception:
            return False

# Global MCP client instance
_mcp_client: Optional[MCPClient] = None

async def get_mcp_client() -> MCPClient:
    """Get or create the global MCP client instance"""
    global _mcp_client
    if _mcp_client is None:
        _mcp_client = MCPClient()
    return _mcp_client

async def call_mcp_tool(tool_name: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Call an MCP tool with retry logic"""
    client = await get_mcp_client()
    
    for attempt in range(client.max_retries):
        try:
            result = await client.call_tool(tool_name, params)
            if "error" not in result or "Failed to start" not in result.get("error", ""):
                return result
            
            # If it's a startup error, try restarting the server
            if attempt < client.max_retries - 1:
                logger.warning(f"MCP tool call failed, attempt {attempt + 1}/{client.max_retries}")
                await client.stop_server()
                await asyncio.sleep(2)
                
        except Exception as e:
            logger.error(f"Error calling MCP tool {tool_name}: {e}")
            if attempt < client.max_retries - 1:
                await asyncio.sleep(1)
    
    return {"error": f"Failed to call MCP tool {tool_name} after {client.max_retries} attempts"}

async def shutdown_mcp_client():
    """Shutdown the MCP client"""
    global _mcp_client
    if _mcp_client:
        await _mcp_client.stop_server()
        _mcp_client = None 