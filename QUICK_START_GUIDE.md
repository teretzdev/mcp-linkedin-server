# 🚀 Quick Start Guide - LinkedIn Job Hunter

Get the LinkedIn Job Hunter up and running in minutes with this comprehensive quick start guide.

## Unified Startup & Management

All startup, port cleanup, and service management is now handled through a single menu:

```
python manage.py
```

Use the arrow keys to select actions. All previous .bat files have been removed.

## ⚡ Super Quick Start (Recommended)

### One-Command Setup
```bash
# Clone and setup everything automatically
git clone <repository-url>
cd mcp-linkedin-server
python create_env.py
.\start_auto.bat
```

That's it! The application will automatically:
- ✅ Install all dependencies
- ✅ Configure your environment
- ✅ Start all services
- ✅ Open the dashboard in your browser

## 📋 Prerequisites Check

Before starting, ensure you have:

### Required Software
- [ ] **Python 3.8+** - [Download here](https://www.python.org/downloads/)
- [ ] **Node.js 16+** - [Download here](https://nodejs.org/)
- [ ] **Git** - [Download here](https://git-scm.com/)

### Quick Verification
```bash
# Check Python
python --version  # Should show 3.8 or higher

# Check Node.js
node --version    # Should show 16 or higher

# Check npm
npm --version     # Should show 8 or higher

# Check Git
git --version     # Should show any recent version
```

## 🛠️ Step-by-Step Setup

### Step 1: Clone the Repository
```bash
git clone <repository-url>
cd mcp-linkedin-server
```

### Step 2: Environment Setup
```bash
# Create virtual environment
python -m venv env

# Activate virtual environment (Windows)
env\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt

# Install Node.js dependencies
npm install
```

### Step 3: Configuration
```bash
# Create environment file with your LinkedIn credentials
python create_env.py
```

This will create a `.env` file. Edit it with your LinkedIn credentials:
```bash
LINKEDIN_USERNAME=your_email@example.com
LINKEDIN_PASSWORD=your_password
```

### Step 4: Start the Application
```bash
# Automated startup (recommended)
.\start_auto.bat

# Or manual startup
python linkedin_browser_mcp.py
python api_bridge.py
npm start
```

## 🧪 Verify Installation

### Quick Health Check
```bash
# Run comprehensive health check
python test_runner.py --category quick
```

Expected output:
```
✅ Python Version: 3.9.7 (Compatible)
✅ Required Dependencies: All installed
✅ Node.js: v16.15.0 (Compatible)
✅ npm: 8.5.5 (Available)
✅ Environment Variables: Configured
✅ Port Availability: All ports free
✅ Services: Ready to start
```

### Test All Features
```bash
# Run all tests
python test_runner.py --category all
```

## 🌐 Access the Application

Once started, access the application at:
- **Dashboard**: http://localhost:3000
- **API Health**: http://localhost:8001/api/health
- **API Docs**: http://localhost:8001/docs

## 🎯 First Steps

### 1. Login to LinkedIn
- The system will automatically log in using your credentials
- Sessions are encrypted and persisted between runs

### 2. Search for Jobs
- Go to "Job Search" in the dashboard
- Enter job keywords and location
- Click "Search Jobs" to find matching positions

### 3. Apply to Jobs
- Click "Apply" on any job card
- The system will attempt Easy Apply for you
- Track your applications in the "Applications" section

### 4. Save Jobs
- Click "Save" on interesting jobs
- View saved jobs in the "Saved Jobs" section
- Get personalized recommendations

## 🔧 Common Issues & Solutions

### Issue 1: Python Not Found
**Error:** `'python' is not recognized`
**Solution:**
```bash
# Add Python to PATH or use full path
C:\Python39\python.exe --version

# Or install Python from python.org
```

### Issue 2: Node.js Not Found
**Error:** `'node' is not recognized`
**Solution:**
```bash
# Install Node.js from nodejs.org
# Or use Node Version Manager (nvm)
```

### Issue 3: Port Already in Use
**Error:** `Port 8001 is already in use`
**Solution:**
```bash
# Use automated startup (handles automatically)
.\start_auto.bat

# Or manually free the port
netstat -ano | findstr :8001
taskkill /PID <PID> /F
```

### Issue 4: Missing Dependencies
**Error:** `ModuleNotFoundError: No module named 'fastapi'`
**Solution:**
```bash
# Install missing dependencies
pip install -r requirements.txt

# Or let automation handle it
python auto_startup.py --auto-install
```

### Issue 5: Login Failed
**Error:** `LinkedIn login failed`
**Solution:**
- Check your credentials in `.env` file
- Ensure 2FA is disabled or use app passwords
- Clear browser cache and try again

## 🚀 Advanced Setup

### Production Setup
```bash
# Production configuration
python create_env.py --environment production

# Start with production settings
python auto_startup.py --config production.json
```

### Development Setup
```bash
# Development configuration
python create_env.py --environment development

# Start with debug mode
python auto_startup.py --debug
```

### Custom Configuration
```bash
# Create custom configuration
python create_env.py --custom

# Edit configuration file
notepad config.json
```

## 📊 Monitoring & Maintenance

### Check Service Status
```bash
# Health check
curl http://localhost:8001/api/health

# Service status
python health_check.py
```

### View Logs
```bash
# Application logs
tail -f logs/app.log

# Startup logs
tail -f startup.log

# Error logs
tail -f logs/error.log
```

### Backup Data
```bash
# Create backup
python backup_manager.py

# Restore from backup
python backup_manager.py --restore latest
```

## 🔒 Security Best Practices

### Credential Security
- ✅ Keep your `.env` file secure
- ✅ Never commit credentials to version control
- ✅ Use strong, unique passwords
- ✅ Enable 2FA on your LinkedIn account

### Application Security
- ✅ Run security tests regularly
- ✅ Keep dependencies updated
- ✅ Monitor logs for suspicious activity
- ✅ Use HTTPS in production

## 📚 Next Steps

### Learn More
- [Full Documentation](README.md)
- [Automation Guide](AUTOMATION_GUIDE.md)
- [Testing Guide](TESTING_GUIDE.md)
- [Security Guide](SECURITY_GUIDE.md)
- [Deployment Guide](DEPLOYMENT_GUIDE.md)

### Advanced Features
- [Application Tracking](docs/application-tracking.md)
- [Analytics Dashboard](docs/analytics.md)
- [API Reference](docs/api-reference.md)
- [Customization Guide](docs/customization.md)

### Troubleshooting
- [Common Issues](docs/troubleshooting.md)
- [Error Codes](docs/error-codes.md)
- [Performance Tuning](docs/performance.md)
- [Support Guide](docs/support.md)

## 🆘 Getting Help

### Quick Support
```bash
# Run diagnostics
python diagnostics.py

# Generate support report
python support_report.py

# Check system requirements
python system_check.py
```

### Documentation
- Check the troubleshooting section above
- Review the comprehensive documentation
- Run tests to identify issues
- Check logs for error details

### Community Support
- Create an issue in the repository
- Check existing issues for solutions
- Review the FAQ section
- Join the community discussions

## 🎉 Success Checklist

You're ready to go when you can:

- [ ] ✅ Application starts without errors
- [ ] ✅ Dashboard loads at http://localhost:3000
- [ ] ✅ LinkedIn login works
- [ ] ✅ Job search functionality works
- [ ] ✅ Easy Apply works for compatible jobs
- [ ] ✅ Application tracking works
- [ ] ✅ All tests pass: `python test_runner.py --category quick`

## 🚀 What's Next?

Now that you're up and running:

1. **Explore the Dashboard** - Familiarize yourself with all features
2. **Set Up Job Preferences** - Configure your job search criteria
3. **Start Job Hunting** - Begin your automated job search
4. **Track Applications** - Monitor your application progress
5. **Customize Settings** - Adjust automation and notification settings
6. **Learn Advanced Features** - Explore analytics and reporting

---

**Happy Job Hunting! 🎯**

The LinkedIn Job Hunter is now ready to help you automate your job search process. Start exploring and let the automation work for you! 