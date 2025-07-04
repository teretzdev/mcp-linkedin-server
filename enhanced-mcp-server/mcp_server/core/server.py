"""
Enhanced MCP Server Core
Main server implementation with improved error handling and configuration
"""

from fastmcp import FastMCP, Context
from typing import Dict, Any, Optional, List
import asyncio
import logging
import json
import os
from pathlib import Path
from datetime import datetime
import structlog

from .browser_manager import BrowserManager
from .auth_manager import AuthManager
from .error_handler import ErrorHandler

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger(__name__)

class LinkedInMCPServer:
    """Enhanced MCP server for LinkedIn job automation"""
    
    def __init__(self, config_path: Optional[Path] = None):
        self.config = self._load_config(config_path)
        self.mcp = FastMCP(
            "linkedin-job-hunter",
            dependencies=[
                "playwright==1.40.0",
                "python-dotenv>=0.19.0",
                "cryptography>=35.0.0",
                "httpx>=0.24.0",
                "sqlalchemy>=2.0.0",
                "pydantic>=2.0.0",
                "structlog>=23.0.0"
            ],
            debug=self.config.get("debug", True)
        )
        
        # Initialize core components
        self.browser_manager = BrowserManager(self.config.get("browser", {}))
        self.auth_manager = AuthManager(self.config.get("encryption_key"))
        self.error_handler = ErrorHandler()
        
        # Session management
        self._sessions: Dict[str, Dict[str, Any]] = {}
        self._active_tools: Dict[str, Any] = {}
        
        # Setup logging
        self._setup_logging()
        
        # Register tools
        self._register_tools()
        
        logger.info("LinkedIn MCP Server initialized", version="2.0.0")
    
    def _load_config(self, config_path: Optional[Path]) -> Dict[str, Any]:
        """Load configuration from JSON file or environment"""
        default_config = {
            "debug": True,
            "log_level": "INFO",
            "browser": {
                "headless": True,
                "timeout": 30000,
                "max_retries": 3
            },
            "security": {
                "rate_limit": {
                    "requests_per_minute": 60,
                    "burst_size": 10
                },
                "session_timeout": 3600  # 1 hour
            },
            "database": {
                "url": "sqlite:///./linkedin_jobs.db",
                "echo": False
            }
        }
        
        if config_path and config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    file_config = json.load(f)
                default_config.update(file_config)
                logger.info("Configuration loaded from file", path=str(config_path))
            except Exception as e:
                logger.warning("Failed to load config file, using defaults", error=str(e))
        
        # Override with environment variables
        if os.getenv("MCP_DEBUG"):
            default_config["debug"] = os.getenv("MCP_DEBUG").lower() == "true"
        
        if os.getenv("MCP_LOG_LEVEL"):
            default_config["log_level"] = os.getenv("MCP_LOG_LEVEL")
        
        return default_config
    
    def _setup_logging(self):
        """Setup logging configuration"""
        log_level = getattr(logging, self.config.get("log_level", "INFO").upper())
        logging.basicConfig(level=log_level)
        
        # Create logs directory
        logs_dir = Path("logs")
        logs_dir.mkdir(exist_ok=True)
        
        logger.info("Logging configured", level=self.config.get("log_level"))
    
    def _register_tools(self):
        """Register all MCP tools"""
        try:
            # Import and register tool modules
            from ..tools import authentication, job_search, job_application, profile_management, analytics
            
            # Register authentication tools
            self._register_tool_module(authentication)
            
            # Register job search tools
            self._register_tool_module(job_search)
            
            # Register job application tools
            self._register_tool_module(job_application)
            
            # Register profile management tools
            self._register_tool_module(profile_management)
            
            # Register analytics tools
            self._register_tool_module(analytics)
            
            logger.info("All tools registered successfully")
            
        except ImportError as e:
            logger.error("Failed to import tool modules", error=str(e))
            # Register basic tools as fallback
            self._register_basic_tools()
    
    def _register_tool_module(self, module):
        """Register tools from a module"""
        if hasattr(module, 'register_tools'):
            module.register_tools(self.mcp)
        else:
            # Auto-register decorated functions
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if hasattr(attr, '_is_mcp_tool'):
                    self._active_tools[attr_name] = attr
    
    def _register_basic_tools(self):
        """Register basic tools as fallback"""
        @self.mcp.tool()
        async def health_check(ctx: Context = None) -> Dict[str, Any]:
            """Check server health status"""
            try:
                return {
                    "status": "healthy",
                    "timestamp": datetime.utcnow().isoformat(),
                    "version": "2.0.0",
                    "sessions": len(self._sessions)
                }
            except Exception as e:
                logger.error("Health check failed", error=str(e))
                return {"status": "unhealthy", "error": str(e)}
        
        @self.mcp.tool()
        async def get_server_info(ctx: Context = None) -> Dict[str, Any]:
            """Get server information"""
            return {
                "name": "LinkedIn Job Hunter MCP Server",
                "version": "2.0.0",
                "capabilities": list(self._active_tools.keys()),
                "config": {k: v for k, v in self.config.items() if k != "encryption_key"}
            }
    
    async def initialize(self):
        """Initialize the server and all components"""
        try:
            # Initialize browser manager
            await self.browser_manager.initialize()
            
            # Initialize database connection
            # TODO: Add database initialization
            
            logger.info("Server initialization completed")
            return True
            
        except Exception as e:
            logger.error("Server initialization failed", error=str(e))
            return False
    
    async def cleanup(self):
        """Cleanup server resources"""
        try:
            # Cleanup browser sessions
            await self.browser_manager.cleanup_all()
            
            # Cleanup database connections
            # TODO: Add database cleanup
            
            logger.info("Server cleanup completed")
            
        except Exception as e:
            logger.error("Server cleanup failed", error=str(e))
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session information"""
        return self._sessions.get(session_id)
    
    def create_session(self, session_id: str) -> Dict[str, Any]:
        """Create a new session"""
        session = {
            "id": session_id,
            "created_at": datetime.utcnow(),
            "last_activity": datetime.utcnow(),
            "status": "active"
        }
        self._sessions[session_id] = session
        logger.info("Session created", session_id=session_id)
        return session
    
    def update_session_activity(self, session_id: str):
        """Update session last activity"""
        if session_id in self._sessions:
            self._sessions[session_id]["last_activity"] = datetime.utcnow()
    
    def cleanup_expired_sessions(self):
        """Cleanup expired sessions"""
        timeout = self.config.get("security", {}).get("session_timeout", 3600)
        current_time = datetime.utcnow()
        
        expired_sessions = []
        for session_id, session in self._sessions.items():
            time_diff = (current_time - session["last_activity"]).total_seconds()
            if time_diff > timeout:
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            del self._sessions[session_id]
            logger.info("Expired session cleaned up", session_id=session_id)
    
    def get_server(self) -> FastMCP:
        """Get the underlying FastMCP server instance"""
        return self.mcp

# Global server instance
_server_instance: Optional[LinkedInMCPServer] = None

def get_server() -> LinkedInMCPServer:
    """Get the global server instance"""
    global _server_instance
    if _server_instance is None:
        _server_instance = LinkedInMCPServer()
    return _server_instance

async def initialize_server() -> bool:
    """Initialize the global server instance"""
    server = get_server()
    return await server.initialize()

async def cleanup_server():
    """Cleanup the global server instance"""
    global _server_instance
    if _server_instance:
        await _server_instance.cleanup()
        _server_instance = None 