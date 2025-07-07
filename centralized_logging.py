#!/usr/bin/env python3
"""
Centralized Logging System for LinkedIn Job Hunter
Provides unified logging across all services with error tracking and monitoring
"""

import os
import sys
import json
import logging
import logging.handlers
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional, List
import traceback
import threading
import queue
import time

# Create logs directory if it doesn't exist
LOGS_DIR = Path("logs")
LOGS_DIR.mkdir(exist_ok=True)

class CentralizedLogger:
    """Centralized logging system for all services"""
    
    def __init__(self, service_name: str, log_level: str = "INFO"):
        self.service_name = service_name
        self.log_level = getattr(logging, log_level.upper())
        
        # Create service-specific log files
        self.log_file = LOGS_DIR / f"{service_name.lower()}.log"
        self.error_file = LOGS_DIR / f"{service_name.lower()}_errors.log"
        self.audit_file = LOGS_DIR / f"{service_name.lower()}_audit.log"
        
        # Initialize logger
        self.logger = self._setup_logger()
        
        # Error tracking
        self.error_count = 0
        self.last_error_time = None
        self.error_threshold = 10  # Alert after 10 errors in 5 minutes
        self.error_window = timedelta(minutes=5)
        
        # Performance tracking
        self.performance_log = []
        self.max_performance_log_size = 1000
        
        # Add a utility function to check if log files are writable
        if not self._check_log_file_access(self.log_file):
            print(f"[LOGGING WARNING] Main log file {self.log_file} is not writable!")
        if not self._check_log_file_access(self.error_file):
            print(f"[LOGGING WARNING] Error log file {self.error_file} is not writable!")
        if not self._check_log_file_access(self.audit_file):
            print(f"[LOGGING WARNING] Audit log file {self.audit_file} is not writable!")
        
    def _setup_logger(self) -> logging.Logger:
        """Setup the logger with multiple handlers"""
        logger = logging.getLogger(f"linkedin_hunter.{self.service_name}")
        logger.setLevel(self.log_level)
        
        # Clear existing handlers
        logger.handlers.clear()
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(self.log_level)
        console_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
        
        # Main log file handler
        file_handler = logging.handlers.RotatingFileHandler(
            self.log_file,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        file_handler.setLevel(self.log_level)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
        
        # Error log file handler
        error_handler = logging.handlers.RotatingFileHandler(
            self.error_file,
            maxBytes=5*1024*1024,  # 5MB
            backupCount=3
        )
        error_handler.setLevel(logging.ERROR)
        error_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s\n---\n'
        )
        error_handler.setFormatter(error_formatter)
        logger.addHandler(error_handler)
        
        # Audit log file handler
        audit_handler = logging.handlers.RotatingFileHandler(
            self.audit_file,
            maxBytes=5*1024*1024,  # 5MB
            backupCount=3
        )
        audit_handler.setLevel(logging.INFO)
        audit_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - AUDIT - %(message)s'
        )
        audit_handler.setFormatter(audit_formatter)
        logger.addHandler(audit_handler)
        
        return logger
    
    def log_info(self, message: str, **kwargs):
        """Log info message with optional context"""
        context = f" | Context: {json.dumps(kwargs)}" if kwargs else ""
        self.logger.info(f"{message}{context}")
    
    def log_warning(self, message: str, **kwargs):
        """Log warning message with optional context"""
        context = f" | Context: {json.dumps(kwargs)}" if kwargs else ""
        self.logger.warning(f"{message}{context}")
    
    def log_error(self, message: str, exception: Optional[Exception] = None, **kwargs):
        """Log error message with exception and context"""
        self.error_count += 1
        self.last_error_time = datetime.now()
        
        context = f" | Context: {json.dumps(kwargs)}" if kwargs else ""
        error_msg = f"{message}{context}"
        
        if exception:
            self.logger.error(
                error_msg,
                exc_info=True
            )
        else:
            self.logger.error(error_msg)
        
        # Check error threshold
        self._check_error_threshold()
    
    def log_critical(self, message: str, exception: Optional[Exception] = None, **kwargs):
        """Log critical error message"""
        context = f" | Context: {json.dumps(kwargs)}" if kwargs else ""
        error_msg = f"CRITICAL: {message}{context}"
        
        if exception:
            self.logger.critical(
                error_msg,
                exc_info=True
            )
        else:
            self.logger.critical(error_msg)
    
    def log_audit(self, action: str, user: str = "system", **kwargs):
        """Log audit events"""
        audit_msg = f"Action: {action} | User: {user}"
        if kwargs:
            audit_msg += f" | Details: {json.dumps(kwargs)}"
        self.logger.info(audit_msg)
    
    def log_performance(self, operation: str, duration: float, **kwargs):
        """Log performance metrics"""
        perf_data = {
            'timestamp': datetime.now().isoformat(),
            'operation': operation,
            'duration': duration,
            'service': self.service_name,
            **kwargs
        }
        
        self.performance_log.append(perf_data)
        
        # Keep only recent entries
        if len(self.performance_log) > self.max_performance_log_size:
            self.performance_log = self.performance_log[-self.max_performance_log_size:]
        
        # Log if duration is significant
        if duration > 1.0:  # Log operations taking more than 1 second
            self.log_warning(f"Slow operation: {operation} took {duration:.2f}s", **kwargs)
        else:
            self.log_info(f"Performance: {operation} took {duration:.3f}s", **kwargs)
    
    def _check_error_threshold(self):
        """Check if error threshold has been exceeded"""
        if self.last_error_time and self.error_count >= self.error_threshold:
            time_diff = datetime.now() - self.last_error_time
            if time_diff <= self.error_window:
                self.log_critical(
                    f"Error threshold exceeded: {self.error_count} errors in {time_diff.total_seconds():.1f}s",
                    error_count=self.error_count,
                    error_window_seconds=self.error_window.total_seconds()
                )
                # Reset counter
                self.error_count = 0
                self.last_error_time = None
    
    def get_error_summary(self) -> Dict[str, Any]:
        """Get summary of recent errors"""
        return {
            'service': self.service_name,
            'error_count': self.error_count,
            'last_error_time': self.last_error_time.isoformat() if self.last_error_time else None,
            'error_threshold': self.error_threshold,
            'error_window_seconds': self.error_window.total_seconds()
        }
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get summary of performance metrics"""
        if not self.performance_log:
            return {'service': self.service_name, 'operations': 0}
        
        durations = [op['duration'] for op in self.performance_log]
        return {
            'service': self.service_name,
            'operations': len(self.performance_log),
            'avg_duration': sum(durations) / len(durations),
            'max_duration': max(durations),
            'min_duration': min(durations),
            'recent_operations': self.performance_log[-10:]  # Last 10 operations
        }

    def _check_log_file_access(self, log_file):
        try:
            with open(log_file, 'a') as f:
                f.write('')
            return True
        except Exception as e:
            print(f"[LOGGING WARNING] Cannot write to log file {log_file}: {e}")
            return False

class LogManager:
    """Manages all loggers and provides centralized access"""
    
    def __init__(self):
        self.loggers: Dict[str, CentralizedLogger] = {}
        self.log_queue = queue.Queue()
        self.running = True
        
        # Start log processing thread
        self.log_thread = threading.Thread(target=self._process_logs, daemon=True)
        self.log_thread.start()
    
    def get_logger(self, service_name: str, log_level: str = "INFO") -> CentralizedLogger:
        """Get or create a logger for a service"""
        if service_name not in self.loggers:
            self.loggers[service_name] = CentralizedLogger(service_name, log_level)
        return self.loggers[service_name]
    
    def log_system_event(self, event: str, **kwargs):
        """Log system-wide events"""
        system_logger = self.get_logger("system")
        system_logger.log_info(f"System Event: {event}", **kwargs)
    
    def log_service_start(self, service_name: str, port: Optional[int] = None):
        """Log service startup"""
        logger = self.get_logger(service_name)
        logger.log_info(f"Service started", port=port, pid=os.getpid())
        self.log_system_event("service_started", service=service_name, port=port)
    
    def log_service_stop(self, service_name: str):
        """Log service shutdown"""
        logger = self.get_logger(service_name)
        logger.log_info(f"Service stopped")
        self.log_system_event("service_stopped", service=service_name)
    
    def log_api_request(self, service_name: str, method: str, endpoint: str, 
                       status_code: int, duration: float, **kwargs):
        """Log API requests"""
        logger = self.get_logger(service_name)
        logger.log_performance(
            f"API {method} {endpoint}",
            duration,
            status_code=status_code,
            **kwargs
        )
        
        # Log errors
        if status_code >= 400:
            logger.log_error(
                f"API Error: {method} {endpoint} returned {status_code}",
                status_code=status_code,
                duration=duration,
                **kwargs
            )
    
    def log_database_operation(self, service_name: str, operation: str, 
                              table: str, duration: float, **kwargs):
        """Log database operations"""
        logger = self.get_logger(service_name)
        logger.log_performance(
            f"DB {operation} on {table}",
            duration,
            table=table,
            **kwargs
        )
    
    def get_all_summaries(self) -> Dict[str, Any]:
        """Get summaries from all loggers"""
        summaries = {
            'system': {
                'timestamp': datetime.now().isoformat(),
                'total_services': len(self.loggers),
                'services': {}
            }
        }
        
        for service_name, logger in self.loggers.items():
            summaries['system']['services'][service_name] = {
                'error_summary': logger.get_error_summary(),
                'performance_summary': logger.get_performance_summary()
            }
        
        return summaries
    
    def _process_logs(self):
        """Process logs in background thread"""
        while self.running:
            try:
                # Process any queued logs
                while not self.log_queue.empty():
                    log_entry = self.log_queue.get_nowait()
                    # Process log entry if needed
                    pass
                
                time.sleep(1)
            except Exception as e:
                # Use basic logging for log processing errors
                print(f"Log processing error: {e}")
    
    def shutdown(self):
        """Shutdown the log manager"""
        self.running = False
        self.log_system_event("log_manager_shutdown")

# Global log manager instance
log_manager = LogManager()

# Convenience functions
def get_logger(service_name: str, log_level: str = "INFO") -> CentralizedLogger:
    """Get a logger for a service"""
    return log_manager.get_logger(service_name, log_level)

def log_error(service_name: str, message: str, exception: Optional[Exception] = None, **kwargs):
    """Log an error for a service"""
    logger = get_logger(service_name)
    logger.log_error(message, exception, **kwargs)

def log_api_request(service_name: str, method: str, endpoint: str, 
                   status_code: int, duration: float, **kwargs):
    """Log an API request"""
    log_manager.log_api_request(service_name, method, endpoint, status_code, duration, **kwargs)

def log_service_start(service_name: str, port: Optional[int] = None):
    """Log service startup"""
    log_manager.log_service_start(service_name, port)

def log_service_stop(service_name: str):
    """Log service shutdown"""
    log_manager.log_service_stop(service_name)

# Example usage
if __name__ == "__main__":
    # Test the logging system
    logger = get_logger("test_service")
    
    logger.log_info("Test service started")
    logger.log_warning("Test warning message")
    
    try:
        # Simulate an error
        raise ValueError("Test error")
    except Exception as e:
        logger.log_error("Test error occurred", e)
    
    logger.log_audit("test_action", "test_user", action_type="test")
    logger.log_performance("test_operation", 0.5)
    
    # Get summaries
    summaries = log_manager.get_all_summaries()
    print(json.dumps(summaries, indent=2)) 