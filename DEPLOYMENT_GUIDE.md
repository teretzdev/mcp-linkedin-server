# 🚀 Deployment Guide - LinkedIn Job Hunter

This guide covers production deployment, environment setup, monitoring, and maintenance for the LinkedIn Job Hunter application.

## 📋 Pre-Deployment Checklist

### Environment Requirements

- [ ] Python 3.8+ installed
- [ ] Node.js 16+ installed
- [ ] Git installed
- [ ] Windows 10/11 (tested environment)
- [ ] Sufficient disk space (minimum 2GB)
- [ ] Stable internet connection

### Security Requirements

- [ ] JWT secret key configured
- [ ] Environment variables set
- [ ] HTTPS certificate (for production)
- [ ] Firewall rules configured
- [ ] Rate limiting enabled
- [ ] Security headers implemented

### Dependencies

- [ ] Python dependencies installed
- [ ] Node.js dependencies installed
- [ ] Playwright browsers installed
- [ ] Database initialized (if using)

## 🏗️ Production Deployment

### 1. Environment Setup

#### Clone Repository
```bash
git clone <repository-url>
cd mcp-linkedin-server
```

#### Create Virtual Environment
```bash
# Create virtual environment
python -m venv env

# Activate (Windows)
env\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt
```

#### Install Node.js Dependencies
```bash
# Install frontend dependencies
npm install

# Install Playwright browsers
npx playwright install
```

### 2. Configuration

#### Environment Variables
Create a production `.env` file:

```bash
# LinkedIn Credentials
LINKEDIN_USERNAME=your_email@example.com
LINKEDIN_PASSWORD=your_secure_password

# Security Configuration
JWT_SECRET_KEY=your-super-secret-production-key
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
RATE_LIMIT_REQUESTS_PER_MINUTE=100
ENCRYPTION_KEY=your-production-encryption-key

# Application Configuration
DEBUG_MODE=false
LOG_LEVEL=INFO
PORT=8001
FRONTEND_PORT=3000

# Database Configuration (if using)
DATABASE_URL=sqlite:///./linkedin_jobs.db

# Monitoring
ENABLE_MONITORING=true
LOG_FILE_PATH=./logs/app.log
```

#### Security Configuration
```bash
# Generate secure keys
python -c "import secrets; print(secrets.token_urlsafe(32))"
python -c "import secrets; print(secrets.token_hex(32))"
```

### 3. Service Deployment

#### Automated Deployment Script
```bash
# Run automated deployment
python deploy.py --environment production
```

#### Manual Deployment Steps

1. **Start MCP Server**
   ```bash
   # Terminal 1: Start MCP Server
   python linkedin_browser_mcp.py --production
   ```

2. **Start API Bridge**
   ```bash
   # Terminal 2: Start API Bridge
   python api_bridge.py --production
   ```

3. **Start Frontend**
   ```bash
   # Terminal 3: Start React Frontend
   npm run build
   npm start --production
   ```

### 4. Process Management

#### Using PM2 (Recommended)
```bash
# Install PM2
npm install -g pm2

# Create PM2 configuration
cat > ecosystem.config.js << EOF
module.exports = {
  apps: [
    {
      name: 'linkedin-mcp',
      script: 'linkedin_browser_mcp.py',
      interpreter: 'python',
      env: {
        NODE_ENV: 'production'
      }
    },
    {
      name: 'linkedin-api',
      script: 'api_bridge.py',
      interpreter: 'python',
      env: {
        NODE_ENV: 'production'
      }
    },
    {
      name: 'linkedin-frontend',
      script: 'npm',
      args: 'start',
      cwd: './',
      env: {
        NODE_ENV: 'production'
      }
    }
  ]
};
EOF

# Start all services
pm2 start ecosystem.config.js

# Monitor services
pm2 monit

# View logs
pm2 logs
```

#### Using Windows Services
```bash
# Create Windows service scripts
python create_windows_services.py
```

## 🔧 Configuration Management

### Environment-Specific Configs

#### Development
```bash
# development.env
DEBUG_MODE=true
LOG_LEVEL=DEBUG
RATE_LIMIT_REQUESTS_PER_MINUTE=1000
```

#### Staging
```bash
# staging.env
DEBUG_MODE=false
LOG_LEVEL=INFO
RATE_LIMIT_REQUESTS_PER_MINUTE=500
```

#### Production
```bash
# production.env
DEBUG_MODE=false
LOG_LEVEL=WARNING
RATE_LIMIT_REQUESTS_PER_MINUTE=100
```

### Configuration Validation
```bash
# Validate configuration
python validate_config.py --environment production
```

## 📊 Monitoring & Logging

### Application Monitoring

#### Health Checks
```bash
# Health check endpoint
curl http://localhost:8001/api/health

# System status
curl http://localhost:8001/api/status
```

#### Performance Monitoring
```python
# performance_monitor.py
import psutil
import time
import logging

class PerformanceMonitor:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def monitor_system(self):
        cpu_percent = psutil.cpu_percent()
        memory_percent = psutil.virtual_memory().percent
        disk_percent = psutil.disk_usage('/').percent
        
        self.logger.info(f"CPU: {cpu_percent}%, Memory: {memory_percent}%, Disk: {disk_percent}%")
        
        if cpu_percent > 80 or memory_percent > 80:
            self.logger.warning("High resource usage detected")
```

### Logging Configuration

#### Log Format
```python
# logging_config.py
import logging
import logging.handlers

def setup_logging():
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # File handler
    file_handler = logging.handlers.RotatingFileHandler(
        'logs/app.log',
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setFormatter(formatter)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
```

