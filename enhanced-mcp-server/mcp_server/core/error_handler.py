"""
Error Handler
Provides consistent error handling and logging across the MCP server
"""

import traceback
from typing import Dict, Any, Optional, Callable
import structlog
from datetime import datetime

logger = structlog.get_logger(__name__)

class MCPError(Exception):
    """Base exception for MCP server errors"""
    
    def __init__(self, message: str, error_code: str = "UNKNOWN_ERROR", details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        self.timestamp = datetime.utcnow()

class AuthenticationError(MCPError):
    """Authentication related errors"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "AUTHENTICATION_ERROR", details)

class BrowserError(MCPError):
    """Browser automation errors"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "BROWSER_ERROR", details)

class ValidationError(MCPError):
    """Input validation errors"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "VALIDATION_ERROR", details)

class SessionError(MCPError):
    """Session management errors"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "SESSION_ERROR", details)

class ErrorHandler:
    """Centralized error handling for the MCP server"""
    
    def __init__(self):
        self.error_handlers: Dict[str, Callable] = {}
        self._setup_default_handlers()
    
    def _setup_default_handlers(self):
        """Setup default error handlers"""
        self.register_handler("AUTHENTICATION_ERROR", self._handle_auth_error)
        self.register_handler("BROWSER_ERROR", self._handle_browser_error)
        self.register_handler("VALIDATION_ERROR", self._handle_validation_error)
        self.register_handler("SESSION_ERROR", self._handle_session_error)
        self.register_handler("UNKNOWN_ERROR", self._handle_unknown_error)
    
    def register_handler(self, error_code: str, handler: Callable):
        """Register a custom error handler"""
        self.error_handlers[error_code] = handler
    
    def handle_error(self, error: Exception, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Handle an error and return standardized error response"""
        try:
            # Log the error
            self._log_error(error, context)
            
            # Determine error type
            if isinstance(error, MCPError):
                error_code = error.error_code
                error_details = error.details
            else:
                error_code = "UNKNOWN_ERROR"
                error_details = {}
            
            # Get handler for this error type
            handler = self.error_handlers.get(error_code, self._handle_unknown_error)
            
            # Handle the error
            return handler(error, context, error_details)
            
        except Exception as e:
            # Fallback error handling
            logger.error("Error in error handler", error=str(e))
            return self._create_error_response("ERROR_HANDLER_FAILED", str(error), {})
    
    def _log_error(self, error: Exception, context: Optional[Dict[str, Any]] = None):
        """Log error with context"""
        error_info = {
            "error_type": type(error).__name__,
            "error_message": str(error),
            "traceback": traceback.format_exc(),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if context:
            error_info["context"] = context
        
        if isinstance(error, MCPError):
            error_info["error_code"] = error.error_code
            error_info["details"] = error.details
        
        logger.error("MCP Server Error", **error_info)
    
    def _handle_auth_error(self, error: Exception, context: Optional[Dict[str, Any]], details: Dict[str, Any]) -> Dict[str, Any]:
        """Handle authentication errors"""
        return self._create_error_response(
            "AUTHENTICATION_ERROR",
            str(error),
            {
                "suggestion": "Please check your credentials and try again",
                "retry_after": 60
            }
        )
    
    def _handle_browser_error(self, error: Exception, context: Optional[Dict[str, Any]], details: Dict[str, Any]) -> Dict[str, Any]:
        """Handle browser automation errors"""
        return self._create_error_response(
            "BROWSER_ERROR",
            str(error),
            {
                "suggestion": "Browser session may have expired. Please try again.",
                "retry_after": 30
            }
        )
    
    def _handle_validation_error(self, error: Exception, context: Optional[Dict[str, Any]], details: Dict[str, Any]) -> Dict[str, Any]:
        """Handle validation errors"""
        return self._create_error_response(
            "VALIDATION_ERROR",
            str(error),
            {
                "suggestion": "Please check your input and try again",
                "retry_after": 0
            }
        )
    
    def _handle_session_error(self, error: Exception, context: Optional[Dict[str, Any]], details: Dict[str, Any]) -> Dict[str, Any]:
        """Handle session errors"""
        return self._create_error_response(
            "SESSION_ERROR",
            str(error),
            {
                "suggestion": "Session may have expired. Please login again.",
                "retry_after": 0
            }
        )
    
    def _handle_unknown_error(self, error: Exception, context: Optional[Dict[str, Any]], details: Dict[str, Any]) -> Dict[str, Any]:
        """Handle unknown errors"""
        return self._create_error_response(
            "UNKNOWN_ERROR",
            str(error),
            {
                "suggestion": "An unexpected error occurred. Please try again later.",
                "retry_after": 300
            }
        )
    
    def _create_error_response(self, error_code: str, message: str, details: Dict[str, Any]) -> Dict[str, Any]:
        """Create standardized error response"""
        return {
            "success": False,
            "error": {
                "code": error_code,
                "message": message,
                "details": details,
                "timestamp": datetime.utcnow().isoformat()
            }
        }
    
    def create_success_response(self, data: Any = None, message: str = "Success") -> Dict[str, Any]:
        """Create standardized success response"""
        response = {
            "success": True,
            "message": message,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if data is not None:
            response["data"] = data
        
        return response
    
    def validate_input(self, data: Any, validation_rules: Dict[str, Any]) -> bool:
        """Validate input data against rules"""
        try:
            for field, rules in validation_rules.items():
                if field not in data:
                    if rules.get("required", False):
                        raise ValidationError(f"Required field '{field}' is missing")
                    continue
                
                value = data[field]
                
                # Type validation
                expected_type = rules.get("type")
                if expected_type and not isinstance(value, expected_type):
                    raise ValidationError(f"Field '{field}' must be of type {expected_type.__name__}")
                
                # Length validation
                if "min_length" in rules and len(str(value)) < rules["min_length"]:
                    raise ValidationError(f"Field '{field}' must be at least {rules['min_length']} characters")
                
                if "max_length" in rules and len(str(value)) > rules["max_length"]:
                    raise ValidationError(f"Field '{field}' must be at most {rules['max_length']} characters")
                
                # Range validation
                if "min_value" in rules and value < rules["min_value"]:
                    raise ValidationError(f"Field '{field}' must be at least {rules['min_value']}")
                
                if "max_value" in rules and value > rules["max_value"]:
                    raise ValidationError(f"Field '{field}' must be at most {rules['max_value']}")
                
                # Pattern validation
                if "pattern" in rules:
                    import re
                    if not re.match(rules["pattern"], str(value)):
                        raise ValidationError(f"Field '{field}' does not match required pattern")
            
            return True
            
        except ValidationError:
            raise
        except Exception as e:
            raise ValidationError(f"Validation failed: {str(e)}")
    
    def retry_with_backoff(self, func: Callable, max_retries: int = 3, base_delay: float = 1.0):
        """Retry function with exponential backoff"""
        import asyncio
        
        async def _retry():
            last_exception = None
            
            for attempt in range(max_retries):
                try:
                    if asyncio.iscoroutinefunction(func):
                        return await func()
                    else:
                        return func()
                        
                except Exception as e:
                    last_exception = e
                    
                    if attempt < max_retries - 1:
                        delay = base_delay * (2 ** attempt)
                        logger.warning(f"Attempt {attempt + 1} failed, retrying in {delay}s", error=str(e))
                        await asyncio.sleep(delay)
                    else:
                        logger.error(f"All {max_retries} attempts failed", error=str(e))
            
            raise last_exception
        
        return _retry 