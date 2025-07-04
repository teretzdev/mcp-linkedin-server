#!/usr/bin/env python3
"""
Error Handling Module for LinkedIn Job Hunter
Provides consistent error handling and logging across the application
"""

import logging
import traceback
import sys
import os
from typing import Dict, Any, Optional, Union
from datetime import datetime
from enum import Enum
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('error.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

class ErrorSeverity(Enum):
    """Error severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ErrorCategory(Enum):
    """Error categories"""
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    VALIDATION = "validation"
    NETWORK = "network"
    DATABASE = "database"
    EXTERNAL_SERVICE = "external_service"
    INTERNAL = "internal"
    UNKNOWN = "unknown"

class AppError(Exception):
    """Base application error class"""
    
    def __init__(
        self,
        message: str,
        category: ErrorCategory = ErrorCategory.UNKNOWN,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        details: Optional[Dict[str, Any]] = None,
        original_error: Optional[Exception] = None
    ):
        self.message = message
        self.category = category
        self.severity = severity
        self.details = details or {}
        self.original_error = original_error
        self.timestamp = datetime.utcnow()
        self.traceback = traceback.format_exc()
        
        super().__init__(self.message)

class AuthenticationError(AppError):
    """Authentication related errors"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, ErrorCategory.AUTHENTICATION, ErrorSeverity.HIGH, details)

class ValidationError(AppError):
    """Validation related errors"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, ErrorCategory.VALIDATION, ErrorSeverity.MEDIUM, details)

class NetworkError(AppError):
    """Network related errors"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, ErrorCategory.NETWORK, ErrorSeverity.MEDIUM, details)

class DatabaseError(AppError):
    """Database related errors"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, ErrorCategory.DATABASE, ErrorSeverity.HIGH, details)

class ExternalServiceError(AppError):
    """External service related errors"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, ErrorCategory.EXTERNAL_SERVICE, ErrorSeverity.MEDIUM, details)

class ErrorHandler:
    """Centralized error handler"""
    
    def __init__(self):
        self.error_counts = {}
        self.alert_thresholds = {
            ErrorSeverity.CRITICAL: 1,
            ErrorSeverity.HIGH: 5,
            ErrorSeverity.MEDIUM: 10,
            ErrorSeverity.LOW: 20
        }
    
    def handle_error(
        self,
        error: Exception,
        context: Optional[Dict[str, Any]] = None,
        request: Optional[Request] = None
    ) -> Dict[str, Any]:
        """Handle and log an error"""
        
        # Convert to AppError if needed
        if not isinstance(error, AppError):
            error = AppError(
                str(error),
                ErrorCategory.UNKNOWN,
                ErrorSeverity.MEDIUM,
                {"original_error_type": type(error).__name__},
                error
            )
        
        # Add context
        if context:
            error.details.update(context)
        
        # Add request info
        if request:
            error.details.update({
                "method": request.method,
                "url": str(request.url),
                "client_ip": request.client.host if request.client else "unknown",
                "user_agent": request.headers.get("user-agent", "unknown")
            })
        
        # Log the error
        self._log_error(error)
        
        # Track error counts
        self._track_error(error)
        
        # Check for alerts
        self._check_alerts(error)
        
        # Return error response
        return self._create_error_response(error)
    
    def _log_error(self, error: AppError):
        """Log error with appropriate level"""
        log_message = f"{error.category.value.upper()} ERROR: {error.message}"
        
        if error.details:
            log_message += f" | Details: {error.details}"
        
        if error.original_error:
            log_message += f" | Original: {error.original_error}"
        
        if error.severity == ErrorSeverity.CRITICAL:
            logger.critical(log_message, exc_info=True)
        elif error.severity == ErrorSeverity.HIGH:
            logger.error(log_message, exc_info=True)
        elif error.severity == ErrorSeverity.MEDIUM:
            logger.warning(log_message)
        else:
            logger.info(log_message)
    
    def _track_error(self, error: AppError):
        """Track error counts for monitoring"""
        key = f"{error.category.value}_{error.severity.value}"
        self.error_counts[key] = self.error_counts.get(key, 0) + 1
    
    def _check_alerts(self, error: AppError):
        """Check if alerts should be triggered"""
        key = f"{error.category.value}_{error.severity.value}"
        count = self.error_counts.get(key, 0)
        threshold = self.alert_thresholds.get(error.severity, 10)
        
        if count >= threshold:
            logger.critical(f"ALERT: {count} {error.severity.value} {error.category.value} errors detected")
            # Here you could send alerts via email, Slack, etc.
    
    def _create_error_response(self, error: AppError) -> Dict[str, Any]:
        """Create standardized error response"""
        response = {
            "error": {
                "message": error.message,
                "category": error.category.value,
                "severity": error.severity.value,
                "timestamp": error.timestamp.isoformat(),
                "error_id": self._generate_error_id(error)
            }
        }
        
        # Add details in development mode
        if os.getenv("DEBUG", "false").lower() == "true":
            response["error"]["details"] = error.details
            response["error"]["traceback"] = str(error.traceback)
        
        return response
    
    def _generate_error_id(self, error: AppError) -> str:
        """Generate unique error ID"""
        import hashlib
        error_data = f"{error.message}{error.timestamp}{error.category.value}"
        return hashlib.md5(error_data.encode()).hexdigest()[:8]

# Global error handler instance
error_handler = ErrorHandler()

# FastAPI exception handlers
async def app_error_handler(request: Request, exc: AppError):
    """Handle AppError exceptions"""
    error_response = error_handler.handle_error(exc, request=request)
    return JSONResponse(
        status_code=400,
        content=error_response
    )

async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions"""
    error_response = error_handler.handle_error(exc, request=request)
    return JSONResponse(
        status_code=500,
        content=error_response
    )

async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions"""
    error = AppError(
        exc.detail,
        ErrorCategory.VALIDATION if exc.status_code == 422 else ErrorCategory.UNKNOWN,
        ErrorSeverity.MEDIUM,
        {"status_code": exc.status_code}
    )
    error_response = error_handler.handle_error(error, request=request)
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response
    )