#### Log Rotation
```bash
# logrotate configuration
/path/to/mcp-linkedin-server/logs/*.log {
    daily
    missingok
    rotate 7
    compress
    delaycompress
    notifempty
    create 644 user group
}
```

## 🔄 Backup & Recovery

### Data Backup

#### Automated Backup Script
```python
# backup_manager.py
import shutil
import os
import datetime
import zipfile

class BackupManager:
    def __init__(self, backup_dir="backups"):
        self.backup_dir = backup_dir
        os.makedirs(backup_dir, exist_ok=True)
    
    def create_backup(self):
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"linkedin_jobs_backup_{timestamp}"
        
        # Create backup directory
        backup_path = os.path.join(self.backup_dir, backup_name)
        os.makedirs(backup_path, exist_ok=True)
        
        # Backup database
        if os.path.exists("linkedin_jobs.db"):
            shutil.copy2("linkedin_jobs.db", backup_path)
        
        # Backup configuration
        if os.path.exists(".env"):
            shutil.copy2(".env", backup_path)
        
        # Backup logs
        if os.path.exists("logs"):
            shutil.copytree("logs", os.path.join(backup_path, "logs"))
        
        # Create zip archive
        zip_path = f"{backup_path}.zip"
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(backup_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, backup_path)
                    zipf.write(file_path, arcname)
        
        # Clean up temporary directory
        shutil.rmtree(backup_path)
        
        return zip_path
```

#### Scheduled Backups
```bash
# Windows Task Scheduler
schtasks /create /tn "LinkedInBackup" /tr "python backup_manager.py" /sc daily /st 02:00

# Or use cron (if available)
0 2 * * * cd /path/to/mcp-linkedin-server && python backup_manager.py
```

### Recovery Procedures

#### Database Recovery
```python
# recovery_manager.py
import sqlite3
import shutil
import os

class RecoveryManager:
    def restore_database(self, backup_path):
        if os.path.exists(backup_path):
            # Stop services
            self.stop_services()
            
            # Restore database
            shutil.copy2(backup_path, "linkedin_jobs.db")
            
            # Start services
            self.start_services()
            
            return True
        return False
```

## 🔧 Maintenance Procedures

### Regular Maintenance

#### Daily Tasks
- [ ] Check application logs for errors
- [ ] Monitor system resources
- [ ] Verify service health
- [ ] Check backup completion

#### Weekly Tasks
- [ ] Review security logs
- [ ] Update dependencies
- [ ] Clean old log files
- [ ] Performance analysis

#### Monthly Tasks
- [ ] Security audit
- [ ] Database optimization
- [ ] Configuration review
- [ ] Disaster recovery test

### Update Procedures

#### Application Updates
```bash
# Update application
git pull origin main

# Update dependencies
pip install -r requirements.txt --upgrade
npm update

# Restart services
pm2 restart all
```

#### Dependency Updates
```bash
# Update Python packages
pip list --outdated
pip install --upgrade package_name

# Update Node.js packages
npm outdated
npm update
```

## 🚨 Troubleshooting

### Common Issues

#### Service Won't Start
```bash
# Check port availability
netstat -ano | findstr :8001
netstat -ano | findstr :3000

# Check process status
tasklist | findstr python
tasklist | findstr node

# Check logs
tail -f logs/app.log
```

#### Performance Issues
```bash
# Monitor system resources
python performance_monitor.py

# Check memory usage
python -c "import psutil; print(psutil.virtual_memory())"

# Check disk space
python -c "import psutil; print(psutil.disk_usage('/'))"
```

#### Security Issues
```bash
# Check security logs
grep -i "error\|warning\|failed" logs/app.log

# Validate configuration
python validate_config.py --security

# Run security tests
python test_runner.py --category security
```

### Emergency Procedures

#### Service Recovery
```bash
# Emergency restart
pm2 restart all

# Manual restart
python emergency_restart.py
```

#### Data Recovery
```bash
# Restore from backup
python recovery_manager.py --restore latest

# Database repair
python database_repair.py
```

## 📈 Scaling Considerations

### Horizontal Scaling
- Load balancer configuration
- Multiple service instances
- Database clustering
- Cache implementation

### Vertical Scaling
- Resource allocation optimization
- Performance tuning
- Memory management
- CPU optimization

## 🔒 Security Hardening

### Production Security Checklist

- [ ] HTTPS enabled
- [ ] Firewall configured
- [ ] Rate limiting active
- [ ] Security headers set
- [ ] Input validation enabled
- [ ] Error handling secure
- [ ] Logging configured
- [ ] Backup encryption
- [ ] Access control implemented
- [ ] Monitoring active

### Security Monitoring
```python
# security_monitor.py
class SecurityMonitor:
    def monitor_failed_logins(self):
        # Monitor failed login attempts
        pass
    
    def monitor_rate_limit_violations(self):
        # Monitor rate limit violations
        pass
    
    def monitor_suspicious_activity(self):
        # Monitor suspicious patterns
        pass
```

## 📚 Additional Resources

- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [PM2 Documentation](https://pm2.keymetrics.io/docs/)
- [Windows Service Management](https://docs.microsoft.com/en-us/windows/win32/services/services)
- [Logging Best Practices](https://docs.python.org/3/howto/logging.html)

---

**Remember**: Regular maintenance and monitoring are essential for a stable production deployment. Keep backups current and test recovery procedures regularly. 