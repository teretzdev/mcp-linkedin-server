# 🔒 Security Guide - LinkedIn Job Hunter

This guide documents the comprehensive security features implemented in the LinkedIn Job Hunter application to ensure data protection, secure authentication, and safe operation.

## 🛡️ Security Overview

The LinkedIn Job Hunter implements a multi-layered security approach:

1. **Authentication & Authorization**: JWT-based token system
2. **Input Validation**: Comprehensive sanitization and validation
3. **Rate Limiting**: Protection against abuse and DDoS
4. **Security Headers**: Modern web security headers
5. **Error Handling**: Secure error management
6. **Data Protection**: Encryption and secure storage

## 🔐 Authentication System

### JWT Implementation

The application uses JSON Web Tokens (JWT) for secure authentication:

```python
# JWT Configuration
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Token generation
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt
```

### Password Security

Passwords are securely hashed using bcrypt:

```python
# Password hashing
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

# Password verification
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
```

### Session Management

- **Token Expiration**: JWT tokens expire after 30 minutes
- **Secure Storage**: Tokens stored in HTTP-only cookies
- **Automatic Refresh**: Token refresh mechanism for long sessions

## 🛡️ Input Validation & Sanitization

### Request Validation

All incoming requests are validated using Pydantic models:

```python
class JobSearchRequest(BaseModel):
    keywords: str = Field(..., min_length=1, max_length=200)
    location: str = Field(..., min_length=1, max_length=100)
    limit: int = Field(default=10, ge=1, le=100)
    
    @validator('keywords')
    def validate_keywords(cls, v):
        # Remove potentially dangerous characters
        cleaned = re.sub(r'[<>"\']', '', v)
        if not cleaned.strip():
            raise ValueError('Keywords cannot be empty after sanitization')
        return cleaned.strip()
```

### SQL Injection Prevention

- **Parameterized Queries**: All database queries use parameterized statements
- **Input Sanitization**: Special characters are escaped or removed
- **Type Validation**: Strict type checking for all inputs

### XSS Protection

- **Output Encoding**: All user-generated content is HTML-encoded
- **Content Security Policy**: CSP headers prevent XSS attacks
- **Input Filtering**: Dangerous HTML tags and scripts are filtered

## 🚦 Rate Limiting

### Implementation

Rate limiting is implemented using a sliding window approach:

```python
class RateLimiter:
    def __init__(self, requests_per_minute: int = 100):
        self.requests_per_minute = requests_per_minute
        self.requests = {}
    
    def is_allowed(self, client_ip: str) -> bool:
        now = time.time()
        if client_ip not in self.requests:
            self.requests[client_ip] = []
        
        # Remove old requests
        self.requests[client_ip] = [
            req_time for req_time in self.requests[client_ip]
            if now - req_time < 60
        ]
        
        # Check if limit exceeded
        if len(self.requests[client_ip]) >= self.requests_per_minute:
            return False
        
        # Add current request
        self.requests[client_ip].append(now)
        return True
```

### Rate Limits by Endpoint

- **Authentication**: 5 attempts per minute
- **Job Search**: 50 requests per minute
- **Job Application**: 10 applications per minute
- **General API**: 100 requests per minute

## 🔒 Security Headers

### Implementation

Security headers are automatically added to all responses:

```python
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    
    # Security headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self' 'unsafe-inline'"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    
    return response
```

### Header Descriptions

- **X-Content-Type-Options**: Prevents MIME type sniffing
- **X-Frame-Options**: Prevents clickjacking attacks
- **X-XSS-Protection**: Enables browser XSS filtering
- **HSTS**: Forces HTTPS connections
- **CSP**: Controls resource loading
- **Referrer-Policy**: Controls referrer information

## 🛡️ Error Handling

### Secure Error Management

Errors are handled securely to prevent information leakage:

```python
class ErrorHandler:
    def __init__(self):
        self.error_categories = {
            'authentication': 'High',
            'authorization': 'High',
            'validation': 'Medium',
            'system': 'Low'
        }
    
    def handle_error(self, error: Exception, category: str = 'system') -> dict:
        # Log error securely
        self.log_error(error, category)
        
        # Return safe error message
        if category in ['authentication', 'authorization']:
            return {"error": "Authentication failed"}
        elif category == 'validation':
            return {"error": "Invalid input provided"}
        else:
            return {"error": "An error occurred"}
    
    def log_error(self, error: Exception, category: str):
        # Log to secure location without sensitive data
        logger.error(f"Category: {category}, Type: {type(error).__name__}")
```

### Error Categories

1. **Authentication Errors**: Invalid credentials, expired tokens
2. **Authorization Errors**: Insufficient permissions
3. **Validation Errors**: Invalid input data
4. **System Errors**: Internal server errors

## 🔐 Data Protection

### Encryption

Sensitive data is encrypted before storage:

