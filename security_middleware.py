#!/usr/bin/env python3
"""
Security Middleware for LinkedIn Job Hunter
Provides authentication, rate limiting, and input validation
"""

import time
import hashlib
import hmac
import os
from typing import Dict, Optional, Callable
from datetime import datetime, timedelta
from collections import defaultdict
import re
import json

from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, validator
import jwt

# Security configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Rate limiting configuration
RATE_LIMIT_WINDOW = 60  # seconds
RATE_LIMIT_MAX_REQUESTS = 100  # requests per window

# Input validation patterns
EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
PASSWORD_PATTERN = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$')
URL_PATTERN = re.compile(r'^https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:[\w.])*)?)?$')

class SecurityConfig:
    """Security configuration class"""
    
    def __init__(self):
        self.secret_key = SECRET_KEY
        self.algorithm = ALGORITHM
        self.access_token_expire_minutes = ACCESS_TOKEN_EXPIRE_MINUTES
        self.rate_limit_window = RATE_LIMIT_WINDOW
        self.rate_limit_max_requests = RATE_LIMIT_MAX_REQUESTS

class RateLimiter:
    """Rate limiting implementation"""
    
    def __init__(self):
        self.requests = defaultdict(list)
    
    def is_allowed(self, client_id: str) -> bool:
        """Check if request is allowed based on rate limit"""
        now = time.time()
        window_start = now - RATE_LIMIT_WINDOW
        
        # Clean old requests
        self.requests[client_id] = [
            req_time for req_time in self.requests[client_id]
            if req_time > window_start
        ]
        
        # Check if under limit
        if len(self.requests[client_id]) < RATE_LIMIT_MAX_REQUESTS:
            self.requests[client_id].append(now)
            return True
        
        return False

class InputValidator:
    """Input validation utilities"""
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format"""
        return bool(EMAIL_PATTERN.match(email))
    
    @staticmethod
    def validate_password(password: str) -> bool:
        """Validate password strength"""
        return bool(PASSWORD_PATTERN.match(password))
    
    @staticmethod
    def validate_url(url: str) -> bool:
        """Validate URL format"""
        return bool(URL_PATTERN.match(url))
    
    @staticmethod
    def sanitize_input(text: str) -> str:
        """Sanitize user input"""
        # Remove potentially dangerous characters
        dangerous_chars = ['<', '>', '"', "'", '&', 'script', 'javascript']
        sanitized = text
        for char in dangerous_chars:
            sanitized = sanitized.replace(char, '')
        return sanitized.strip()
    
    @staticmethod
    def validate_json_payload(payload: Dict) -> bool:
        """Validate JSON payload structure"""
        try:
            # Check for nested objects that might be too deep
            def check_depth(obj, depth=0):
                if depth > 10:  # Max depth of 10
                    return False
                if isinstance(obj, dict):
                    return all(check_depth(v, depth + 1) for v in obj.values())
                elif isinstance(obj, list):
                    return all(check_depth(item, depth + 1) for item in obj)
                return True
            
            return check_depth(payload)
        except Exception:
            return False

class JWTManager:
    """JWT token management"""
    
    def __init__(self, secret_key: str, algorithm: str = "HS256"):
        self.secret_key = secret_key
        self.algorithm = algorithm
    
    def create_access_token(self, data: Dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def verify_token(self, token: str) -> Dict:
        """Verify JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token has expired")
        except jwt.JWTError:
            raise HTTPException(status_code=401, detail="Invalid token")

# Global instances
security_config = SecurityConfig()
rate_limiter = RateLimiter()
input_validator = InputValidator()
jwt_manager = JWTManager(security_config.secret_key)
security = HTTPBearer()

# Request models with validation
class LoginRequest(BaseModel):
    username: str
    password: str
    
    @validator('username')
    def validate_username(cls, v):
        if not input_validator.validate_email(v):
            raise ValueError('Invalid email format')
        return input_validator.sanitize_input(v)
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v

class JobSearchRequest(BaseModel):
    query: str
    location: Optional[str] = None
    filters: Optional[Dict] = None
    
    @validator('query')
    def validate_query(cls, v):
        if len(v) < 2:
            raise ValueError('Search query must be at least 2 characters')
        if len(v) > 200:
            raise ValueError('Search query too long')
        return input_validator.sanitize_input(v)
    
    @validator('location')
    def validate_location(cls, v):
        if v and len(v) > 100:
            raise ValueError('Location too long')
        return input_validator.sanitize_input(v) if v else v

# Security middleware functions
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict:
    """Get current authenticated user"""
    token = credentials.credentials
    payload = jwt_manager.verify_token(token)
    return payload

async def rate_limit_middleware(request: Request):
    """Rate limiting middleware"""
    client_id = request.client.host if request.client else "unknown"
    
    if not rate_limiter.is_allowed(client_id):
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded. Please try again later."
        )

async def input_validation_middleware(request: Request):
    """Input validation middleware"""
    # Check content length
    content_length = request.headers.get("content-length")
    if content_length and int(content_length) > 1024 * 1024:  # 1MB limit
        raise HTTPException(
            status_code=413,
            detail="Request too large"
        )
    
    # Validate content type for POST requests
    if request.method == "POST":
        content_type = request.headers.get("content-type", "")
        if not content_type.startswith("application/json"):
            raise HTTPException(
                status_code=400,
                detail="Content-Type must be application/json"
            )

def create_security_middleware():
    """Create security middleware for FastAPI app"""
    
    async def security_middleware(request: Request, call_next: Callable):
        # Rate limiting
        await rate_limit_middleware(request)
        
        # Input validation
        await input_validation_middleware(request)
        
        # Add security headers
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        return response
    
    return security_middleware

# Utility functions
def hash_password(password: str) -> str:
    """Hash password using bcrypt-like approach"""
    salt = os.urandom(16)
    hash_obj = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
    return salt.hex() + hash_obj.hex()

def verify_password(password: str, hashed: str) -> bool:
    """Verify password against hash"""
    try:
        salt = bytes.fromhex(hashed[:32])
        hash_obj = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
        return hashed[32:] == hash_obj.hex()
    except Exception:
        return False

def generate_csrf_token() -> str:
    """Generate CSRF token"""
    return hashlib.sha256(os.urandom(32)).hexdigest()

def verify_csrf_token(token: str, expected: str) -> bool:
    """Verify CSRF token"""
    return hmac.compare_digest(token, expected) 