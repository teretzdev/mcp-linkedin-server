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
    
    def __init__(self, config: Optional[MCPConfig] = None):
        self.config = config or MCPConfig()
        self.connection_pool = MCPConnectionPool(self.config)
        self.circuit_breaker = CircuitBreaker()
        self.status = MCPStatus.DISCONNECTED
        self._health_check_task: Optional[asyncio.Task] = None
        self._lock = asyncio.Lock()
    
    async def connect(self):
        """Initialize the MCP client"""
        try:
            await self.connection_pool.initialize()
            await self._health_check()
            self.status = MCPStatus.CONNECTED
            self._start_health_monitoring()
            logger.info("MCP client connected successfully")
        except Exception as e:
            self.status = MCPStatus.ERROR
            logger.error(f"Failed to connect MCP client: {e}")
            raise
    
    async def disconnect(self):
        """Disconnect the MCP client"""
        if self._health_check_task:
            self._health_check_task.cancel()
        
        await self.connection_pool.close()
        self.status = MCPStatus.DISCONNECTED
        logger.info("MCP client disconnected")
    
    async def _health_check(self) -> bool:
        """Perform health check on MCP server"""
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                response = await client.get(
                    f"http://{self.config.host}:{self.config.port}/health"
                )
                if response.status_code == 200:
                    return True
        except Exception as e:
            logger.warning(f"Health check failed: {e}")
        
        return False
    
    def _start_health_monitoring(self):
        """Start periodic health monitoring"""
        async def health_monitor():
            while True:
                try:
                    await asyncio.sleep(self.config.health_check_interval)
                    is_healthy = await self._health_check()
                    
                    if is_healthy and self.status != MCPStatus.CONNECTED:
                        self.status = MCPStatus.CONNECTED
                        logger.info("MCP server health restored")
                    elif not is_healthy and self.status == MCPStatus.CONNECTED:
                        self.status = MCPStatus.ERROR
                        logger.warning("MCP server health check failed")
                
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.error(f"Health monitoring error: {e}")
        
        self._health_check_task = asyncio.create_task(health_monitor())
    
    async def _execute_with_retry(self, method: str, endpoint: str, 
                                data: Optional[Dict] = None) -> Dict[str, Any]:
        """Execute MCP request with retry logic"""
        if not self.circuit_breaker.can_execute():
            raise Exception("Circuit breaker is open")
        
        last_exception = None
        
        for attempt in range(self.config.max_retries + 1):
            try:
                connection = await self.connection_pool.get_connection()
                
                try:
                    if method.upper() == "GET":
                        response = await connection.get(endpoint)
                    elif method.upper() == "POST":
                        response = await connection.post(endpoint, json=data)
                    else:
                        raise ValueError(f"Unsupported HTTP method: {method}")
                    
                    if response.status_code == 200:
                        self.circuit_breaker.on_success()
                        return response.json()
                    else:
                        raise Exception(f"HTTP {response.status_code}: {response.text}")
                
                finally:
                    await self.connection_pool.release_connection(connection)
            
            except Exception as e:
                last_exception = e
                self.circuit_breaker.on_failure()
                
                if attempt < self.config.max_retries:
                    logger.warning(f"MCP request failed (attempt {attempt + 1}): {e}")
                    await asyncio.sleep(self.config.retry_delay * (2 ** attempt))
                else:
                    logger.error(f"MCP request failed after {self.config.max_retries} attempts: {e}")
        
        raise last_exception or Exception("Unknown error")
    
    async def search_jobs(self, keywords: str, location: str, 
                         limit: int = 10) -> Dict[str, Any]:
        """Search for jobs using MCP server"""
        data = {
            "keywords": keywords,
            "location": location,
            "limit": limit
        }
        
        return await self._execute_with_retry("POST", "/api/search_jobs", data)
    
    async def apply_job(self, job_id: str, resume_path: Optional[str] = None) -> Dict[str, Any]:
        """Apply to a job using MCP server"""
        data = {
            "job_id": job_id,
            "resume_path": resume_path
        }
        
        return await self._execute_with_retry("POST", "/api/apply_job", data)
    
    async def save_job(self, job_id: str) -> Dict[str, Any]:
        """Save a job using MCP server"""
        data = {"job_id": job_id}
        return await self._execute_with_retry("POST", "/api/save_job", data)
    
    async def get_job_recommendations(self, user_id: str) -> Dict[str, Any]:
        """Get job recommendations using MCP server"""
        return await self._execute_with_retry("GET", f"/api/recommendations/{user_id}")
    
    async def get_application_status(self, application_id: str) -> Dict[str, Any]:
        """Get application status using MCP server"""
        return await self._execute_with_retry("GET", f"/api/application/{application_id}")
    
    async def update_application_status(self, application_id: str, 
                                      status: str, notes: Optional[str] = None) -> Dict[str, Any]:
        """Update application status using MCP server"""
        data = {
            "status": status,
            "notes": notes
        }
        return await self._execute_with_retry("POST", f"/api/application/{application_id}/status", data)
    
    async def get_dashboard_stats(self) -> Dict[str, Any]:
        """Get dashboard statistics using MCP server"""
        return await self._execute_with_retry("GET", "/api/dashboard/stats")
    
    async def get_saved_jobs(self, user_id: str) -> Dict[str, Any]:
        """Get saved jobs using MCP server"""
        return await self._execute_with_retry("GET", f"/api/saved_jobs/{user_id}")
    
    async def get_applied_jobs(self, user_id: str) -> Dict[str, Any]:
        """Get applied jobs using MCP server"""
        return await self._execute_with_retry("GET", f"/api/applied_jobs/{user_id}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get client status information"""
        return {
            "status": self.status.value,
            "circuit_breaker_state": self.circuit_breaker.state,
            "failure_count": self.circuit_breaker.failure_count,
            "connection_pool_size": len(self.connection_pool._connections),
            "available_connections": len(self.connection_pool._available)
        }


# Global MCP client instance
_mcp_client: Optional[MCPClient] = None


async def get_mcp_client() -> MCPClient:
    """Get or create the global MCP client instance"""
    global _mcp_client
    
    if _mcp_client is None:
        _mcp_client = MCPClient()
        await _mcp_client.connect()
    
    return _mcp_client


async def close_mcp_client():
    """Close the global MCP client instance"""
    global _mcp_client
    
    if _mcp_client:
        await _mcp_client.disconnect()
        _mcp_client = None


@asynccontextmanager
async def mcp_client_context():
    """Context manager for MCP client"""
    client = await get_mcp_client()
    try:
        yield client
    finally:
        # Don't close the global client here, it's managed globally
        pass


# Convenience functions for common operations
async def search_jobs(keywords: str, location: str, limit: int = 10) -> Dict[str, Any]:
    """Search for jobs"""
    client = await get_mcp_client()
    return await client.search_jobs(keywords, location, limit)


async def apply_job(job_id: str, resume_path: Optional[str] = None) -> Dict[str, Any]:
    """Apply to a job"""
    client = await get_mcp_client()
    return await client.apply_job(job_id, resume_path)


async def save_job(job_id: str) -> Dict[str, Any]:
    """Save a job"""
    client = await get_mcp_client()
    return await client.save_job(job_id)


async def get_dashboard_stats() -> Dict[str, Any]:
    """Get dashboard statistics"""
    client = await get_mcp_client()
    return await client.get_dashboard_stats()


if __name__ == "__main__":
    # Example usage
    async def main():
        client = MCPClient()
        try:
            await client.connect()
            
            # Search for jobs
            jobs = await client.search_jobs("python developer", "remote", 5)
            print(f"Found {len(jobs.get('jobs', []))} jobs")
            
            # Get dashboard stats
            stats = await client.get_dashboard_stats()
            print(f"Dashboard stats: {stats}")
            
        finally:
            await client.disconnect()
    
    asyncio.run(main()) 