```python
class DataEncryption:
    def __init__(self, key: str):
        self.key = hashlib.sha256(key.encode()).digest()
    
    def encrypt(self, data: str) -> str:
        cipher = AES.new(self.key, AES.MODE_GCM)
        ciphertext, tag = cipher.encrypt_and_digest(data.encode())
        return base64.b64encode(cipher.nonce + tag + ciphertext).decode()
    
    def decrypt(self, encrypted_data: str) -> str:
        data = base64.b64decode(encrypted_data.encode())
        nonce = data[:12]
        tag = data[12:28]
        ciphertext = data[28:]
        cipher = AES.new(self.key, AES.MODE_GCM, nonce=nonce)
        return cipher.decrypt_and_verify(ciphertext, tag).decode()
```

### Secure Storage

- **LinkedIn Credentials**: Encrypted in `.env` file
- **Session Data**: Encrypted cookies
- **Application Data**: Local storage with encryption
- **Logs**: No sensitive data in logs

## 🚨 Security Monitoring

### Audit Logging

All security-relevant events are logged:

```python
class SecurityLogger:
    def log_login_attempt(self, username: str, success: bool, ip: str):
        logger.info(f"Login attempt: {username}, Success: {success}, IP: {ip}")
    
    def log_rate_limit_exceeded(self, ip: str, endpoint: str):
        logger.warning(f"Rate limit exceeded: {ip}, Endpoint: {endpoint}")
    
    def log_validation_error(self, input_data: str, error: str):
        logger.warning(f"Validation error: {error}")
```

### Security Metrics

- **Failed Login Attempts**: Tracked per IP address
- **Rate Limit Violations**: Monitored for abuse patterns
- **Validation Errors**: Tracked for potential attacks
- **System Errors**: Monitored for security implications

## 🔧 Security Configuration

### Environment Variables

```bash
# Security configuration
JWT_SECRET_KEY=your-super-secret-key-change-in-production
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
RATE_LIMIT_REQUESTS_PER_MINUTE=100
ENCRYPTION_KEY=your-encryption-key
DEBUG_MODE=false
LOG_LEVEL=INFO
```

### Security Settings

```python
# Security configuration
SECURITY_CONFIG = {
    "jwt_secret_key": os.getenv("JWT_SECRET_KEY"),
    "jwt_expire_minutes": int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30")),
    "rate_limit_requests": int(os.getenv("RATE_LIMIT_REQUESTS_PER_MINUTE", "100")),
    "encryption_key": os.getenv("ENCRYPTION_KEY"),
    "debug_mode": os.getenv("DEBUG_MODE", "false").lower() == "true",
    "log_level": os.getenv("LOG_LEVEL", "INFO")
}
```

## 🧪 Security Testing

### Test Categories

1. **Authentication Tests**: Token validation, password security
2. **Authorization Tests**: Permission checks, access control
3. **Input Validation Tests**: XSS, SQL injection prevention
4. **Rate Limiting Tests**: Abuse prevention
5. **Error Handling Tests**: Information leakage prevention

### Running Security Tests

```bash
# Run security tests
python test_runner.py --category security

# Run comprehensive security testing
python test_framework.py --category security --verbose
```

## 🚨 Security Best Practices

### For Developers

1. **Never Log Sensitive Data**: Avoid logging passwords, tokens, or personal information
2. **Use Parameterized Queries**: Always use parameterized database queries
3. **Validate All Inputs**: Validate and sanitize all user inputs
4. **Keep Dependencies Updated**: Regularly update security-related packages
5. **Use HTTPS**: Always use HTTPS in production

### For Users

1. **Secure Credentials**: Keep your `.env` file secure and never share it
2. **Regular Updates**: Keep the application updated
3. **Monitor Activity**: Check logs for suspicious activity
4. **Strong Passwords**: Use strong, unique passwords
5. **Two-Factor Authentication**: Enable 2FA on your LinkedIn account

## 🔍 Security Checklist

### Pre-Deployment

- [ ] JWT secret key is changed from default
- [ ] All environment variables are properly set
- [ ] HTTPS is configured for production
- [ ] Rate limiting is enabled
- [ ] Security headers are implemented
- [ ] Input validation is comprehensive
- [ ] Error handling is secure
- [ ] Logging excludes sensitive data

### Regular Maintenance

- [ ] Security dependencies are updated
- [ ] Security logs are reviewed
- [ ] Failed login attempts are monitored
- [ ] Rate limit violations are investigated
- [ ] Security tests are run regularly

## 📚 Additional Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [JWT Security Best Practices](https://auth0.com/blog/a-look-at-the-latest-draft-for-jwt-bcp/)
- [Rate Limiting Strategies](https://cloud.google.com/architecture/rate-limiting-strategies-techniques)

---

**Remember**: Security is an ongoing process. Regularly review and update security measures to protect against new threats. 