# Utility functions for common error scenarios
def handle_authentication_error(message: str, details: Optional[Dict[str, Any]] = None) -> AppError:
    """Create and handle authentication error"""
    error = AuthenticationError(message, details)
    error_handler.handle_error(error)
    return error

def handle_validation_error(message: str, details: Optional[Dict[str, Any]] = None) -> AppError:
    """Create and handle validation error"""
    error = ValidationError(message, details)
    error_handler.handle_error(error)
    return error

def handle_network_error(message: str, details: Optional[Dict[str, Any]] = None) -> AppError:
    """Create and handle network error"""
    error = NetworkError(message, details)
    error_handler.handle_error(error)
    return error

def handle_database_error(message: str, details: Optional[Dict[str, Any]] = None) -> AppError:
    """Create and handle database error"""
    error = DatabaseError(message, details)
    error_handler.handle_error(error)
    return error

def handle_external_service_error(message: str, details: Optional[Dict[str, Any]] = None) -> AppError:
    """Create and handle external service error"""
    error = ExternalServiceError(message, details)
    error_handler.handle_error(error)
    return error

# Context manager for error handling
class ErrorContext:
    """Context manager for error handling"""
    
    def __init__(self, operation: str, context: Optional[Dict[str, Any]] = None):
        self.operation = operation
        self.context = context or {}
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_val:
            self.context["operation"] = self.operation
            error_handler.handle_error(exc_val, self.context)
        return False  # Don't suppress the exception

# Decorator for error handling
def handle_errors(operation: str = None):
    """Decorator for automatic error handling"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                context = {"operation": operation or func.__name__}
                error_handler.handle_error(e, context)
                raise
        return wrapper
    return decorator 