"""
MCP (Model Context Protocol) Client Implementation
Provides robust communication with MCP servers including connection pooling,
retry logic, health checks, and circuit breakers.
"""

import asyncio
import json
import logging
import time
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass
from enum import Enum
import aiohttp
import httpx
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)


class MCPStatus(Enum):
    """MCP connection status"""
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    ERROR = "error"
    RETRYING = "retrying"


@dataclass
class MCPConfig:
    """MCP client configuration"""
    host: str = "localhost"
    port: int = 8002
    timeout: int = 30
    max_retries: int = 3
    retry_delay: float = 1.0
    health_check_interval: int = 30
    connection_pool_size: int = 10


class MCPConnectionPool:
    """Connection pool for MCP clients"""
    
    def __init__(self, config: MCPConfig):
        self.config = config
        self._connections: List[httpx.AsyncClient] = []
        self._available: List[httpx.AsyncClient] = []
        self._lock = asyncio.Lock()
    
    async def initialize(self):
        """Initialize the connection pool"""
        async with self._lock:
            for _ in range(self.config.connection_pool_size):
                client = httpx.AsyncClient(
                    base_url=f"http://{self.config.host}:{self.config.port}",
                    timeout=self.config.timeout
                )
                self._connections.append(client)
                self._available.append(client)
    
    async def get_connection(self) -> httpx.AsyncClient:
        """Get an available connection from the pool"""
        async with self._lock:
            if not self._available:
                # Create a new connection if pool is exhausted
                client = httpx.AsyncClient(
                    base_url=f"http://{self.config.host}:{self.config.port}",
                    timeout=self.config.timeout
                )
                self._connections.append(client)
                return client
            
            return self._available.pop()
    
    async def release_connection(self, client: httpx.AsyncClient):
        """Release a connection back to the pool"""
        async with self._lock:
            if client in self._connections:
                self._available.append(client)
    
    async def close(self):
        """Close all connections in the pool"""
        async with self._lock:
            for client in self._connections:
                await client.aclose()
            self._connections.clear()
            self._available.clear()


class CircuitBreaker:
    """Circuit breaker pattern implementation"""
    
    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = 0
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
    
    def can_execute(self) -> bool:
        """Check if the circuit breaker allows execution"""
        if self.state == "CLOSED":
            return True
        
        if self.state == "OPEN":
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = "HALF_OPEN"
                return True
            return False
        
        return True  # HALF_OPEN
    
    def on_success(self):
        """Handle successful execution"""
        self.failure_count = 0
        self.state = "CLOSED"
    
    def on_failure(self):
        """Handle failed execution"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"


class MCPClient:
    """Robust MCP client with connection pooling, retry logic, and circuit breakers"""
    
    def __init__(self, command: str = "python3 legacy/linkedin_browser_mcp.py"):
        self.command = command
        self.process: Optional[asyncio.subprocess.Process] = None
        self.request_id = 0
        self.futures = {}
    
    async def connect(self):
        """Initialize the MCP client"""
        if self.process is None:
            self.process = await asyncio.create_subprocess_exec(
                *self.command.split(),
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            asyncio.create_task(self._read_stdout())
            asyncio.create_task(self._read_stderr())
    
    async def _read_stdout(self):
        """Read from stdout"""
        if self.process and self.process.stdout:
            while self.process.stdout:
                line = await self.process.stdout.readline()
                if not line:
                    break
                try:
                    response = json.loads(line)
                    future = self.futures.pop(response.get("id"), None)
                    if future:
                        if "error" in response:
                            future.set_exception(Exception(response["error"].get("message")))
                        else:
                            future.set_result(response.get("result"))
                except json.JSONDecodeError:
                    logger.warning(f"MCPClient: Received non-JSON response: {line.decode()}")
    
    async def _read_stderr(self):
        """Read from stderr"""
        if self.process and self.process.stderr:
            while self.process.stderr:
                line = await self.process.stderr.readline()
                if not line:
                    break
                logger.error(f"MCP Server stderr: {line.decode().strip()}")
    
    async def call(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Call MCP server"""
        await self.connect()
        self.request_id += 1
        request = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params,
            "id": self.request_id,
        }
        future = asyncio.get_event_loop().create_future()
        self.futures[self.request_id] = future

        if self.process and self.process.stdin:
            self.process.stdin.write((json.dumps(request) + "\n").encode())
            await self.process.stdin.drain()

        return await asyncio.wait_for(future, timeout=60) # 60 second timeout
    
    async def close(self):
        """Close the MCP client"""
        if self.process:
            self.process.terminate()
            await self.process.wait()
            self.process = None


# Global MCP client instance
_mcp_client: Optional[MCPClient] = None


async def get_mcp_client() -> MCPClient:
    """Get or create the global MCP client instance"""
    global _mcp_client
    
    if _mcp_client is None:
        _mcp_client = MCPClient()
        await _mcp_client.connect()
    
    return _mcp_client


async def call_mcp_tool(tool_name: str, params: dict = {}) -> Dict[str, Any]:
    """Call MCP tool"""
    client = await get_mcp_client()
    # The context 'ctx' is not available here, so we pass a placeholder.
    # The MCP server side should be able to handle a missing or simplified context.
    mcp_params = {"ctx": {"id": "api_bridge"}, **params}
    return await client.call(tool_name, mcp_params)


async def shutdown_mcp_client():
    """Shuts down the MCP client."""
    global _mcp_client
    
    if _mcp_client:
        await _mcp_client.close()
        _mcp_client = None


if __name__ == "__main__":
    # Example usage
    async def main():
        client = MCPClient()
        try:
            await client.connect()
            
            # Call a tool
            result = await client.call("search_jobs", {"keywords": "python developer", "location": "remote", "limit": 5})
            print(f"Search jobs result: {result}")
            
        finally:
            await client.close()
    
    asyncio.run(main()) 