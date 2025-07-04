# 🚀 LinkedIn Job Hunter - Quick Start Guide

## 🎯 Get Started in 5 Minutes

This guide will help you get the LinkedIn Job Hunter application running quickly with the latest fixes.

## 📋 Prerequisites

- **Python 3.8+** - [Download here](https://www.python.org/downloads/)
- **Node.js 16+** - [Download here](https://nodejs.org/)
- **LinkedIn Account** - For job searching and applications

## 🚀 Quick Setup

### Option 1: Automated Setup (Recommended)

1. **Run the quick setup script:**
   ```bash
   python quick_setup.py
   ```

2. **Edit your credentials:**
   - Open the `.env` file
   - Add your LinkedIn email and password
   - Add your Gemini API key (optional, for AI features)

3. **Start the application:**
   ```bash
   python auto_startup.py
   ```

### Option 2: Manual Setup

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Install Node.js dependencies:**
   ```bash
   npm install
   ```

3. **Install Playwright browsers:**
   ```bash
   python -m playwright install chromium
   ```

4. **Create environment file:**
   ```bash
   python create_env.py
   ```

5. **Edit .env file with your credentials**

6. **Start the application:**
   ```bash
   python auto_startup.py
   ```

## 🔧 What Was Fixed

### ✅ Critical Issues Resolved

1. **psutil Windows Compatibility**
   - Fixed the "invalid attr name 'connections'" error
   - Added proper Windows-specific API handling

2. **Node.js Installation Check**
   - Added automatic Node.js detection
   - Automatic npm dependency installation
   - Clear error messages if Node.js is missing

3. **Environment Setup**
   - Improved .env file creation
   - Added missing configuration options
   - Better error handling

4. **Missing Dependencies**
   - Added `google-generativeai` to requirements.txt
   - Fixed dependency conflicts

## 🧪 Test the Fixes

Run the test script to verify everything is working:

```bash
python test_startup_fixes.py
```

## 🎯 Expected Behavior

After running `python auto_startup.py`, you should see:

```
2025-07-03 21:32:59,392 - INFO - Starting LinkedIn Job Hunter - Automated Mode
2025-07-03 21:32:59,395 - INFO - Node.js and npm are properly installed
2025-07-03 21:32:59,400 - INFO - Successfully installed npm dependencies
2025-07-03 21:32:59,405 - INFO - Successfully created .env file
2025-07-03 21:33:00,395 - INFO - Starting API Bridge on port 8001...
2025-07-03 21:33:05,558 - INFO - API Bridge started successfully
2025-07-03 21:33:06,562 - INFO - Starting MCP Backend on port 8002...
2025-07-03 21:33:10,696 - INFO - MCP Backend started successfully
2025-07-03 21:33:11,700 - INFO - Starting LLM Controller on port 8003...
2025-07-03 21:33:15,842 - INFO - LLM Controller started successfully
2025-07-03 21:33:16,851 - INFO - Starting React frontend on port 3000...
2025-07-03 21:33:25,881 - INFO - React frontend started successfully on port 3000
2025-07-03 21:33:25,881 - INFO - All services started successfully!
```

## 🌐 Access the Application

Once all services are running:

- **Dashboard:** http://localhost:3000
- **API Bridge:** http://localhost:8001
- **Health Check:** http://localhost:8001/api/health

## 🔧 Troubleshooting

### Common Issues

1. **"Node.js not found"**
   - Install Node.js from https://nodejs.org/
   - Make sure it's added to your PATH

2. **"npm install failed"**
   - Check your internet connection
   - Try running as administrator
   - Clear npm cache: `npm cache clean --force`

3. **"Port already in use"**
   - The script will automatically find available ports
   - Or manually kill processes using those ports

4. **"LinkedIn login failed"**
   - Check your credentials in the .env file
   - Make sure 2FA is disabled or use app passwords
   - Try logging in manually to LinkedIn first

### Getting Help

1. **Check the logs** in `startup.log`
2. **Run the test script:** `python test_startup_fixes.py`
3. **Check the gaps analysis:** `CODEBASE_GAPS_ANALYSIS.md`

## 🎉 Success!

Once you see "All services started successfully!", you can:

1. **Open your browser** to http://localhost:3000
2. **Configure your credentials** in the Settings page
3. **Start job searching** and applying!

## 📚 Next Steps

- Read the full documentation in `README.md`
- Check out the advanced features in the dashboard
- Review the gaps analysis for future improvements

---

**Need help?** Check the troubleshooting section above or review the comprehensive gaps analysis document. 